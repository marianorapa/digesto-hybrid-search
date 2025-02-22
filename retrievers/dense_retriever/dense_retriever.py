from sentence_transformers import SentenceTransformer
import faiss
import json
import os
import glob
from utils.objects.document import Document
from utils.objects.ranking import Ranking
from utils.url_finder import get_url

config = os.environ

INDEXES = {
        "VISTO": config['EMBEDDINGS_GENERATOR_VISTO_DIR'],
        "CONSIDERANDO": config['EMBEDDINGS_GENERATOR_CONSIDERANDO_DIR'],
        "RESUELVE": config['EMBEDDINGS_GENERATOR_RESUELVE_DIR'],
        "RESOLUTIVA": config['EMBEDDINGS_GENERATOR_RESOLUTIVA_DIR'],
        "COMPLETE_COMPLETE": config['EMBEDDINGS_GENERATOR_COMPLETE_COMPLETE_DIR'],
        "COMPLETE_RESUELVE": config['EMBEDDINGS_GENERATOR_COMPLETE_RESUELVE_DIR'],
        "COMPLETE_DISPONE": config['EMBEDDINGS_GENERATOR_COMPLETE_DISPONE_DIR'],
}

config = os.environ

model = SentenceTransformer(config["SENTENCE_TRANSFORMER_MODEL"])

def retrieve_index(index_name):
    # lee el indice del archivo -> .bin? 
    index_dir = INDEXES[index_name]
    
    bin_files = glob.glob(os.path.join(index_dir, "*.bin"))
    bin_filename = os.path.basename(bin_files[0])
    index = faiss.read_index(index_dir + '/' + bin_filename)
    metadata_file = index_dir + '/' + "index_metadata.json"
    with open(metadata_file) as f:
        metadata = json.load(f)
    return index, metadata

def get_doc_id_from_metadata(metadata, i):
    return metadata[str(i)]

def get_url_from_filename(filename):
    return get_url(filename)

def get_ranking_dense(index_name, query, k, relevant_documents_ids):
    # index_name: str con el nombre de la coleccion/indice ej. COMPLETE_RESUELVE
    # devuelve los docs

    query_embedding = model.encode(query)
    faiss_query_embedding = query_embedding.reshape(1, -1)

    index, metadata = retrieve_index(index_name)
    D, I = index.search(faiss_query_embedding, int(config['RANKING_LIMIT']))

    dense_ranking = Ranking()
    dense_ranking.set_ranking_name("Rank Dense")
    dense_ranking.set_k_documents(k)
    dense_ranking.set_relevant_documents_ids(relevant_documents_ids)

    for distance, i in zip(D[0], I[0]):
        if (i > -1):
            doc_id = get_doc_id_from_metadata(metadata, i)
            document = Document()
            document.set_id(doc_id)
            dense_ranking.add_document(document, distance)

    return dense_ranking