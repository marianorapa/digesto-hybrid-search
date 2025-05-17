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

COMPLETE_COMPLETE = "COMPLETE_COMPLETE"
RESOLUCIONES = "RESUELVE"
DISPOSICIONES = "DISPONE"
RESOLUTIVA = "RESOLUTIVA"

DEFAULT_INDEX = RESOLUTIVA

def query_sparse(query, k, relevant_documents_ids, docs_metadata, ranking_name, index_name = DEFAULT_INDEX):
    ranking_sparse = get_ranking_sparse(index_name, query, k, relevant_documents_ids, docs_metadata, ranking_name)
    return ranking_sparse

def query_dense(query, k, relevant_documents_ids, docs_metadata, ranking_name, index_name = DEFAULT_INDEX):
    ranking_dense = get_ranking_dense(index_name, query, k, relevant_documents_ids, docs_metadata, ranking_name)
    return ranking_dense

def query_hybrid_interpolating_rank(query, k, relevant_documents_ids, docs_metadata, ranking_name, index_name = DEFAULT_INDEX):
    ranking_hybrid = get_ranking_hybrid_interpolating_rank(index_name, query, k, relevant_documents_ids, docs_metadata, ranking_name)
    return ranking_hybrid

def query_hybrid_interpolating_score(query, k, relevant_documents_ids, docs_metadata, ranking_name, index_name = DEFAULT_INDEX):
    ranking_hybrid = get_ranking_hybrid_interpolating_score(index_name, query, k, relevant_documents_ids, docs_metadata, ranking_name)
    return ranking_hybrid

