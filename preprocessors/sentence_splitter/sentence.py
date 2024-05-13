import os
from sentence_transformers import SentenceTransformer
import nltk
import re
from tqdm import tqdm
import csv


BASE_OUTPUT_DIR = "collection"

VISTO_DIR = f"{BASE_OUTPUT_DIR}/visto"
CONSIDERANDO_DIR = f"{BASE_OUTPUT_DIR}/considerando"
RESUELVE_DIR = f"{BASE_OUTPUT_DIR}/resuelve"
DISPONE_DIR = f"{BASE_OUTPUT_DIR}/dispone"

def split_sentences(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('º.-', ':').replace('.-', '.')
    return es_tokenizer.tokenize(text)


def save_file(filename, sentences):
    file = filename.replace('.txt', '.csv')
    with open(file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(sentences)


def split_sentences_from_dir(dir):
    if not os.path.exists(dir + '/sentences'):
        os.mkdir(dir + '/sentences')
    for file in tqdm(os.listdir(dir)):
        if file.endswith('.txt'):
            with open(dir + '/' + file, 'r') as f:
                text = f.read()
                sentences = split_sentences(text)
                save_file(dir + '/sentences/' + file, sentences)


nltk.download('punkt')
es_tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")
model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')

split_sentences_from_dir(VISTO_DIR)
split_sentences_from_dir(CONSIDERANDO_DIR)
split_sentences_from_dir(DISPONE_DIR)
split_sentences_from_dir(RESUELVE_DIR)
