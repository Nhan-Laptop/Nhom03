# Lab 1 – B.2 (SSDLC trên chức năng json_search) : log lệnh & output thực tế

- Tiếp nối B.1 (`LAB1-B1-evidence.md`). Repo: `/home/nhanlaptop/UIT/NT521/TH1/Nhom03`
- Ngày chạy: 2026-09-23 08:40:51 +07

---

## B.2 (chuẩn bị) Đưa folder unittest lên branch master

$ tar -xzf ../unittest.tar.gz   # giải nén bộ tài nguyên unittest.tar.gz vào repo
Nội dung gói tài nguyên:
unittest/
unittest/test_json_search.py
unittest/recursive_json_search.py
unittest/policy.py
unittest/test_data.py

$ ls -la unittest
total 28
drwxr-xr-x 2 nhanlaptop nhanlaptop 4096 Sep 15 21:39 .
drwxrwxr-x 6 nhanlaptop nhanlaptop 4096 Sep 23 08:40 ..
-rw-r--r-- 1 nhanlaptop nhanlaptop  563 Sep 15 21:39 policy.py
-rw-r--r-- 1 nhanlaptop nhanlaptop   36 Sep 15 21:39 recursive_json_search.py
-rw-r--r-- 1 nhanlaptop nhanlaptop 4787 Sep 15 21:39 test_data.py
-rw-r--r-- 1 nhanlaptop nhanlaptop   36 Sep 15 21:39 test_json_search.py

### Bước 1. Đưa thư mục unittest lên branch master
$ git status
On branch master
Your branch is up to date with 'origin/master'.

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	unittest/

nothing added to commit but untracked files present (use "git add" to track)

$ git add unittest/

$ git status
On branch master
Your branch is up to date with 'origin/master'.

Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	new file:   unittest/policy.py
	new file:   unittest/recursive_json_search.py
	new file:   unittest/test_data.py
	new file:   unittest/test_json_search.py


$ git commit -m Nhom03 Add baseline unittest resources for B2
[master 026c591] Nhom03 Add baseline unittest resources for B2
 4 files changed, 132 insertions(+)
 create mode 100644 unittest/policy.py
 create mode 100644 unittest/recursive_json_search.py
 create mode 100644 unittest/test_data.py
 create mode 100644 unittest/test_json_search.py

$ git log --oneline
026c591 Nhom03 Add baseline unittest resources for B2
777d732 Nhom03 Add .gitignore and group intro note
a6c11b2 Manually merged from test branch
62a858e branch master Changed feature to master
eda981f branch test Change feature to test
6f0dc98 Added a third line in feature branch
b889aa8 Nhom03 Added additional line to file
6b0c49e Committing README.MD from Nhom03 to begin tracking changes

### Bước 2. Tạo 2 branch manual và agent từ branch master
$ git branch manual

$ git branch agent

$ git branch -a
  agent
  manual
* master
  test
  remotes/origin/master

$ git log --oneline --decorate --graph --all
* 026c591 (HEAD -> master, manual, agent) Nhom03 Add baseline unittest resources for B2
* 777d732 (origin/master) Nhom03 Add .gitignore and group intro note
*   a6c11b2 Manually merged from test branch
|\  
| * eda981f (test) branch test Change feature to test
* | 62a858e branch master Changed feature to master
|/  
* 6f0dc98 Added a third line in feature branch
* b889aa8 Nhom03 Added additional line to file
* 6b0c49e Committing README.MD from Nhom03 to begin tracking changes

---

## B.2.1 Phát triển thủ công (branch manual)

$ git checkout manual
$ git checkout manual
Switched to branch 'manual'

### Bước 1. Security Requirements & Threat Model (Yêu cầu 3)
Tạo `unittest/security-requirements.md`:
Nội dung tài liệu (xem file đầy đủ tại `unittest/security-requirements.md`):

- Actor/role: viewer → `issueSummary`; operator → + `managementIpAddress`; admin → + `apiKey`; `role=None` → không đọc được trường nào trong POLICY (fail-closed).
- Asset nhạy cảm: `apiKey` = SNMP-COMMUNITY-STRING-7f3a9c (thông tin xác thực thiết bị), `managementIpAddress` = 10.10.20.21, thông tin định danh thiết bị (serialNumber/macAddress/instanceUuid).
- Trust boundary bị bỏ qua: hàm trả kết quả mà KHÔNG kiểm tra role ⇒ mọi caller đọc được cả secret; không thể thay thế bằng xác thực ở tầng trên.
- Threat STRIDE: T1 Information Disclosure (viewer đọc apiKey), T2 Information Disclosure (bỏ role để bypass - fail-closed), T3 Elevation of Privilege (client tự khai role=admin), T4 Information Disclosure (bypass bằng key cha deviceDetails), T5 DoS, T6 Repudiation.
- Security Requirements SR-1..SR-5, mỗi SR ánh xạ 1-1 tới security test ở Bước 7.

$ git add unittest/security-requirements.md
$ git commit -m "docs: add security requirements and threat model for json_search()"
$ git add unittest/security-requirements.md

$ git commit -m docs: add security requirements and threat model for json_search()
[manual cbde878] docs: add security requirements and threat model for json_search()
 1 file changed, 92 insertions(+)
 create mode 100644 unittest/security-requirements.md

$ git log --oneline -3
cbde878 docs: add security requirements and threat model for json_search()
026c591 Nhom03 Add baseline unittest resources for B2
777d732 Nhom03 Add .gitignore and group intro note

### Bước 2. Thiết lập hàm json_search (bản trong PDF - còn bug)
$ cat unittest/recursive_json_search.py
$ cat unittest/recursive_json_search.py
from test_data import *


def json_search(key, input_object):
    ret_val = []
    if isinstance(input_object, dict):  # Iterate dictionary
        for k, v in input_object.items():  # searching key in the dict
            if k == key:
                temp = {k: v}
                ret_val.append(temp)
            if isinstance(v, dict):  # the value is another dict so repeat
                json_search(key, v)
            elif isinstance(v, list):  # it's a list
                for item in v:
                    if not isinstance(item, (str, int)):  # if dict or list repeat
                        json_search(key, item)
    else:  # Iterate a list because some APIs return JSON object in a list
        for val in input_object:
            if not isinstance(val, (str, int)):
                json_search(key, val)
    return ret_val


print(json_search("issueSummary", data))

$ git status
On branch manual
Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   unittest/recursive_json_search.py

no changes added to commit (use "git add" and/or "git commit -a")

### Bước 3. Kiểm thử chức năng — chạy chương trình
$ python3 recursive_json_search.py
[]

