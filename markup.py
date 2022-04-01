from aiogram import types

# Markup for "/start" command
start_markup = types.inline_keyboard.InlineKeyboardMarkup()
start_markup.row(types.inline_keyboard.InlineKeyboardButton(text="🎮️ Game Query & Recommendation",
                                                            callback_data="game_query_0"))
start_markup.row(types.inline_keyboard.InlineKeyboardButton(text="🗄 Game Recommendation by Genre",
                                                            callback_data="game_recommendation_genre_0"))
start_markup.row(types.inline_keyboard.InlineKeyboardButton(text="📰️ Latest Games & News",
                                                            callback_data="game_news_0"))
start_markup.row(types.inline_keyboard.InlineKeyboardButton(text="❓️ Help",
                                                            callback_data="help"))

# Markup for cancel button
cancel_markup = types.inline_keyboard.InlineKeyboardMarkup()
cancel_markup.row(types.inline_keyboard.InlineKeyboardButton(text="Cancel",
                                                             callback_data="main_menu"))