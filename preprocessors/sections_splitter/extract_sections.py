import re
import os
import logging
from utils.objects.document import Document
from utils.objects.metadata import Metadata

logger = logging.getLogger("digesto-hybrid-search-logger")

config = os.environ

downloader_converter_metadata = None
extract_sections_metadata = None

# Define the k
keywords = ["VISTO:", "CONSIDERANDO:"]
last_key = ["R E S U E L V E", "D I S P O N E", "RESUELVE", "DISPONE"]

def init_metadata():
    global downloader_converter_metadata, extract_sections_metadata
    downloader_converter_metadata = Metadata(config["DOWNLOADER_CONVERTER_META_FILE"]).load()
    extract_sections_metadata = Metadata(config["EXTRACT_SECTIONS_META_FILE"])

def documents_dir(base_dir: str):
    return base_dir + '/documents'

def create_directories():
    os.makedirs(documents_dir(config["SECTION_VISTO_DIR"]), exist_ok = True)
    os.makedirs(documents_dir(config["SECTION_CONSIDERANDO_DIR"]), exist_ok=True)
    os.makedirs(documents_dir(config["SECTION_RESOLUTIVA_DIR"]), exist_ok=True)
    os.makedirs(documents_dir(config["SECTION_RESUELVE_DIR"]), exist_ok=True)
    os.makedirs(documents_dir(config["SECTION_DISPONE_DIR"]), exist_ok=True)

def extract_sections_from_document(document: Document) -> list[str]:
    text = document.get_text_content()
    # Split the text using regular expressions
    last = None

    for key in last_key:
        if key in text:
            last = key
            break

    if last is None:
        extract_sections_metadata.error(document, "Missing last section key")

    all_keywords = keywords + [last]
    text = re.sub(r'\s+', ' ', text)

    sections = re.split("|".join(map(re.escape, all_keywords)), text)

    # Remove empty sections
    return [section.strip() for section in sections if section.strip()][-3:]

def save_section(document: Document, section_text: str, output_dir: str):
    try:
        output_file = f"{output_dir}/{document.get_txt_filename()}"
        with open(output_file, "w") as output:
            output.write(section_text)
        return output_file
    except Exception as e:
        extract_sections_metadata.error(document, f"Failure {e} saving section to {output_dir}")

def do_extract_sections():
    downloader_converter_valid_documents = downloader_converter_metadata.get_valid_documents()

    # downloader_converter_valid_document: Document
    for document in downloader_converter_valid_documents:

        sections = extract_sections_from_document(document)
        
        if len(sections) < 3:
            extract_sections_metadata.error(document, "Less than 3 sections")
            pass

        visto_section = sections[0]
        considerando_section = sections[1]
        resolutiva_section = sections[2]
        
        visto_file = save_section(document, visto_section, documents_dir(config["SECTION_VISTO_DIR"]))
        document.set_visto_file_path(visto_file)

        considerando_file = save_section(document, considerando_section, documents_dir(config["SECTION_CONSIDERANDO_DIR"]))
        document.set_considerando_file_path(considerando_file)
        
        resolutiva_file = save_section(document, resolutiva_section, documents_dir(config["SECTION_RESOLUTIVA_DIR"]))
        document.set_resolutiva_file_path(resolutiva_file)

        if document.is_resolution():
            resuelve_file = save_section(document, resolutiva_section, documents_dir(config["SECTION_RESUELVE_DIR"]))
            document.set_resuelve_file_path(resuelve_file)

        elif document.is_disposition():
            dispone_file = save_section(document, resolutiva_section, documents_dir(config["SECTION_DISPONE_DIR"]))
            document.set_dispone_file_path(dispone_file)

        extract_sections_metadata.success(document)

def extract_sections():
    logger.info("Sections Splitter Started")

    create_directories()
    init_metadata()
    do_extract_sections()
    extract_sections_metadata.save()

    logger.info("Sections Splitter Ended")