→ Kết quả in ra là `[]` (list RỖNG): hàm KHÔNG trả về giá trị `issueSummary` nào, dù trong `test_data.py` có 1 giá trị nằm ở
`data['enrichmentInfo']['issueDetails']['issue'][0]['issueSummary']`. Hàm hoạt động CHƯA đúng như dự định.

### Bước 4. Kiểm tra chức năng bằng unit test
Tạo `unittest/test_json_search.py` với 3 test case chức năng (`test_search_found`, `test_search_not_found`, `test_is_a_list`), mỗi method có docstring:
$ cat test_json_search.py
import unittest

from recursive_json_search import *
from test_data import *


class json_search_test(unittest.TestCase):
    '''test module to test search function in `recursive_json_search.py`'''

    def test_search_found(self):
        '''key should be found, return list should not be empty'''
        self.assertTrue([] != json_search(key1, data))

    def test_search_not_found(self):
        '''key should not be found, should return an empty list'''
        self.assertTrue([] == json_search(key2, data))

    def test_is_a_list(self):
        '''Should return a list'''
        self.assertIsInstance(json_search(key1, data), list)


if __name__ == '__main__':
    unittest.main()

$ python3 -m unittest -v test_json_search.py
test_is_a_list (test_json_search.json_search_test.test_is_a_list)
Should return a list ... ok
test_search_found (test_json_search.json_search_test.test_search_found)
key should be found, return list should not be empty ... FAIL
test_search_not_found (test_json_search.json_search_test.test_search_not_found)
key should not be found, should return an empty list ... ok

======================================================================
FAIL: test_search_found (test_json_search.json_search_test.test_search_found)
key should be found, return list should not be empty
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/home/nhanlaptop/UIT/NT521/TH1/Nhom03/unittest/test_json_search.py", line 12, in test_search_found
    self.assertTrue([] != json_search(key1, data))
    ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: False is not true

----------------------------------------------------------------------
Ran 3 tests in 0.001s

FAILED (failures=1)
[]

-> exit status = 1

### Bước 5. Phân tích test case, nguyên nhân lỗi và sửa code (Yêu cầu 4)

**So sánh 2 lần chạy unittest ở Bước 4:** `test_search_found` **FAIL**, `test_search_not_found` và `test_is_a_list` **PASS**.

**Nguyên nhân gốc (root cause):** `ret_val = []` được khởi tạo lại ở **mỗi lần gọi đệ quy** và giá trị trả về của lần gọi con bị
**bỏ đi** (không được gán/gộp vào `ret_val` của lần gọi cha). Vì vậy hàm chỉ giữ được các match nằm ở **cùng cấp** với lần gọi
hiện tại, còn kết quả tìm thấy ở các nhánh con thì bị mất.

- `issueSummary` nằm sâu trong dữ liệu: `data` → `enrichmentInfo` → `issueDetails` → `issue[0]` → `issueSummary`.
  Mọi match đều rơi vào các lần gọi con ⇒ lần gọi gốc trả về `[]` (đúng như kết quả quan sát ở Bước 3).
- `test_search_not_found` PASS (kể cả khi bug) vì `key2` không tồn tại nên `[] == []` vẫn đúng.
- `test_is_a_list` PASS (kể cả khi bug) vì hàm vẫn trả về đúng kiểu `list`.

**Cách sửa:** gộp (aggregate) kết quả của mỗi lần gọi đệ quy vào `ret_val` của lần gọi hiện tại — sửa 3 chỗ
(`json_search(key, v)` → `ret_val += json_search(key, v)`): nhánh value là dict, nhánh list bên trong dict, và nhánh input_object là list.

$ diff -u recursive_json_search.buggy.py recursive_json_search.py   # bản còn bug vs bản đã sửa

Kiểm chứng sau khi sửa:
$ python3 recursive_json_search.py
[{'issueSummary': 'Network Device 10.10.20.82 Is Unreachable From Controller'}]

$ python3 -m unittest -v test_json_search.py
test_is_a_list (test_json_search.json_search_test.test_is_a_list)
Should return a list ... ok
test_search_found (test_json_search.json_search_test.test_search_found)
key should be found, return list should not be empty ... ok
test_search_not_found (test_json_search.json_search_test.test_search_not_found)
key should not be found, should return an empty list ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.001s

OK
[{'issueSummary': 'Network Device 10.10.20.82 Is Unreachable From Controller'}]

→ Cả 3 test case đều OK (PASS). Hàm đã gộp được kết quả tìm kiếm đệ quy.

### Bước 6. Commit code đã sửa lên nhánh manual
$ git add recursive_json_search.py test_json_search.py
$ git commit -m "Nhom03 Fix ret_val bug in json_search, 3 unit tests PASS"
(đang đứng trong thư mục `unittest/`)
$ git add recursive_json_search.py test_json_search.py

$ git commit -m Nhom03 Fix ret_val bug in json_search, 3 unit tests PASS
[manual 5542c34] Nhom03 Fix ret_val bug in json_search, 3 unit tests PASS
 2 files changed, 48 insertions(+), 2 deletions(-)

$ git log --oneline -3
5542c34 Nhom03 Fix ret_val bug in json_search, 3 unit tests PASS
cbde878 docs: add security requirements and threat model for json_search()
026c591 Nhom03 Add baseline unittest resources for B2

$ git status
On branch manual
Untracked files:
  (use "git add <file>..." to include in what will be committed)
	__pycache__/

nothing added to commit but untracked files present (use "git add" to track)

### Bước 7. Bổ sung kiểm soát truy cập theo role và viết security test (Yêu cầu 5)

Đọc và phân tích policy.py:
$ cat policy.py
# policy.py
# Quy định vai trò (role) nào được phép đọc giá trị của một trường (key)
# cụ thể trong dữ liệu JSON trả về bởi json_search().
#
# Sinh viên dùng bảng này để viết security test ở Yêu cầu 6: gọi
# json_search(key, data, role=...) với một role KHÔNG nằm trong danh sách
# cho phép của key đó, và kỳ vọng kết quả trả về là rỗng.

POLICY = {
    "apiKey": ["admin"],
    "managementIpAddress": ["admin", "operator"],
    "issueSummary": ["admin", "operator", "viewer"],
}

→ POLICY là **allowlist theo từng trường**: `apiKey` chỉ `admin`; `managementIpAddress` cho `admin`,`operator`;
`issueSummary` cho cả 3 role. Hàm `json_search()` được cập nhật thành `json_search(key, input_object, role=None)`:

