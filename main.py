import logging
import logging.config

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "simple": {
            "format": "%(levelname)s - %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "default",
            "filename": "app.log",
        },
    },
    "loggers": {
        "": {  # Logger raíz
            "level": "WARNING",
            "handlers": ["console", "file"],
        },
        "digesto-hybrid-search-logger": {  # Logger personalizado
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": False,  # Evita que este logger pase los mensajes al logger raíz
        },
    },
}

logging.config.dictConfig(LOGGING_CONFIG)

logger = logging.getLogger("digesto-hybrid-search-logger")


from dotenv import load_dotenv
load_dotenv(verbose=True)
from simple_term_menu import TerminalMenu
from utils.execution_cleaner import clear_execution_dirs
from preprocessors.digest_downloader_converter.downloader_converter import download_and_convert
from preprocessors.sections_splitter.extract_sections import extract_sections
from preprocessors.sentence_splitter.sentence import split_sentences
from indexers.dense_indexer.embeddings_generator import generate_embeddings
from indexers.sparse_indexer.terrier_indexer import terrier_index
from retrievers.sparse_retriever.terrier_retriever import get_ranking_sparse
from retrievers.hybrid_retriever.hybrid_retriever import get_ranking_hybrid_interpolating_rank
from retrievers.hybrid_retriever.hybrid_retriever import get_ranking_hybrid_interpolating_score
from retrievers.dense_retriever.dense_retriever import get_ranking_dense
import utils.query_executor

DOWNLOAD_INDEX_DOCS = 0
DOWNLOAD_DOCS = 1
INDEX_DOCS = 2
RETRIEVE_DOCS = 3
COMPARE_MODELS = 4
CLEAR = 5
EXIT = 6

def process_option(menu_entry_index):
    if menu_entry_index == DOWNLOAD_DOCS:
        number_of_docs = input("Cantidad docs a descargar: ")
        download_and_convert(int(number_of_docs))
        extract_sections()
        split_sentences()
    elif menu_entry_index == INDEX_DOCS:
        generate_embeddings()
        terrier_index()
    elif menu_entry_index == DOWNLOAD_INDEX_DOCS:
        number_of_docs = input("Cantidad docs a descargar: ")
        download_and_convert(int(number_of_docs))
        extract_sections()
        split_sentences()
        generate_embeddings()
        terrier_index()
    elif menu_entry_index == RETRIEVE_DOCS:
        retrieve_suboptions()
    elif menu_entry_index == COMPARE_MODELS:
        compare_models()
    elif menu_entry_index == CLEAR:
        confirmation = input(
            "¿Estás seguro de que querés limpiar el entorno? Esto eliminará archivos. (s/n): ").strip().lower()
        if confirmation == "s":
            clear_execution_dirs()
            print("El entorno ha sido limpiado.")
        else:
            print("Operación cancelada.")

def compare_models():
    query = input("Query: ")
    k = int(input("k documentos a recuperar: "))
    input_relevant_documents = input("Doc IDS relevantes a priori conocidos, separados por coma: ")
    try:
        relevant_documents = [int(x) for x in input_relevant_documents.split(",")]
    except:
        relevant_documents = []

    utils.query_executor.query(query, k, relevant_documents)


def retrieve_suboptions():
    type_options = ["Sparse", "Dense", "Hybrid (Score)", "Hybrid (Rank)", "Volver"]
    index_type_menu = TerminalMenu(type_options)
    collection_options = {
        "Completo": "COMPLETE_COMPLETE",
        "Resoluciones": "COMPLETE_RESUELVE",
        "Disposiciones": "COMPLETE_DISPONE",
        "Visto": "VISTO",
        "Considerando": "CONSIDERANDO",
        "Resuelve": "RESUELVE",
        "Dispone": "DISPONE",
        "Resolutiva": "RESOLUTIVA",
        "Volver": ""
    }

    sections_menu = TerminalMenu(collection_options.keys())

    back_to_main_menu = False
    while not back_to_main_menu:
        index_sel = index_type_menu.show()
        if (index_sel == 0):
            retriever = get_ranking_sparse
        elif (index_sel == 1):
            retriever = get_ranking_dense
        elif (index_sel == 2):
            retriever = get_ranking_hybrid_interpolating_score
        elif (index_sel == 3):
            retriever = get_ranking_hybrid_interpolating_rank
        elif (index_sel == 4):
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
    ranking = retriever(collection, query, k, [])
    print("Resultados: ")
    ranking.set_output_columns(["Order", "ID", "URL", "Relevant", "Score"])
    print(f"\nResults (Total {ranking.get_last_rank()}):")
    print(ranking.get_first_k_documents_as_table())
    input("Enter para continuar")

def menu():
    options = ["Descargar, preprocesar e indexar", "Descargar y preprocesar", "Indexar (sparse & dense)", "Recuperar", "Comparar modelos", "Limpiar Entorno", "Salir"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = -1
    while menu_entry_index != EXIT:
        menu_entry_index = terminal_menu.show()
        process_option(menu_entry_index)

if __name__ == "__main__":
    menu()

