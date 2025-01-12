import os
from typing import List
from sentence_transformers import SentenceTransformer
import nltk
import re
from tqdm import tqdm
import csv
import logging
from utils.file_eraser import erase_file_from_everywhere
from utils.objects.document import Document
from utils.objects.metadata import Metadata

config = os.environ
extract_sections_metadata = Metadata(config["EXTRACT_SECTIONS_META_FILE"])
sentences_metadata = Metadata(config["SENTENCES_META_FILE"])

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

def sentences_dir(base_dir: str):
    return base_dir + '/sentences'

def documents_dir(base_dir: str):
    return base_dir + '/documents'

def split_sentences_from_dir(es_tokenizer, dir):
    sentences_dir = sentences_dir(dir)
    if not os.path.exists(sentences_dir):
        os.mkdir(sentences_dir)
    
    documents_dir = documents_dir(dir)
    for file in os.listdir(documents_dir):
        if file.endswith('.txt'):
            with open(documents_dir + '/' + file, 'r') as f:
                text = f.read()
                sentences = split_sentences_from_text(es_tokenizer, text)

                if len(sentences) <= 0:
                    logging.error("File without sentences {dir}/{file}")  
                    erase_file_from_everywhere(file, "NO_SENTENCES")
                    
                save_file(sentences_dir + '/' + file, sentences)

def split_sentences(doc: Document):
    sentences = doc.get_text_content()
    if len(sentences) <= 0:
        logging.error("File without sentences {dir}/{file}")
        sentences_metadata.error()
    

def split_sentences(documents: List[Document]):
    for document in documents:
        split_sentences(document)

def split_sentences():
    logging.info("Sentence Splitter Started")
    nltk.download('punkt')
    es_tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")

    split_sentences(extract_sections_metadata.get_valid_documents())

    split_sentences_from_dir(es_tokenizer, config["SECTION_VISTO_DIR"])
    split_sentences_from_dir(es_tokenizer, config["SECTION_CONSIDERANDO_DIR"])
    split_sentences_from_dir(es_tokenizer, config["SECTION_DISPONE_DIR"])
    split_sentences_from_dir(es_tokenizer, config["SECTION_RESUELVE_DIR"])
    split_sentences_from_dir(es_tokenizer, config["SECTION_RESOLUTIVA_DIR"])