- **SR-1** kiểm tra `role in POLICY[key]` trước khi append kết quả;
- **SR-2** fail-closed: `role=None` không nằm trong bất kỳ allowlist nào ⇒ không đọc được trường trong POLICY;
- **SR-3** thêm hàm `_filter_value()` lọc đệ quy mọi dict/list trong cây kết quả, chặn bypass bằng key cha.

$ git diff   # thay đổi code của Bước 7 so với commit ở Bước 6
diff --git a/unittest/recursive_json_search.py b/unittest/recursive_json_search.py
index 32887f2..408b1a4 100644
--- a/unittest/recursive_json_search.py
+++ b/unittest/recursive_json_search.py
@@ -1,24 +1,70 @@
+"""recursive_json_search.py
+
+json_search(key, input_object, role=None)
+    - Tìm ĐỆ QUY mọi cặp key/value có `key` trùng trong JSON object lồng nhau (dict/list).
+    - Gộp kết quả ở MỌI cấp: kết quả của các lần gọi đệ quy được cộng dồn vào ret_val
+      (fix bug: trước đây ret_val của lần gọi con bị bỏ đi).
+    - Kiểm soát truy cập theo role dựa trên POLICY trong policy.py:
+        SR-1 allowlist theo trường: chỉ trả về trường X nếu role nằm trong POLICY[X]
+        SR-2 fail-closed: role=None hoặc role không hợp lệ KHÔNG đọc được trường trong POLICY
+        SR-3 lọc đệ quy: kết quả không chứa trường bị hạn chế ở bất kỳ độ sâu nào
+             (chống bypass bằng cách truy vấn key cha, ví dụ "deviceDetails")
+
+Tham chiếu: unittest/security-requirements.md
+"""
+
+from policy import POLICY
 from test_data import *
 
 
-def json_search(key, input_object):
+def _is_allowed(key, role):
+    """Trả về True nếu `role` được phép đọc giá trị của trường `key` (SR-1, SR-2)."""
+    if key not in POLICY:
+        return True  # trường không bị hạn chế bởi policy
+    return role in POLICY[key]
+
+
+def _filter_value(value, role):
+    """Lọc đệ quy (SR-3): loại bỏ mọi trường trong POLICY mà `role` không được phép đọc.
+
+    Nhờ vậy viewer/operator truy vấn key cha (ví dụ "deviceDetails") sẽ không nhận
+    được "apiKey" nằm sâu bên trong cây con.
+    """
+    if isinstance(value, dict):
+        return {k: _filter_value(v, role)
+                for k, v in value.items() if _is_allowed(k, role)}
+    if isinstance(value, list):
+        return [_filter_value(item, role) for item in value]
+    return value
+
+
+def json_search(key, input_object, role=None):
     ret_val = []
     if isinstance(input_object, dict):  # Iterate dictionary
         for k, v in input_object.items():  # searching key in the dict
-            if k == key:
-                temp = {k: v}
+            if k == key and _is_allowed(k, role):  # SR-1/SR-2: kiểm tra quyền trước khi trả về
+                temp = {k: _filter_value(v, role)}  # SR-3: lọc cây con
                 ret_val.append(temp)
             if isinstance(v, dict):  # the value is another dict so repeat
-                ret_val += json_search(key, v)
+                ret_val += json_search(key, v, role)
             elif isinstance(v, list):  # it's a list
                 for item in v:
                     if not isinstance(item, (str, int)):  # if dict or list repeat
-                        ret_val += json_search(key, item)
+                        ret_val += json_search(key, item, role)
     else:  # Iterate a list because some APIs return JSON object in a list
         for val in input_object:
             if not isinstance(val, (str, int)):
-                ret_val += json_search(key, val)
+                ret_val += json_search(key, val, role)
     return ret_val
 
 
-print(json_search("issueSummary", data))
+if __name__ == "__main__":
+    # Minh hoạ kiểm soát truy cập theo role
+    print("admin    + issueSummary ->", json_search("issueSummary", data, role="admin"))
+    print("viewer   + issueSummary ->", json_search("issueSummary", data, role="viewer"))
+    print("viewer   + apiKey       ->", json_search("apiKey", data, role="viewer"))
+    print("operator + apiKey       ->", json_search("apiKey", data, role="operator"))
+    print("admin    + apiKey       ->", json_search("apiKey", data, role="admin"))
+    print("role=None+ apiKey       ->", json_search("apiKey", data))
+    print("viewer   + deviceDetails (không lộ apiKey) ->",
+          json_search("deviceDetails", data, role="viewer"))
diff --git a/unittest/test_json_search.py b/unittest/test_json_search.py
index 5812a9e..18bcd33 100644
--- a/unittest/test_json_search.py
+++ b/unittest/test_json_search.py
@@ -1,15 +1,43 @@
+"""Unit test + security test cho json_search() trong recursive_json_search.py.
+
+- 3 test chức năng gốc (Yêu cầu 4): test_search_found, test_search_not_found, test_is_a_list
+- 1 test bổ sung cho việc gộp kết quả đệ quy: test_nested_matches_are_aggregated
+- 7 security test (Yêu cầu 5), ánh xạ tới SR-1..SR-3 trong security-requirements.md:
+    test_wrong_role_cannot_read_secret
+    test_operator_cannot_read_api_key
+    test_admin_can_read_api_key
+    test_no_role_cannot_read_secret
+    test_management_ip_requires_operator_or_admin
+    test_viewer_can_read_issue_summary
+    test_parent_key_does_not_leak_secret
+"""
+
 import unittest
 
-from recursive_json_search import *
-from test_data import *
+from recursive_json_search import json_search
+from test_data import data, key1, key2
+
+
+def _iter_dicts(value):
+    """Sinh ra mọi dict nằm trong cây `value` (kể cả lồng bên trong list)."""
+    if isinstance(value, dict):
+        yield value
+        for v in value.values():
+            yield from _iter_dicts(v)
+    elif isinstance(value, list):
+        for item in value:
+            yield from _iter_dicts(item)
 
 
 class json_search_test(unittest.TestCase):
     '''test module to test search function in `recursive_json_search.py`'''
 
+    # ---------------------- test chức năng (Yêu cầu 4) ----------------------
+
     def test_search_found(self):
         '''key should be found, return list should not be empty'''
-        self.assertTrue([] != json_search(key1, data))
+        # issueSummary nằm trong POLICY với viewer nên phải truyền role (SR-1)
+        self.assertTrue([] != json_search(key1, data, role="viewer"))
 
     def test_search_not_found(self):
         '''key should not be found, should return an empty list'''
@@ -19,6 +47,49 @@ class json_search_test(unittest.TestCase):
         '''Should return a list'''
         self.assertIsInstance(json_search(key1, data), list)
 
