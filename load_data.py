import logging
import numpy as np
import pandas as pd

logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)


def load_game_data():
    """
    Loads the steam data from the csv file
    """
    try:
        df = pd.read_csv("data/cleaned_games.csv")
        logging.info("Game data loaded successfully!")
        
        return df
    
    except Exception as e:
        logging.error(f"Error when loading game data: {e}")
    

def load_embedding_data():
    """
    Loads the embeddings data from the numpy file
    """
    try:
        embeddings = np.load("data/embeddings.npy")
        logging.info("Embedding data loaded successfully!")
        
        return embeddings
    
    except Exception as e:
        logging.error(f"Error when loading embedding data: {e}")


def load_summary_data():
    """
    Loads the game description summaries from the csv file
    """
    try:
        df = pd.read_csv("data/game_summaries.csv")
        logging.info("Summary data loaded successfully!")

        return df

    except Exception as e:
        logging.error(f"Error when loading summary data: {e}")


def load_recommendation_data():
    """
    Loads the recommendations from the csv file
    """
    try:
        recommendations = np.load("data/recommendations.npy", allow_pickle=True)
        logging.info("Recommendations data loaded successfully!")

        return recommendations.tolist()

    except Exception as e:
        logging.error(f"Error when loading recommendations data: {e}")