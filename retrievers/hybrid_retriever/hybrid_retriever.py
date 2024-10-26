from retrievers.sparse_retriever.terrier_retriever import get_relevant_documents_sparse
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy import dot
from numpy.linalg import norm
import logging
from utils.url_finder import get_url

BASE_OUTPUT_DIR = "./indexes"
DENSE_OUTPUT_DIR = f"{BASE_OUTPUT_DIR}/dense_index"

VISTO_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/visto"
CONSIDERANDO_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/considerando"
RESUELVE_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/resuelve"
DISPONE_OUTPUT_DIR = f"{DENSE_OUTPUT_DIR}/dispone"

COMPLETE_DENSE_OUTPUT_DIR = f"{BASE_OUTPUT_DIR}/dense_index/completa"
COMPLETE_RESUELVE_OUTPUT_DIR = f"{COMPLETE_DENSE_OUTPUT_DIR}/resuelve"
COMPLETE_DISPONE_OUTPUT_DIR = f"{COMPLETE_DENSE_OUTPUT_DIR}/dispone"

INDEXES = {
        "VISTO": VISTO_OUTPUT_DIR,
        "CONSIDERANDO": CONSIDERANDO_OUTPUT_DIR,
        "RESUELVE": RESUELVE_OUTPUT_DIR,
        "COMPLETE_COMPLETE": None,
        "COMPLETE_RESUELVE": COMPLETE_RESUELVE_OUTPUT_DIR,
        "COMPLETE_DISPONE": COMPLETE_DISPONE_OUTPUT_DIR,
}

def cosine_similarity_of_vectors(a, b):
    return dot(a, b)/(norm(a)*norm(b))

def create_embedding(query):
    model = SentenceTransformer('hiiamsid/sentence_similarity_spanish_es')

    return model.encode(query)

def get_document_url(document):
    return get_url(document[2])

def rerank_documents(relevant_documents_with_cosine_similarity):
    sorted_documents = sorted(relevant_documents_with_cosine_similarity, key=lambda x: x[4], reverse=True)

    dense_reranked_documents = []
    k = 60
    dense_rank = 1
    for sorted_document in sorted_documents:

        sparse_rank = sorted_document[3]

        score = (1/(k+sparse_rank))+(1/(k+dense_rank))
        doc_url = get_document_url(sorted_document)
        sorted_document.extend([dense_rank, score, doc_url])
        dense_reranked_documents.append(sorted_document)
        dense_rank = dense_rank + 1

    sorted_reranked_documents = sorted(sorted_documents, key=lambda x: x[6], reverse=True)

    return sorted_reranked_documents

def get_relevant_documents_hybrid(index, query, k):

    query_vector = create_embedding(query)

    relevant_documents_with_cosine_similarity = []

    relevant_documents_sparse = get_relevant_documents_sparse(index, query, k)

    for relevant_document_sparse in relevant_documents_sparse:
        filename = relevant_document_sparse[2].split("/")[-1]

        #print(f"Document {relevant_document_sparse[0]}, with Score {relevant_document_sparse[1]}")
        #print(f"Should get embedding of {relevant_document_sparse[2]}")
        #print(f"Cosine Similarity Compare with {query_vector}")

        dense_path = INDEXES[index]

        if dense_path == None:
            if "RES" in filename:
                dense_path = INDEXES["COMPLETE_RESUELVE"]
            if "DISP" in filename:
                dense_path = INDEXES["COMPLETE_DISPONE"]
            else:
                logging.error("Not DIS or RES in filename")

        try:
            document_embedding = np.loadtxt(f"{dense_path}/{filename}")

            cosine_similarity = cosine_similarity_of_vectors(query_vector, document_embedding)
        except:
            # If embedding is not available
            cosine_similarity = -1

        relevant_document_sparse.append(cosine_similarity)
        relevant_documents_with_cosine_similarity.append(relevant_document_sparse)

    return rerank_documents(relevant_documents_with_cosine_similarity)