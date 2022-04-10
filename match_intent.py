import json
import logging
import random
import torch
from nltk.tokenize import word_tokenize
from nltk.stem.porter import PorterStemmer
import numpy as np
from intent_classifier.model import NeuralNet

logging.basicConfig(format='%(asctime)s | %(name)s | %(levelname)s | %(message)s', level=logging.INFO)

torch.manual_seed(678)

with open("intent_classifier/responses.json", "r") as fp:
    responses = json.load(fp)

device = "cpu"
data = torch.load('intent_classifier/intent_classifier.pth', map_location=torch.device(device))
logging.info("Loaded intents and the model!")

input_size = data['input_size']
hidden_size = data['hidden_size']
output_size = data['output_size']
all_words = data['all_words']
tags = data['tags']
model_state = data['model_state']

ps = PorterStemmer()

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()


def match_intent(message):
    tokens = word_tokenize(message)
    X = bag_of_words(tokens)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)

    output = model(X)
    _, predicted = torch.max(output, dim=1)
    tag = tags[predicted.item()]

    probs = torch.softmax(output, dim=1)
    prob = probs[0][predicted.item()]

    if prob.item() > 0.48:
        response = random.choice(responses[tag])

    else:
        tag = "apology"
        response = random.choice(responses[tag])

    return tag, response


def bag_of_words(tokenized_sentence):
    """
    Example:
        sentence = ['hi', 'good', 'day']
        words =    ['hi', 'hello', 'sorry', 'good', 'bye', 'day']
        bag =      [1,       0,       0,      1,      0,      1]
    """
    global all_words, ps
    tokenized_sentence = [ps.stem(word) for word in tokenized_sentence]

    bag = np.zeros(len(all_words), dtype=np.float32)

    for idx, word in enumerate(all_words):
        if word in tokenized_sentence:
            bag[idx] = 1.0

    return bag
