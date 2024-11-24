from retrievers.current_digest.current_digest_retriever import get_relevant_documents_current_digest
from utils.objects.document import Document
from utils.objects.ranking import Ranking
from retrievers.sparse_retriever.terrier_retriever import get_ranking_sparse
from retrievers.hybrid_retriever.hybrid_retriever import get_ranking_hybrid
from retrievers.dense_retriever.dense_retriever import get_ranking_dense

def query_sparse(query, k, relevant_documents_ids):
    default_index = "COMPLETE_COMPLETE"
    ranking_sparse = get_ranking_sparse(default_index, query, k, relevant_documents_ids)

    return ranking_sparse

def query_dense(query, k, relevant_documents_ids):
    default_index = "COMPLETE_COMPLETE"
    ranking_dense = get_ranking_dense(default_index, query, k, relevant_documents_ids)
    return ranking_dense

def query_hybrid(query, k, relevant_documents_ids):
    default_index = "COMPLETE_COMPLETE"
    ranking_hybrid = get_ranking_hybrid(default_index, query, k, relevant_documents_ids)
    return ranking_hybrid

def query_current_digest(query, k, relevant_documents_ids):
    default_index = "COMPLETE_COMPLETE"
    ranking = get_relevant_documents_current_digest(default_index, query, k, relevant_documents_ids)
    return ranking

def query(query, k, relevant_documents_ids):
    ranking_of_relevant_documents = Ranking()
    for relevant_document_id in relevant_documents_ids:
        document = Document()
        document.set_id(relevant_document_id)

        ranking_of_relevant_documents.add_document(document)

    ranking_of_relevant_documents.set_output_columns(["ID", "URL", "Indexed"])
    print("\nRelevant Documents Searched:")
    print(ranking_of_relevant_documents)

    current_digest_ranking = query_current_digest(query, k, relevant_documents_ids)
    current_digest_ranking.set_relevant_documents_ids(relevant_documents_ids)
    current_digest_ranking.set_output_columns(["Order", "ID", "URL", "Indexed", "Relevant", "Rank Sparse", "Rank Dense", "Rank Hybrid"])
    print("\nCurrent Digest Results:")
    print(current_digest_ranking)
    
    sparse_ranking = query_sparse(query, k, relevant_documents_ids)
    print("\nSparse Results:")
    sparse_ranking.set_output_columns(
        ["Order", "ID", "URL", "Relevant", "Rank Current Digest"])
    print(sparse_ranking)
    
    dense_ranking = query_dense(query, k, relevant_documents_ids)
    print("\nDense Results:")
    dense_ranking.set_output_columns(
        ["Order", "ID", "URL", "Relevant", "Rank Current Digest"])
    print(dense_ranking)
    
    hybrid_ranking = query_hybrid(query, k, relevant_documents_ids)
    print("\nHybrid Results:")
    hybrid_ranking.set_output_columns(
        ["Order", "ID", "URL", "Relevant", "Rank Current Digest"])
    print(hybrid_ranking)
    
