import logging
from aiogram import types
import faiss
import numpy as np
import requests
import spacy
from load_data import load_game_data, load_embeddings_data

logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)

games_by_row = load_game_data()
games_by_appid = load_game_data().set_index("appid")

embeddings = load_embeddings_data()

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

nlp = spacy.load('en_stsb_roberta_base')

steam_api = "https://store.steampowered.com/api/appdetails?appids={}&cc={}"


class Game(object):
    def __init__(self, appid, name, release_date, developer, platforms, num_ratings, positive_rate, url=None):
        self._appid = appid
        self._name = name
        self._release_date = release_date
        self._developer = developer
        self._platforms = platforms
        self._num_ratings = num_ratings
        self._positive_rate = positive_rate
        self._url = f"https://store.steampowered.com/app/{appid}/" if url is None else url
        self._price = None

    def get_price(self):
        global steam_api
        resp = requests.get(steam_api.format(self._appid, "sg"))
        data = resp.json()
        if data[str(self._appid)]["success"]:
            game_details = data[str(self._appid)]["data"]
            logging.info(f"Details retrieved for {self._name}")

            if game_details["is_free"]:
                self._price = "Free"
            else:
                self._price = game_details["price_overview"]["final_formatted"]
                if game_details["price_overview"]["discount_percent"] > 0:
                    self._price += f" ({game_details['price_overview']['discount_percent']}% off)"
        else:
            logging.error(f"Game details of {self._name} not found")
            return

    def format_introduction(self):
        intro = f"**Game Name:** {self._name}\n" \
                f"**Release Date:** {self._release_date}\n" \
                f"**Developer:** {self._developer if self._developer else 'N/A'}\n" \
                f"**Supported Platform(s):** {' '.join([s.capitalize() for s in self._platforms.split(';')])}\n" \
                f"**Positive Ratings**: {self._positive_rate:.2%} ({self._num_ratings} reviews)\n\n" \
                f"**Current Price**: {self._price}\n\n" \
                f"[See *{self._name}* on Steam]({self._url})"
        return intro


def game_object_creator():
    def create_game(row=None, appid=None):
        global games_by_row, games_by_appid
        if row is not None:
            game = games_by_row.iloc[row]
        if appid is not None:
            game = games_by_appid.loc[appid]

        return Game(game["appid"], game["name"], game["release_date"],
                    game["developer"], game["platforms"], game["num_ratings"], game["positive_rate"])
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


def create_game_markup(game_choices):
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    for i, game in enumerate(game_choices):
        markup.row(types.inline_keyboard.InlineKeyboardButton(text=game._name,
                                                              callback_data=f"Option_{i}"))
    markup.row(types.inline_keyboard.InlineKeyboardButton(text="🔙 Back", callback_data="game_query_0"))
    markup.insert(types.inline_keyboard.InlineKeyboardButton(text="🏠️ Main Menu", callback_data="main_menu"))
    return markup