+    def test_nested_matches_are_aggregated(self):
+        '''Recursive search must aggregate matches from every nested dict and list'''
+        nested = {"target": 1, "a": {"b": [{"target": 2}, {"c": {"target": 3}}]}}
+        self.assertEqual(3, len(json_search("target", nested)))
+
+    # -------------------- security test (Yêu cầu 5, SR-1..SR-3) --------------------
+
+    def test_wrong_role_cannot_read_secret(self):
+        '''SR-1: viewer must not read the apiKey (SNMP community string)'''
+        self.assertEqual([], json_search("apiKey", data, role="viewer"))
+
+    def test_operator_cannot_read_api_key(self):
+        '''SR-1: operator is not in POLICY["apiKey"], only admin may read it'''
+        self.assertEqual([], json_search("apiKey", data, role="operator"))
+
+    def test_admin_can_read_api_key(self):
+        '''SR-1 (positive control): admin must still be able to read the apiKey'''
+        self.assertNotEqual([], json_search("apiKey", data, role="admin"))
+
+    def test_no_role_cannot_read_secret(self):
+        '''SR-2 fail-closed: omitting the role must not grant access to protected fields'''
+        self.assertEqual([], json_search("apiKey", data))
+        self.assertEqual([], json_search("managementIpAddress", data))
+
+    def test_management_ip_requires_operator_or_admin(self):
+        '''SR-1: managementIpAddress is readable by operator/admin but not by viewer'''
+        self.assertEqual([], json_search("managementIpAddress", data, role="viewer"))
+        self.assertNotEqual([], json_search("managementIpAddress", data, role="operator"))
+
+    def test_viewer_can_read_issue_summary(self):
+        '''SR-1 (guard against over-blocking): viewer is allowed to read issueSummary'''
+        result = json_search("issueSummary", data, role="viewer")
+        self.assertNotEqual([], result)
+        self.assertEqual(1, len(result))
+
+    def test_parent_key_does_not_leak_secret(self):
+        '''SR-3: querying a parent key must not leak restricted fields nested in the result'''
+        result = json_search("deviceDetails", data, role="viewer")
+        self.assertNotEqual([], result)  # key cha vẫn trả được dữ liệu không hạn chế
+        keys = [k for value in result for d in _iter_dicts(value) for k in d]
+        self.assertNotIn("apiKey", keys)
+        self.assertNotIn("managementIpAddress", keys)
+
 
 if __name__ == '__main__':
     unittest.main()

Bổ sung **7 security test** (yêu cầu tối thiểu 3) — chi tiết trong `test_json_search.py`:

| Test | Security requirement | Kỳ vọng |
|---|---|---|
| test_wrong_role_cannot_read_secret | SR-1 | viewer + apiKey → [] |
| test_operator_cannot_read_api_key | SR-1 | operator + apiKey → [] |
| test_admin_can_read_api_key | SR-1 (positive control) | admin + apiKey → khác [] |
| test_no_role_cannot_read_secret | SR-2 (fail-closed) | role=None + apiKey/managementIpAddress → [] |
| test_management_ip_requires_operator_or_admin | SR-1 | viewer → []; operator → khác [] |
| test_viewer_can_read_issue_summary | SR-1 (chống chặn nhầm) | viewer + issueSummary → đúng 1 kết quả |
| test_parent_key_does_not_leak_secret | SR-3 | viewer hỏi `deviceDetails` không chứa apiKey/managementIpAddress |

Chạy lại toàn bộ unittest:
$ python3 -m unittest -v test_json_search.py
test_admin_can_read_api_key (test_json_search.json_search_test.test_admin_can_read_api_key)
SR-1 (positive control): admin must still be able to read the apiKey ... ok
test_is_a_list (test_json_search.json_search_test.test_is_a_list)
Should return a list ... ok
test_management_ip_requires_operator_or_admin (test_json_search.json_search_test.test_management_ip_requires_operator_or_admin)
SR-1: managementIpAddress is readable by operator/admin but not by viewer ... ok
test_nested_matches_are_aggregated (test_json_search.json_search_test.test_nested_matches_are_aggregated)
Recursive search must aggregate matches from every nested dict and list ... ok
test_no_role_cannot_read_secret (test_json_search.json_search_test.test_no_role_cannot_read_secret)
SR-2 fail-closed: omitting the role must not grant access to protected fields ... ok
test_operator_cannot_read_api_key (test_json_search.json_search_test.test_operator_cannot_read_api_key)
SR-1: operator is not in POLICY["apiKey"], only admin may read it ... ok
test_parent_key_does_not_leak_secret (test_json_search.json_search_test.test_parent_key_does_not_leak_secret)
SR-3: querying a parent key must not leak restricted fields nested in the result ... ok
test_search_found (test_json_search.json_search_test.test_search_found)
key should be found, return list should not be empty ... ok
test_search_not_found (test_json_search.json_search_test.test_search_not_found)
key should not be found, should return an empty list ... ok
test_viewer_can_read_issue_summary (test_json_search.json_search_test.test_viewer_can_read_issue_summary)
SR-1 (guard against over-blocking): viewer is allowed to read issueSummary ... ok
test_wrong_role_cannot_read_secret (test_json_search.json_search_test.test_wrong_role_cannot_read_secret)
SR-1: viewer must not read the apiKey (SNMP community string) ... ok

----------------------------------------------------------------------
Ran 11 tests in 0.003s

OK

