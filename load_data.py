import logging
import numpy as np
import pandas as pd

logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)

def load_game_data():
    """
    Loads the steam data from the csv file
    """
    try:
        df = pd.read_csv("cleaned_games.csv")
        logging.info("Game data loaded successfully!")
        
        return df
    
    except Exception as e:
        logging.error(f"Error when loading game data: {e}")
    

def load_embeddings_data(scope=None):
    """
    Loads the embeddings data from the numpy file
    """
    try:
        if scope is None:
            embeddings = np.load("embeddings/embeddings.npy")
        elif scope == 100:
            embeddings = np.load("embeddings/embeddings100.npy")
        elif scope == 1000:
            embeddings = np.load("embeddings/embeddings1000.npy")
            
        logging.info("Embedding data loaded successfully!")
        
        return embeddings
    
    except Exception as e:
        logging.error(f"Error when loading embedding data: {e}")