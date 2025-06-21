from sentence_transformers import SentenceTransformer
from utils.objects.metadata import Metadata
from utils.objects.document import Document
from typing import List
from tqdm import tqdm
import numpy as np
import logging
import os.path
import faiss
import json
import os


logger = logging.getLogger("digesto-hybrid-search-logger")

config = os.environ

def init_metadata():
    global sentences_metadata, embeddings_generator_metadata
    sentences_metadata = Metadata(config["SENTENCES_META_FILE"]).load()
    embeddings_generator_metadata = Metadata(config["EMBEDDINGS_GENERATOR_META_FILE"])

def create_directories():
    os.makedirs(config["EMBEDDINGS_GENERATOR_VISTO_DIR"], exist_ok=True)
    os.makedirs(config["EMBEDDINGS_GENERATOR_CONSIDERANDO_DIR"], exist_ok=True)
    os.makedirs(config["EMBEDDINGS_GENERATOR_RESUELVE_DIR"], exist_ok=True)
    os.makedirs(config["EMBEDDINGS_GENERATOR_DISPONE_DIR"], exist_ok=True)
    os.makedirs(config["EMBEDDINGS_GENERATOR_RESOLUTIVA_DIR"], exist_ok=True)
    os.makedirs(config["EMBEDDINGS_GENERATOR_COMPLETE_COMPLETE_DIR"], exist_ok=True)
    os.makedirs(config["EMBEDDINGS_GENERATOR_COMPLETE_RESUELVE_DIR"], exist_ok=True)
    os.makedirs(config["EMBEDDINGS_GENERATOR_COMPLETE_DISPONE_DIR"], exist_ok=True)

# TODO: Changed filename to ID (Fix in next steps)
# TODO: Should we normalize the vector?
def add_to_dense_index(dense_indexes, embedding, document_type, doc_id):
    # Validar que los vectores estén normalizados (L2 norm = 1) antes de agregarlos al índice
    norm = np.linalg.norm(embedding)
    if abs(norm - 1.0) > 1e-5:  # Usando un pequeño epsilon para comparaciones de punto flotante
        logger.warning(f"Vector no normalizado para doc_id {doc_id} (norm={norm}). Normalizando antes de añadir al índice.")
        embedding = embedding / norm

    dense_indexes[document_type]["index"].add(embedding.reshape(1, -1))
    counter = dense_indexes[document_type]["counter"]
    dense_indexes[document_type]["counter"] = dense_indexes[document_type]["counter"] + 1
    dense_indexes[document_type]["metadata"][counter] = doc_id

def generate_embedding_of_sentences(model, sentences):
    embeddings_of_sentences = []
    for sentence in sentences:
        embedding = model.encode(sentence, normalize_embeddings=False)
        embeddings_of_sentences.append(embedding)

    # Calcular el promedio de los embeddings
    mean_embedding = np.mean(embeddings_of_sentences, axis=0)
    
    return mean_embedding