$ python3 recursive_json_search.py
admin    + issueSummary -> [{'issueSummary': 'Network Device 10.10.20.82 Is Unreachable From Controller'}]
viewer   + issueSummary -> [{'issueSummary': 'Network Device 10.10.20.82 Is Unreachable From Controller'}]
viewer   + apiKey       -> []
operator + apiKey       -> []
admin    + apiKey       -> [{'apiKey': 'SNMP-COMMUNITY-STRING-7f3a9c'}]
role=None+ apiKey       -> []
viewer   + deviceDetails (không lộ apiKey) -> [{'deviceDetails': {'family': 'Switches and Hubs', 'type': 'Cisco Catalyst 9300 Switch', 'errorCode': 'SNMP-TIMEOUT', 'macAddress': '50:60:ab:cd:70:80', 'role': 'ACCESS', 'apManagerInterfaceIp': '', 'associatedWlcIp': '', 'bootDateTime': '2020-01-01 00:00:01', 'collectionStatus': 'Partial Collection Failure', 'interfaceCount': '66', 'lineCardCount': '1', 'lineCardId': '022daaff-2a4a-4eb6-9050-91aab668fdf2', 'memorySize': '888963920', 'platformId': 'C9300-48U', 'reachabilityFailureReason': 'Collection Failure', 'reachabilityStatus': 'Unreachable', 'snmpContact': '', 'snmpLocation': '', 'series': 'Cisco Catalyst 9300 Series Switches', 'inventoryStatusDetail': '<status><general code="SNMP_TIMEOUT"/></status>', 'collectionInterval': 'Global Default', 'serialNumber': 'FCW1234L0UZ', 'softwareVersion': '16.6.3', 'roleSource': 'AUTO', 'hostname': 'leaf2.abc.inc', 'upTime': '01:08:43.96', 'lastUpdateTime': 1542693255158, 'errorDescription': 'SNMP timeouts are occurring with this device. Either the SNMP credentials are not correctly provided to controller or the device is responding slow and snmp timeout is low. If its a timeout issue, controller will attempt to progressively adjust the timeout in subsequent collection cycles to get device to managed state. User can also run discovery again only for this device using the discovery feature after adjusting the timeout and snmp credentials as required. Or user can update the timeout and snmp credentials as required using update credentials.', 'tagCount': '0', 'lastUpdated': '2018-11-20 05:54:15', 'instanceUuid': 'a7633ae5-d3c9-4aea-837d-c3ad5b19c802', 'id': 'a7633ae5-d3c9-4aea-837d-c3ad5b19c802', 'neighborTopology': [{'errorCode': 5000, 'message': 'An internal has error occurred while processing this request.', 'detail': 'An internal has error occurred while processing this request.'}], 'cisco360view': 'https://10.10.20.22/dna/assurance/home#networkDevice/a7633ae5-d3c9-4aea-837d-c3ad5b19c802'}}]

### Bước 8. Commit code + security test lên nhánh manual
Lưu ý: `test_search_found` được cập nhật để truyền `role="viewer"` (bắt buộc sau khi áp dụng SR-1/SR-2 fail-closed);
3 test chức năng vẫn giữ nguyên tên và docstring. Chữ "enfore" trong PDF được sửa chính tả thành "enforce".
$ git add policy.py recursive_json_search.py test_json_search.py
$ git commit -m "feat: enforce role-based access control in json_search()"
$ git add policy.py recursive_json_search.py test_json_search.py

$ git commit -m feat: enforce role-based access control in json_search()
[manual 3039abe] feat: enforce role-based access control in json_search()
 2 files changed, 127 insertions(+), 10 deletions(-)

(policy.py không bị thay đổi so với baseline, vẫn add theo đúng lệnh trong PDF)

$ git status
On branch manual
nothing to commit, working tree clean

$ git log --oneline
3039abe feat: enforce role-based access control in json_search()
5542c34 Nhom03 Fix ret_val bug in json_search, 3 unit tests PASS
cbde878 docs: add security requirements and threat model for json_search()
026c591 Nhom03 Add baseline unittest resources for B2
777d732 Nhom03 Add .gitignore and group intro note
a6c11b2 Manually merged from test branch
62a858e branch master Changed feature to master
eda981f branch test Change feature to test
6f0dc98 Added a third line in feature branch
b889aa8 Nhom03 Added additional line to file
6b0c49e Committing README.MD from Nhom03 to begin tracking changes

### Tổng kết nhánh manual
$ git log --oneline --decorate --graph --all
* 3039abe (HEAD -> manual) feat: enforce role-based access control in json_search()
* 5542c34 Nhom03 Fix ret_val bug in json_search, 3 unit tests PASS
* cbde878 docs: add security requirements and threat model for json_search()
* 026c591 (master, agent) Nhom03 Add baseline unittest resources for B2
* 777d732 (origin/master) Nhom03 Add .gitignore and group intro note
*   a6c11b2 Manually merged from test branch
|\  
| * eda981f (test) branch test Change feature to test
* | 62a858e branch master Changed feature to master
|/  
* 6f0dc98 Added a third line in feature branch
* b889aa8 Nhom03 Added additional line to file
* 6b0c49e Committing README.MD from Nhom03 to begin tracking changes

---

## B.2.2 Áp dụng AI Coding Agent trên một chức năng phần mềm (branch agent)

### Bước 1. Đưa tài liệu đặc tả an toàn từ manual sang agent
$ git checkout agent
Switched to branch 'agent'

$ git checkout manual -- unittest/security-requirements.md   # lấy spec từ nhánh manual sang nhánh agent
$ git status
On branch agent
Changes to be committed:
  (use "git restore --staged <file>..." to unstage)
	new file:   unittest/security-requirements.md


$ git commit -m docs: bring security specification from manual to agent branch
[agent 41bdbf9] docs: bring security specification from manual to agent branch
 1 file changed, 92 insertions(+)
 create mode 100644 unittest/security-requirements.md

$ ls -la unittest
total 44
drwxr-xr-x 3 nhanlaptop nhanlaptop 4096 Sep 23 08:43 .
drwxrwxr-x 6 nhanlaptop nhanlaptop 4096 Sep 23 08:40 ..
drwxrwxr-x 2 nhanlaptop nhanlaptop 4096 Sep 23 08:43 __pycache__
-rw-r--r-- 1 nhanlaptop nhanlaptop  563 Sep 15 21:39 policy.py
-rw-rw-r-- 1 nhanlaptop nhanlaptop   36 Sep 23 08:43 recursive_json_search.py
-rw-rw-r-- 1 nhanlaptop nhanlaptop 8434 Sep 23 08:43 security-requirements.md
-rw-r--r-- 1 nhanlaptop nhanlaptop 4787 Sep 15 21:39 test_data.py
-rw-rw-r-- 1 nhanlaptop nhanlaptop   36 Sep 23 08:43 test_json_search.py

$ git log --oneline -2
41bdbf9 docs: bring security specification from manual to agent branch
026c591 Nhom03 Add baseline unittest resources for B2

### Bước 2. Chạy AI coding agent trên nhánh agent (chế độ không tự commit)

**Sandbox guard:** cài `.git/hooks/pre-commit` chặn mọi lệnh `git commit` trong thời gian agent chạy ⇒ agent chỉ được phép ghi file,
không thể tự tạo commit. Người kiểm duyệt (sinh viên) tự chạy test, đọc diff rồi mới commit.
$ cat .git/hooks/pre-commit
#!/bin/sh
echo "BLOCKED: commits are disabled during the AI agent sandbox run." >&2
exit 1

**Agent được dùng:** AI coding agent chạy headless: `pi --mode json -p --provider opencode-go --model deepseek-v4-flash-vision-exp`
(model `deepseek-v4-flash-vision-exp`, giao thức qua provider `opencode-go`).

