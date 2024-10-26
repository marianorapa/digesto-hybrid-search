from sentence_transformers import SentenceTransformer
import faiss
import json
import os
import glob
from utils.url_finder import get_url

BASE_OUTPUT_DIR = "./indexes"
DENSE_OUTPUT_DIR = f"{BASE_OUTPUT_DIR}/dense_index"

VISTO_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/visto"
CONSIDERANDO_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/considerando"
RESUELVE_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/resuelve"
DISPONE_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/dispone"

COMPLETE_DENSE_OUTPUT_DIR = f"{BASE_OUTPUT_DIR}/dense_index/completa"
COMPLETE_COMPLETE_OUTPUT_DIR = f"{COMPLETE_DENSE_OUTPUT_DIR}/completa"
COMPLETE_RESUELVE_OUTPUT_DIR = f"{COMPLETE_DENSE_OUTPUT_DIR}/resuelve"
COMPLETE_DISPONE_OUTPUT_DIR = f"{COMPLETE_DENSE_OUTPUT_DIR}/dispone"

INDEXES = {
        "VISTO": VISTO_OUTPUT_DIR,
        "CONSIDERANDO": CONSIDERANDO_OUTPUT_DIR,
        "RESUELVE": RESUELVE_OUTPUT_DIR,
        "COMPLETE_COMPLETE": COMPLETE_COMPLETE_OUTPUT_DIR,
        "COMPLETE_RESUELVE": COMPLETE_RESUELVE_OUTPUT_DIR,
        "COMPLETE_DISPONE": COMPLETE_DISPONE_OUTPUT_DIR,
}

model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')

def retrieve_index(index_name):
    # lee el indice del archivo -> .bin? 
    index_dir = INDEXES[index_name]
    
    bin_files = glob.glob(os.path.join(index_dir, "*.bin"))
    bin_filename = os.path.basename(bin_files[0])
    index = faiss.read_index(index_dir + '/' + bin_filename)
    metadata_file = index_dir + '/' + "index_metadata.json";
    with open(metadata_file) as f:
        metadata = json.load(f)
    return index, metadata

def get_filename_from_metadata(metadata, i):
    return metadata[str(i)];

def get_url_from_filename(filename):
    return get_url(filename)

def get_relevant_documents_dense(index_name, query, k):
    # index_name: str con el nombre de la coleccion/indice ej. COMPLETE_RESUELVE
    # devuelve los docs

    query_embedding = model.encode(query)
    faiss_query_embedding = query_embedding.reshape(1, -1)

    index, metadata = retrieve_index(index_name)
    D, I = index.search(faiss_query_embedding, k)
    results = []
    for distance, i in zip(D[0], I[0]):
        filename = get_filename_from_metadata(metadata, i)
        url = get_url_from_filename(filename)
        results.append((i, filename, distance, url))

    return results