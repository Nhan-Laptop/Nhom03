"""
recursive_json_search.py
========================

Recursive JSON lookup with role-based access control.

``json_search(key, input_object, role=None)`` walks an arbitrarily nested JSON
object (``dict`` / ``list`` / ``tuple``) and aggregates **every** occurrence of
``key``, at any depth, without dropping any branch.

Return contract (round 2 review): the result is a ``list`` whose **every**
element is a single-entry dict ``{key: value}`` - one element per match - which
is the shape produced by the reference implementation
(``temp = {k: v}; ret_val.append(temp)``), for example::

    json_search("apiKey", data, role="admin")
    -> [{'apiKey': 'SNMP-COMMUNITY-STRING-7f3a9c'}]

Before a value is appended, and before any subtree is entered, the caller's
``role`` is checked against the allow-list in ``policy.py``
(``POLICY[field]`` = roles allowed to read ``field``):

* SR-1  A value is returned only when ``role`` is listed in ``POLICY[field]``.
* SR-2  Fail-closed: an unknown role - including ``role=None`` - reads nothing
        (not even the fields that are absent from ``POLICY``).
* SR-3  Redaction is applied at *every* depth, so asking for a parent key
        (e.g. ``deviceDetails``) never leaks a restricted child field, and a
        restricted subtree is never traversed at all (no side-door via a
        non-restricted child key).
* SR-4  The function never raises and always returns a ``list``; malformed or
        cyclic input cannot crash it.
* SR-5  Matches coming from nested dicts and lists are aggregated completely,
        including falsy values such as ``[]``.

Tóm tắt: tìm kiếm JSON đệ quy, gộp kết quả ở mọi cấp, kiểm soát truy cập theo
``POLICY`` trong ``policy.py`` và fail-closed khi ``role=None``.
"""

from policy import POLICY

__all__ = ["json_search", "KNOWN_ROLES", "FAIL_CLOSED_FOR_UNKNOWN_ROLE"]

#: Every role that the policy knows about, derived from POLICY itself so that
#: ``policy.py`` stays the single source of truth for authorisation decisions.
KNOWN_ROLES = frozenset(
    role for allowed_roles in POLICY.values() for role in allowed_roles
)

#: When ``True`` (default, and the behaviour required by SR-2) a caller that
#: does not present a valid role - ``role=None`` or any unknown/unsupported
#: value - is denied *every* field, not only the fields listed in ``POLICY``.
#: Set it to ``False`` to relax the behaviour to the strict minimum of SR-2:
#: unknown callers would then still read fields that are absent from ``POLICY``
#: (operational data such as ``hostname``).  The secure default is kept.
FAIL_CLOSED_FOR_UNKNOWN_ROLE = True


def _is_known_role(role):
    """Return ``True`` only for a role explicitly declared in ``POLICY``.

    ``None``, empty/unknown strings, non-string values and case variants
    (``"Admin"``) are rejected: role names are compared exactly as written in
    the policy table, and normalising them is the caller's responsibility.
    """
    return isinstance(role, str) and role in KNOWN_ROLES


def _may_read(field, role):
    """Return ``True`` only when ``role`` is allowed to read ``field``.

    This is the single authorisation decision point used by both the search and
    the redaction pass:

    * field listed in ``POLICY``  -> allow only if ``role in POLICY[field]``;
    * field not listed in ``POLICY`` -> operational data, allow for any valid
      role;
    * unknown ``role`` (``None``, arbitrary string, non-string) -> fail-closed
      (SR-2).
    """
    restricted = isinstance(field, str) and field in POLICY

    if _is_known_role(role):
        if not restricted:
            return True
        return role in POLICY[field]

    if FAIL_CLOSED_FOR_UNKNOWN_ROLE:
        return False
    return not restricted


def _keys_equal(candidate, wanted):
    """Compare two field names defensively (exotic ``__eq__`` must not crash)."""
    try:
        return bool(candidate == wanted)
    except Exception:  # pragma: no cover - only for hostile input objects
        return False


def _redact(value, role):
    """Return a sanitised deep copy of ``value`` for ``role``.

    Restricted fields the caller may not read are removed at every depth, so a
    matched container (parent key) cannot leak a protected child field (SR-3).
    The input object is never modified; the data store stays intact.
    """
    if isinstance(value, dict):
        return {
            field: _redact(child, role)
            for field, child in value.items()
            if _may_read(field, role)
        }
    if isinstance(value, list):
        return [_redact(item, role) for item in value]
    if isinstance(value, tuple):
        return tuple(_redact(item, role) for item in value)
    # JSON scalars (str/int/float/bool/None) are immutable, nothing to redact.
    return value


def _search(key, node, role, results):
    """Depth-first walk of ``node``, appending every match of ``key``.

    ``results`` is a shared accumulator so that partial matches found before a
    ``RecursionError`` are still returned instead of being lost (SR-4).
    """
    if isinstance(node, dict):
        for field, value in node.items():
            readable = _may_read(field, role)

            if readable and _keys_equal(field, key):
                # Reference contract: one single-entry dict per match, where
                # the entry key is the field name that matched (= ``key``).
                results.append({field: _redact(value, role)})

            # Only descend into a subtree the caller is allowed to read: a
            # restricted container key (e.g. "apiKey") must not be reachable
            # through one of its non-restricted child keys.
            if readable and isinstance(value, (dict, list, tuple)):
                _search(key, value, role, results)

    elif isinstance(node, (list, tuple)):
        for item in node:
            _search(key, item, role, results)


def json_search(key, input_object, role=None):
    """Recursively collect every occurrence of ``key`` in ``input_object``.

    :param key: field name to look for (any hashable value; normally ``str``).
    :param input_object: nested JSON-like structure (``dict``/``list``). Any
        other type is simply not traversed and yields an empty result.
    :param role: role of the caller as authenticated by the upper layer
        (``"admin"``, ``"operator"`` or ``"viewer"``). ``None`` - or any role
        not declared in ``POLICY`` - is treated as unauthenticated and the
        function fails closed (SR-2).

    :return: a new ``list`` in document order in which **every** element is a
        single-entry dict ``{key: value}`` - one element per match, with the
        value redacted for ``role``. It is never a non-list and it never
        raises (SR-1..SR-5).
    """
    results = []

    # Safe short-circuit: an unauthenticated/unknown caller can read nothing.
    if FAIL_CLOSED_FOR_UNKNOWN_ROLE and not _is_known_role(role):
        return results

    try:
        _search(key, input_object, role, results)
    except RecursionError:
        # Pathological input (excessively deep nesting, self-referential
        # structures) must not crash the caller: return what was collected.
        # Residual risk (T5): the recursion depth is not bounded explicitly.
        pass

    return results
