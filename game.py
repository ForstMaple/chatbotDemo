import logging
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
import faiss
import numpy as np
import requests
import spacy_sentence_bert
from load_data import load_game_data, load_embedding_data, load_summary_data, load_recommendation_data

logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)

games = load_game_data()
embeddings = load_embedding_data()
summaries = load_summary_data()
recommendations = load_recommendation_data()

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

nlp = spacy_sentence_bert.load_model('en_stsb_roberta_base')

steam_api = "https://store.steampowered.com/api/appdetails?appids={}&cc={}"


class Game(object):
    def __init__(self, appid, name, year, developer, platforms, num_rating, positive_rate, url=None):
        self._appid = appid
        self._name = name
        self._year = year
        self._developer = developer
        self._platforms = platforms
        self._num_rating = num_rating
        self._positive_rate = positive_rate
        self._url = f"https://store.steampowered.com/app/{appid}/" if url is None else url
        self._price = None

    def get_price(self):
        global steam_api
        resp = requests.get(steam_api.format(self._appid, "sg"))
        data = resp.json()
        try:
            game_details = data[str(self._appid)]["data"]

            logging.info(f"Details retrieved for {self._name}")

            if game_details["is_free"]:
                self._price = "Free"
            else:
                self._price = game_details["price_overview"]["final_formatted"]
                if game_details["price_overview"]["discount_percent"] > 0:
                    self._price += f" ({game_details['price_overview']['discount_percent']}% off)"

        except Exception as e:
            logging.error(f"Error when retrieving price for {self._name}: {e}")
            self._price = "N/A"

    def get_summary(self):
        global summaries

        try:
            summary = summaries.at[self._appid, "GeneratedText"]
            logging.info(f"Summary retrieved for {self._name} ({self._appid})")
            return summary
        except Exception as e:
            logging.error(f"Error when retrieving summary for {self._name} ({self._appid}): {e}")
            return None

    def format_introduction(self):
        intro = f"*Game Name*: {self._name}\n" \
                f"*Year of Release:* {str(int(self._year))}\n" \
                f"*Developer:* {self._developer if self._developer else 'N/A'}\n" \
                f"*Supported Platform(s):* {' '.join([s.capitalize() for s in self._platforms.split(';')])}\n" \
                f"*Positive Ratings:* {self._positive_rate:.2%} ({self._num_rating} reviews)\n\n" \
                f"*Current Price*: {self._price}\n\n" \
                f"[{self._name} on Steam]({self._url})\n\n" \
                f"{self.get_summary()}"
        return intro


def game_object_creator():
    def create_game(row=None, appid=None):
        global games
        if row is not None:
            game = games.iloc[row]
        if appid is not None:
            game = games.set_index("appid").loc[int(appid)]
            game["appid"] = int(appid)

        return Game(game["appid"], game["name"], game["year"],
                    game["developer"], game["platforms"], game["num_rating"], game["positive_rate"])
    return create_game


create_game = game_object_creator()


def game_choice_creator():
    def create_game_choices(user_input, k=5):
        global embeddings, index, nlp, create_game
        input_vec = nlp(str(user_input).lower()).vector
        _, I = index.search(np.array([input_vec]), k)
        candidates = I.tolist()[0]
        logging.info(f"Candidates: {candidates}")
        game_choices = [create_game(row=candidate) for candidate in candidates]
        
        return game_choices

    return create_game_choices


create_game_choices = game_choice_creator()


def create_game_markup(game_choices, prefix="option"):
    markup = InlineKeyboardMarkup()
    for i, game in enumerate(game_choices):
        markup.row(InlineKeyboardButton(text=game._name, callback_data=f"{prefix}_{i}"))
    return markup


def create_recommendations(appid):
    global recommendations, create_game
    appids = recommendations.get(int(appid), None)

    if appids is not None:
        game_recommendations = [create_game(appid=appid) for appid in appids]
    else:
        game_recommendations = None

    return game_recommendations


