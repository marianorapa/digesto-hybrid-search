from retrievers.current_digest.current_digest_retriever import get_relevant_documents_current_digest
from utils.objects.document import Document
from utils.objects.ranking import Ranking
from retrievers.sparse_retriever.terrier_retriever import get_ranking_sparse
from retrievers.hybrid_retriever.hybrid_retriever import get_ranking_hybrid_interpolating_rank
from retrievers.hybrid_retriever.hybrid_retriever import get_ranking_hybrid_interpolating_score
from retrievers.dense_retriever.dense_retriever import get_ranking_dense

def query_sparse(query, k, relevant_documents_ids):
    default_index = "COMPLETE_COMPLETE"
    ranking_sparse = get_ranking_sparse(default_index, query, k, relevant_documents_ids)
    return ranking_sparse

def query_dense(query, k, relevant_documents_ids):
    default_index = "COMPLETE_COMPLETE"
    ranking_dense = get_ranking_dense(default_index, query, k, relevant_documents_ids)
    return ranking_dense

def query_hybrid_interpolating_rank(query, k, relevant_documents_ids):
    default_index = "COMPLETE_COMPLETE"
    ranking_hybrid = get_ranking_hybrid_interpolating_rank(default_index, query, k, relevant_documents_ids)
    return ranking_hybrid

def query_hybrid_interpolating_score(query, k, relevant_documents_ids):
    default_index = "COMPLETE_COMPLETE"
    ranking_hybrid = get_ranking_hybrid_interpolating_score(default_index, query, k, relevant_documents_ids)
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
    
    print("\nBefore current:")
    current_digest_ranking = query_current_digest(query, k, relevant_documents_ids)
    current_digest_ranking.set_relevant_documents_ids(relevant_documents_ids)
    current_digest_ranking.set_output_columns(["Order", "ID", "URL", "Indexed", "Relevant"])
    
    print("\nBefore sparse:")
    sparse_ranking = query_sparse(query, k, relevant_documents_ids)
    sparse_ranking.set_output_columns(
        ["Order", "ID", "URL", "Relevant"])
    
    print("\nBefore Dense:")
    dense_ranking = query_dense(query, k, relevant_documents_ids)
    dense_ranking.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    
    print("\nBefore hybrid:")
    hybrid_ranking_interpolated_score = query_hybrid_interpolating_score(query, k, relevant_documents_ids)
    hybrid_ranking_interpolated_score.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    
    print("\nBefore hybrid 2:")
    hybrid_ranking_interpolated_rank = query_hybrid_interpolating_rank(query, k, relevant_documents_ids)
    hybrid_ranking_interpolated_rank.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    
    # Set reference rankings to compare positions over different systems
    current_digest_ranking.add_reference_ranking(sparse_ranking)
    current_digest_ranking.add_reference_ranking(dense_ranking)
    current_digest_ranking.add_reference_ranking(hybrid_ranking_interpolated_score)
    current_digest_ranking.add_reference_ranking(hybrid_ranking_interpolated_rank)

    ranking_of_relevant_documents.add_reference_ranking(current_digest_ranking)
    ranking_of_relevant_documents.add_reference_ranking(dense_ranking)
    ranking_of_relevant_documents.add_reference_ranking(sparse_ranking)
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_score)
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_rank)

    sparse_ranking.add_reference_ranking(current_digest_ranking)

    dense_ranking.add_reference_ranking(current_digest_ranking)
    

    hybrid_ranking_interpolated_score.add_reference_ranking(current_digest_ranking)
    hybrid_ranking_interpolated_score.add_reference_ranking(sparse_ranking)
    hybrid_ranking_interpolated_score.add_reference_ranking(dense_ranking)
    hybrid_ranking_interpolated_score.add_reference_ranking(hybrid_ranking_interpolated_rank)

    hybrid_ranking_interpolated_rank.add_reference_ranking(current_digest_ranking)
    hybrid_ranking_interpolated_rank.add_reference_ranking(sparse_ranking)
    hybrid_ranking_interpolated_rank.add_reference_ranking(dense_ranking)
    hybrid_ranking_interpolated_rank.add_reference_ranking(hybrid_ranking_interpolated_score)

    print("\nRelevant Documents Searched:")
    print(ranking_of_relevant_documents)
    
    # Print results from all systems

    print(f"\nCurrent Digest Results (Total {current_digest_ranking.get_last_rank()}):")
    print(current_digest_ranking.get_first_k_documents_as_table())
    
    print(f"\nSparse Results (Total {sparse_ranking.get_last_rank()}):")
    print(sparse_ranking.get_first_k_documents_as_table())

    print(f"\nDense Results (Total {dense_ranking.get_last_rank()}):")
    print(dense_ranking.get_first_k_documents_as_table())

    print(f"\nHybrid Results Score Interpolated (Total {hybrid_ranking_interpolated_score.get_last_rank()}):")
    print(hybrid_ranking_interpolated_score.get_first_k_documents_as_table())

    print(f"\nHybrid Results Rank Interpolated (Total {hybrid_ranking_interpolated_rank.get_last_rank()}):")
    print(hybrid_ranking_interpolated_rank.get_first_k_documents_as_table())

