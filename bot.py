import logging
import toml
from aiogram import Bot, Dispatcher, executor, types
import sticker
import markup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
config = toml.load('config.toml')

bot = Bot(token=config["bot"]["token"])
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    logging.info(f"Chat started: {message.chat.id}")
    await message.answer_sticker(sticker.hi)
    await message.reply("Hello! I can present you recommendations or news of a game. You can click on the button "
                        "or type something to get started.", reply_markup=markup.start_markup)



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
