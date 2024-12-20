from retrievers.sparse_retriever.terrier_retriever import get_relevant_documents_sparse
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy import dot
from numpy.linalg import norm
import logging

from utils.objects.document import Document
from utils.objects.ranking import Ranking
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
        "DISPONE": DISPONE_OUTPUT_DIR,
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

def rerank_documents(relevant_documents_with_cosine_similarity, k_results):
    # input format: [doc_id, score, filename, sparse_rank, doc_url, cosine_similarity]
    cosine_similarity_index = 5
    sorted_documents = sorted(relevant_documents_with_cosine_similarity, key=lambda x: x[cosine_similarity_index], reverse=True)

    dense_reranked_documents = []
    k_formula = 60
    dense_rank = 1
    for sorted_document in sorted_documents:

        sparse_rank = sorted_document[3]

        hybrid_combined_ranks = (1/(k_formula+sparse_rank))+(1/(k_formula+dense_rank))
        sorted_document.extend([dense_rank, hybrid_combined_ranks])
        # final format: [doc_id, score, filename, sparse_rank, doc_url, cosine_similarity, dense_rank, hybrid_combined_ranks]
        dense_reranked_documents.append(sorted_document)
        dense_rank = dense_rank + 1
    
    hybrid_combined_rank_index = 7
    sorted_reranked_documents = sorted(sorted_documents, key=lambda x: x[hybrid_combined_rank_index], reverse=True)

    return sorted_reranked_documents[0:k_results]

def get_relevant_documents_hybrid(index, query, k):

    query_vector = create_embedding(query)

    relevant_documents_with_cosine_similarity = []

    # returns [doc_id, score, filename, rank, doc_url] for sparse results
    sparse_search_size = 1000
    relevant_documents_sparse = get_relevant_documents_sparse(index, query, sparse_search_size)

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

        # relevant_document_sparse ends up being [doc_id, score, filename, rank, doc_url, cosine_similarity]
        relevant_document_sparse.append(cosine_similarity)
        relevant_documents_with_cosine_similarity.append(relevant_document_sparse)

    return rerank_documents(relevant_documents_with_cosine_similarity, k)


def get_ranking_hybrid(default_index, query, k, relevant_documents_ids):
    # TODO Construct raking in runtime: Do not use previous function, to avoid iterating throw result.
    relevant_documents_hybrid = get_relevant_documents_hybrid(default_index, query, k)

    hybrid_ranking = Ranking()
    hybrid_ranking.set_ranking_name("Hybrid Ranking Interpolating Rank")
    hybrid_ranking.set_relevant_documents_ids(relevant_documents_ids)
    hybrid_ranking.set_k_documents(k)

    for relevant_document_hybrid in relevant_documents_hybrid:
        terrier_doc_id, score, filename, sparse_rank, doc_url, cosine_similarity, dense_rank, hybrid_combined_ranks = relevant_document_hybrid
        document = Document()
        document.set_id_from_url(doc_url)

        hybrid_ranking.add_document(document, hybrid_combined_ranks)

    return hybrid_ranking




