import shutil
import os

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

    remove_whatever("collection")
    remove_whatever("indexes")
    remove_whatever("./preprocessors/digest_downloader_converter/raw")