def generate_embeddings_from_doc_list(model, documents: List[Document], dense_indexes):
    for document in tqdm(documents, desc="Construyendo embeddings de los documentos", unit="doc"):
        document_embeddings = []

        visto_embedding = generate_embedding_of_sentences(model, document.get_visto_sentences())
        document_embeddings.append(visto_embedding)
        # Save it in a list, to build document embedding
        # Save it to dense index
        add_to_dense_index(dense_indexes, visto_embedding, "visto", document.get_id())
        # Save it to file, for hybrid legacy implementation
        np.savetxt(f"{config['EMBEDDINGS_GENERATOR_VISTO_DIR']}/{document.get_id()}", visto_embedding)


        considerando_embedding = generate_embedding_of_sentences(model, document.get_considerando_sentences())
        # Save it in a list, to build document embedding
        document_embeddings.append(considerando_embedding)
        # Save it to dense index
        add_to_dense_index(dense_indexes, considerando_embedding, "considerando", document.get_id())
        # Save it to file, for hybrid legacy implementation
        np.savetxt(f"{config['EMBEDDINGS_GENERATOR_CONSIDERANDO_DIR']}/{document.get_id()}", considerando_embedding)

        resolutiva_embedding = generate_embedding_of_sentences(model, document.get_resolutiva_sentences())
        # Do not save it to document embeddings
        # Save it to dense index
        add_to_dense_index(dense_indexes, resolutiva_embedding, "resolutiva", document.get_id())
        # Save it to file, for hybrid legacy implementation
        np.savetxt(f"{config['EMBEDDINGS_GENERATOR_RESOLUTIVA_DIR']}/{document.get_id()}", resolutiva_embedding)
        
        if document.is_resolution():
            resuelve_embedding = generate_embedding_of_sentences(model, document.get_resuelve_sentences())
            # Save it in a list, to build document embedding
            document_embeddings.append(resuelve_embedding)
            # Save it to dense index
            add_to_dense_index(dense_indexes, resuelve_embedding, "resuelve", document.get_id())
            # Save it to file, for hybrid legacy implementation
            np.savetxt(f"{config['EMBEDDINGS_GENERATOR_RESUELVE_DIR']}/{document.get_id()}", resuelve_embedding)

            # Build document embedding
            document_embedding = np.mean(document_embeddings, axis=0)
            add_to_dense_index(dense_indexes, document_embedding, "resoluciones", document.get_id())
            np.savetxt(f"{config['EMBEDDINGS_GENERATOR_COMPLETE_RESUELVE_DIR']}/{document.get_id()}", document_embedding)
        
        if document.is_disposition():
            dispone_embedding = generate_embedding_of_sentences(model, document.get_dispone_sentences())
            # Save it in a list, to build document embedding
            document_embeddings.append(dispone_embedding)
            # Save it to dense index
            add_to_dense_index(dense_indexes, dispone_embedding, "dispone", document.get_id())
            # Save it to file, for hybrid legacy implementation
            np.savetxt(f"{config['EMBEDDINGS_GENERATOR_DISPONE_DIR']}/{document.get_id()}", dispone_embedding)

            # Build document embedding
            document_embedding = np.mean(document_embeddings, axis=0)
            add_to_dense_index(dense_indexes, document_embedding, "disposiciones", document.get_id())
            np.savetxt(f"{config['EMBEDDINGS_GENERATOR_COMPLETE_DISPONE_DIR']}/{document.get_id()}", document_embedding)

        add_to_dense_index(dense_indexes, document_embedding, "completo", document.get_id())
        np.savetxt(f"{config['EMBEDDINGS_GENERATOR_COMPLETE_COMPLETE_DIR']}/{document.get_id()}", document_embedding)

def create_dense_indexes_structure():
    dense_indexes = {}

    for key in ["visto", "considerando", "resuelve", "dispone", "resoluciones", "disposiciones", "completo", "resolutiva"]:
        dense_indexes[key] = {}
        dense_indexes[key]["index"] = faiss.IndexFlatIP(int(config["SENTENCE_TRANSFORMER_MODEL_DIMENSIONS"]))
        dense_indexes[key]["counter"] = 0
        dense_indexes[key]["metadata"] = {}

    return dense_indexes

# Para chusmear la semana que viene: No sé por que están los output dir acá
def persist_dense_indexes(dense_indexes):
     for key in dense_indexes:
        if key == "visto":
            root_directory = config['EMBEDDINGS_GENERATOR_VISTO_DIR']
        elif key == "considerando":
            root_directory = config['EMBEDDINGS_GENERATOR_CONSIDERANDO_DIR']
        elif key == "resuelve":
            root_directory = config['EMBEDDINGS_GENERATOR_RESUELVE_DIR']
        elif key == "dispone":
            root_directory = config['EMBEDDINGS_GENERATOR_DISPONE_DIR']
        elif key == "resolutiva":
            root_directory = config['EMBEDDINGS_GENERATOR_RESOLUTIVA_DIR']
        elif key == "resoluciones":
            root_directory = config['EMBEDDINGS_GENERATOR_COMPLETE_RESUELVE_DIR']
        elif key == "disposiciones":
            root_directory = config['EMBEDDINGS_GENERATOR_COMPLETE_DISPONE_DIR']
        elif key == "completo":
            root_directory = config['EMBEDDINGS_GENERATOR_COMPLETE_COMPLETE_DIR']

        index = dense_indexes[key]["index"]
        faiss.write_index(index, f"{root_directory}/index_{key}.bin")

        with open(f"{root_directory}/index_metadata.json", "w") as outfile: 
            json.dump(dense_indexes[key]["metadata"], outfile)


def generate_embeddings():
    logger.info("Dense Indexer Started")

    create_directories()

    model = SentenceTransformer(config["SENTENCE_TRANSFORMER_MODEL"])

    init_metadata()

    dense_indexes = create_dense_indexes_structure()

    valid_docs = sentences_metadata.get_valid_documents()

    generate_embeddings_from_doc_list(model, valid_docs, dense_indexes)

    persist_dense_indexes(dense_indexes)

    logger.info("Dense Indexer Ended")

   

