from pathlib import Path
from zipfile import ZipFile

# Теперь по команде doit из директории /0 идёт пересборка всего при каких-то изменениях, иначе ничего не происходит


DOIT_CONFIG = {"default_tasks": ['docs']}
DOCZIP = 'docs.zip'
DOCLIST = 'docs.list'


def task_docs():
    """Build..."""
    yield {'name': "html",
           "file_dep": [*Path(".").glob("*.py"), *Path(".").glob("*.rst")],
           "actions": ["sphinx-build -M html ./source _build"],
    }

    yield {'name': "text",
           "file_dep": [*Path(".").glob("*.py"), *Path(".").glob("*.rst")],
           "actions": ["sphinx-build -M text ./source _build"],
    }


def task_zip():
    return {'actions': [f"zip -r {DOCZIP} ./_build"],
            'task_dep':['docs'],
            'targets':['docs.zip']}


'''def task_stat():
    return {'actions': ["python3 -m zipfile -l docs.zip > ./docs.list"],
            'file_dep': ["docs.zip"],
            'targets': ["docs.list"]
            }'''

def task_stat():

    def make_list():
        src, curdir = "./docs.zip", "./"
        with ZipFile(src, 'r') as zf:
            res = zf.namelist()

        with open("docs.list", "w") as of:
            print("\n".join(res), file=of)



    return {
        'actions': [make_list],
        'file_dep': ["docs.zip"],
        'targets': ["docs.list"],
    }
    


def task_erase():
    "Erase all..."
    return {
        "actions": ["git reset --hard", "git clean -xdf"]
    }