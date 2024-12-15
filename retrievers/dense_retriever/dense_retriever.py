from sentence_transformers import SentenceTransformer
import faiss
import json
import os
import glob

from utils.objects.document import Document
from utils.objects.ranking import Ranking
from utils.url_finder import get_url

RANKING_LIMIT = 140000

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
    rank = 1
    for distance, i in zip(D[0], I[0]):
        filename = get_filename_from_metadata(metadata, i)
        url = get_url_from_filename(filename)
        results.append((rank, i, filename, distance, url))
        rank =+ 1
    return results


def get_ranking_dense(index_name, query, k, relevant_documents_ids):
    # index_name: str con el nombre de la coleccion/indice ej. COMPLETE_RESUELVE
    # devuelve los docs

    query_embedding = model.encode(query)
    faiss_query_embedding = query_embedding.reshape(1, -1)

    index, metadata = retrieve_index(index_name)
    D, I = index.search(faiss_query_embedding, RANKING_LIMIT)

    dense_ranking = Ranking()
    dense_ranking.set_ranking_name("Rank Dense")
    dense_ranking.set_k_documents(k)
    dense_ranking.set_relevant_documents_ids(relevant_documents_ids)

    for distance, i in zip(D[0], I[0]):
        if (i > -1):
            filename = get_filename_from_metadata(metadata, i)
            url = get_url_from_filename(filename)

            document = Document()
            document.set_id_from_url(url)
            dense_ranking.add_document(document, distance)

    return dense_ranking