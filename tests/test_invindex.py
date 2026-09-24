import json
import threading
import unittest
import urllib.error
import urllib.request

from invindex import InvIndex
from server import serve

class TestInvIndex(unittest.TestCase):
    def test_add_then_search(self):
        index = InvIndex()
        index.add("d1", "the quick fox")
        self.assertEqual(index.search("quick")["docs"], ["d1"])

    def test_search_unknown_term(self):
        self.assertEqual(InvIndex().search("nope")["docs"], [])

    def test_search_is_case_insensitive(self):
        index = InvIndex()
        index.add("d1", "The Quick Fox")
        self.assertEqual(index.search("QUICK")["docs"], ["d1"])

    def test_delete_reports(self):
        index = InvIndex()
        index.add("d1", "the quick fox")
        self.assertTrue(index.delete("d1")["deleted"])

    def test_http_add_search(self):
        server = serve(0)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = "http://127.0.0.1:%d" % server.server_port
        urllib.request.urlopen(base + "/add", data=b'{"doc": "d1", "text": "the quick fox"}', timeout=5).read()
        with urllib.request.urlopen(base + "/search", data=b'{"term": "quick"}', timeout=5) as response:
            self.assertEqual(json.loads(response.read())["docs"], ["d1"])
        server.shutdown()
