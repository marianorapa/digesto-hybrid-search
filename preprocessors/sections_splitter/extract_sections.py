import re
import os
import logging
from utils.objects.document import Document
from utils.objects.metadata import Metadata

logger = logging.getLogger("digesto-hybrid-search-logger")

config = os.environ

downloader_converter_metadata = Metadata(config["DOWNLOADER_CONVERTER_META_FILE"]).load()
extract_sections_metadata = Metadata(config["EXTRACT_SECTIONS_META_FILE"])

# Define the k
keywords = ["VISTO:", "CONSIDERANDO:"]
last_key = ["R E S U E L V E", "D I S P O N E", "RESUELVE", "DISPONE"]

def create_directories():
    os.makedirs(config["EXTRACT_SECTION_VISTO_OUTPUT_DIR"], exist_ok = True)
    os.makedirs(config["EXTRACT_SECTION_CONSIDERANDO_OUTPUT_DIR"], exist_ok=True)
    os.makedirs(config["EXTRACT_SECTION_RESUELVE_OUTPUT_DIR"], exist_ok=True)
    os.makedirs(config["EXTRACT_SECTION_DISPONE_OUTPUT_DIR"], exist_ok=True)

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
    with open(f"{output_dir}/{document.get_txt_filename()}", "w") as output:
        output.write(section_text)

def do_extract_sections():
    downloader_converter_valid_documents = downloader_converter_metadata.get_valid_documents()

    # downloader_converter_valid_document: Document
    for document in downloader_converter_valid_documents:

        sections = extract_sections_from_document(document)
        
        if len(sections) < 3:
            extract_sections_metadata.error(document, "Less than 3 sections")
            pass

        save_section(document, sections[0], config["EXTRACT_SECTION_VISTO_OUTPUT_DIR"])
        save_section(document, sections[1], config["EXTRACT_SECTION_CONSIDERANDO_OUTPUT_DIR"])

        if document.is_resolution():
            save_section(document, sections[2], config["EXTRACT_SECTION_RESUELVE_OUTPUT_DIR"])

        elif document.is_disposition():
            save_section(document, sections[2], config["EXTRACT_SECTION_DISPONE_OUTPUT_DIR"])

    #for file in os.listdir(base_dir):
    #    if file.endswith(".txt"):
    #        with open(base_dir + "/" + file) as f:
    #            text = f.read()
    #            sections = extract_sections_from_text_and_save_to_file(text, file)
    #            if len(sections) == 3:
    #                with open(f"{config["EXTRACT_SECTION_VISTO_OUTPUT_DIR"]}/{file}", "w") as output:
    #                    output.write(sections[0])
    #                    
    #                with open(f"{config["EXTRACT_SECTION_CONSIDERANDO_OUTPUT_DIR"]}/{file}", "w") as output:
    #                    output.write(sections[1])
    #
    #                if last_section == "resuelve":
    #                    last_section_dir = config["EXTRACT_SECTION_RESUELVE_OUTPUT_DIR"]
    #                elif last_section == "dispone":
    #                    last_section_dir = config["EXTRACT_SECTION_DISPONE_OUTPUT_DIR"]
    #
    #                with open(f"{last_section_dir}/{file}", "w") as output:
    #                    output.write(sections[2])
    #                        
    #            else:
    #                failures.append(file)

def extract_sections():
    logger.info("Sections Splitter Started")

    create_directories()
    do_extract_sections()

    #failures_resuelve = extract_sections_and_write_to_file("resuelve")
    #failures_dispone = extract_sections_and_write_to_file("dispone")

    #if failures_dispone is not None and failures_resuelve is not None:
    #    with open(config["EXTRACT_SECTIONS_META_FILE"], 'w') as file:
    #        file.writelines(str(failures_resuelve))
    #        file.writelines(str(failures_dispone))