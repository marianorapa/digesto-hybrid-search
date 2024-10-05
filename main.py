from simple_term_menu import TerminalMenu
from utils.execution_cleaner import clear_execution_dirs
from preprocessors.digest_downloader_converter.downloader_converter import download_and_convert
from preprocessors.sections_splitter.extract_sections import extract_sections
from preprocessors.sentence_splitter.sentence import split_sentences
from indexers.dense_indexer.embeddings_generator import generate_embeddings
from indexers.sparse_indexer.terrier_indexer import terrier_index
from retrievers.sparse_retriever.terrier_retriever import get_relevant_documents_sparse
from retrievers.hybrid_retriever.hybrid_retriever import get_relevant_documents_hybrid
from retrievers.dense_retriever.dense_retriever import get_relevant_documents_dense
import logging
import os

logging.basicConfig(level=logging.INFO, filename=f"app.log", filemode="w")

os.environ["TOKENIZERS_PARALLELISM"] = "false"


DOWNLOAD_INDEX_DOCS = 0
DOWNLOAD_DOCS = 1
INDEX_DOCS = 2
RETRIEVE_DOCS = 3
CLEAR = 4
EXIT = 5

def process_option(menu_entry_index):
    if menu_entry_index == DOWNLOAD_DOCS:
        download_and_convert(0, 1000)
        extract_sections()
        split_sentences()
    elif menu_entry_index == INDEX_DOCS:
        generate_embeddings()
        terrier_index()
    elif menu_entry_index == DOWNLOAD_INDEX_DOCS:
        download_and_convert(0, 1000)
        extract_sections()
        split_sentences()
        generate_embeddings()
        terrier_index()
    elif menu_entry_index == RETRIEVE_DOCS:
        retrieve_suboptions()
    elif menu_entry_index == CLEAR:
        clear_execution_dirs()


def retrieve_suboptions():
    type_options = ["Sparse", "Dense", "Hybrid", "Volver"]
    index_type_menu = TerminalMenu(type_options)
    collection_options = {
        "Completo": "COMPLETE_COMPLETE",
        "Resoluciones": "COMPLETE_RESUELVE",
        "Disposiciones": "COMPLETE_DISPONE",
        "Visto": "VISTO",
        "Considerando": "CONSIDERANDO",
        "Resuelve": "RESUELVE",
        "Dispone": "DISPONE",
        "Volver": ""
    }

    sections_menu = TerminalMenu(collection_options.keys())

    back_to_main_menu = False
    while not back_to_main_menu:
        index_sel = index_type_menu.show()
        if (index_sel == 0):
            retriever = get_relevant_documents_sparse
        elif (index_sel == 1):
            retriever = get_relevant_documents_dense
        elif (index_sel == 2):
            retriever = get_relevant_documents_hybrid
        elif (index_sel == 3):
            back_to_main_menu = True

        section_options_back = False
        while not section_options_back and not back_to_main_menu:
            sections_sel = sections_menu.show()
            if (sections_sel == 7):
                section_options_back = True
            else:
                selected_key = list(collection_options.keys())[sections_sel]
                do_retrieve(retriever, collection_options[selected_key])
                section_options_back = True
                back_to_main_menu = True

def do_retrieve(retriever, collection):
    print(retriever)
    print(collection)
    query = input("Query: ")
    k = int(input("k documentos a recuperar: "))
    docs = retriever(collection, query, k)
    print("Resultados: ")
    for doc in docs:
        print(doc)
    input("Enter para continuar")

def menu():
    options = ["Descargar, preprocesar e indexar", "Descargar documentos y preprocesar", "Indexar (sparse & dense)", "Recuperar", "Limpiar Entorno", "Salir"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = -1
    while menu_entry_index != EXIT:
        menu_entry_index = terminal_menu.show()
        process_option(menu_entry_index)

if __name__ == "__main__":
    menu()

