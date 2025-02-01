import pyterrier as pt
import logging
import nltk
import os

logger = logging.getLogger("digesto-hybrid-search-logger")

config = os.environ

def create_directories():
    os.makedirs(config["SPARSE_INDEX_VISTO_DIR"], exist_ok = True)
    os.makedirs(config["SPARSE_INDEX_CONSIDERANDO_DIR"], exist_ok = True)
    os.makedirs(config["SPARSE_INDEX_RESUELVE_DIR"], exist_ok = True)
    os.makedirs(config["SPARSE_INDEX_DISPONE_DIR"], exist_ok = True)
    os.makedirs(config["SPARSE_INDEX_RESOLUTIVA_DIR"], exist_ok = True)
    os.makedirs(config["SPARSE_INDEX_COMPLETE_COMPLETE_DIR"], exist_ok = True)
    os.makedirs(config["SPARSE_INDEX_COMPLETE_DISPONE_DIR"], exist_ok = True)
    os.makedirs(config["SPARSE_INDEX_COMPLETE_RESUELVE_DIR"], exist_ok = True)

def index_directory(INPUT_DIR, OUTPUT_DIR, stopwords):

    #print(stopwords)
    
    indexer = pt.FilesIndexer(index_path = OUTPUT_DIR, 
                          overwrite = True, 
                          verbose = True,
                          stemmer = 'SpanishSnowballStemmer',
                          tokeniser = "utf")
                          #stopwords = stopwords)
    
    # Deuda de comprender más el transfondo de estos parámetros. https://github.com/terrier-org/pyterrier/blob/master/examples/notebooks/non_en_retrieval.ipynb
    
    indexref = indexer.index(INPUT_DIR)


def documents_dir(base_dir: str):
    return base_dir + '/documents'


def terrier_index():
    logger.info("Sparse Indexer Started")

    if not pt.started():
        pt.init()

    nltk.download('stopwords')

    stopwords = nltk.corpus.stopwords.words("spanish")

    index_directory(documents_dir(config["SECTION_VISTO_DIR"]), config["SPARSE_INDEX_VISTO_DIR"], stopwords)
    index_directory(documents_dir(config["SECTION_CONSIDERANDO_DIR"]), config["SPARSE_INDEX_CONSIDERANDO_DIR"], stopwords)
    index_directory(documents_dir(config["SECTION_RESUELVE_DIR"]), config["SPARSE_INDEX_RESUELVE_DIR"], stopwords)
    index_directory(documents_dir(config["SECTION_DISPONE_DIR"]), config["SPARSE_INDEX_DISPONE_DIR"], stopwords)
    index_directory(documents_dir(config["SECTION_RESOLUTIVA_DIR"]), config["SPARSE_INDEX_RESOLUTIVA_DIR"], stopwords)

    index_directory(config["COMPLETE_DIR"], config["SPARSE_INDEX_COMPLETE_COMPLETE_DIR"], stopwords)
    index_directory(config["DISPOSITIONS_DIR"], config["SPARSE_INDEX_COMPLETE_DISPONE_DIR"], stopwords)
    index_directory(config["RESOLUTIONS_DIR"], config["SPARSE_INDEX_COMPLETE_RESUELVE_DIR"], stopwords)

    logger.info("Sparse Indexer Ended")
