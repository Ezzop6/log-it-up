import json
from rich.pretty import Pretty
import traceback
import threading
import sys
import signal
from task_manager import TaskManager
from debug_menu import MenuManager
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import os
import time
import re
console = Console()

args = sys.argv[1:]
shutdown_event = threading.Event()
start_time = time.perf_counter()
SHOW_TRACEBACK = "--traceback" in args


def create_app():
    manager = TaskManager()
    manager.load_tasks()
    manager.start()


def exit_on_sigint(signum, frame):
    console.print("\n[bold yellow]Received SIGINT. Exiting...[/]")
    sys.exit(0)


def print_traceback(args):
    formatted_traceback = "".join(traceback.format_tb(args.exc_traceback))
    console.print(Panel(
        formatted_traceback,
        title="Traceback",
        border_style="blue"
    ))


def print_exception(args):
    tb = args.exc_traceback
    filename, line_no = None, None

    while tb:
        frame = tb.tb_frame
        file_path = frame.f_code.co_filename
        if "site-packages" not in file_path and "threading.py" not in file_path:
            filename = os.path.abspath(file_path)
            line_no = tb.tb_lineno
        tb = tb.tb_next

    if not filename:
        filename, line_no = "Unknown", "Unknown"

    console.print(
        Panel(
            f"[bold red]Uncaught exception:[/bold red] [yellow]{args.thread.name}[/yellow]\n"
            f"[bold white]Exception:[/bold white] {args.exc_type.__name__}\n"
            f"[bold white]Message:[/bold white] {args.exc_value}\n"
            f"[bold blue]File:[/bold blue] {filename}:{line_no}\n",
            title="Exception",
            border_style="red",

        ),
    )


def print_variables(args):
    extracted_variables = {}

    tb = args.exc_traceback
    while tb:
        frame = tb.tb_frame
        for key, value in frame.f_locals.items():
            if key not in {"self", "cls"} and key not in extracted_variables:
                extracted_variables[key] = value
        tb = tb.tb_next

    if extracted_variables:
        console.print(Panel(
            Pretty(extracted_variables, expand_all=True),
            title="Function Parameters",
            border_style="green",
        ))
    else:
        console.print("[bold yellow]No additional parameters found.[/bold yellow]")


def extract_details(exc_message):
    details = []

    # Check SQL query and parameters
    sql_match = re.search(r"SQL: (.*?)\n", exc_message, re.DOTALL)
    params_match = re.search(r"Params: (.*?)\]", exc_message, re.DOTALL)
    if sql_match:
        sql_query = sql_match.group(1).strip()
        params = params_match.group(1).strip() if params_match else "N/A"
        details.append(f"SQL: {sql_query} | Params: {params}")

    # Check JSON data
    json_match = re.search(r"(\{.*?\})", exc_message, re.DOTALL)
    if json_match:
        try:
            json_data = json.loads(json_match.group(1))
            details.append(f"JSON Data: {json.dumps(json_data, indent=2)}")
        except json.JSONDecodeError:
            pass

    # Check context
    context_match = re.search(r"Error Context: (.*?)\n", exc_message, re.DOTALL)
    if context_match:
        context_info = context_match.group(1).strip()
        details.append(f"Context: {context_info}")

    if not details:
        return f'[bold yellow]See Function Parameters for more details.[/bold yellow]'
    return "\n".join(details)


def print_caller_context(args):
    exc_value = args.exc_value
    exc_traceback = args.exc_traceback
    table = Table(title="Caller Context", border_style="cyan", expand=True)
    table.add_column("Level", justify="center", style="bold blue")
    table.add_column("File:Line", style="magenta")
    table.add_column("Function", style="green")
    table.add_column("Code", style="white")

    level = 0
    current_exception = exc_value
    current_traceback = exc_traceback

    while current_exception:
        stack = traceback.extract_tb(current_traceback)
        for frame in stack:
            level += 1
            table.add_row(
                str(level),
                f'{os.path.abspath(frame.filename)}:{frame.lineno}',
                frame.name,
                frame.line.strip() if frame.line else "[N/A]"
            )

        if current_exception.__cause__:
            current_exception = current_exception.__cause__
            current_traceback = current_exception.__traceback__
        elif current_exception.__context__:
            current_exception = current_exception.__context__
            current_traceback = current_exception.__traceback__
        else:
            break

    console.print(table)


def print_chained_exceptions_table(args):
    exc_type = args.exc_type
    exc_value = args.exc_value
    exc_traceback = args.exc_traceback
    table = Table(title="Chained Exceptions", border_style="cyan", expand=True)
    table.add_column("Level", style="bold blue", justify="center")
    table.add_column("Type", style="magenta")
    table.add_column("Message", style="yellow")
    table.add_column("File:Line", style="green")
    table.add_column("Details", style="cyan")

    current_exception = exc_value
    current_traceback = exc_traceback
    level = 0

    while current_exception:
        level += 1

        extracted_file = "Unknown"
        extracted_line = "Unknown"
        details = extract_details(str(current_exception))

        if current_traceback:
            tb_frame = current_traceback.tb_frame
            extracted_file = os.path.abspath(tb_frame.f_code.co_filename)
            extracted_line = current_traceback.tb_lineno

        table.add_row(
            str(level),
            type(current_exception).__name__,
            str(current_exception).split("\n")[0],
            f"{extracted_file}:{extracted_line}",
            details
        )

        if current_exception.__cause__:
            current_exception = current_exception.__cause__
            current_traceback = current_exception.__traceback__
        elif current_exception.__context__:
            current_exception = current_exception.__context__
            current_traceback = current_exception.__traceback__
        else:
            break

    console.print(table)


def minimal_exception_handler(exc_type, exc_value, exc_traceback):
    console.print(
        Panel.fit(
            f"[bold red]Error:[/bold red] [yellow]{exc_type.__name__}[/yellow]\n"
            f"[white]{exc_value}[/white]",
            title="Exception",
            border_style="red",
        )
    )
    if SHOW_TRACEBACK:
        console.print_exception(show_locals=True)


def global_thread_exception_handler(args):
    print_traceback(args)
    print_exception(args)
    print_caller_context(args)
    print_chained_exceptions_table(args)
    print_variables(args)


sys.excepthook = minimal_exception_handler
threading.excepthook = global_thread_exception_handler
signal.signal(signal.SIGINT, exit_on_sigint)


if __name__ == "__main__":
    try:
        if args and args[0].lower() == "debug":
            MenuManager.run_menu()
        elif not args or "--traceback" in args:
            create_app()
    except KeyboardInterrupt:
        exit_on_sigint(signal.SIGINT, None)
    except Exception as e:
        minimal_exception_handler(type(e), e, sys.exc_info()[2])
        sys.exit(1)
