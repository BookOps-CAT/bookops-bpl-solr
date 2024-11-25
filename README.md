![tests](https://github.com/BookOps-CAT/bookops-bpl-solr/actions/workflows/unit-tests.yaml/badge.svg?branch=main) [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-bpl-solr/badge.svg?branch=main)](https://coveralls.io/github/BookOps-CAT/bookops-bpl-solr?branch=main) ![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/BookOps-CAT/bookops-bpl-solr) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# bookops-bpl-solr client
BookOps Python wrapper around BPL Solr service.

Requires Python 3.8 & up.
Requires credentials from BPL WebApps.


## version

> 0.5.0

## Instalation
Install via pip:

```bash
python -m pip install git+https://github.com/BookOps-CAT/bookops-bpl-solr
```

## Basic usage

Retrieve a specific Sierra bib:
```python
with SolrSession(
    authorization="your_client_key", endpoint="solr_endpoint"
) as session:
    response = session.search_bibNo(10841318)
    print(response.json())

```
```json
{
  "response": {
    "numFound": 1,
    "start": 0,
    "numFoundExact": true,
    "docs": [
      {
        "id": "10841318",
        "title": "The Civil War.",
        "author_raw": "Robertson, James I.",
        "created_date": "2002-08-31T21:14:32Z",
        "publishYear": 1963,
        "material_type": "Book",
        "call_number": "973.7 R651 C",
        "language": [
          "English"
        ]
      }
    ]
  }
}
```

Retrieve records matching particular ISBNs:
```python
with SolrSession(authorization="your_client_key", endpoint="solr_endpoint") as session:
    response = session.search_isbns(
        ["9780810984912", "9781419741890", "0810984911"]
    print(response.status_code)
    print(response.url)
```

Retrive records by e-content reserve id (037$a MARC tag):
```python
with SolrSession(authorization="your_client_key", endpoint="solr_endpoint") as session:
    response = session.search_reserveId("8CD53ED9-CEBD-4F78-8BEF-20A58F6F3857")
```

Retrieve expired e-content (Overdrive):
```python
with SolrSession(authorization="your_client_key", endpoint="solr_endpoint") as session:
    response = session.find_expired_content()
```

Custom query:
```python
with SolrSession(authorization="your_client_key", endpoint="solr_endpoint") as session:
    payload = {
        "q": "title:civil AND war",
        "fq": "ss_type:catalog",
        "fq": "material_type:Book",
        "rows": 20,
    }
    response = session._send_request(payload)
```

## Changelog

### [0.5.0] - 2024-11-25
#### Added
 + type annotations where they were missing in `SolrSession` class and methods
 + py.typed marker so applications using `bookops-bpl-solr` will use the annotations from this package
 + Python 3.13 to GitHub Actions automated tests
 + `BookopsSolrError` as top-level import per #8 

#### Changed:
 + implicit optional types changed to explicit optional types in `SolrSession`
 + default value for `SolrSession.timeout` is now `(3,3,)` as specified in docstring
 + changed `if type() is` syntax to `if isinstance()` in all type checks in `SolrSession`
 + ignore Flake8 F401 errors in `__init__.py` and `test_bookops_bpl_solr.py`
 + moved `pytest.ini_options` to `pyproject.toml` and removed `pytest.ini` file
 + updated authors in `pyproject.toml` per #21 
 + Updated dependencies:
   + `certifi` (2024.8.30)
   + `charset-normalizer` (3.4.0)
   + `idna` (3.10)
   + `requests` (2.32.3)
   + `urllib3` (2.2.3)
 + Updated dev depenencies:
   + `click` (8.1.7)
   + `colorama` (0.4.6)
   + `coverage` (7.6.1)
   + `exceptiongroup` (1.2.2)
   + `iniconfig` (2.0.0)
   + `mypy-extensions` (1.0.0)
   + `packaging` (24.2)
   + `pathspec` (0.12.1)
   + `platformdirs` (4.3.6)
   + `pluggy` (1.5.0)
   + `pytest-mock` (3.14.0)
   + `pytest` (7.4.4)
   + `tomli` (2.1.0)
   + `types-requests` (2.32.0.241016)
   + `typing-extensions` (4.12.2)
   + `urllib3` (2.2.3)

#### Fixed
 + type annotation error for `SolrSession.search_controlNo`. `default_response_fields` should be `bool` not `str` or `list`
 + urls in responses of livetests

#### Removed
 + unused imports from `session.py`

### [0.4.0] - 2024-1-2
#### Added
+ dev dependencies:
    + exceptiongroup (1.2.0)
  
#### Changed
+ dependencies:
    + python 3.8
    + requests (2.31.0)
    + certifi (2023.11.17)
+ dev dependencies:
    + black (22.12.0)
    + pytest (7.4.3)
    + pytest-cov (4.1.0)
    + pytest-mock (3.12.0)
+ `test_search_controlNo()` edited with updated control numbers 
+ `conftest.py` path to credentials
+ `coverage` configuration moved from `.coveragerc` to `pyproject.toml`
+ `master` branch renamed to `main`
+ GitHub-Actions updated 
    + checkout and setup-python actions upgraded to v4
    + tests triggered only on push to main and PR to main
    + Python 3.11 and 3.12 added to tests

#### Fixed
+ corrected application of two filters (`fq`) in live test request so both filters are used in a query

#### Removed
 + dev dependencies:
    + atomicwrites
    + attrs
    + ghp-import
    + importlib-metadata
    + py
    + toml
    + typed-ast
    + zipp

### [0.3.0] - 2022-06-28
#### Added
+ `search_controlNo()` to query by control number (MARC 001 tag)
+ `search_upcs()` to query by UPC number (MARC 024 tag)
+ dev dependencies:
    + mypy (0.961)
    + types-requests (2.28.0)

#### Fixed
+ typing errors in `session.py`

### [0.2.0] - 2022-02-06
#### Changed
+ dependencies:
    + certifi to 2021.10.8
    + requests to 2.27.1
    + urllib3 to 1.26.8
    + idna to 3.3
    + removed mkdocs, mike, mkapi
+ CI moved from Travis to Github-Actions
    + added Python 3.10

### [0.1.1] - 2020-10-30
#### Fixed
+ pyproject.toml python 3.9 compatibility added
+ default py 3.8 env
#### Changed
+ urllib3 bump from 1.25.10 to 1.25.11

## References

+ [Apache Solr Reference Guide](https://lucene.apache.org/solr/guide/8_6/)
+ [pysolr](https://pypi.org/project/pysolr/)

[0.3.0]: https://github.com/BookOps-CAT/bookops-bpl-solr/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/BookOps-CAT/bookops-bpl-solr/compare/v0.1.1...v0.2.0
[0.1.1]: https://github.com/BookOps-CAT/bookops-bpl-solr/compare/v0.1.0...v0.1.1
[0.3.0]: https://github.com/BookOps-CAT/bookops-bpl-solr/compare/v0.2.0...v0.3.0
[0.4.0]: https://github.com/BookOps-CAT/bookops-bpl-solr/compare/v0.3.0...v0.4.0