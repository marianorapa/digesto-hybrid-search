import os
from typing import List
from sentence_transformers import SentenceTransformer
import nltk
import re
import csv
import logging
from utils.file_eraser import erase_file_from_everywhere
from utils.objects.document import Document
from utils.objects.metadata import Metadata

config = os.environ
extract_sections_metadata = None
sentences_metadata = None

logger = logging.getLogger("digesto-hybrid-search-logger")

nltk.download('punkt')
es_tokenizer = nltk.data.load("tokenizers/punkt/spanish.pickle")

def init_metadata():
    global extract_sections_metadata, sentences_metadata
    extract_sections_metadata = Metadata(config["EXTRACT_SECTIONS_META_FILE"]).load()
    sentences_metadata = Metadata(config["SENTENCES_META_FILE"])


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
    sentences_directory = sentences_dir(dir)
    if not os.path.exists(sentences_directory):
        os.mkdir(sentences_directory)
    
    documents_directory = documents_dir(dir)
    for file in os.listdir(documents_directory):
        if file.endswith('.txt'):
            with open(documents_directory + '/' + file, 'r') as f:
                text = f.read()
                sentences = split_sentences_from_text(es_tokenizer, text)

                if len(sentences) <= 0:
                    logger.error("File without sentences {dir}/{file}")
                    erase_file_from_everywhere(file, "NO_SENTENCES")
                    
                save_file(sentences_directory + '/' + file, sentences)

def split_sentences_from_doc(doc: Document):
    
    sentences = split_sentences_from_text(es_tokenizer, doc.get_text_content())
    if len(sentences) <= 0:
        logging.error("File without sentences {dir}/{file}")
        sentences_metadata.error()
    else:
        save_file(sentences_dir(doc.get_directory()) + '/' + doc.get_file_name(), sentences)
        sentences_metadata.success()

def split_sentences_from_doc_list(documents: List[Document]):
    for document in documents:
        split_sentences_from_doc(document)

def split_sentences():
    logger.info("Sentence Splitter Started")
    
    init_metadata()
    valid_docs = extract_sections_metadata.get_valid_documents()    
    split_sentences_from_doc_list(valid_docs)

    split_sentences_from_dir(es_tokenizer, config["SECTION_VISTO_DIR"])
    split_sentences_from_dir(es_tokenizer, config["SECTION_CONSIDERANDO_DIR"])
    split_sentences_from_dir(es_tokenizer, config["SECTION_DISPONE_DIR"])
    split_sentences_from_dir(es_tokenizer, config["SECTION_RESUELVE_DIR"])
    split_sentences_from_dir(es_tokenizer, config["SECTION_RESOLUTIVA_DIR"])

    sentences_metadata.save()
    logger.info("Sentence Splitter Ended")
