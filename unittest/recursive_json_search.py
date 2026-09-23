"""recursive_json_search.py

json_search(key, input_object, role=None)
    - Tìm ĐỆ QUY mọi cặp key/value có `key` trùng trong JSON object lồng nhau (dict/list).
    - Gộp kết quả ở MỌI cấp: kết quả của các lần gọi đệ quy được cộng dồn vào ret_val
      (fix bug: trước đây ret_val của lần gọi con bị bỏ đi).
    - Kiểm soát truy cập theo role dựa trên POLICY trong policy.py:
        SR-1 allowlist theo trường: chỉ trả về trường X nếu role nằm trong POLICY[X]
        SR-2 fail-closed: role=None hoặc role không hợp lệ KHÔNG đọc được trường trong POLICY
        SR-3 lọc đệ quy: kết quả không chứa trường bị hạn chế ở bất kỳ độ sâu nào
             (chống bypass bằng cách truy vấn key cha, ví dụ "deviceDetails")

Tham chiếu: unittest/security-requirements.md
"""

from policy import POLICY
from test_data import *


def _is_allowed(key, role):
    """Trả về True nếu `role` được phép đọc giá trị của trường `key` (SR-1, SR-2)."""
    if key not in POLICY:
        return True  # trường không bị hạn chế bởi policy
    return role in POLICY[key]


def _filter_value(value, role):
    """Lọc đệ quy (SR-3): loại bỏ mọi trường trong POLICY mà `role` không được phép đọc.

    Nhờ vậy viewer/operator truy vấn key cha (ví dụ "deviceDetails") sẽ không nhận
    được "apiKey" nằm sâu bên trong cây con.
    """
    if isinstance(value, dict):
        return {k: _filter_value(v, role)
                for k, v in value.items() if _is_allowed(k, role)}
    if isinstance(value, list):
        return [_filter_value(item, role) for item in value]
    return value


def json_search(key, input_object, role=None):
    ret_val = []
    if isinstance(input_object, dict):  # Iterate dictionary
        for k, v in input_object.items():  # searching key in the dict
            if k == key and _is_allowed(k, role):  # SR-1/SR-2: kiểm tra quyền trước khi trả về
                temp = {k: _filter_value(v, role)}  # SR-3: lọc cây con
                ret_val.append(temp)
            if isinstance(v, dict):  # the value is another dict so repeat
                ret_val += json_search(key, v, role)
            elif isinstance(v, list):  # it's a list
                for item in v:
                    if not isinstance(item, (str, int)):  # if dict or list repeat
                        ret_val += json_search(key, item, role)
    else:  # Iterate a list because some APIs return JSON object in a list
        for val in input_object:
            if not isinstance(val, (str, int)):
                ret_val += json_search(key, val, role)
    return ret_val


if __name__ == "__main__":
    # Minh hoạ kiểm soát truy cập theo role
    print("admin    + issueSummary ->", json_search("issueSummary", data, role="admin"))
    print("viewer   + issueSummary ->", json_search("issueSummary", data, role="viewer"))
    print("viewer   + apiKey       ->", json_search("apiKey", data, role="viewer"))
    print("operator + apiKey       ->", json_search("apiKey", data, role="operator"))
    print("admin    + apiKey       ->", json_search("apiKey", data, role="admin"))
    print("role=None+ apiKey       ->", json_search("apiKey", data))
    print("viewer   + deviceDetails (không lộ apiKey) ->",
          json_search("deviceDetails", data, role="viewer"))
