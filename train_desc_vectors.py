import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


if __name__ == "__main__":
    model = SentenceTransformer('sentence-transformers/stsb-roberta-base-v2', device="cuda")

    games = pd.read_csv("data/game_summaries.csv")
    summaries = games["GeneratedText"]
    vectors = summaries.apply(lambda x: model.encode(str(x).lower()))

    np.save("data/summary_vectors.npy", np.array(vectors.to_list()))
