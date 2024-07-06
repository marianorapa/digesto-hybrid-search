import pyterrier as pt
import os
import nltk

#inputpath = "/home/agustin/digesto-hybrid-search/collection/visto"
#outputpath = "/home/agustin/digesto-hybrid-search/indexes/sparse_indexer/"


BASE_INPUT_DIR = "./collection"

VISTO_INPUT_DIR = f"{BASE_INPUT_DIR}/visto/documents"
CONSIDERANDO_INPUT_DIR = f"{BASE_INPUT_DIR}/considerando/documents"
RESUELVE_INPUT_DIR = f"{BASE_INPUT_DIR}/resuelve/documents"
DISPONE_INPUT_DIR = f"{BASE_INPUT_DIR}/dispone/documents"

COMPLETE_COMPLETE_INPUT_DIR = f"{BASE_INPUT_DIR}/completa"
COMPLETE_RESUELVE_INPUT_DIR = f"{BASE_INPUT_DIR}/completa/resuelve"
COMPLETE_DISPONE_INPUT_DIR = f"{BASE_INPUT_DIR}/completa/dispone"

BASE_OUTPUT_DIR = "./indexes"
SPARSE_OUTPUT_DIR = f"{BASE_OUTPUT_DIR}/sparse_index"

VISTO_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/visto"
CONSIDERANDO_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/considerando"
RESUELVE_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/resuelve"
DISPONE_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/dispone"

COMPLETE_BASE_OUTPUT_DIR = f"{SPARSE_OUTPUT_DIR}/completa"
COMPLETE_COMPLETE_OUTPUT_DIR = f"{COMPLETE_BASE_OUTPUT_DIR}/completa"
COMPLETE_RESUELVE_OUTPUT_DIR = f"{COMPLETE_BASE_OUTPUT_DIR}/resuelve"
COMPLETE_DISPONE_OUTPUT_DIR = f"{COMPLETE_BASE_OUTPUT_DIR}/dispone"

def create_directories():
    if not os.path.exists(BASE_OUTPUT_DIR):
        os.mkdir(BASE_OUTPUT_DIR)
    
    if not os.path.exists(SPARSE_OUTPUT_DIR):
        os.mkdir(SPARSE_OUTPUT_DIR)

    if not os.path.exists(VISTO_OUTPUT_DIR):
        os.mkdir(VISTO_OUTPUT_DIR)

    if not os.path.exists(CONSIDERANDO_OUTPUT_DIR):
        os.mkdir(CONSIDERANDO_OUTPUT_DIR)

    if not os.path.exists(RESUELVE_OUTPUT_DIR):
        os.mkdir(RESUELVE_OUTPUT_DIR)

    if not os.path.exists(DISPONE_OUTPUT_DIR):
        os.mkdir(DISPONE_OUTPUT_DIR)

    if not os.path.exists(COMPLETE_BASE_OUTPUT_DIR):
        os.mkdir(COMPLETE_BASE_OUTPUT_DIR)

    if not os.path.exists(COMPLETE_COMPLETE_OUTPUT_DIR):
        os.mkdir(COMPLETE_COMPLETE_OUTPUT_DIR)

    if not os.path.exists(COMPLETE_RESUELVE_OUTPUT_DIR):
        os.mkdir(COMPLETE_RESUELVE_OUTPUT_DIR)

    if not os.path.exists(COMPLETE_DISPONE_OUTPUT_DIR):
        os.mkdir(COMPLETE_DISPONE_OUTPUT_DIR)


def index_directory(INPUT_DIR, OUTPUT_DIR, stopwords):

    print(stopwords)
    
    indexer = pt.FilesIndexer(index_path = OUTPUT_DIR, 
                          overwrite = True, 
                          verbose = True,
                          stemmer = 'SpanishSnowballStemmer',
                          tokeniser = "utf")
                          #stopwords = stopwords)
    
    # Deuda de comprender más el transfondo de estos parámetros. https://github.com/terrier-org/pyterrier/blob/master/examples/notebooks/non_en_retrieval.ipynb
    
    indexref = indexer.index(INPUT_DIR)



def terrier_index():
    if not pt.started():
        pt.init()

    nltk.download('stopwords')

    stopwords = nltk.corpus.stopwords.words("spanish")

    index_directory(VISTO_INPUT_DIR, VISTO_OUTPUT_DIR, stopwords)
    index_directory(RESUELVE_INPUT_DIR, RESUELVE_OUTPUT_DIR, stopwords)
    index_directory(CONSIDERANDO_INPUT_DIR, CONSIDERANDO_OUTPUT_DIR, stopwords)
    index_directory(DISPONE_INPUT_DIR, DISPONE_OUTPUT_DIR, stopwords)

    index_directory(COMPLETE_COMPLETE_INPUT_DIR, COMPLETE_COMPLETE_OUTPUT_DIR, stopwords)
    index_directory(COMPLETE_RESUELVE_INPUT_DIR, COMPLETE_RESUELVE_OUTPUT_DIR, stopwords)
    index_directory(COMPLETE_DISPONE_INPUT_DIR, COMPLETE_DISPONE_OUTPUT_DIR, stopwords)




terrier_index()