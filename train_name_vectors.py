#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import spacy_sentence_bert
from load_data import load_game_data


if __name__ == '__main__':
    games = load_game_data()
    nlp = spacy_sentence_bert.load_model('en_stsb_roberta_base')

    data = games["name"].apply(lambda x: nlp(str(x).lower()))
    vectors = data.apply(lambda x: x.vector)
    np.save("data/embeddings.npy", np.array(vectors.to_list()))
