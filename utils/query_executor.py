from retrievers.current_digest.current_digest_retriever import get_relevant_documents_current_digest
from utils.objects.document import Document
from utils.objects.metadata import Metadata
from utils.objects.ranking import Ranking
from retrievers.sparse_retriever.terrier_retriever import get_ranking_sparse
from retrievers.hybrid_retriever.hybrid_retriever import get_ranking_hybrid_interpolating_rank
from retrievers.hybrid_retriever.hybrid_retriever import get_ranking_hybrid_interpolating_score
from retrievers.dense_retriever.dense_retriever import get_ranking_dense
import logging

METADATA_FILE_PATH = 'preprocessors/sentence_splitter/sentences_meta.json'

logger = logging.getLogger("digesto-hybrid-search-logger")
INDEX_TO_QUERY = "RESOLUTIVA"

def query_sparse(query, k, relevant_documents_ids, docs_metadata):
    default_index = INDEX_TO_QUERY
    ranking_sparse = get_ranking_sparse(default_index, query, k, relevant_documents_ids, docs_metadata)
    return ranking_sparse

def query_dense(query, k, relevant_documents_ids, docs_metadata):
    default_index = INDEX_TO_QUERY
    ranking_dense = get_ranking_dense(default_index, query, k, relevant_documents_ids, docs_metadata)
    return ranking_dense

def query_hybrid_interpolating_rank(query, k, relevant_documents_ids, docs_metadata):
    default_index = INDEX_TO_QUERY
    ranking_hybrid = get_ranking_hybrid_interpolating_rank(default_index, query, k, relevant_documents_ids, docs_metadata)
    return ranking_hybrid

def query_hybrid_interpolating_score(query, k, relevant_documents_ids, docs_metadata):
    default_index = INDEX_TO_QUERY
    ranking_hybrid = get_ranking_hybrid_interpolating_score(default_index, query, k, relevant_documents_ids, docs_metadata)
    return ranking_hybrid

def query_current_digest(query, k, relevant_documents_ids, metadata):
    default_index = INDEX_TO_QUERY
    ranking = get_relevant_documents_current_digest(default_index, query, k, relevant_documents_ids, metadata)
    return ranking

def load_metadata(filepath):
    metadata = Metadata(filepath)
    metadata.load()
    return metadata

def query(query, k, relevant_documents_ids):
    metadata = load_metadata(METADATA_FILE_PATH)

    ranking_of_relevant_documents = Ranking()
    for relevant_document_id in relevant_documents_ids:
        document = metadata.get_document_by_id(relevant_document_id, True)
        ranking_of_relevant_documents.add_document(document)

    ranking_of_relevant_documents.set_output_columns(["ID", "Indexed", "URL"])

    print("\nQuerying current digest")
    current_digest_ranking = query_current_digest(query, k, relevant_documents_ids, metadata)
    current_digest_ranking.set_relevant_documents_ids(relevant_documents_ids)
    current_digest_ranking.set_output_columns(["Order", "ID", "URL", "Indexed", "Relevant"])
    print("\nQuerying current digest done!")

    print("\nQuerying sparse index")
    sparse_ranking = query_sparse(query, k, relevant_documents_ids, metadata)
    sparse_ranking.set_output_columns(
        ["Order", "ID", "URL",  "Relevant"])
    print("\nQuerying sparse index done!")

    print("\nQuerying dense index")
    dense_ranking = query_dense(query, k, relevant_documents_ids, metadata)
    dense_ranking.set_output_columns(
        ["Order", "ID", "Score", "URL",  "Relevant"])
    print("\nQuerying dense index done!")

    print("\nQuerying hybrid index interpolated score")
    hybrid_ranking_interpolated_score = query_hybrid_interpolating_score(query, k, relevant_documents_ids, metadata)
    hybrid_ranking_interpolated_score.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    print("\nQuerying hybrid index done!")

    print("\nQuerying hybrid index interpolated ranking")
    hybrid_ranking_interpolated_rank = query_hybrid_interpolating_rank(query, k, relevant_documents_ids, metadata)
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
