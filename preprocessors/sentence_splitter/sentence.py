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

def create_directories():
    os.makedirs(sentences_dir(config["SECTION_VISTO_DIR"]), exist_ok = True)
    os.makedirs(sentences_dir(config["SECTION_CONSIDERANDO_DIR"]), exist_ok=True)
    os.makedirs(sentences_dir(config["SECTION_RESOLUTIVA_DIR"]), exist_ok=True)
    os.makedirs(sentences_dir(config["SECTION_RESUELVE_DIR"]), exist_ok=True)
    os.makedirs(sentences_dir(config["SECTION_DISPONE_DIR"]), exist_ok=True)

def split_sentences_from_text(es_tokenizer, text):
    text = re.sub(r'\s+', ' ', text)
    text = text.replace('º.-', ':').replace('.-', '.')
    return es_tokenizer.tokenize(text)

def save_file(filename, sentences):
    file = filename.replace('.pdf', '.csv')
    with open(file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(sentences)
    return file

def sentences_dir(base_dir: str):
    return base_dir + '/sentences'

def documents_dir(base_dir: str):
    return base_dir + '/documents'

def save_sentences(document: Document, sentences, section_dir):
    if len(sentences) <= 0:
        logging.error(f"File without sentences {section_dir}/{document.cleaned_filename()}")
        raise ValueError("File without sentences")
    else:
        section_sentences_dir = sentences_dir(section_dir)
        return save_file(section_sentences_dir + "/" + document.cleaned_filename(), sentences)

def split_sentences_from_doc(doc: Document):
    try:
        path = save_sentences(doc, doc.get_visto_sentences(es_tokenizer), config["SECTION_VISTO_DIR"])
        doc.set_visto_sentences_path(path)

        path = save_sentences(doc, doc.get_considerando_sentences(es_tokenizer), config["SECTION_CONSIDERANDO_DIR"])
        doc.set_considerando_sentences_path(path)

        path = save_sentences(doc, doc.get_resolutiva_sentences(es_tokenizer), config["SECTION_RESOLUTIVA_DIR"])
        doc.set_resolutiva_sentences_path(path)
        
        if doc.is_resolution():
            path = save_sentences(doc, doc.get_resuelve_sentences(es_tokenizer), config["SECTION_RESUELVE_DIR"])
            doc.set_resuelve_sentences_path(path)
        
        if doc.is_disposition():
            path = save_sentences(doc, doc.get_dispone_sentences(es_tokenizer), config["SECTION_DISPONE_DIR"])
            doc.set_dispone_sentences_path(path)

        sentences_metadata.success(doc)
    except ValueError:
        sentences_metadata.error(doc, "Section without sentences")


def split_sentences_from_doc_list(documents: List[Document]):
    for document in documents:
        split_sentences_from_doc(document)

def split_sentences():
    logger.info("Sentence Splitter Started")

    init_metadata()
    create_directories()

    valid_docs = extract_sections_metadata.get_valid_documents()    
    split_sentences_from_doc_list(valid_docs)

    sentences_metadata.save()
    logger.info("Sentence Splitter Ended")