def query_current_digest(query, k, relevant_documents_ids, metadata):
    ranking = get_relevant_documents_current_digest(None, query, k, relevant_documents_ids, metadata)
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

    current_digest_ranking = query_current_digest(query, k, relevant_documents_ids, metadata)
    current_digest_ranking.set_relevant_documents_ids(relevant_documents_ids)
    current_digest_ranking.set_output_columns(["Order", "ID", "URL", "Indexed", "Relevant"])
    print("Querying current digest done!\n\n")

    ## Sparse
    sparse_ranking_complete = query_sparse(query, k, relevant_documents_ids, metadata, "sparse_complete", COMPLETE_COMPLETE)
    sparse_ranking_complete.set_output_columns(
        ["Order", "ID", "URL",  "Relevant"])
    print("Querying sparse index done!\n\n")

    sparse_ranking_resolution = query_sparse(query, k, relevant_documents_ids, metadata, "sparse_resolution", RESOLUCIONES)
    sparse_ranking_resolution.set_output_columns(
        ["Order", "ID", "URL",  "Relevant"])
    print("sparse_ranking_resolution done!\n\n")

    sparse_ranking_disposition = query_sparse(query, k, relevant_documents_ids, metadata, "sparse_disposition", DISPOSICIONES)
    sparse_ranking_disposition.set_output_columns(
        ["Order", "ID", "URL",  "Relevant"])
    print("sparse_ranking_disposition done!\n\n")

    sparse_ranking_resolutive = query_sparse(query, k, relevant_documents_ids, metadata, "sparse_resolutive", RESOLUTIVA)
    sparse_ranking_resolutive.set_output_columns(
        ["Order", "ID", "URL",  "Relevant"])
    print("sparse_ranking_resolution done!\n\n")

    ## Dense
    dense_ranking_complete = query_dense(query, k, relevant_documents_ids, metadata, "dense_complete", COMPLETE_COMPLETE)
    dense_ranking_complete.set_output_columns(
        ["Order", "ID", "Score", "URL",  "Relevant"])
    print("Querying dense index done!\n\n")

    dense_ranking_resolutions = query_dense(query, k, relevant_documents_ids, metadata, "dense_resolution", RESOLUCIONES)
    dense_ranking_resolutions.set_output_columns(
        ["Order", "ID", "Score", "URL",  "Relevant"])
    print("dense_ranking_resolutions done!\n\n")

    dense_ranking_disposition = query_dense(query, k, relevant_documents_ids, metadata, "dense_disposition", DISPOSICIONES)
    dense_ranking_disposition.set_output_columns(
        ["Order", "ID", "Score", "URL",  "Relevant"])
    print("dense_ranking_disposition done!\n\n")

    dense_ranking_resolutive = query_dense(query, k, relevant_documents_ids, metadata, "dense_resolutive", RESOLUTIVA)
    dense_ranking_resolutive.set_output_columns(
        ["Order", "ID", "Score", "URL",  "Relevant"])
    print("dense_ranking_resolutive done!\n\n")

    ## Hybrid x score
    hybrid_ranking_interpolated_score_complete = query_hybrid_interpolating_score(query, k, relevant_documents_ids, metadata, "hybrid_score_complete", COMPLETE_COMPLETE)
    hybrid_ranking_interpolated_score_complete.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    print("hybrid_ranking_interpolated_score_complete done!\n\n")

    hybrid_ranking_interpolated_score_resolution = query_hybrid_interpolating_score(query, k, relevant_documents_ids, metadata, "hybrid_score_resolution", RESOLUCIONES)
    hybrid_ranking_interpolated_score_resolution.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    print("hybrid_ranking_interpolated_score_resolution done!\n\n")
    
    hybrid_ranking_interpolated_score_disposition = query_hybrid_interpolating_score(query, k, relevant_documents_ids, metadata, "hybrid_score_disposition", DISPOSICIONES)
    hybrid_ranking_interpolated_score_disposition.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    print("hybrid_ranking_interpolated_score_disposition done!\n\n")

    hybrid_ranking_interpolated_score_resolutive = query_hybrid_interpolating_score(query, k, relevant_documents_ids, metadata, "hybrid_score_resolutive", RESOLUTIVA)
    hybrid_ranking_interpolated_score_resolutive.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    print("hybrid_ranking_interpolated_score_resolutive done!\n\n")
    
    ## Hybrid x rank
    hybrid_ranking_interpolated_rank_complete = query_hybrid_interpolating_rank(query, k, relevant_documents_ids, metadata, "hybrid_position_complete", COMPLETE_COMPLETE)
    hybrid_ranking_interpolated_rank_complete.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    print("hybrid_ranking_interpolated_rank_complete done!\n\n")
    
    hybrid_ranking_interpolated_rank_resolution = query_hybrid_interpolating_rank(query, k, relevant_documents_ids, metadata, "hybrid_position_resolution", RESOLUCIONES)
    hybrid_ranking_interpolated_rank_resolution.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    print("hybrid_ranking_interpolated_rank_resolution done!\n\n")

    hybrid_ranking_interpolated_rank_disposition = query_hybrid_interpolating_rank(query, k, relevant_documents_ids, metadata, "hybrid_position_disposition", DISPOSICIONES)
    hybrid_ranking_interpolated_rank_disposition.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    print("hybrid_ranking_interpolated_rank_disposition done!\n\n")

    hybrid_ranking_interpolated_rank_resolutive = query_hybrid_interpolating_rank(query, k, relevant_documents_ids, metadata, "hybrid_position_resolutive", RESOLUTIVA)
    hybrid_ranking_interpolated_rank_resolutive.set_output_columns(
        ["Order", "ID", "Score", "URL", "Relevant"])
    print("hybrid_ranking_interpolated_rank_resolutive done!\n\n")

    # Set reference rankings to compare positions over different systems
    current_digest_ranking.add_reference_ranking(sparse_ranking_complete)
    current_digest_ranking.add_reference_ranking(dense_ranking_complete)
    current_digest_ranking.add_reference_ranking(hybrid_ranking_interpolated_score_complete)
    current_digest_ranking.add_reference_ranking(hybrid_ranking_interpolated_rank_complete)

    # Relevant documents rankins is compared to every index search (even the ones not displayed)
    ranking_of_relevant_documents.add_reference_ranking(current_digest_ranking)
    
    # Compare to every dense index
    ranking_of_relevant_documents.add_reference_ranking(dense_ranking_complete)
    ranking_of_relevant_documents.add_reference_ranking(dense_ranking_resolutions)
    ranking_of_relevant_documents.add_reference_ranking(dense_ranking_disposition)
    ranking_of_relevant_documents.add_reference_ranking(dense_ranking_resolutive)
    
    # Compare to every sparse index
    ranking_of_relevant_documents.add_reference_ranking(sparse_ranking_complete)
    ranking_of_relevant_documents.add_reference_ranking(sparse_ranking_resolution)
    ranking_of_relevant_documents.add_reference_ranking(sparse_ranking_disposition)
    ranking_of_relevant_documents.add_reference_ranking(sparse_ranking_resolutive)
    
    # Compare to every hybrid (score) index
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_score_complete)
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_score_resolution)
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_score_disposition)
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_score_resolutive)
    
    # Compare to every hybrid (rank) index
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_rank_complete)
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_rank_resolution)
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_rank_disposition)
    ranking_of_relevant_documents.add_reference_ranking(hybrid_ranking_interpolated_rank_resolutive)

    sparse_ranking_complete.add_reference_ranking(current_digest_ranking)

    dense_ranking_complete.add_reference_ranking(current_digest_ranking)
    

    hybrid_ranking_interpolated_score_complete.add_reference_ranking(current_digest_ranking)
    hybrid_ranking_interpolated_score_complete.add_reference_ranking(sparse_ranking_complete)
    hybrid_ranking_interpolated_score_complete.add_reference_ranking(dense_ranking_complete)
    hybrid_ranking_interpolated_score_complete.add_reference_ranking(hybrid_ranking_interpolated_rank_complete)

    hybrid_ranking_interpolated_rank_complete.add_reference_ranking(current_digest_ranking)
    hybrid_ranking_interpolated_rank_complete.add_reference_ranking(sparse_ranking_complete)
    hybrid_ranking_interpolated_rank_complete.add_reference_ranking(dense_ranking_complete)
    hybrid_ranking_interpolated_rank_complete.add_reference_ranking(hybrid_ranking_interpolated_score_complete)

    print("\nRelevant Documents Searched:")
    print(ranking_of_relevant_documents)
    
    # Print results from all systems

    print(f"\nCurrent Digest Results (Total {current_digest_ranking.get_last_rank()}):")
    print(current_digest_ranking.get_first_k_documents_as_table())
    
    print(f"\nSparse Results (Total {sparse_ranking_complete.get_last_rank()}):")
    print(sparse_ranking_complete.get_first_k_documents_as_table())

    print(f"\nDense Results (Total {dense_ranking_complete.get_last_rank()}):")
    print(dense_ranking_complete.get_first_k_documents_as_table())

    print(f"\nHybrid Results Score Interpolated (Total {hybrid_ranking_interpolated_score_complete.get_last_rank()}):")
    print(hybrid_ranking_interpolated_score_complete.get_first_k_documents_as_table())

    print(f"\nHybrid Results Rank Interpolated (Total {hybrid_ranking_interpolated_rank_complete.get_last_rank()}):")
    print(hybrid_ranking_interpolated_rank_complete.get_first_k_documents_as_table())
