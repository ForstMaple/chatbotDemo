import logging
import pickle
import toml
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types.inline_keyboard import InlineKeyboardButton
from cache_manager import set_user_state, get_user_state, del_user_state
from game import create_game_choices, create_game_markup, create_recommendations, create_recommendation_markup, \
    format_user_filters, parse_filter
from match_intent import match_intent
import markup
import msg

logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)

config = toml.load('config.toml')

bot = Bot(token=config["bot"]["token"])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class QueryFlow(StatesGroup):
    pending_game_input = State()
    pending_game_confirmation = State()
    game_details = State()


@dp.message_handler(commands=['start'], state='*')
async def start_command(message: types.Message, state: FSMContext):
    await message.reply(msg.start_msg, reply_markup=markup.start_markup)
    await state.finish()
    logging.info(f"Chat ID: {message.chat.id} | Start Command - Main Menu")
    del_all_user_states(message.chat.id)


@dp.callback_query_handler(lambda cb: cb.data == "main_menu", state='*')
async def main_menu(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_reply_markup(reply_markup=None)
    await bot.send_message(query.message.chat.id, msg.start_msg, reply_markup=markup.start_markup)
    await state.finish()
    logging.info(f"Chat ID: {query.message.chat.id} | Back to main menu")
    del_all_user_states(query.message.chat.id)


@dp.message_handler(commands=['help'], state='*')
async def help_command(message: types.Message, state: FSMContext):
    await message.reply(msg.help_msg, reply_markup=markup.start_markup, parse_mode="Markdown")
    await state.finish()
    logging.info(f"Chat ID: {message.chat.id} | /help Command")


@dp.callback_query_handler(lambda cb: cb.data == "help", state='*')
async def start_callback(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_reply_markup(reply_markup=None)
    await bot.send_message(query.message.chat.id, msg.help_msg, reply_markup=markup.start_markup, parse_mode="Markdown")
    await state.finish()
    logging.info(f"Chat ID: {query.message.chat.id} | Help Callback")


# Game Query - Step 1 - Ask for Input
@dp.callback_query_handler(lambda cb: cb.data == "game_query_0", state='*')
async def ask_game_input(query: types.CallbackQuery):
    logging.info(f"Chat ID: {query.message.chat.id} | Game query - Started")
    await query.message.edit_reply_markup(reply_markup=None)
    await bot.send_message(query.message.chat.id,
                           msg.ask_game_input_msg,
                           reply_markup=markup.cancel_markup,
                           parse_mode="Markdown")
    
    await QueryFlow.pending_game_input.set()
    
    logging.info(f"Chat ID: {query.message.chat.id} | Game query - Pending game input")


# Game Query - Step 2 - Give & Confirm Options
@dp.message_handler(state=QueryFlow.pending_game_input)
async def process_game_input(message: types.Message, state: FSMContext):
    logging.info(f"Chat ID: {message.chat.id} | Game query - Processing user input")
    logging.info(f"Chat ID: {message.chat.id} | User input: {message.text}")

    game_choices = create_game_choices(message.text)
    game_markup = create_game_markup(game_choices)
    game_markup.row(InlineKeyboardButton(text="🔙 Back", callback_data="game_query_0"))
    game_markup.insert(InlineKeyboardButton(text="🏠️ Main Menu", callback_data="main_menu"))

    await message.reply(msg.confirm_game_input_msg, reply_markup=game_markup)
    await QueryFlow.next()
    set_user_state(message.chat.id, "game_choices", pickle.dumps(game_choices))
    set_user_state(message.chat.id, "game_markup", pickle.dumps(game_markup))
    
    logging.info(f"Chat ID: {message.chat.id} | Game query - Pending confirmation")


# Game Query - Step 3 - Display Game Details
@dp.callback_query_handler(lambda cb: cb.data.startswith("option_"), state='*')
@dp.callback_query_handler(lambda cb: cb.data == "back_to_game_details", state='*')
async def display_game(query: types.CallbackQuery, state: FSMContext):
    if query.data == "back_to_game_details":
        logging.info(f"Chat ID: {query.message.chat.id} | Back to game details from recommendations")
        await query.message.delete()
    else:
        game_choices = pickle.loads(get_user_state(query.message.chat.id, "game_choices"))
        game_markup = pickle.loads(get_user_state(query.message.chat.id, "game_markup"))
        game = game_choices[int(query.data.split("_")[1])]
        game_markup.row(InlineKeyboardButton(text="🤩 Get Recommendations",
                                             callback_data=f"get_recommendation_{game._appid}"))
        game.get_price()

        await bot.edit_message_text(text=game.format_introduction(),
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=game_markup,
                                    parse_mode="Markdown")


# Game Query - Step 4 - Display Recommendations
@dp.callback_query_handler(lambda cb: cb.data.startswith("get_recommendation_"), state='*')
@dp.callback_query_handler(lambda cb: cb.data.startswith("recommendation_"), state='*')
async def display_recommendations(query: types.CallbackQuery, state: FSMContext):
    if query.data.startswith("Get_Recommendation_"):
        appid = query.data.split('_')[2]
        logging.info(f"Chat ID: {query.message.chat.id} | Getting recommendations for appid {appid}")

        game_recommendations = create_recommendations(appid)

        if game_recommendations is None:
            await query.answer("Recommendations not available for this game")
        else:
            recommendation_markup = create_recommendation_markup(game_recommendations)
            game = game_recommendations[0]
            game.get_price()
            await bot.send_message(query.message.chat.id,
                                   text=game.format_introduction(),
                                   reply_markup=recommendation_markup,
                                   parse_mode="Markdown")
            appids = [r._appid for r in game_recommendations]
            set_user_state(query.message.chat.id, "appids", pickle.dumps(appids))
            set_user_state(query.message.chat.id, "game_recommendations", pickle.dumps(game_recommendations))
            set_user_state(query.message.chat.id, "recommendation_markup", pickle.dumps(recommendation_markup))
    else:
        appid = int(query.data.split('_')[1])
        appids = pickle.loads(get_user_state(query.message.chat.id, "appids"))
        recommendation_markup = pickle.loads(get_user_state(query.message.chat.id, "recommendation_markup"))
        option = appids.index(appid)

        logging.info(f"Chat ID: {query.message.chat.id} | Getting recommendations for appid {appid}")

        game_recommendations = pickle.loads(get_user_state(query.message.chat.id, "game_recommendations"))
        game = game_recommendations[option]
        game.get_price()

        await bot.edit_message_text(text=game.format_introduction(),
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=recommendation_markup,
                                    parse_mode="Markdown")


# Recommendation by Filtering - Step 1 - Greeting & Entry
@dp.callback_query_handler(lambda cb: cb.data == "game_filtering_0", state='*')
@dp.callback_query_handler(lambda cb: cb.data == "back_to_game_filtering", state='*')
async def display_filters(query: types.CallbackQuery, state: FSMContext):
    if get_user_state(query.message.chat.id, "user_filters"):
        user_filters = pickle.loads(get_user_state(query.message.chat.id, "user_filters"))
    else:
        user_filters = {}
        set_user_state(query.message.chat.id, "user_filters", pickle.dumps(user_filters))

    logging.info(f"Chat ID: {query.message.chat.id} | Displaying filters | User filters: {user_filters}")

    await bot.edit_message_text(text=msg.display_filter_msg.format(format_user_filters(user_filters)),
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=markup.filters_markup,
                                parse_mode="Markdown")


# Recommendation by Filtering - Step 2 - Set Filters
@dp.callback_query_handler(lambda cb: cb.data.startswith("filter_"), state='*')
async def handle_filters(query: types.CallbackQuery, state: FSMContext):
    filter_type = query.data.split('_')[1]
    filter_value = query.data.split('_')[2]

    logging.info(f"Chat ID: {query.message.chat.id} | Setting filter {filter_type} to {filter_value}")

    user_filters = pickle.loads(get_user_state(query.message.chat.id, "user_filters"))

    if filter_value == "100":
        await bot.edit_message_text(text=msg.filter_msg.format(filter_type, format_user_filters(user_filters)),
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=eval(f"markup.{filter_type}_markup"),
                                    parse_mode="Markdown")
    else:
        user_filters[filter_type] = filter_value
        await bot.edit_message_text(text=msg.filter_msg.format(filter_type, format_user_filters(user_filters)),
                                    chat_id=query.message.chat.id,
                                    message_id=query.message.message_id,
                                    reply_markup=eval(f"markup.{filter_type}_markup"),
                                    parse_mode="Markdown")
        logging.info(f"Chat ID: {query.message.chat.id} | Setting filters | User filters: {user_filters}")
        set_user_state(query.message.chat.id, "user_filters", pickle.dumps(user_filters))


# Recommendation by Filtering - Step 3 - Display Recommendations
@dp.callback_query_handler(lambda cb: cb.data == "done", state='*')
async def display_filtering_results(query: types.CallbackQuery, state: FSMContext):
    user_filters = pickle.loads(get_user_state(query.message.chat.id, "user_filters"))
    logging.info(f"Chat ID: {query.message.chat.id} | Displaying Recommendations | User filters: {user_filters}")
    if not user_filters:
        await query.answer("Please set at least one filter.")
        return

    games_rating, games_rate, markup_rating, markup_rate = parse_filter(user_filters)

    if not games_rating or not games_rate:
        await query.answer("No games match your filters.")
        return

    games_rating[0].get_price()

    await bot.edit_message_text(text=games_rating[0].format_introduction(),
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=markup_rating,
                                parse_mode="Markdown")

    set_user_state(query.message.chat.id, "games_rating", pickle.dumps(games_rating))
    set_user_state(query.message.chat.id, "games_rate", pickle.dumps(games_rate))
    set_user_state(query.message.chat.id, "markup_rating", pickle.dumps(markup_rating))
    set_user_state(query.message.chat.id, "markup_rate", pickle.dumps(markup_rate))


# Recommendation by Filtering - Step 4, - Update Recommendations
@dp.callback_query_handler(lambda cb: cb.data.startswith("sort_by_"), state='*')
@dp.callback_query_handler(lambda cb: cb.data.startswith("rating_option_"), state='*')
@dp.callback_query_handler(lambda cb: cb.data.startswith("rate_option_"), state='*')
async def update_filtering_results(query: types.CallbackQuery, state: FSMContext):
    if query.data.startswith("sort_by_"):
        sort_by = query.data.split('_')[2]
        option = 0
    else:
        sort_by = query.data.split("_")[0]
        option = int(query.data.split("_")[2])

    if sort_by == "rating":
        game = pickle.loads(get_user_state(query.message.chat.id, "games_rating"))[option]
        reply_markup = pickle.loads(get_user_state(query.message.chat.id, "markup_rating"))
    else:
        game = pickle.loads(get_user_state(query.message.chat.id, "games_rate"))[option]
        reply_markup = pickle.loads(get_user_state(query.message.chat.id, "markup_rate"))

    if not game._price:
        game.get_price()

    await bot.edit_message_text(text=game.format_introduction(),
                                chat_id=query.message.chat.id,
                                message_id=query.message.message_id,
                                reply_markup=reply_markup,
                                parse_mode="Markdown")


# New Intent Teaching
@dp.message_handler(commands=["teach"], state="*")
async def teach_new_intent(message: types.Message):
    try:
        if "-t" in message.text:
            logging.info(f"message: {message.text}")
            chunks = message.text.lstrip("/teach").split(" -t ")
            intent, text = chunks[0].strip(), chunks[1].strip()

            with open("intent_classifier/more_topic.txt", "a") as f:
                f.write(f"{intent}:{text}\n")

            await message.reply("Thank you for teaching me! I will be more intelligent in the future.")

            logging.info(f"Chat ID: {message.chat.id} | New Intent & Text Written |Intent: {intent} | Text: {text}")

        else:
            await message.reply("Sorry, I didn't understand your input. "
                                "Please use the following format: /teach <text> -t <intent>")
    except Exception as e:
        logging.error(f"Chat ID: {message.chat.id} | Teaching Intent |Error: {e}")
        await message.reply("Sorry, I didn't understand your input. "
                            "Please use the following format: /teach <text> -t <intent>")


# Enable intent matching
@dp.message_handler(lambda message: message.text)
async def intent_match(message: types.Message):
    intent, response = match_intent(message.text)

    logging.info(f"Chat ID: {message.chat.id} | Matched Intent: {intent}")

    if intent in ["greeting", "goodbay", "thanks", "apology"]:
        await message.reply(response)

    elif intent == "recommendation_query":

        logging.info(f"Chat ID: {message.chat.id} | Game query - Started by Intent Matching")
        await message.reply(msg.ask_game_input_msg,
                            reply_markup=markup.cancel_markup,
                            parse_mode="Markdown")
        await QueryFlow.pending_game_input.set()

    elif intent == "recommendation_cate":
        user_filters = {}
        set_user_state(message.chat.id, "user_filters", pickle.dumps(user_filters))

        logging.info(f"Chat ID: {message.chat.id} | Filtering | User filters: {user_filters}")

        await message.reply(text=msg.display_filter_msg.format(format_user_filters(user_filters)),
                            reply_markup=markup.filters_markup,
                            parse_mode="Markdown")


def del_all_user_states(chat_id):
    try:
        del_user_state(chat_id, "game_choices")
        del_user_state(chat_id, "game_markup")
        del_user_state(chat_id, "appids")
        del_user_state(chat_id, "game_recommendations")
        del_user_state(chat_id, "recommendation_markup")
        del_user_state(chat_id, "user_filters")
        del_user_state(chat_id, "games_rating")
        del_user_state(chat_id, "games_rate")
        del_user_state(chat_id, "markup_rating")
        del_user_state(chat_id, "markup_rate")
        logging.info(f"Chat ID: {chat_id} | All user states deleted")
    except Exception as e:
        logging.error(f"Chat ID: {chat_id} | Error when deleting user states: {e}")


async def on_shutdown(dp):
    
    await dp.storage.close()
    await dp.storage.wait_closed()
    
    logging.info("Storage closed.")
    logging.info("Bot has been shutdown.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)
    
