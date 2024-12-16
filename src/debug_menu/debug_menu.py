import sys
from typing import Callable, Optional
from dataclasses import dataclass
from simple_term_menu import TerminalMenu
from config import CollectorType
from database import Database

database = Database()


@dataclass
class MenuItem:
    title: str
    action: Optional[Callable] = None
    next_menu: Optional[str] = None


class MenuManager:
    _menus: dict[str, list[MenuItem]] = {}

    @classmethod
    def menu(cls, name: str):
        def decorator(func):
            # get menu items
            menu_items = func()

            cls._menus[name] = menu_items
            return func
        return decorator

    @classmethod
    def run_menu(cls, menu_name: str = "main"):
        if menu_name not in cls._menus:
            return

        while True:
            menu_items = cls._menus[menu_name]
            options = [item.title for item in menu_items]
            terminal_menu = TerminalMenu(options, title=menu_name.capitalize())
            choice_index = terminal_menu.show()

            if choice_index is None:
                break

            selected_item = menu_items[choice_index]

            if selected_item.action:
                selected_item.action()

            if selected_item.next_menu:
                cls.run_menu(selected_item.next_menu)


EXIT = MenuItem("Exit", action=sys.exit)


def print_collectors_info(query_result):
    # print collectors info
    if not query_result:
        print("No collectors found.")
        return

    for collector in query_result:
        print(f"ID: {collector.id}, Name: {collector.name}, Type: {collector.type}, Timestamp: {getattr(collector, 'timestamp', 'N/A')}")
    print()
# fmt: off
COLLECTOR_INFO_LOGS = lambda: print_collectors_info(database.get_collectors_info(CollectorType.LOGS))
COLLECTOR_INFO_BASH = lambda: print_collectors_info(database.get_collectors_info(CollectorType.BASH))
# fmt: off


@MenuManager.menu('main')
def create_main_menu():
    return [
        MenuItem("Database", next_menu="db_submenu"),
        EXIT
    ]


@MenuManager.menu('db_submenu')
def create_db_submenu():
    return [
        MenuItem("Database Collectors info", next_menu="db_submenu_collectors"),
        MenuItem("Database Data of items", next_menu="db_submenu_data"),
        MenuItem("Back", next_menu="main"),
        EXIT
    ]


@MenuManager.menu('db_submenu_collectors')
def create_db_submenu_collectors():
    return [
        MenuItem("Log Collectors", action=COLLECTOR_INFO_LOGS),
        MenuItem("Bash Collectors", action=COLLECTOR_INFO_BASH),
        MenuItem("Back", next_menu="db_submenu"),
        EXIT
    ]
