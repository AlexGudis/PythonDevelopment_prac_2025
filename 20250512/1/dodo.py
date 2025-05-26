import os
import shutil
import sys
from pathlib import Path
from doit.tools import create_folder, run_once, CmdAction

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))
LOCALE_DIR = PROJECT_ROOT / "mood" / "server" / "locales"
POT_FILE = LOCALE_DIR / "messages.pot"
PO_FILE_RU = LOCALE_DIR / "ru" / "LC_MESSAGES" / "messages.po"
MO_FILE_RU = LOCALE_DIR / "ru" / "LC_MESSAGES" / "messages.mo"
I18N_SOURCE_FILES = list(PROJECT_ROOT.glob("mood/server/**/*.py"))
DOCS_DIR = PROJECT_ROOT / "docs"
DOCS_SOURCE_DIR = DOCS_DIR / "source"
DOCS_BUILD_DIR = DOCS_DIR / "build"
TEST_FILES = list(PROJECT_ROOT.glob("test.py"))
SOURCE_FILES = list(PROJECT_ROOT.glob("mood/**/*.py"))

DOIT_CONFIG = {'default_tasks': ['html']}


SERVER_LOCALE_DIR = PROJECT_ROOT / "mood" / "server" / "locales"
SERVER_POT_FILE = SERVER_LOCALE_DIR / "messages.pot"
SERVER_PO_FILE_RU = SERVER_LOCALE_DIR / "ru" / "LC_MESSAGES" / "messages.po"
SERVER_MO_FILE_RU = SERVER_LOCALE_DIR / "ru" / "LC_MESSAGES" / "messages.mo"
SERVER_SOURCE_FILES = list(PROJECT_ROOT.glob("mood/server/**/*.py"))


CLIENT_LOCALE_DIR = PROJECT_ROOT / "mood" / "client" / "locales"
CLIENT_POT_FILE = CLIENT_LOCALE_DIR / "messages.pot"
CLIENT_PO_FILE_RU = CLIENT_LOCALE_DIR / "ru" / "LC_MESSAGES" / "messages.po"
CLIENT_MO_FILE_RU = CLIENT_LOCALE_DIR / "ru" / "LC_MESSAGES" / "messages.mo"
CLIENT_SOURCE_FILES = list(PROJECT_ROOT.glob("mood/client/**/*.py"))


