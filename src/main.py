from task_manager import TaskManager
import sys
from debug_menu import MenuManager
import signal


args = sys.argv[1:]


def create_app():
    manager = TaskManager()
    manager.load_tasks()
    manager.start()


def exit_on_sigint(signum, frame):
    sys.exit(0)


if __name__ == "__main__":
    if args and args[0].lower() == "debug":
        signal.signal(signal.SIGINT, exit_on_sigint)
        MenuManager.run_menu()
    if not args:
        create_app()
