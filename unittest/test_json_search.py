"""
test_json_search.py
===================

Unit tests (functional + security) for ``json_search()``.

Return contract (round 2 review)
--------------------------------
``json_search()`` returns a ``list`` in which **every** element is a
single-entry dict ``{searched_key: value}`` - one element per match - matching
the reference implementation (``temp = {k: v}; ret_val.append(temp)``)::

    json_search("apiKey", data, role="admin")
    -> [{'apiKey': 'SNMP-COMMUNITY-STRING-7f3a9c'}]

Every assertion in this suite goes through ``assertKeyValuePairs()``, so the
shape is pinned *and* the expected values are still compared exactly.

Test inventory (24 tests)
-------------------------
Baseline functionality (3)
* ``test_search_found`` / ``test_search_not_found`` / ``test_is_a_list``

Return-contract tests (2)
* ``test_every_match_is_a_single_entry_key_value_pair``
* ``test_pair_contract_on_synthetic_payload``

Security requirements from ``security-requirements.md`` / ``policy.py``
-----------------------------------------------------------------------
* SR-1 -> ``test_viewer_can_read_issue_summary``,
           ``test_viewer_cannot_read_management_ip``,
           ``test_operator_can_read_management_ip``,
           ``test_admin_can_read_management_ip``,
           ``test_operator_cannot_read_api_key``,
           ``test_admin_can_read_api_key``,
           ``test_wrong_role_cannot_read_secret``,
           ``test_policy_allow_list_is_enforced_for_every_field``
* SR-2 -> ``test_no_role_cannot_read_secret``, ``test_unknown_role_is_rejected``
* SR-3 -> ``test_parent_key_does_not_leak_secret``,
           ``test_redaction_applies_at_every_depth``,
           ``test_restricted_subtree_is_not_traversed``
* SR-4 -> ``test_search_not_found``, ``test_is_a_list``,
           ``test_unusual_input_never_crashes``
* SR-5 -> ``test_search_found``, ``test_nested_matches_are_aggregated``,
           ``test_empty_list_values_are_not_dropped``

Run with::

    python3 -m unittest -v test_json_search.py
"""

import copy
import unittest

from policy import POLICY
from recursive_json_search import json_search
from test_data import data, key1, key2

# --- Fixtures taken from test_data.py ----------------------------------------
ISSUE_SUMMARY = "Network Device 10.10.20.82 Is Unreachable From Controller"
SECRET_API_KEY = "SNMP-COMMUNITY-STRING-7f3a9c"
MANAGEMENT_IP = "10.10.20.21"
DEVICE_HOSTNAME = "leaf2.abc.inc"
DEVICE_MAC = "50:60:ab:cd:70:80"
FLOW_STATUS = "NEW"
EXPECTED_MESSAGES = [
    # three messages inside enrichmentInfo.issueDetails.issue[0].suggestedActions
    "From the controller, verify whether the last hop is reachable.",
    (
        "Verify that the physical port(s) on the network device associated "
        "with the network device discovery(IP) is UP."
    ),
    "Verify access to the device.",
    # ... and 1 more inside ...deviceDetails.neighborTopology[0].message
    "An internal has error occurred while processing this request.",
]

#: Pristine copy of the shared fixture, used by tearDown to prove that
#: json_search() never mutates the caller's data store.
_PRISTINE_DATA = copy.deepcopy(data)


def _forbidden_keys_in(value, role):
    """Return every restricted key reachable inside ``value``.

    A key is forbidden when it belongs to ``POLICY`` and ``role`` is not in its
    allow-list. The helper walks dicts, lists and tuples, i.e. the whole shape
    of a returned object, so SR-3 is checked at every depth.
    """
    forbidden = []

    if isinstance(value, dict):
        for field, child in value.items():
            if isinstance(field, str) and field in POLICY:
                if role not in POLICY[field]:
                    forbidden.append(field)
            forbidden.extend(_forbidden_keys_in(child, role))
    elif isinstance(value, (list, tuple)):
        for item in value:
            forbidden.extend(_forbidden_keys_in(item, role))

    return forbidden