Hai phương án spawn khác đã thử trước đó: (1) `herd_spawn` role worker — timeout khi khởi động pane (2 lần),
(2) `bg_delegate` — chỉ có quyền đọc, không ghi được file. Do đó dùng Pi worker headless có đầy đủ tool.

**Prompt gửi cho agent** (nguyên văn, đã lưu tại `agent-run/prompt.txt`):

    You are an AI coding agent working inside a sandboxed working copy of a university lab repository.
    
    WORKING DIRECTORY: /home/nhanlaptop/UIT/NT521/TH1/Nhom03/unittest
    
    HARD CONSTRAINTS — a human reviewer reviews and commits, NOT you:
    - Do NOT run any git command that changes repository state: no commit / add / checkout / branch / stash / reset / restore / clean / merge. Read-only git commands (status, diff, log) are allowed.
    - Only create/edit files inside /home/nhanlaptop/UIT/NT521/TH1/Nhom03/unittest/
    - Do NOT modify test_data.py or policy.py.
    - Work in an "ask for approval" spirit: make the change, self-verify, then stop and report. Do not ask questions; just complete the task.
    
    TASK — this is the exact prompt you received from the developer (record it verbatim in your log):
    ---
    Please inspect all files in the unittest/ directory and complete the following requirements:
    
    1. Target Directory: Work inside unittest/ with test_data.py, policy.py, and security-requirements.md.
    2. Function Implementation (recursive_json_search.py):
       - Implement json_search(key, input_object, role=None) with recursive search logic.
       - Aggregate results from all nested dicts and lists properly without dropping data.
       - Enforce role-based access control based on policy.py before returning matched items.
    3. Test Suite Implementation (test_json_search.py):
       - Create test class json_search_test with docstrings inside each test method.
       - Implement 3 baseline functional tests: test_search_found, test_search_not_found, test_is_a_list.
       - Implement at least 3 security tests validating role permissions defined in policy.py.
    4. Self-Verification:
       - Run: python3 -m unittest -v test_json_search.py
       - Ensure all unit tests and security tests pass successfully.
    ---
    
    Read security-requirements.md FIRST. It defines security requirements SR-1..SR-3 and a STRIDE threat model. In particular note SR-2: omitting the role (role=None) must NOT grant access to protected fields (fail-closed).
    
    DELIVERABLES:
    1. Overwrite the placeholders `recursive_json_search.py` and `test_json_search.py` (both currently contain only a single comment line) with your implementation.
    2. Write `AGENT-LOG.md` in Vietnamese documenting your own session: the developer prompt above verbatim, your plan, every file you created/changed, every verification command you ran with its key output, the number of fix/rework rounds you needed before everything passed, and the final `python3 -m unittest -v test_json_search.py` output. Also record the model you are.
    3. Your FINAL ANSWER must report: the number of test cases implemented, the number of fix/rework rounds, the exact verification command, and the final test result line.

### Bước 3–4. Kiểm tra kết quả agent và phê duyệt (lần 1)

Sau khi agent chạy xong (exit code 0), người kiểm duyệt kiểm tra:

- `git branch --show-current` = `agent`; `git reflog` KHÔNG có commit/checkout lạ do agent tạo ⇒ agent tôn trọng sandbox.
- `git status`: chỉ 2 file bị sửa (`recursive_json_search.py`, `test_json_search.py`) + file mới `AGENT-LOG.md`; `policy.py`, `test_data.py`, `security-requirements.md` không bị chạm.
- Agent viết **22 test case**, tự chạy `python3 -m unittest -v test_json_search.py` ⇒ `Ran 22 tests ... OK`.
- Người kiểm duyệt tự chạy lại: `Ran 22 tests in 0.005s / OK` (tái lập được).

**Lỗi phát hiện khi review (chặn merge) — vi phạm hợp đồng trả về:**

| | Theo đặc tả trong đề bài | Kết quả agent (vòng 1) |
|---|---|---|
| `json_search("apiKey", data, role="admin")` | `[{'apiKey': 'SNMP-COMMUNITY-STRING-7f3a9c'}]` | `['SNMP-COMMUNITY-STRING-7f3a9c']` |
| `json_search("issueSummary", data, role="viewer")` | `[{'issueSummary': 'Network Device ... Unreachable From Controller'}]` | `['Network Device ... Unreachable From Controller']` |

Đề bài ghi rõ hàm "trả về list các cặp key/value" và code mẫu dùng `temp = {k: v}`; agent trả về **list giá trị trần**.
Bộ test của agent assert đúng theo shape sai này (`assertEqual(json_search("apiKey", data, role="admin"), [SECRET_API_KEY])`)
nên 22/22 test vẫn xanh — đây là **lỗi chức năng mà test của agent không bắt được, do con người phát hiện khi review**.
⇒ Yêu cầu agent sửa (vòng rework thứ 2), đồng thời phải cập nhật test để kiểm tra đúng hợp đồng.
### Bước 5–6. Kiểm tra code diff, chạy test và commit trên nhánh agent

Người kiểm duyệt tự chạy lại test: `Ran 24 tests in 0.005s / OK`; kiểm tra shape bằng tay:

```
admin  + apiKey       -> [{'apiKey': 'SNMP-COMMUNITY-STRING-7f3a9c'}]
viewer + issueSummary -> [{'issueSummary': 'Network Device 10.10.20.82 Is Unreachable From Controller'}]
viewer + apiKey       -> []
role=None + apiKey    -> []
viewer + deviceDetails: ket qua khong chua apiKey
```

$ git status --short   # chi 2 file code/test bi sua + AGENT-LOG.md moi; policy.py, test_data.py, security-requirements.md khong bi cham
$ git reflog          # xac nhan agent khong tao commit/checkout nao
$ git status --short
 M unittest/recursive_json_search.py
 M unittest/test_json_search.py
?? unittest/AGENT-LOG.md

$ git reflog -3
41bdbf9 HEAD@{0}: commit: docs: bring security specification from manual to agent branch
026c591 HEAD@{1}: checkout: moving from manual to agent
3039abe HEAD@{2}: commit: feat: enforce role-based access control in json_search()

Gỡ sandbox guard và commit kết quả của agent:
$ rm .git/hooks/pre-commit
$ git add unittest/recursive_json_search.py unittest/test_json_search.py
$ git commit -m "feat: enforce role-based access control in json_search() (AI agent implementation)"
$ git add unittest/AGENT-LOG.md
$ git commit -m "docs: add B.2.2 agent log (prompt, review rounds, verification)"
$ git add recursive_json_search.py test_json_search.py

