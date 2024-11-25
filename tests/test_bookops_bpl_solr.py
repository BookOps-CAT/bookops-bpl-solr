from bookops_bpl_solr import __version__


def test_version():
    assert __version__ == "0.5.0"


def test_SolrSession_top_import():
    from bookops_bpl_solr import SolrSession  # noqa: F401


def test_BookopsSolrError_import():
    from bookops_bpl_solr import BookopsSolrError  # noqa: F401
