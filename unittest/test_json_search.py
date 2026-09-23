"""Unit test + security test cho json_search() trong recursive_json_search.py.

- 3 test chức năng gốc (Yêu cầu 4): test_search_found, test_search_not_found, test_is_a_list
- 1 test bổ sung cho việc gộp kết quả đệ quy: test_nested_matches_are_aggregated
- 7 security test (Yêu cầu 5), ánh xạ tới SR-1..SR-3 trong security-requirements.md:
    test_wrong_role_cannot_read_secret
    test_operator_cannot_read_api_key
    test_admin_can_read_api_key
    test_no_role_cannot_read_secret
    test_management_ip_requires_operator_or_admin
    test_viewer_can_read_issue_summary
    test_parent_key_does_not_leak_secret
"""

import unittest

from recursive_json_search import json_search
from test_data import data, key1, key2


def _iter_dicts(value):
    """Sinh ra mọi dict nằm trong cây `value` (kể cả lồng bên trong list)."""
    if isinstance(value, dict):
        yield value
        for v in value.values():
            yield from _iter_dicts(v)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_dicts(item)


class json_search_test(unittest.TestCase):
    '''test module to test search function in `recursive_json_search.py`'''

    # ---------------------- test chức năng (Yêu cầu 4) ----------------------

    def test_search_found(self):
        '''key should be found, return list should not be empty'''
        # issueSummary nằm trong POLICY với viewer nên phải truyền role (SR-1)
        self.assertTrue([] != json_search(key1, data, role="viewer"))

    def test_search_not_found(self):
        '''key should not be found, should return an empty list'''
        self.assertTrue([] == json_search(key2, data))

    def test_is_a_list(self):
        '''Should return a list'''
        self.assertIsInstance(json_search(key1, data), list)

    def test_nested_matches_are_aggregated(self):
        '''Recursive search must aggregate matches from every nested dict and list'''
        nested = {"target": 1, "a": {"b": [{"target": 2}, {"c": {"target": 3}}]}}
        self.assertEqual(3, len(json_search("target", nested)))

    # -------------------- security test (Yêu cầu 5, SR-1..SR-3) --------------------

    def test_wrong_role_cannot_read_secret(self):
        '''SR-1: viewer must not read the apiKey (SNMP community string)'''
        self.assertEqual([], json_search("apiKey", data, role="viewer"))

    def test_operator_cannot_read_api_key(self):
        '''SR-1: operator is not in POLICY["apiKey"], only admin may read it'''
        self.assertEqual([], json_search("apiKey", data, role="operator"))

    def test_admin_can_read_api_key(self):
        '''SR-1 (positive control): admin must still be able to read the apiKey'''
        self.assertNotEqual([], json_search("apiKey", data, role="admin"))

    def test_no_role_cannot_read_secret(self):
        '''SR-2 fail-closed: omitting the role must not grant access to protected fields'''
        self.assertEqual([], json_search("apiKey", data))
        self.assertEqual([], json_search("managementIpAddress", data))

    def test_management_ip_requires_operator_or_admin(self):
        '''SR-1: managementIpAddress is readable by operator/admin but not by viewer'''
        self.assertEqual([], json_search("managementIpAddress", data, role="viewer"))
        self.assertNotEqual([], json_search("managementIpAddress", data, role="operator"))

    def test_viewer_can_read_issue_summary(self):
        '''SR-1 (guard against over-blocking): viewer is allowed to read issueSummary'''
        result = json_search("issueSummary", data, role="viewer")
        self.assertNotEqual([], result)
        self.assertEqual(1, len(result))

    def test_parent_key_does_not_leak_secret(self):
        '''SR-3: querying a parent key must not leak restricted fields nested in the result'''
        result = json_search("deviceDetails", data, role="viewer")
        self.assertNotEqual([], result)  # key cha vẫn trả được dữ liệu không hạn chế
        keys = [k for value in result for d in _iter_dicts(value) for k in d]
        self.assertNotIn("apiKey", keys)
        self.assertNotIn("managementIpAddress", keys)


if __name__ == '__main__':
    unittest.main()