def _clean_file(filepath):
    """Безопасно удаляет файл, если он существует."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"Removed: {filepath}")
    except OSError as e:
        print(f"Error removing file {filepath}: {e}")


def _clean_dir(dirpath):
    """Безопасно удаляет каталог, если он существует."""
    try:
        dirpath_str = str(dirpath)
        if os.path.isdir(dirpath_str):
            shutil.rmtree(dirpath_str, ignore_errors=True)
    except OSError as e:
        print(f"Error removing directory {dirpath_str}: {e}")





def task_server_pot():
    """Генерирует .pot файл для сервера."""
    babel_cfg_file_path = str(SERVER_LOCALE_DIR / "babel.cfg")
    return {
        "actions": [
            (create_folder, [SERVER_LOCALE_DIR]),
            f'pybabel extract -F {babel_cfg_file_path} -o {SERVER_POT_FILE} {PROJECT_ROOT / "mood/server"}',
        ],
        "targets": [SERVER_POT_FILE],
        "file_dep": SERVER_SOURCE_FILES,
        "clean": [(_clean_file, [SERVER_POT_FILE])],
        "doc": "Generate .pot translation template file for server."
    }

def task_client_pot():
    """Генерирует .pot файл для клиента."""
    babel_cfg_file_path = str(CLIENT_LOCALE_DIR / "babel.cfg")
    return {
        "actions": [
            (create_folder, [CLIENT_LOCALE_DIR]),
            f'pybabel extract -F {babel_cfg_file_path} -o {CLIENT_POT_FILE} {PROJECT_ROOT / "mood/client"}',
        ],
        "targets": [CLIENT_POT_FILE],
        "file_dep": CLIENT_SOURCE_FILES,
        "clean": [(_clean_file, [CLIENT_POT_FILE])],
        "doc": "Generate .pot translation template file for client."
    }





def task_server_po():
    """Обновляет .po файл для сервера."""
    return {
        "actions": [
            (create_folder, [SERVER_PO_FILE_RU.parent]),
            f"pybabel update -i {SERVER_POT_FILE} -d {SERVER_LOCALE_DIR} -l ru",
        ],
        "file_dep": [SERVER_POT_FILE],
        "targets": [SERVER_PO_FILE_RU],
        "clean": True,
        "doc": "Update .po translation file from .pot template for server."
    }

def task_client_po():
    """Обновляет .po файл для клиента."""
    return {
        "actions": [
            (create_folder, [CLIENT_PO_FILE_RU.parent]),
            f"pybabel update -i {CLIENT_POT_FILE} -d {CLIENT_LOCALE_DIR} -l ru",
        ],
        "file_dep": [CLIENT_POT_FILE],
        "targets": [CLIENT_PO_FILE_RU],
        "clean": True,
        "doc": "Update .po translation file from .pot template for client."
    }






def task_server_mo():
    """Компилирует .mo файл для сервера."""
    return {
        "actions": [f"pybabel compile -d {SERVER_LOCALE_DIR} -l ru"],
        "file_dep": [SERVER_PO_FILE_RU],
        "targets": [SERVER_MO_FILE_RU],
        "clean": [(_clean_file, [SERVER_MO_FILE_RU])],
        "doc": "Compile .po file into .mo binary format."
    }


def task_client_mo():
    """Компилирует .mo файл для клиента."""
    return {
        "actions": [f"pybabel compile -d {CLIENT_LOCALE_DIR} -l ru"],
        "file_dep": [CLIENT_PO_FILE_RU],
        "targets": [CLIENT_MO_FILE_RU],
        "clean": [(_clean_file, [CLIENT_MO_FILE_RU])],
        "doc": "Compile .po file into .mo binary format."
    }



def task_server_i18n():
    """Полный цикл перевода для сервера."""
    return {
        "actions": None,
        "task_dep": ["server_pot", "server_po", "server_mo"],
        "doc": "Complete translation process for server",
    }

def task_client_i18n():
    """Полный цикл перевода для клиента."""
    return {
        "actions": None,
        "task_dep": ["client_pot", "client_po", "client_mo"],
        "doc": "Complete translation process for client",
    }

def task_i18n():
    """Полный цикл перевода для всех компонентов."""
    return {
        "actions": None,
        "task_dep": ["server_i18n", "client_i18n"],
        "doc": "Complete translation process for all components",
    }


def task_html():
    """
    Генерация HTML документации с помощью Sphinx.
    """
    html_index_path = str(DOCS_BUILD_DIR / "html" / "index.html")
    build_dir_path = str(DOCS_BUILD_DIR)
    docs_dir_path = str(DOCS_DIR)

    source_files = [str(p) for p in DOCS_SOURCE_DIR.glob("**/*") if p.is_file()]
    mood_files = [str(p) for p in PROJECT_ROOT.glob("mood/**/*.py") if p.is_file()]

    action = CmdAction("make html", cwd=docs_dir_path)

    return {
        "actions": [(create_folder, [DOCS_BUILD_DIR / "html"]), action],
        "file_dep": source_files + mood_files,
        "targets": [html_index_path],
        "clean": [(_clean_dir, [build_dir_path])],
        "doc": "Generate HTML documentation.",
    }



def task_test():
    """
    Запуск интеграционных тестов сервер-клиент.
    """
    test_paths = [str(p) for p in TEST_FILES]
    source_paths = [str(p) for p in SOURCE_FILES]
    mo_file_path = str(MO_FILE_RU)

    return {
        "actions": ["python -m unittest test.py"],
        "file_dep": test_paths + source_paths + [mo_file_path],
        "task_dep": ["i18n"],
        "clean": True,
        "doc": "Run integration tests.",
    }


def task_erase():
    """Clean represitory"""
    return {
            'actions': ['git clean -xdf'],
    }


def task_sdist():
    """Make sdist"""
    return {
            'task_dep': ['html', 'erase'],
            'actions': ['python3 -m build -s -n']
    }


def task_wheel():
    """Make wheel"""
    return {
            'task_dep': ['html'],
            'actions': ['python3 -m build -w']
    }


babel_cfg_content = """\
[python: mood/**.py]
"""
babel_cfg_path = LOCALE_DIR / "babel.cfg"
if not babel_cfg_path.exists():
    LOCALE_DIR.mkdir(parents=True, exist_ok=True)
    with open(babel_cfg_path, "w") as f:
        f.write(babel_cfg_content)