$ git commit -m feat: enforce role-based access control in json_search() (AI agent implementation)
[agent b0001f5] feat: enforce role-based access control in json_search() (AI agent implementation)
 2 files changed, 720 insertions(+), 2 deletions(-)

$ git add AGENT-LOG.md

$ git commit -m docs: add B.2.2 agent log (prompt, review rounds, verification)
[agent 9d66705] docs: add B.2.2 agent log (prompt, review rounds, verification)
 1 file changed, 522 insertions(+)
 create mode 100644 unittest/AGENT-LOG.md

$ git status
On branch agent
nothing to commit, working tree clean

$ git log --oneline --decorate --graph --all
* 9d66705 (HEAD -> agent) docs: add B.2.2 agent log (prompt, review rounds, verification)
* b0001f5 feat: enforce role-based access control in json_search() (AI agent implementation)
* 41bdbf9 docs: bring security specification from manual to agent branch
| * 3039abe (manual) feat: enforce role-based access control in json_search()
| * 5542c34 Nhom03 Fix ret_val bug in json_search, 3 unit tests PASS
| * cbde878 docs: add security requirements and threat model for json_search()
|/  
* 026c591 (master) Nhom03 Add baseline unittest resources for B2
* 777d732 (origin/master) Nhom03 Add .gitignore and group intro note
*   a6c11b2 Manually merged from test branch
|\  
| * eda981f (test) branch test Change feature to test
* | 62a858e branch master Changed feature to master
|/  
* 6f0dc98 Added a third line in feature branch
* b889aa8 Nhom03 Added additional line to file
* 6b0c49e Committing README.MD from Nhom03 to begin tracking changes


---

## B.2.2 (tiếp) Trả lời câu hỏi lý thuyết: AI coding agent có những chế độ vận hành nào?

Agent dùng trong bài: **Pi coding agent** (`pi` CLI), model `opencode-go/deepseek-v4-flash-vision-exp`.
Các chế độ vận hành và cơ chế khác nhau:

| Nhóm chế độ | Chế độ | Cơ chế hoạt động | Dùng trong bài? |
|---|---|---|---|
| **Giao diện / mức tương tác** | TUI tương tác (mặc định) | Mở terminal UI, agent hiển thị từng bước, người dùng xem/duyệt/trả lời ngay trong phiên | Không |
| | `-p/--print` (non-interactive, `--mode text`) | Nhận prompt, chạy hết, in câu trả lời cuối rồi thoát; không hỏi lại | Không (dùng bản JSON bên dưới) |
| | `--mode json -p` | Non-interactive nhưng xuất **luồng sự kiện có cấu trúc** (assistant text, reasoning, tool call, token/cost). Phù hợp chạy nền/CI, log lại được để kiểm toán | **Có** — đây là chế độ chạy cả 2 vòng |
| | `--mode rpc` | Agent chạy như một service, host (IDE/editor) điều khiển qua RPC | Không |
| **Quyền / phê duyệt (approval)** | Ask-for-approval | Agent **đề xuất** thay đổi; người dùng duyệt rồi mới áp dụng/commit. Trong bài được cài bằng 2 lớp: (1) `.git/hooks/pre-commit` chặn cứng mọi `git commit` trong lúc agent chạy; (2) người kiểm duyệt tự chạy test, đọc diff rồi mới commit | **Có** (đúng yêu cầu đề bài) |
| | `--approve` / `--no-approve` | Tin (hoặc bỏ qua) file cấu hình/extension/prompt template nằm trong project. `--no-approve` ⇒ môi trường kín, không nạp cấu hình lạ | **Có** (`--no-approve`) |
| | Auto-edit / full-auto | Cho agent ghi file, chạy lệnh và commit tự động, không hỏi | Không |
| **Phạm vi công cụ** | `--tools <ds>` / `--exclude-tools <ds>` / `--no-tools` / `--no-builtin-tools` | Giới hạn allowlist/denylist công cụ: ví dụ chỉ cho `read/grep` (chế độ chỉ đọc, chỉ tư vấn) hoặc chỉ cho bash (không sửa file) | Không (dùng bộ tool đầy đủ) |
| **Phiên làm việc** | Mặc định (lưu session) | Lưu hội thoại vào session file, có thể `--continue`, `--session <id>`, `--fork` để chạy tiếp/ rẽ nhánh | **Có** — vòng 2 chạy `--session <path>` để agent nhớ feedback và sửa tiếp |
| | `--no-session` | Phiên tạm (ephemeral), không lưu lịch sử | Không |

**Cách vận hành khác nhau cốt lõi:** *chế độ tương tác* quyết định ai duyệt (người dùng duyệt ngay trong TUI vs. duyệt bằng hook + review sau khi chạy xong);
*phạm vi công cụ* quyết định agent có ghi được file hay không; *chế độ phiên* quyết định agent có nhớ ngữ cảnh giữa các lần chạy hay không.
Trong bài, cả 2 vòng đều chạy **non-interactive JSON + `--no-approve` + không tự commit**, còn quyền "approve" nằm ở con người (chạy test, đọc diff, commit).

---

## B.2.2 Bước 7. Đối sánh hai quy trình (manual vs AI agent)

Số liệu đo được:

| Chỉ số đo được | manual | agent |
|---|---|---|
| Số commit tạo ra (B.2) | 3 (`cbde878`, `5542c34`, `3039abe`) | 3 (`41bdbf9`, `b0001f5`, `9d66705`) |
| Số test case | 11 (`test_json_search.py` 95 dòng) | 24 (543 dòng) |
| Số dòng code hàm | 70 dòng | 177 dòng |
| Thời gian chạy (wall-clock) | 08:40:51 → 08:43:22 ≈ **2 phút 31 giây** (từng bước có người điều khiển) | vòng 1: 08:46:19 → 08:49:53 (**3p34s**); vòng 2: 08:50:44 → 09:00:53 (**10p09s**); tổng ≈ **13p43s**, chạy nền không cần người |
| Số lượt tool call của agent | — | 62 (vòng 1: 34, vòng 2: 28), 1 lỗi |
| Model | người viết code | vòng 1 `deepseek-v4-flash-vision-exp`; vòng 2 `qwen3.8-flash` (provider tự failover giữa 2 vòng) |
| Chi phí token | — | ≈ 0,046 + 0,069 = **≈ 0,115 USD** |
| Số lần chạy test đỏ (`FAILED`) | 1 (đúng như kịch bản Bước 4 của đề bài) | 2 (vòng 1: 1 lần đỏ do kỳ vọng test của chính agent; vòng 2: 0 lần đỏ) |

### Bảng đối sánh theo 6 tiêu chí của đề bài

