import os
from sentence_transformers import SentenceTransformer
import nltk
import re
from tqdm import tqdm
import csv
import logging
from utils.file_eraser import erase_file_from_everywhere

BASE_OUTPUT_DIR = "./collection"

COMPLETA_RESUELVE_DIR = f"{BASE_OUTPUT_DIR}/completa/resuelve"
COMPLETA_DISPONE_DIR = f"{BASE_OUTPUT_DIR}/completa/dispone"

VISTO_DIR = f"{BASE_OUTPUT_DIR}/visto"
CONSIDERANDO_DIR = f"{BASE_OUTPUT_DIR}/considerando"
RESUELVE_DIR = f"{BASE_OUTPUT_DIR}/resuelve"
DISPONE_DIR = f"{BASE_OUTPUT_DIR}/dispone"

def split_sentences_from_text(es_tokenizer, text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('º.-', ':').replace('.-', '.')
    return es_tokenizer.tokenize(text)


def save_file(filename, sentences):
    file = filename.replace('.txt', '.csv')
    with open(file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(sentences)


def split_sentences_from_dir(es_tokenizer, dir):
    if not os.path.exists(dir + '/sentences'):
        os.mkdir(dir + '/sentences')
    for file in os.listdir(dir):
        if file.endswith('.txt'):
            with open(dir + '/' + file, 'r') as f:
                text = f.read()
                sentences = split_sentences_from_text(es_tokenizer, text)

                if len(sentences) <= 0:
                    logging.error("File without sentences {dir}/{file}")  
                    erase_file_from_everywhere(file, "NO_SENTENCES")
                    
                save_file(dir + '/sentences/' + file, sentences)

def split_sentences():
    logging.info("Sentence Splitter Started")

    nltk.download('punkt')
    es_tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")
    #model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')

    split_sentences_from_dir(es_tokenizer, VISTO_DIR)
    split_sentences_from_dir(es_tokenizer, CONSIDERANDO_DIR)
    split_sentences_from_dir(es_tokenizer, DISPONE_DIR)
    split_sentences_from_dir(es_tokenizer, RESUELVE_DIR)