class json_search_test(unittest.TestCase):
    """Functional and security test suite for ``json_search()``."""

    def tearDown(self):
        """Data integrity: no test may mutate the shared ``test_data`` fixture."""
        self.assertEqual(
            data,
            _PRISTINE_DATA,
            msg="json_search() must not mutate the caller's data store",
        )

    def assertKeyValuePairs(self, result, searched_key):
        """Pin the return contract and hand back the matched values.

        Contract under test: ``result`` is a ``list`` in which every element is
        a dict with **exactly one** entry, keyed by the searched key
        (``{searched_key: value}``) - one element per match, in document order.

        :return: the matched values, so callers can still assert the exact
            expected content (the helper must not weaken the assertions).
        """
        self.assertIsInstance(result, list, msg="json_search() must return a list")

        values = []
        for index, item in enumerate(result):
            with self.subTest(match=index):
                self.assertIsInstance(item, dict, msg="every match must be a dict")
                if not isinstance(item, dict):
                    continue  # shape violation recorded; skip extraction below
                self.assertEqual(
                    len(item), 1, msg="every match must hold exactly one entry"
                )
                self.assertEqual(
                    list(item.keys()),
                    [searched_key],
                    msg="the single entry must be keyed by the searched key",
                )
                if len(item) != 1 or list(item.keys()) != [searched_key]:
                    continue
                values.append(item[searched_key])

        return values

    # ------------------------------------------------------------------ #
    # Yêu cầu 3 - Baseline functional tests                             #
    # ------------------------------------------------------------------ #
    def test_search_found(self):
        """SR-5: an allowed key must be found and returned as {key: value} once."""
        result = json_search(key1, data, role="viewer")
        values = self.assertKeyValuePairs(result, key1)

        self.assertEqual(result, [{key1: ISSUE_SUMMARY}])
        self.assertEqual(values, [ISSUE_SUMMARY])

    def test_search_not_found(self):
        """SR-4: a key that does not exist returns an empty list, without raising."""
        self.assertEqual(json_search(key2, data, role="admin"), [])
        self.assertEqual(json_search("nonExistingField", data, role="viewer"), [])

    def test_is_a_list(self):
        """SR-4: every call returns a list, whatever the key, the data or the role."""
        cases = [
            (key1, data, "admin"),
            (key2, data, "admin"),
            (key1, data, None),
            ("issueSummary", None, "viewer"),
            ("issueSummary", 42, "viewer"),
        ]

        for search_key, payload, role in cases:
            with self.subTest(key=search_key, role=role):
                self.assertIsInstance(json_search(search_key, payload, role=role), list)

    # ------------------------------------------------------------------ #
    # Return contract: list of single-entry {key: value} dicts           #
    # ------------------------------------------------------------------ #
    def test_every_match_is_a_single_entry_key_value_pair(self):
        """Contract: every element is a dict of exactly one entry keyed by the key."""
        cases = (
            "apiKey",
            "issueSummary",
            "managementIpAddress",
            "errorCode",
            "message",
            "steps",
            "apsImpacted",
            "hostname",
            "deviceDetails",
            "connectedDevice",
        )
        roles = ("viewer", "operator", "admin")

        for search_key in cases:
            for role in roles:
                with self.subTest(key=search_key, role=role):
                    result = json_search(search_key, data, role=role)
                    values = self.assertKeyValuePairs(result, search_key)

                    # No match is lost by the wrapping: aggregation is unchanged.
                    if search_key == "message":
                        self.assertEqual(values, EXPECTED_MESSAGES)
                    if search_key == "steps":
                        self.assertEqual(values, [[], [], []])
                    if search_key == "errorCode":
                        self.assertEqual(values, ["SNMP-TIMEOUT", 5000])

        # Fail-closed roles must yield no element at all - not even a wrapper.
        for role in (None, "root", "Admin"):
            with self.subTest(key=key1, role=role):
                self.assertEqual(json_search(key1, data, role=role), [])

    def test_pair_contract_on_synthetic_payload(self):
        """Contract: shape holds on synthetic data, at every depth, for any role."""
        payload = {
            "target": 1,
            "outer": {"target": []},
            "branch": [{"target": {"deep": "x"}}, {"other": 2}, [{"target": None}]],
        }

        values = self.assertKeyValuePairs(
            json_search("target", payload, role="viewer"), "target"
        )
        self.assertEqual(
            json_search("target", payload, role="viewer"),
            [{"target": 1}, {"target": []}, {"target": {"deep": "x"}}, {"target": None}],
        )
        self.assertEqual(values, [1, [], {"deep": "x"}, None])

        # The same shape is produced for a restricted key by an allowed role...
        protected = {"apiKey": "secret", "nested": {"apiKey": "secret2"}}
        self.assertEqual(
            json_search("apiKey", protected, role="admin"),
            [{"apiKey": "secret"}, {"apiKey": "secret2"}],
        )
        # ... and unknown roles get nothing (no empty wrappers either).
        self.assertEqual(json_search("apiKey", protected, role=None), [])

    # ------------------------------------------------------------------ #
    # SR-5 - recursive aggregation                                      #
    # ------------------------------------------------------------------ #
    def test_nested_matches_are_aggregated(self):
        """SR-5: matches at different depths/lists are aggregated, not dropped."""
        # "errorCode" exists in deviceDetails and again inside neighborTopology.
        self.assertEqual(
            json_search("errorCode", data, role="viewer"),
            [{"errorCode": "SNMP-TIMEOUT"}, {"errorCode": 5000}],
        )

        # "message" lives in four dicts at different depths: three siblings in
        # suggestedActions plus one inside deviceDetails.neighborTopology.
        self.assertEqual(
            json_search("message", data, role="viewer"),
            [{"message": text} for text in EXPECTED_MESSAGES],
        )

        # "managementIpAddress" is found through a six-level deep path.
        self.assertEqual(
            json_search("managementIpAddress", data, role="admin"),
            [{"managementIpAddress": MANAGEMENT_IP}],
        )

    def test_empty_list_values_are_not_dropped(self):
        """SR-5: falsy matches such as ``[]`` are real matches and must be kept."""
        result = json_search("steps", data, role="viewer")
        values = self.assertKeyValuePairs(result, "steps")

        self.assertEqual(len(result), 3)
        self.assertEqual(result, [{"steps": []}, {"steps": []}, {"steps": []}])
        self.assertEqual(values, [[], [], []])
        self.assertEqual(json_search("apsImpacted", data, role="admin"), [{"apsImpacted": []}])

    # ------------------------------------------------------------------ #
    # policy.py consistency                                              #
    # ------------------------------------------------------------------ #
    def test_policy_matches_security_spec(self):
        """The POLICY table must still match the allow-lists of the security spec."""
        self.assertEqual(
            POLICY,
            {
                "apiKey": ["admin"],
                "managementIpAddress": ["admin", "operator"],
                "issueSummary": ["admin", "operator", "viewer"],
            },
        )

    def test_policy_allow_list_is_enforced_for_every_field(self):
        """SR-1: for every protected field and every role, access == POLICY allow-list."""
        roles = ("viewer", "operator", "admin")

        for field in POLICY:
            for role in roles:
                with self.subTest(field=field, role=role):
                    result = json_search(field, data, role=role)
                    allowed = role in POLICY[field]

                    self.assertEqual(
                        bool(result),
                        allowed,
                        msg=f"{role!r} reading {field!r} must be allowed={allowed}",
                    )
                    if allowed:
                        # A granted read must produce a properly shaped pair.
                        self.assertKeyValuePairs(result, field)
                    else:
                        # A denied read must be empty, never a redacted wrapper.
                        self.assertEqual(result, [])

    # ------------------------------------------------------------------ #
    # SR-1 - role based access control                                   #
    # ------------------------------------------------------------------ #
    def test_viewer_can_read_issue_summary(self):
        """SR-1: viewer is allowed to read issueSummary."""
        self.assertEqual(
            json_search("issueSummary", data, role="viewer"),
            [{"issueSummary": ISSUE_SUMMARY}],
        )

    def test_viewer_cannot_read_management_ip(self):
        """SR-1: viewer is NOT allowed to read managementIpAddress."""
        self.assertEqual(json_search("managementIpAddress", data, role="viewer"), [])

    def test_operator_can_read_management_ip(self):
        """SR-1: operator is allowed to read managementIpAddress."""
        self.assertEqual(
            json_search("managementIpAddress", data, role="operator"),
            [{"managementIpAddress": MANAGEMENT_IP}],
        )

    def test_admin_can_read_management_ip(self):
        """SR-1: admin is allowed to read managementIpAddress."""
        self.assertEqual(
            json_search("managementIpAddress", data, role="admin"),
            [{"managementIpAddress": MANAGEMENT_IP}],
        )

    def test_operator_cannot_read_api_key(self):
        """SR-1: operator is NOT allowed to read the apiKey credential."""
        self.assertEqual(json_search("apiKey", data, role="operator"), [])

    def test_admin_can_read_api_key(self):
        """SR-1: admin is allowed to read the apiKey credential."""
        self.assertEqual(
            json_search("apiKey", data, role="admin"),
            [{"apiKey": SECRET_API_KEY}],
        )

    def test_wrong_role_cannot_read_secret(self):
        """SR-1/T3: a wrong or self-declared privileged role never leaks the secret."""
        for role in ("viewer", "operator", "admin ", "administrator", "operator2"):
            with self.subTest(role=role):
                result = json_search("apiKey", data, role=role)

                self.assertEqual(result, [])
                self.assertNotIn(SECRET_API_KEY, repr(result))

    # ------------------------------------------------------------------ #
    # SR-2 - fail-closed when the role is absent / unknown               #
    # ------------------------------------------------------------------ #
    def test_no_role_cannot_read_secret(self):
        """SR-2: omitting the role (role=None) returns no protected field at all."""
        for field in POLICY:
            with self.subTest(field=field):
                self.assertEqual(json_search(field, data), [])
                self.assertEqual(json_search(field, data, role=None), [])

        self.assertNotIn(SECRET_API_KEY, repr(json_search("apiKey", data)))

    def test_unknown_role_is_rejected(self):
        """SR-2/T3: an unknown, malformed or non-string role is refused entirely."""
        unknown_roles = (
            "root",
            "superadmin",
            "Admin",
            "VIEWER",
            "viewer ",
            "",
            "admin\n",
            123,
            True,
            ["admin"],
            {"role": "admin"},
        )

        for role in unknown_roles:
            with self.subTest(role=role):
                # Protected field: denied.
                self.assertEqual(json_search("apiKey", data, role=role), [])
                # Operational field: also denied (fail-closed, defence in depth).
                self.assertEqual(json_search("status", data, role=role), [])
                # Unknown role still gets a list, never an exception.
                self.assertIsInstance(json_search(key1, data, role=role), list)

    # ------------------------------------------------------------------ #
    # SR-3 - no leak through parent keys, at any depth                   #
    # ------------------------------------------------------------------ #
    def test_parent_key_does_not_leak_secret(self):
        """SR-3: querying a parent key never returns restricted children."""
        for role in ("viewer", "operator"):
            with self.subTest(role=role):
                for parent in ("connectedDevice", "deviceDetails", "enrichmentInfo"):
                    result = json_search(parent, data, role=role)
                    self.assertKeyValuePairs(result, parent)

                    self.assertNotEqual(result, [])
                    self.assertNotIn(SECRET_API_KEY, repr(result))
                    self.assertEqual(_forbidden_keys_in(result, role), [])

        # operator may read the management IP but still not the credential.
        operator_view = self.assertKeyValuePairs(
            json_search("deviceDetails", data, role="operator"), "deviceDetails"
        )[0]
        self.assertEqual(operator_view["managementIpAddress"], MANAGEMENT_IP)
        self.assertNotIn("apiKey", operator_view)

        # admin gets the full, unredacted subtree.
        admin_view = self.assertKeyValuePairs(
            json_search("deviceDetails", data, role="admin"), "deviceDetails"
        )[0]
        self.assertEqual(admin_view["apiKey"], SECRET_API_KEY)

    def test_redaction_applies_at_every_depth(self):
        """SR-3: a whole container returned to a viewer is sanitised recursively."""
        result = json_search("enrichmentInfo", data, role="viewer")
        values = self.assertKeyValuePairs(result, "enrichmentInfo")

        self.assertEqual(len(result), 1)
        self.assertEqual(len(values), 1)
        self.assertEqual(_forbidden_keys_in(result, "viewer"), [])
        self.assertNotIn(SECRET_API_KEY, repr(result))
        self.assertNotIn(MANAGEMENT_IP, repr(result))
        # Non-restricted operational data is preserved by the redaction pass.
        self.assertIn(DEVICE_HOSTNAME, repr(result))

    def test_restricted_subtree_is_not_traversed(self):
        """SR-3: no side-door into a restricted subtree through a child key."""
        probe = {"apiKey": {"value": SECRET_API_KEY}, "public": {"value": "ok"}}

        self.assertEqual(
            json_search("value", probe, role="viewer"), [{"value": "ok"}]
        )
        self.assertEqual(
            json_search("value", probe, role="operator"), [{"value": "ok"}]
        )
        self.assertEqual(
            json_search("value", probe, role="admin"),
            [{"value": SECRET_API_KEY}, {"value": "ok"}],
        )

    # ------------------------------------------------------------------ #
    # Residual risk (§7) and data integrity                              #
    # ------------------------------------------------------------------ #
    def test_non_policy_field_is_readable_by_valid_roles(self):
        """§7: fields absent from POLICY stay readable for every valid role."""
        for role in ("viewer", "operator", "admin"):
            with self.subTest(role=role):
                self.assertEqual(
                    json_search("hostname", data, role=role),
                    [{"hostname": DEVICE_HOSTNAME}],
                )
                self.assertEqual(
                    json_search("macAddress", data, role=role),
                    [{"macAddress": DEVICE_MAC}],
                )
                self.assertEqual(
                    json_search("status", data, role=role), [{"status": FLOW_STATUS}]
                )

    def test_redaction_does_not_mutate_input(self):
        """The caller's data store and the returned objects must stay independent."""
        snapshot = copy.deepcopy(data)

        snippet = self.assertKeyValuePairs(
            json_search("deviceDetails", data, role="viewer"), "deviceDetails"
        )[0]
        json_search("apiKey", data, role="viewer")
        json_search("connectedDevice", data, role="admin")

        # The source object still holds the secret...
        self.assertEqual(
            json_search("apiKey", data, role="admin"),
            [{"apiKey": SECRET_API_KEY}],
        )

        # ... and the redacted copy is a real copy: mutating it changes nothing.
        snippet["hostname"] = "tampered"
        self.assertEqual(
            data["enrichmentInfo"]["connectedDevice"][0]["deviceDetails"]["hostname"],
            DEVICE_HOSTNAME,
        )
        self.assertNotIn(SECRET_API_KEY, repr(snippet))
        self.assertEqual(
            snapshot["enrichmentInfo"]["connectedDevice"][0]["deviceDetails"]["apiKey"],
            SECRET_API_KEY,
        )

    def test_unusual_input_never_crashes(self):
        """SR-4/T5: malformed, hostile or cyclic input never raises and returns a list."""
        cyclic = {}
        cyclic["self"] = cyclic

        deep = {"leaf": "hit"}
        for _ in range(2000):
            deep = {"nested": deep}

        samples = (
            None,
            123,
            3.14,
            "plain string",
            b"bytes",
            set(),
            (),
            [],
            {},
            {"a": [1, [2, [3, [4]]]]},
            {"target": "hit"},
            {"nested": {"deep": [[{"target": "hit"}]]}},
            cyclic,
            deep,
            object(),
        )

        for sample in samples:
            with self.subTest(sample=type(sample).__name__):
                self.assertIsInstance(json_search("target", sample, role="admin"), list)

        # A real match inside well-formed data is still reported as a pair.
        self.assertEqual(
            json_search(
                "target", {"nested": {"deep": [[{"target": "hit"}]]}}, role="admin"
            ),
            [{"target": "hit"}],
        )
        # Weird keys are simply not found instead of crashing the search.
        self.assertEqual(json_search(None, data, role="admin"), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