def create_recommendation_markup(game_recommendations):
    markup = InlineKeyboardMarkup()
    for game in game_recommendations:
        markup.row(InlineKeyboardButton(text=game._name,
                                        callback_data=f"recommendation_{game._appid}"))
    markup.row(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_game_details"))
    markup.insert(InlineKeyboardButton(text="🏠️ Main Menu", callback_data="main_menu"))
    return markup


genre_tags = ['action', 'strategy', 'adventure', 'indie', 'rpg', 'animation & modeling', 'video production', 'casual',
              'simulation', 'racing', 'violent', 'massively multiplayer', 'sports', 'early access', 'gore',
              'utilities', 'design & illustration', 'web publishing', 'education']

theme_tags = ['puzzle', 'anime', 'visual novel', 'horror', 'point & click', 'hidden object', 'fps', 'pixel graphics',
              "shoot 'em up", 'open world', 'survival', 'space', 'arcade', 'female protagonist', 'rts', 'rpgmaker',
              'classic', 'tower defense', 'turn-based', 'card game', 'zombies', 'sci-fi', 'story rich',
              'world war ii', 'fantasy']

special_tags = ["vr", "full controller support", "co-op",
                "competitive", "steam cloud", "2d", "3d",
                "soundtrack", "cross-platform multiplayer"]


def map_tags(filter_type, tag_index):
    if filter_type == "genre":
        tag_index = genre_tags[int(tag_index)]
    elif filter_type == "theme":
        tag_index = theme_tags[int(tag_index)].capitalize()
    elif filter_type == "special":
        tag_index = special_tags[int(tag_index)].capitalize()
    return tag_index.capitalize()


def format_user_filters(user_filters):
    if not user_filters:
        return "You have not set any filters."
    else:
        filter_msg = "You have set the following filters:\n"
        for filter_type, tag_index in user_filters.items():
            filter_msg += f"*{filter_type.capitalize()}*: {map_tags(filter_type, tag_index)}\n"
        return filter_msg


def parse_filter(user_filters):
    global games, create_game

    # Filter out games with 100% positive ratings
    parsed_filters = games["positive_rate"] != 1

    platform = user_filters.get("platform", None)
    if platform is not None:
        parsed_filters = parsed_filters & games["platforms"].str.contains(platform, na=False)

    player = user_filters.get("player", "")
    if player == "Single-Player":
        parsed_filters = parsed_filters & games["player"].isin([0, 2])
    elif player == "Multi-Player":
        parsed_filters = parsed_filters & games["player"].isin([1, 2])
    else:
        pass

    year = user_filters.get("year", "")
    if year == "Before 2010":
        parsed_filters = parsed_filters & (games["year"] < 2010)
    elif year == "2010-2014":
        parsed_filters = parsed_filters & (games["year"] >= 2010) & (games["year"] <= 2014)
    elif year == "2015-2019":
        parsed_filters = parsed_filters & (games["year"] >= 2015) & (games["year"] <= 2019)
    else:
        pass

    genre = user_filters.get("genre", None)
    if genre is not None:
        parsed_filters = parsed_filters & games["genre"].str.contains(f"'{genre}'", na=False)

    theme = user_filters.get("theme", None)
    if theme is not None:
        parsed_filters = parsed_filters & games["theme"].str.contains(f"'{theme}'", na=False)

    special = user_filters.get("special", None)
    if special is not None:
        parsed_filters = parsed_filters & games["special"].str.contains(f"'{special}'", na=False)

    if parsed_filters.sum() == 0:
        return None, None, None, None
    else:
        rows_rating = list(games[parsed_filters].sort_values(by="positive_rating", ascending=False).head(5).index)
        rows_rate = list(games[parsed_filters].sort_values(by="positive_rate", ascending=False).head(5).index)

        games_rating = [create_game(row) for row in rows_rating]
        games_rate = [create_game(row) for row in rows_rate]

        markup_rating = create_game_markup(games_rating, "rating_option")
        markup_rating.row(InlineKeyboardButton(text="Top 5 Positive Ratings", callback_data="sort_by_rating"))
        markup_rating.insert(InlineKeyboardButton(text="Top 5 % Positive Ratings", callback_data="sort_by_rate"))
        markup_rating.row(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_game_filtering"))
        markup_rating.insert(InlineKeyboardButton(text="🏠️ Main Menu", callback_data="main_menu"))

        markup_rate = create_game_markup(games_rate, "rate_option")
        markup_rate.row(InlineKeyboardButton(text="Top 5 Positive Ratings", callback_data="sort_by_rating"))
        markup_rate.insert(InlineKeyboardButton(text="Top 5 % Positive Ratings", callback_data="sort_by_rate"))
        markup_rate.row(InlineKeyboardButton(text="🔙 Back", callback_data="back_to_game_filtering"))
        markup_rate.insert(InlineKeyboardButton(text="🏠️ Main Menu", callback_data="main_menu"))

        return games_rating, games_rate, markup_rating, markup_rate
