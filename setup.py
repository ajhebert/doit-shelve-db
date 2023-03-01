from setuptools import setup

setup(
    name = 'doit-shelve-db',
    version = "0.1.0",
    description = "A shelve-based backend for PyDoit",
    url = 'https://github.com/ajhebert/doit-shelve-db',
    py_modules=['doit_shelve_db'],
    entry_points = {
        'doit.BACKEND': [
            'shelve = doit_shelve_db:ShelveDB'
        ]
    },
)