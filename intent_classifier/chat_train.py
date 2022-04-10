import random
import json
import torch
from model import NeuralNet
from nltk.tokenize import word_tokenize 
from nltk.stem.porter import PorterStemmer
from train import bag_of_words

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
#%%
with open('../../Intent_matching/dialogue.json', 'r') as f:
    intents = json.load(f)

    
FILE = 'data.pth'
data = torch.load(FILE)

input_size = data['input_size']
hidden_size = data['hidden_size']
output_size = data['output_size']
all_words = data['all_words']
tags = data['tags']
model_state = data['model_state']

model = NeuralNet(input_size, hidden_size, output_size).to(device)
model.load_state_dict(model_state)
model.eval()

#%%
def correction(sentence):
    print(sentence, type(sentence))
    category = input('I am talking about: ')
    
    if category not in tags:
        data = category + ':' + sentence + '\n'
        with open('../../Intent_matching/more_topic.txt', 'a') as f:
            f.write(data)
        
    else:
        with open('../../Intent_matching/dialogue.json', 'w') as f:
            # intents = json.load(f)
            for i in range(len(tags)):
                if intents['intents'][i]['tag'] == category:
                    
                    
                    pattern = intents['intents'][i]['pattern']; print(pattern, type(pattern))
                    pattern_new = pattern + [sentence] ; print(pattern_new)
                    intents['intents'][i]['pattern'] = pattern_new; print(intents['intents'][i]['pattern'])
                    
                    
                    json.dump(intents, f)
                    
        

#%%
bot_name = 'SteamBot'
print("Let's chat! (type 'quit' to exit)")
all_sentence = []
 
while True:
    sentence = input('You: ')
    all_sentence.append(sentence)
    

    if sentence == 'quit':
        break
    
    if sentence == 'call':
        correction(all_sentence[-2])
        break
    
    sentence = word_tokenize(sentence)
    X = bag_of_words(sentence, all_words)
    X = X.reshape(1, X.shape[0])
    X = torch.from_numpy(X).to(device)
    
    output = model(X)
    _, predicted = torch.max(output, dim = 1)
    tag = tags[predicted.item()]
    
    probs = torch.softmax(output, dim = 1)
    pro = probs[0][predicted.item()]
    
    print(probs, pro)
    
    if pro.item() > 0.5:
        for intent in intents['intents']:
            if tag == intent['tag']:
                print(f"{bot_name}: {random.choice(intent['responses'])}")
                
    else:
        # print(f"{bot_name}: I do not understand...")

        print(f"{bot_name}: I do not understand...Could you tell me which category is this topic about?")
        correction(sentence)
        break
    