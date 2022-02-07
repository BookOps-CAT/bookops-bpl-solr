[![tests](https://github.com/BookOps-CAT/bookops-bpl-solr/actions/workflows/unit-tests.yaml/badge.svg?branch=master)] [![Coverage Status](https://coveralls.io/repos/github/BookOps-CAT/bookops-bpl-solr/badge.svg?branch=master)](https://coveralls.io/github/BookOps-CAT/bookops-bpl-solr?branch=master) ![GitHub tag (latest SemVer)](https://img.shields.io/github/v/tag/BookOps-CAT/bookops-bpl-solr) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# bookops-bpl-solr client
BookOps Python wrapper around BPL Solr service.

Requires Python 3.7 & up.
Requires credentials from BPL WebApps.


## version

> 0.2.0

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

### [0.2.0] - 2022-02-06
#### Changed
+ Dependencies:
    + certifi to 2021.10.8
    + requests to 2.27.1
    + urllib3 to 1.26.8
    + idna to 3.3
    + removed mkdocs, mike, mkapi
+ CI moved from Travis to Github-Actions
    + added Python 3.10

## References

+ [Apache Solr Reference Guide](https://lucene.apache.org/solr/guide/8_6/)
+ [pysolr](https://pypi.org/project/pysolr/)


[0.2.0]