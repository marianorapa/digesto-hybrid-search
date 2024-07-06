from simple_term_menu import TerminalMenu
from preprocessors.digest_downloader_converter.downloader_converter import download_and_convert
from preprocessors.sections_splitter.extract_sections import extract_sections
from preprocessors.sentence_splitter.sentence import split_sentences
from indexers.dense_indexer.embeddings_generator import generate_embeddings
from indexers.sparse_indexer.terrier_indexer import terrier_index
from retrievers.sparse_retriever.terrier_retriever import get_relevant_documents_sparse
from retrievers.hybrid_retriever.hybrid_retriever import get_relevant_documents_hybrid
import logging

logging.basicConfig(level=logging.INFO, filename=f"app.log", filemode="w")

DOWNLOAD_DOCS = 0
INDEX_DOCS = 1
RETRIEVE_DOCS = 2
EXIT = 3


def process_option(menu_entry_index):
    if menu_entry_index == DOWNLOAD_DOCS:
        download_and_convert(0, 131500)
        extract_sections()
        split_sentences()
    elif menu_entry_index == INDEX_DOCS:
        generate_embeddings()
        terrier_index()
    elif menu_entry_index == RETRIEVE_DOCS:
        print(get_relevant_documents_hybrid("VISTO", "Gabriel Tolosa", 10))



def menu():
    options = ["Download docs & Preprocess", "Index (sparse & dense)", "Retrieve", "Exit"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = -1
    while menu_entry_index != EXIT:
        menu_entry_index = terminal_menu.show()
        process_option(menu_entry_index)


if __name__ == "__main__":
    menu()