| Tiêu chí | Thủ công (manual) | AI Agent (agent) |
|---|---|---|
| **Mức đáp ứng security requirement** | SR-1 (allowlist theo POLICY) ✅; SR-2 fail-closed cho **các trường trong POLICY** ✅ — nhưng `role=None` vẫn đọc được trường **không** nằm trong POLICY (ví dụ `deviceDetails`, `hostname`); SR-3 lọc đệ quy chống rò rỉ qua key cha ✅; SR-4 luôn trả `list`, không crash ✅ (nhưng **không** bắt `RecursionError`) | SR-1 ✅; SR-2 fail-closed **triệt để**: role lạ/`None`/`"Admin"`/giá trị không phải chuỗi ⇒ trả `[]` cho **mọi** trường; SR-3 ✅ **và mạnh hơn**: không đi vào cây con bị hạn chế (chặn cả đường vòng qua key con), `_redact()` trả bản sao sâu nên input không bị mutate; SR-4 bắt `RecursionError`, chống `__eq__` độc hại; thêm SR-5 (giữ cả match “falsy” như `[]`) — **đáp ứng đầy đủ hơn manual** |
| **Số lỗi chức năng phát hiện được / còn sót** | Phát hiện **1** lỗi ngay trong quy trình: bug `ret_val` (kết quả đệ quy bị bỏ đi) do test ở Bước 4 bắt được — đúng thiết kế của đề bài. Còn sót: **0** | Vòng 1 agent **tự phát hiện 1** lỗi (kỳ vọng test của chính nó sai: fixture có 4 match `message` nhưng test chỉ kỳ vọng 3). Người kiểm duyệt phát hiện **1 lỗi chức năng mà 22/22 test của agent không bắt được**: hàm trả về *list giá trị trần* thay vì *list cặp key/value* theo đặc tả ⇒ vòng 2 sửa xong. Còn sót sau review: **0** |
| **Số lỗi an toàn phát hiện được / còn sót** | Phát hiện **1** lỗ hổng khi làm threat model (T4: viewer hỏi key cha `deviceDetails` để lấy `apiKey`) và chủ động xử lý bằng `_filter_value()`. Còn sót: **1 điểm yếu mức thiết kế** — `role=None` vẫn đọc được trường ngoài POLICY (đã ghi trong `security-requirements.md` mục 7) | **0 lỗ hổng** bị người kiểm duyệt phát hiện trong code (review đối chiếu từng SR đều đạt, thậm chí chặt hơn manual). Tuy nhiên **test của agent không tự bắt được** lỗi hợp đồng — nghĩa là “test xanh” không đồng nghĩa “đúng đặc tả” |
| **Thời gian thực hiện (ước lượng)** | ≈ 2,5 phút wall-clock cho phần code/test ở B.2.1 (không tính thời gian đọc đề, viết threat model và suy nghĩ thiết kế — nếu tính cho người làm thật thì ước lượng **2–4 giờ**), phải có mặt ở từng bước | ≈ **14 phút** tổng cộng cho cả 2 vòng, chạy nền **không cần người ngồi cạnh**; nhưng phải cộng thời gian review của con người (~10 phút) |
| **Mức độ can thiệp của con người** | Can thiệp ở **mọi** bước (viết spec, code, test, chạy test, commit) — 3 commit đều do người tạo; phải sửa tay 1 lần khi thêm RBAC (`test_search_found` phải truyền `role="viewer"`) | Can thiệp **2 lần**: (1) gửi review chặn merge + yêu cầu sửa hợp đồng trả về (vòng rework 2); (2) duyệt diff, gỡ sandbox guard và commit. Ngoài ra phải giám sát: agent vòng 2 bị đổi model do provider failover |
| **Khả năng tái lập (chạy lại từ đầu có ra kết quả tương tự không)** | **Cao**: mọi bước là lệnh xác định, prompt/threat model nằm trong file, test deterministic ⇒ chạy lại cho kết quả giống hệt (`Ran 11 tests / OK`) | **Thấp hơn**: cùng prompt nhưng code/test sinh ra khác nhau giữa các lần (LLM không tất định), và **đã đổi model giữa 2 vòng do failover**. Bù lại phần **kiểm chứng** tái lập được: prompt được lưu (`agent-run/prompt.txt`), session JSONL + telemetry được lưu, và bộ test deterministic (`Ran 24 tests / OK`) ⇒ có thể kiểm chứng lại kết quả dù không tái tạo được quá trình |

### Kết luận

1. **Về độ phủ và độ sâu kỹ thuật, agent vượt trội**: 24 test so với 11, xử lý thêm các ca khó (dữ liệu vòng/`RecursionError`, role không phải chuỗi, giữ match `[]`, không mutate input, không đi vào cây con bị hạn chế) và fail-closed triệt để hơn — trong ~14 phút và ~0,12 USD.
2. **Nhưng “test xanh” của agent không phải bằng chứng đúng đặc tả**: agent tự thay đổi *hợp đồng trả về* của hàm (list giá trị trần thay vì list cặp key/value) rồi **viết test assert theo đúng cái sai của mình**, khiến 22/22 test pass mà vẫn sai đề. Chỉ con người đọc đặc tả mới bắt được. ⇒ Vai trò review của con người **không thể bỏ qua**, và nên có **test khoá hợp đồng (contract test)** độc lập với code.
3. **Điểm mạnh của quy trình thủ công nằm ở pha thiết kế an toàn**: nhờ viết threat model STRIDE trước khi code, lỗ hổng “hỏi key cha để lấy secret” (T4) bị chặn ngay từ thiết kế; agent cũng đạt được điều này nhưng một phần vì `security-requirements.md` (do manual viết) đã được đưa sang branch `agent` làm đầu vào. **Threat model tốt là thứ có thể “tiêm” cho agent để nâng chất lượng đầu ra.**
4. **Kết luận vận hành**: nên dùng agent để **mở rộng độ phủ test và gia cố (hardening)** với tốc độ cao, nhưng bắt buộc có **cổng review của con người** đối chiếu lại security requirement + contract trước khi merge; với thay đổi an toàn, hãy viết đặc tả/threat model trước rồi mới giao cho agent — chất lượng đầu ra phụ thuộc trực tiếp vào chất lượng đặc tả đầu vào.

---

## Phát sinh sau B.2: đẩy các nhánh lên GitHub

```
9d667052b7eb7bb1a7cb68dada6cc693d5287fbe	refs/heads/agent
3039abea023f2b7d7258664100b1ee969699f76d	refs/heads/manual
026c591765af505fa81538b03e54152907286006	refs/heads/master
```
