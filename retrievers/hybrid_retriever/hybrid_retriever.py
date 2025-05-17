from retrievers.sparse_retriever.terrier_retriever import get_ranking_sparse
from retrievers.dense_retriever.dense_retriever import get_ranking_dense
from sentence_transformers import SentenceTransformer
import numpy as np
from numpy import dot
from numpy.linalg import norm
import logging
import os
from utils.objects.document import Document
from utils.objects.ranking import Ranking
from utils.url_finder import get_url

def get_ranking_hybrid_interpolating_rank(default_index, query, k, relevant_documents_ids, docs_metadata, ranking_name):
    ranking_sparse = get_ranking_sparse(default_index, query, k, relevant_documents_ids, docs_metadata)
    ranking_dense = get_ranking_dense(default_index, query, k, relevant_documents_ids, docs_metadata)
    k_formula = 60
    combined = ranking_sparse.merge_interpolating_rank_positions(ranking_dense, k_formula, ranking_name)
    combined.set_k_documents(k)

    return combined

def get_ranking_hybrid_interpolating_score(default_index, query, k, relevant_documents_ids, docs_metadata, ranking_name):
    
    ranking_sparse = get_ranking_sparse(default_index, query, k, relevant_documents_ids, docs_metadata)
    ranking_sparse.set_score_type("Score")
    ranking_dense = get_ranking_dense(default_index, query, k, relevant_documents_ids, docs_metadata)
    ranking_dense.set_score_type("Distance")
    combined = ranking_sparse.merge_interpolating_score(ranking_dense, ranking_name)
    combined.set_k_documents(k)

    return combined


