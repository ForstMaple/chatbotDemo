import logging
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

logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s | %(name)s | %(levelname)s | %(message)s')
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(ch)

config = toml.load('config.toml')

bot = Bot(token=config["bot"]["token"])
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


class QueryFlow(StatesGroup):
    pending_game_input = State()
    pending_game_confirmation = State()
    game_details = State()


class RecommendationFlow(StatesGroup):
    pending_game_input = State()
    pending_game_confirmation = State()


@dp.message_handler(state='*', commands=['start'])
@dp.callback_query_handler(lambda cb: cb.data == "main_menu")
async def start_msg(message: types.Message):
    logging.info(f"Chat ID: {message.chat.id} | Main Menu")
    await message.answer_sticker(sticker.hi)
    await message.reply(msg.start, reply_markup=markup.start_markup)


@dp.message_handler(state='*', commands=['help'])
@dp.message_handler(lambda cb: cb.data == "help")
async def help_msg(message: types.Message):
    logger.info(f"Chat ID: {message.chat.id} | Help")
    await message.reply(msg.help_msg, reply_markup=markup.start_markup)


# Game Query - Step 1 - Ask Input
@dp.callback_query_handler(lambda cb: cb.data == "game_query_0")
async def ask_game_input(callback_query: types.CallbackQuery):
    logger.info(f"Chat ID: {callback_query.message.chat.id} | Game query - Started")
    
    await bot.send_sticker(callback_query.message.chat.id, sticker.question)
    await bot.send_message(callback_query.message.chat.id, msg.ask_game_input_msg, reply_markup=markup.cancel_markup, parse_mode="Markdown")
    
    await QueryFlow.pending_game_input.set()
    
    logging.info(f"Chat ID: {callback_query.message.chat.id} | Game query - Pending game input")


@dp.message_handler(state=QueryFlow.pending_game_input)
async def process_game_input(message: types.Message, state: FSMContext):
    logger.info(f"Chat ID: {message.chat.id} | Game query - Processing user input")

    logger.info(f"Chat ID: {message.chat.id} | message: {message.text}")
    chatid = message.chat.id
    game_choices = create_game_choices(message.text)
    game_markup = create_game_markup(game_choices)
    await message.reply(msg.confirm_game_input_msg, reply_markup=game_markup)
    
    await QueryFlow.next()
    
    logger.info(f"Chat ID: {message.chat.id} | Game query - Pending confirmation")


@dp.callback_query_handler(lambda cb: cb.data == "game_recommendation_0")
async def ask_game_input(callback_query: types.CallbackQuery):
    logger.info(f"Chat ID: {callback_query.message.chat.id} | Recommendation by Game - Started")
    
    await bot.send_sticker(callback_query.message.chat.id, sticker.question)
    await bot.send_message(callback_query.message.chat.id, "Please enter a game name!")
    
    await RecommendationFlow.pending_game_input.set()
    
    logger.info(f"Chat ID: {callback_query.message.chat.id} | Recommendation by Game - Pending user input")


async def on_shutdown(dp):
    
    await dp.storage.close()
    await dp.storage.wait_closed()
    
    logger.info("Storage closed.")
    logger.info("Bot has been shutdown.")


if __name__ == '__main__':
    logger = logging.getLogger('bot')
    logger.setLevel(logging.INFO)
    ch.setLevel(logging.INFO)
    executor.start_polling(dp, skip_updates=True, on_shutdown=on_shutdown)
    
