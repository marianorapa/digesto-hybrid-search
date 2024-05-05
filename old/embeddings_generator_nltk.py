import os
from sentence_transformers import SentenceTransformer
import nltk
import re
import numpy as np
from tqdm import tqdm

OUTPUT_DIR = 'embeddings'
INPUT_DIR = '../../raw-digest/'

nltk.download('punkt')
es_tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")
model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')


def create_embeddings(sections):
    return model.encode(sections)


def split_sentences(text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('º.-', ':').replace('.-', '.')
    return es_tokenizer.tokenize(text)


def save_file(filename, suffix, content):

    file_dir = OUTPUT_DIR + '/' + filename.replace('.pdf.txt', '')
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    with open(file_dir + '/' + suffix + '.txt', 'w') as f:
        f.write(str(content))



def average_vector(vectors):
    return np.mean(vectors, axis=0)


def process(dir, filename):
    file_dir = OUTPUT_DIR + '/' + filename.replace('.pdf.txt', '')
    if not os.path.exists(file_dir):
        with open(dir + filename, 'r') as f:
            text = f.read()
            sentences = split_sentences(text)
            save_file(filename, 'sentences', sentences)
            text_embedding = create_embeddings(text)
            save_file(filename, 'text-embedding', text_embedding)
            sentence_embeddings = create_embeddings(sentences)
            avg_sentence_embeddings = average_vector(sentence_embeddings)
            save_file(filename, 'avg-sentence-embeddings', avg_sentence_embeddings)


if __name__ == '__main__':
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for filename in tqdm(os.listdir(INPUT_DIR)):
        process(INPUT_DIR, filename)
