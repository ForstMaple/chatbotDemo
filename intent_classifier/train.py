import numpy as np
import json
import nltk
from nltk.tokenize import word_tokenize 
from nltk.stem.porter import PorterStemmer
# nltk.download('punkt')

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from model import NeuralNet



torch.manual_seed(123)

ps = PorterStemmer()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

with open('dialogue.json', 'r') as f:
    intents = json.load(f)

all_words = []
tags = []
X_y = []   # in the format: (pattern,tags) 

for intent in intents['intents']:
    tag = intent['tag']
    tags.append(tag)
    
    for pattern in intent['pattern']:
        word = word_tokenize(pattern)
        all_words.extend(word)
        X_y.append((word, tag))
        
stop_words = ['!', '?', ',', '.']
all_words = [ps.stem(word.lower()) for word in all_words if word not in stop_words]
all_words = sorted(set(all_words))  # sorted and remove duplicate
tags = sorted(set(tags))

#%% prepare the training dataset
X_train = []
y_train = []

def bag_of_words(tokenized_sentence, all_words):
    '''
    Example:
        sentence = ['hi', 'good', 'day']
        words =    ['hi', 'hello', 'sorry', 'good', 'bye', 'day']
        bag =      [1,       0,       0,      1,      0,      1]
    '''
    
    tokenized_sentence = [ps.stem(word) for word in tokenized_sentence]
    
    bag = np.zeros(len(all_words), dtype = np.float32)
    
    for idx, word in enumerate(all_words):
        if word in tokenized_sentence:
            bag[idx] = 1.0
    
    return bag


for (pattern, tag) in X_y: 
    bag = bag_of_words(pattern, all_words)
    X_train.append(bag)
    
    label = tags.index(tag) # turn tags into 0, 1, 2, 3...
    y_train.append(label)
    
    
X_train = np.array(X_train)
y_train = np.array(y_train)

#%% Train

class ChatDataset(Dataset):
    def __init__(self):
        self.n_samples = len(X_train)
        self.x_data = X_train
        self.y_data = y_train
        
    def __getitem__(self, index):
        return self.x_data[index], self.y_data[index]
    
    def __len__(self):
        return self.n_samples
    
# define hyperparameter
batch_size = 8
hidden_size = 8
output_size = len(tags)
input_size = len(X_train[0])
learning_rate = 0.001
num_epochs = 800
    
dataset = ChatDataset()
train_loader = DataLoader(dataset = dataset, batch_size = batch_size, shuffle = True)


model = NeuralNet(input_size, hidden_size, output_size).to(device)

# loss and optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr = learning_rate)

for epoch in range(num_epochs):
    for (words, labels) in train_loader:
        words = words.to(device)
        labels = labels.type(torch.LongTensor)
        labels = labels.to(device)
        
        #forward 
        outputs = model(words)
        loss = criterion(outputs, labels)
        
        #backwards and optimizer step
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
    
    if (epoch + 1) % 100 == 0:
        print(f'epoch {epoch + 1}/{num_epochs}, loss = {loss.item(): .4f}')
        
print(f'final loss, loss = {loss.item(): .4f}')


data = {
    'model_state': model.state_dict(),
    'input_size': input_size,
    'hidden_size': hidden_size,
    'output_size': output_size,
    'all_words': all_words,
    'tags': tags}

FILE = 'data.pth'
torch.save(data, FILE)


    



    
