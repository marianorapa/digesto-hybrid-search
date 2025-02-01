import shutil
import os

config = os.environ

def remove_whatever(path):
    try:
        os.remove(path)
    except:
        try:
            shutil.rmtree(path)
        except:
            return

def clear_execution_dirs():
    remove_whatever("app.log")
    remove_whatever("./preprocessors/digest_downloader_converter/downloads-meta.txt")
    remove_whatever("./preprocessors/digest_downloader_converter/downloads-progress.txt")
    remove_whatever("./preprocessors/digest_downloader_converter/downloads-not-founds.txt")
    remove_whatever("deleted-files.txt")
    remove_whatever("downloads-empty.txt")
    remove_whatever("downloads-meta.txt")
    remove_whatever(config["EMBEDDINGS_GENERATOR_META_FILE"])
    remove_whatever(config["SENTENCES_META_FILE"])
    remove_whatever(config["DOWNLOADER_CONVERTER_META_FILE"])
    remove_whatever(config["EXTRACT_SECTIONS_META_FILE"])

    remove_whatever("collection")
    remove_whatever("indexes")
    remove_whatever("./preprocessors/digest_downloader_converter/raw")

