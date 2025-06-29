import json
from unittest import mock

import pytest

nx = pytest.importorskip('networkx')

from app.services import advanced_osint_service as aos


def test_hibp_breaches_no_results():
    with mock.patch('requests.get') as mget:
        mget.return_value.status_code = 404
        res = aos.hibp_breaches('none@example.com', 'KEY')
        assert res == []


def test_build_relation_graph():
    accounts = [
        {'platform': 'tw', 'username': 'alice'},
        {'platform': 'gh', 'username': 'alice'},
        {'platform': 'fb', 'username': 'bob'},
    ]
    graph = aos.build_relation_graph(accounts)
    assert isinstance(graph, nx.Graph)
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 1
