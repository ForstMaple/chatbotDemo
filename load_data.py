import logging
import pandas as pd


def load_game_data():
    """
    Loads the steam data from the csv file
    """
    df = pd.read_csv("steam_data.csv")
    return df
