from aiogram import types

# Mark up for "/start" command
start_markup = types.inline_keyboard.InlineKeyboardMarkup()
start_markup.row(types.inline_keyboard.InlineKeyboardButton(text="🎮️ Game Recommendation",
                                                            callback_data="game_recommendation"))
start_markup.row(types.inline_keyboard.InlineKeyboardButton(text="📰️ News",
                                                            callback_data="game_news"))
start_markup.row(types.inline_keyboard.InlineKeyboardButton(text="💬️ Chit-chat",
                                                            callback_data="start_chit_chat"))

