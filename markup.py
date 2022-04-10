from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from game import genre_tags, theme_tags, special_tags

# Markup for "/start" command
start_markup = InlineKeyboardMarkup()
start_markup.row(InlineKeyboardButton(text="🎮️ Game Query & Recommendation", callback_data="game_query_0"))
start_markup.row(InlineKeyboardButton(text="🗄 Game Recommendation by Filtering", callback_data="game_filtering_0"))
start_markup.row(InlineKeyboardButton(text="❓️ Help", callback_data="help"))

# Markup for cancel button
cancel_markup = InlineKeyboardMarkup()
cancel_markup.row(InlineKeyboardButton(text="Cancel", callback_data="main_menu"))

# Markup for filters
filters_markup = InlineKeyboardMarkup()
filters_markup.row(InlineKeyboardButton(text="Platform", callback_data="filter_platform_100"))
filters_markup.insert(InlineKeyboardButton(text="Number Player", callback_data="filter_player_100"))
filters_markup.row(InlineKeyboardButton(text="Year of Release", callback_data="filter_year_100"))
filters_markup.insert(InlineKeyboardButton(text="Genre", callback_data="filter_genre_100"))
filters_markup.row(InlineKeyboardButton(text="Theme", callback_data="filter_theme_100"))
filters_markup.insert(InlineKeyboardButton(text="Special Requirement", callback_data="filter_special_100"))
filters_markup.row(InlineKeyboardButton(text="✅️ Done", callback_data="done"))
filters_markup.row(InlineKeyboardButton(text="🏠️ Main Menu", callback_data="main_menu"))

# Markup for platform filters
platform_markup = InlineKeyboardMarkup()
platform_markup.row(InlineKeyboardButton(text="Windows", callback_data="filter_platform_windows"))
platform_markup.row(InlineKeyboardButton(text="Mac", callback_data="filter_platform_mac"))
platform_markup.row(InlineKeyboardButton(text="Linux", callback_data="filter_platform_linux"))
platform_markup.row(InlineKeyboardButton(text="🔙 Back", callback_data="game_filtering_0"))

# Markup for player filters
player_markup = InlineKeyboardMarkup()
player_markup.row(InlineKeyboardButton(text="Single-Player", callback_data="filter_player_Single-Player"))
player_markup.row(InlineKeyboardButton(text="Multi-Player", callback_data="filter_player_Multi-Player"))
player_markup.row(InlineKeyboardButton(text="🔙 Back", callback_data="game_filtering_0"))

# Markup for year filters
year_markup = InlineKeyboardMarkup()
year_markup.row(InlineKeyboardButton(text="Before 2010", callback_data="filter_year_Before 2010"))
year_markup.row(InlineKeyboardButton(text="2010-2014", callback_data="filter_year_2010-2014"))
year_markup.row(InlineKeyboardButton(text="2015-2019", callback_data="filter_year_2015-2019"))
year_markup.row(InlineKeyboardButton(text="🔙 Back", callback_data="game_filtering_0"))

# Markup for genre filters
genre_markup = InlineKeyboardMarkup()
for i, tag in enumerate(genre_tags):
    if i % 3 == 0:
        genre_markup.row(InlineKeyboardButton(text=tag.capitalize(), callback_data="filter_genre_" + str(i)))
    else:
        genre_markup.insert(InlineKeyboardButton(text=tag.capitalize(), callback_data="filter_genre_" + str(i)))
genre_markup.row(InlineKeyboardButton(text="🔙 Back", callback_data="game_filtering_0"))

# Markup for theme filters
theme_markup = InlineKeyboardMarkup()
for i, tag in enumerate(theme_tags):
    if i % 3 == 0:
        theme_markup.row(InlineKeyboardButton(text=tag.capitalize(), callback_data="filter_theme_" + str(i)))
    else:
        theme_markup.insert(InlineKeyboardButton(text=tag.capitalize(), callback_data="filter_theme_" + str(i)))
theme_markup.row(InlineKeyboardButton(text="🔙 Back", callback_data="game_filtering_0"))

# Markup for special filters
special_markup = InlineKeyboardMarkup()
for i, tag in enumerate(special_tags):
    if i % 3 == 0:
        special_markup.row(InlineKeyboardButton(text=tag.capitalize(), callback_data="filter_special_" + str(i)))
    else:
        special_markup.insert(InlineKeyboardButton(text=tag.capitalize(), callback_data="filter_special_" + str(i)))
special_markup.row(InlineKeyboardButton(text="🔙 Back", callback_data="game_filtering_0"))

