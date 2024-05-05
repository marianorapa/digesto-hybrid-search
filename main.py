from simple_term_menu import TerminalMenu

from preprocessors.digest_downloader_converter.downloader_converter import download_and_convert

DOWNLOAD_DOCS = 0
INDEX_DOCS = 1
RETRIEVE_DOCS = 2
EXIT = 3


def process_option(menu_entry_index):
    if menu_entry_index == DOWNLOAD_DOCS:
        download_and_convert(1, 10)
    elif menu_entry_index == INDEX_DOCS:
        print("Index")
    elif menu_entry_index == RETRIEVE_DOCS:
        print("Retrieve")


def menu():
    options = ["Download docs", "Index (sparse & dense)", "Retrieve", "Exit"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = -1
    while menu_entry_index != EXIT:
        menu_entry_index = terminal_menu.show()
        process_option(menu_entry_index)


if __name__ == "__main__":
    menu()

