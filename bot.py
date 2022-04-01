import logging
import pickle
import toml
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from cache_manager import set_user_state, get_user_state, del_user_state
from game import create_game_choices, create_game_markup
import sticker
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
    logging.info(f"Chat ID: {message.chat.id} | Main Menu")


@dp.callback_query_handler(lambda cb: cb.data == "main_menu", state='*')
async def main_menu(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_reply_markup(reply_markup=None)
    await bot.send_message(query.message.chat.id, msg.start_msg, reply_markup=markup.start_markup)
    await state.finish()
    logging.info(f"Chat ID: {query.message.chat.id} | Back to main menu")


@dp.message_handler(commands=['help'], state='*')
async def help_command(message: types.Message, state: FSMContext):
    await message.reply(msg.help_msg, reply_markup=markup.start_markup)
    await state.finish()
    logging.info(f"Chat ID: {message.chat.id} | /help Command")


@dp.callback_query_handler(lambda cb: cb.data == "help", state='*')
async def start_callback(query: types.CallbackQuery, state: FSMContext):
    await query.message.edit_reply_markup(reply_markup=None)
    await bot.send_message(query.message.chat.id, msg.help_msg, reply_markup=markup.start_markup)
    await state.finish()
    logging.info(f"Chat ID: {query.message.chat.id} | Help Callback")


# Game Query - Step 1 - Ask for Input
@dp.callback_query_handler(lambda cb: cb.data == "game_query_0")
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

    await message.reply(msg.confirm_game_input_msg, reply_markup=game_markup)
    await QueryFlow.next()
    set_user_state(message.chat.id, "game_choices", pickle.dumps(game_choices))
    set_user_state(message.chat.id, "game_markup", pickle.dumps(game_markup))
    
    logging.info(f"Chat ID: {message.chat.id} | Game query - Pending confirmation")


# Game Query - Step 3 - Display Game Details
@dp.callback_query_handler(lambda cb: cb.data.startswith("Option_"), state='*')
async def display_game(query: types.CallbackQuery, state: FSMContext):
    game_choices = pickle.loads(get_user_state(query.message.chat.id, "game_choices"))
    game_markup = pickle.loads(get_user_state(query.message.chat.id, "game_markup"))
    game = game_choices[int(query.data.split("_")[1])]
    if not game._price:
        game.get_price()
    await bot.send_message(query.message.chat.id, game.format_introduction(),
                           reply_markup=game_markup,
                           parse_mode="Markdown")
    set_user_state(query.message.chat.id, "game_choices", pickle.dumps(game_choices))


async def on_shutdown(dp):
    
    await dp.storage.close()
    await dp.storage.wait_closed()
    
    logging.info("Storage closed.")
    logging.info("Bot has been shutdown.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)
    
