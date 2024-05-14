from simple_term_menu import TerminalMenu
from preprocessors.digest_downloader_converter.downloader_converter import download_and_convert
from preprocessors.sections_splitter.extract_sections import extract_sections
from preprocessors.sentence_splitter.sentence import split_sentences
from indexers.dense_indexer.embeddings_generator import generate_embeddings
import logging

logging.basicConfig(level=logging.INFO, filename=f"app.log", filemode="w")

DOWNLOAD_DOCS = 0
INDEX_DOCS = 1
RETRIEVE_DOCS = 2
EXIT = 3


def process_option(menu_entry_index):
    if menu_entry_index == DOWNLOAD_DOCS:
        #download_and_convert(0, 131500)
        extract_sections()
        #split_sentences()
    elif menu_entry_index == INDEX_DOCS:
        generate_embeddings()
    elif menu_entry_index == RETRIEVE_DOCS:
        print("Retrieve")


def menu():
    options = ["Download docs & Preprocess", "Index (sparse & dense)", "Retrieve", "Exit"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = -1
    while menu_entry_index != EXIT:
        menu_entry_index = terminal_menu.show()
        process_option(menu_entry_index)


if __name__ == "__main__":
    menu()

