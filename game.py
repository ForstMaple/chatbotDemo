import logging
from aiogram import types
from load_data import load_game_data, load_embeddings_data
import faiss
import numpy as np
import spacy
from load_data import load_game_data

logger = logging.getLogger("bot." + __name__)

games_by_row = load_game_data()
games_by_appid = load_game_data().set_index("appid")
embeddings = load_embeddings_data()
index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)


nlp = spacy.load('en_stsb_roberta_base')


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
        logger.info(f"Candidates: {candidates}")
        game_choices = [create_game(row=candidate) for candidate in candidates]
        
        return game_choices

    return create_game_choices


create_game_choices = game_choice_creator()


def create_game_markup(game_choices):
    markup = types.inline_keyboard.InlineKeyboardMarkup()
    for i, game in enumerate(game_choices):
        logger.info(f"{index} {game._name}")
        markup.row(types.inline_keyboard.InlineKeyboardButton(text=game._name,
                                                              callback_data=f"Option_{i}"))
    return markup
