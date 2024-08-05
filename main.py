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
        download_and_convert(0, 50000)
        extract_sections()
        split_sentences()
    elif menu_entry_index == INDEX_DOCS:
        generate_embeddings()
        terrier_index()
    elif menu_entry_index == RETRIEVE_DOCS:
        retrieve_suboptions()


def retrieve_suboptions():
    type_options = ["Sparse", "Hybrid", "Volver"]
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
            # retriever = SparseRetriever()
            #retriever = "SparseRetriever"
            retriever = get_relevant_documents_sparse
        elif (index_sel == 1):
            # retriever = HybridRetriever()
            #retriever = "HybridRetriever"
            retriever = get_relevant_documents_hybrid
        elif (index_sel == 2):
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
    options = ["Descargar documentos y preprocesar", "Indexar (sparse & dense)", "Recuperar", "Salir"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = -1
    while menu_entry_index != EXIT:
        menu_entry_index = terminal_menu.show()
        process_option(menu_entry_index)


if __name__ == "__main__":
    menu()

