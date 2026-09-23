# AGENT-LOG.md — Nhật ký phiên làm việc của AI agent

**Thư mục làm việc:** `/home/nhanlaptop/UIT/NT521/TH1/Nhom03/unittest`
**Ngày ghi log:** 2026-09-23
**Vai trò:** AI coding agent (chạy tự động, không commit/push thay người duyệt)

---

## 0. Model / môi trường

| Mục | Giá trị |
|---|---|
| Model | `deepseek-v4-flash-vision-exp` |
| Provider | `opencode-go` |
| Reasoning level | `max` |
| Harness | Pi coding agent (`PI_CODING_AGENT=true`) |
| Python | 3.14.7 |
| Session ID | `01a0cbf1-3fb3-7189-8c0c-d5ac2962794a` |

---

## 1. Prompt của developer (nguyên văn, verbatim)

> Please inspect all files in the unittest/ directory and complete the following requirements:
>
> 1. Target Directory: Work inside unittest/ with test_data.py, policy.py, and security-requirements.md.
> 2. Function Implementation (recursive_json_search.py):
>    - Implement json_search(key, input_object, role=None) with recursive search logic.
>    - Aggregate results from all nested dicts and lists properly without dropping data.
>    - Enforce role-based access control based on policy.py before returning matched items.
> 3. Test Suite Implementation (test_json_search.py):
>    - Create test class json_search_test with docstrings inside each test method.
>    - Implement 3 baseline functional tests: test_search_found, test_search_not_found, test_is_a_list.
>    - Implement at least 3 security tests validating role permissions defined in policy.py.
> 4. Self-Verification:
>    - Run: python3 -m unittest -v test_json_search.py
>    - Ensure all unit tests and security tests pass successfully.
>
> ---
>
> Read security-requirements.md FIRST. It defines security requirements SR-1..SR-3 and a STRIDE threat model. In particular note SR-2: omitting the role (role=None) must NOT grant access to protected fields (fail-closed).
>
> DELIVERABLES:
> 1. Overwrite the placeholders `recursive_json_search.py` and `test_json_search.py` (both currently contain only a single comment line) with your implementation.
> 2. Write `AGENT-LOG.md` in Vietnamese documenting your own session: the developer prompt above verbatim, your plan, every file you created/changed, every verification command you ran with its key output, the number of fix/rework rounds you needed before everything passed, and the final `python3 -m unittest -v test_json_search.py` output. Also record the model you are.
> 3. Your FINAL ANSWER must report: the number of test cases implemented, the number of fix/rework rounds, the exact verification command, and the final test result line.

---

## 2. Khảo sát ban đầu (read-only)

| File | Trạng thái trước khi làm | Ghi chú |
|---|---|---|
| `test_data.py` | 143 dòng, fixture Cisco DNA Center | **KHÔNG ĐƯỢC SỬA** — chỉ đọc |
| `policy.py` | `POLICY = {apiKey:[admin], managementIpAddress:[admin,operator], issueSummary:[admin,operator,viewer]}` | **KHÔNG ĐƯỢC SỬA** — chỉ đọc |
| `security-requirements.md` | 176 dòng, STRIDE + SR-1..SR-5 | Đọc trước khi code |
| `recursive_json_search.py` | 1 dòng `# Fill the Python code in this file` | Ghi đè |
| `test_json_search.py` | 1 dòng `# Fill the Python code in this file` | Ghi đè |

Các lệnh khảo sát đã chạy (chỉ đọc, không đổi trạng thái repo):

```
$ ls -la
$ git status --short          # sạch trước khi sửa
$ git log --oneline -3        # 41bdbf9 docs: bring security specification ... / 026c591 Nhom03 Add baseline ...
```

Bản đồ yêu cầu bảo mật đọc được từ `security-requirements.md`:

| ID | Nội dung | Threat | Cách hiện thực |
|---|---|---|---|
| SR-1 | Chỉ trả về trường X nếu `role ∈ POLICY[X]` | T1, T3 | Allowlist tại một điểm quyết định duy nhất `_may_read()` |
| SR-2 | Fail-closed khi `role=None`/role không xác định | T2 | `FAIL_CLOSED_FOR_UNKNOWN_ROLE = True`, chặn cả các trường NGOÀI `POLICY` (mạnh hơn mức tối thiểu của SR-2) |
| SR-3 | Không chứa trường hạn chế ở bất kỳ độ sâu nào, kể cả khi hỏi key cha | T4 | `_redact()` duyệt sâu + **không đi vào cây con bị hạn chế** (chặn cửa hậu qua key con không hạn chế) |
| SR-4 | Không crash, luôn trả về `list` | T5 | Chỉ duyệt `dict/list/tuple`; bắt `RecursionError` (dữ liệu lồng sâu/dữ liệu vòng) và trả về kết quả đã gom được |
| SR-5 | Gộp kết quả mọi cấp, không bỏ sót | — | DFS gom vào một accumulator dùng chung, giữ cả giá trị "falsy" như `[]` |

---

## 3. Kế hoạch thực hiện

1. Đọc `security-requirements.md`, `policy.py`, `test_data.py` để chốt semantics (giá trị mẫu, đường dẫn lồng nhau, bảng quyền).
2. Viết `recursive_json_search.py`:
   - `_may_read(field, role)` là **điểm quyết định quyền duy nhất** (dùng chung cho cả tìm kiếm và redaction) → tránh lệch logic giữa 2 đường.
   - `_redact(value, role)` sao chép sâu có lọc; `_search()` DFS gom match; `json_search()` là điểm vào công khai (fail-closed + chống crash).
3. Viết `test_json_search.py`:
   - Class `json_search_test`, mỗi test method có docstring, có `tearDown()` kiểm tra fixture không bị mutate.
   - 3 test baseline bắt buộc + 19 test bảo mật/chức năng (bám theo SR-1..SR-5 và đúng tên test mà `security-requirements.md` §6 nhắc tới).
4. Chạy `python3 -m unittest -v test_json_search.py`, sửa đến khi xanh.
5. Kiểm chứng độc lập ngoài unit test: probe đối kháng quét mọi key × mọi role tìm rò rỉ/crash/aliasing.
6. Viết `AGENT-LOG.md` (file này) và báo cáo cuối.

---

## 4. Các file đã tạo / thay đổi

| File | Hành động | Nội dung chính |
|---|---|---|
| `recursive_json_search.py` | **Ghi đè** (placeholder 1 dòng → 170 dòng) | `json_search()`, `_search()`, `_redact()`, `_may_read()`, `_is_known_role()`, `_keys_equal()`, hằng `KNOWN_ROLES` (suy ra từ `POLICY`) và `FAIL_CLOSED_FOR_UNKNOWN_ROLE = True` |
| `test_json_search.py` | **Ghi đè** (placeholder 1 dòng → 388 dòng) | Class `json_search_test` với **22 test** (3 baseline + 19 bảo mật/chức năng), helper `_forbidden_keys_in()`, snapshot `_PRISTINE_DATA`, `tearDown()` chống mutate dữ liệu |
| `AGENT-LOG.md` | **Tạo mới** | File này |
| `policy.py` | Không đổi | `git diff` rỗng |
| `test_data.py` | Không đổi | `git diff` rỗng |
| `security-requirements.md` | Không đổi | `git diff` rỗng |

Kiểm chứng không đụng file cấm:

```
$ git status --short
 M recursive_json_search.py
 M test_json_search.py

$ git diff --stat -- policy.py test_data.py security-requirements.md
(không có output ⇒ ba file được bảo vệ không bị thay đổi)

$ sha256sum policy.py test_data.py recursive_json_search.py test_json_search.py
5d7f965ff33b11ff8bd3190c11125e634a5bf84613b43f9e31e803151baca748  policy.py
13f40831bbc271a73f353793e81b3ca8fc8bf76b7a30b0f1c558aa91d352a4b8  test_data.py
c3d7d210079b10471064a83eb0adf018f4fdedc9fdebaf36426e36cdde4c51f8  recursive_json_search.py
ce2dccd605397cb2c7ed4260bc7121beaca72b00a518478c69dc37ff8cb590ea  test_json_search.py
```

Không chạy bất kỳ lệnh git nào làm đổi trạng thái repo (`commit/add/checkout/branch/stash/reset/restore/clean/merge`).
Script probe chỉ được ghi vào `/tmp`, không thêm file rác vào repo.

---

## 5. Quyết định thiết kế quan trọng (để người duyệt đối chiếu)

1. **Fail-closed mạnh hơn mức tối thiểu của SR-2.** SR-2 yêu cầu `role=None` không đọc được các trường *nằm trong `POLICY`*. Bản cài đặt này chặn **toàn bộ** trường khi role là `None`/không xác định, kể cả các trường ngoài `POLICY` (ví dụ `hostname`, `macAddress`, `status`) — vì §7 tài liệu chỉ cho phép dữ liệu vận hành được đọc bởi “mọi **role hợp lệ**”, và `serialNumber`/`macAddress` vẫn được liệt kê là asset nhạy cảm ở §3. Nếu hội đồng chấm muốn nới lỏng đúng bằng mức tối thiểu SR-2, chỉ cần đổi **một dòng**: `FAIL_CLOSED_FOR_UNKNOWN_ROLE = False` (đã ghi chú ngay tại chỗ trong code).
2. **Một điểm quyết định quyền duy nhất.** Cả đường tìm kiếm lẫn đường redaction đều gọi `_may_read()`, nên không thể xảy ra tình trạng “chỗ chặn chỗ quên”.
3. **Không đi vào cây con bị hạn chế.** Nếu key cha nằm trong `POLICY` mà role không được đọc (ví dụ `apiKey` chứa object con), toàn bộ cây con bị bỏ qua. Nếu chỉ lọc theo *key khớp* thì `viewer` vẫn có thể hỏi key con bên trong `apiKey` để lấy secret — đã có test `test_restricted_subtree_is_not_traversed` cho cửa hậu này.
4. **Redaction là bản sao sâu, không mutate input.** `test_data.py` là fixture dùng chung: nếu trả reference hoặc xoá field tại chỗ, các test sau sẽ hỏng và dữ liệu nguồn bị phá. `tearDown()` so sánh `data` với `_PRISTINE_DATA` sau **mỗi** test.
5. **Chống crash có chủ đích.** Chỉ duyệt `dict/list/tuple`; `RecursionError` (lồng quá sâu, cấu trúc tự tham chiếu) được bắt ở `json_search()` và trả về phần đã gom được thay vì ném lỗi (SR-4/T5).
6. **So khớp role chính xác, phân biệt hoa/thường.** `"Admin"`, `"VIEWER"`, `"viewer "`, `123`, `True`, `["admin"]`… đều bị coi là không xác định. Việc chuẩn hoá role thuộc tầng xác thực phía server (đã ghi trong docstring của `_is_known_role`).

---

## 6. Danh sách 22 test đã hiện thực

### 6.1 Baseline chức năng (3 — đúng tên yêu cầu)
| # | Test | Docstring / nội dung |
|---|---|---|
| 1 | `test_search_found` | SR-5: key hợp lệ được tìm thấy, trả về đúng giá trị `issueSummary` |
| 2 | `test_search_not_found` | SR-4: key không tồn tại ⇒ `[]`, không raise |
| 3 | `test_is_a_list` | SR-4: luôn trả về `list` với mọi key/data/role |

### 6.2 Bảo mật & chức năng bổ sung (19)
| # | Test | SR / Threat |
|---|---|---|
| 4 | `test_nested_matches_are_aggregated` | SR-5 (gộp match ở nhiều độ sâu: `errorCode`, `message`, `managementIpAddress`) |
| 5 | `test_empty_list_values_are_not_dropped` | SR-5 (giá trị falsy `[]` không bị bỏ) |
| 6 | `test_policy_matches_security_spec` | Phát hiện policy bị trôi khỏi đặc tả |
| 7 | `test_policy_allow_list_is_enforced_for_every_field` | SR-1 (duyệt toàn bộ `POLICY` × 3 role) |
| 8 | `test_viewer_can_read_issue_summary` | SR-1 / T1 |
| 9 | `test_viewer_cannot_read_management_ip` | SR-1 / T1 |
| 10 | `test_operator_can_read_management_ip` | SR-1 |
| 11 | `test_admin_can_read_management_ip` | SR-1 |
| 12 | `test_operator_cannot_read_api_key` | SR-1 / T1 |
| 13 | `test_admin_can_read_api_key` | SR-1 |
| 14 | `test_wrong_role_cannot_read_secret` | SR-1 / T3 (role tự khai, role biến thể) |
| 15 | `test_no_role_cannot_read_secret` | SR-2 / T2 (bỏ `role`, `role=None`) |
| 16 | `test_unknown_role_is_rejected` | SR-2 / T3 (11 biến thể role lạ) |
| 17 | `test_parent_key_does_not_leak_secret` | SR-3 / T4 (hỏi key cha `connectedDevice`, `deviceDetails`, `enrichmentInfo`) |
| 18 | `test_redaction_applies_at_every_depth` | SR-3 / T4 (quét lại toàn bộ cây kết quả) |
| 19 | `test_restricted_subtree_is_not_traversed` | SR-3 / T4 (cửa hậu qua key con) |
| 20 | `test_non_policy_field_is_readable_by_valid_roles` | §7 residual risk, chống siết quá tay |
| 21 | `test_redaction_does_not_mutate_input` | Toàn vẹn dữ liệu (không alias nguồn) |
| 22 | `test_unusual_input_never_crashes` | SR-4 / T5 (16 mẫu dữ liệu dị: `None`, `set`, `bytes`, 2000 cấp lồng, dict tự tham chiếu…) |

Mỗi test method đều có docstring (hiển thị trực tiếp trong output `-v`).

---

## 7. Số vòng sửa / làm lại (fix–rework rounds)

| Vòng | Loại | Mô tả | Kết quả |
|---|---|---|---|
| 0 | Viết lần đầu | Tạo `recursive_json_search.py` + `test_json_search.py` | — |
| **1** | **Fix (do test đỏ)** | Lần chạy đầu: **22 test, 1 failure** — `test_nested_matches_are_aggregated` kỳ vọng 3 `message` nhưng fixture có **4** (thêm `deviceDetails.neighborTopology[0].message = "An internal has error occurred while processing this request."`). Đã sửa kỳ vọng thành `EXPECTED_MESSAGES` (4 phần tử, kèm comment giải thích vị trí) — đúng bản chất SR-5 “không bỏ sót dữ liệu”, lỗi nằm ở kỳ vọng của test chứ không phải ở hàm | ✅ Xanh |
| (2) | Hardening (không do test đỏ) | Thêm `tearDown()` so `data` với `_PRISTINE_DATA` sau mỗi test để bắt mọi hành vi mutate fixture; tiện thể phát hiện 1 dòng docstring bị lặp do thao tác insert và xoá ngay trong cùng vòng, **trước khi** chạy lại test | ✅ Xanh |

**Tổng số vòng phải sửa để hết đỏ: 1 vòng** (1 lần chạy thất bại, sửa 4 dòng kỳ vọng; sau đó là 1 vòng gia cố không phát sinh lỗi).

---

## 8. Nhật ký lệnh kiểm chứng và output chính

### 8.1 Lần chạy thứ nhất — phát hiện 1 failure

```
$ python3 -m unittest -v test_json_search.py
...
FAIL: test_nested_matches_are_aggregated (test_json_search.json_search_test.test_nested_matches_are_aggregated)
SR-5: matches at different depths/lists are aggregated, not dropped.
----------------------------------------------------------------------
Traceback (most recent call last):
  File ".../test_json_search.py", line 125, in test_nested_matches_are_aggregated
    self.assertEqual(
        json_search("message", data, role="viewer"), SUGGESTED_MESSAGES
    )
AssertionError: Lists differ: ['Fro[201 chars]ice.', 'An internal has error occurred while p[20 chars]st.'] != ['Fro[201 chars]ice.']
First list contains 1 additional elements.
First extra element 3:
'An internal has error occurred while processing this request.'
----------------------------------------------------------------------
Ran 22 tests in 0.004s

FAILED (failures=1)
```

### 8.2 Lệnh kiểm chứng bắt buộc — lần chạy cuối (PASS)

Command (đúng như developer yêu cầu):

```
python3 -m unittest -v test_json_search.py
```

Output đầy đủ (exit code = 0):

```
test_admin_can_read_api_key (test_json_search.json_search_test.test_admin_can_read_api_key)
SR-1: admin is allowed to read the apiKey credential. ... ok
test_admin_can_read_management_ip (test_json_search.json_search_test.test_admin_can_read_management_ip)
SR-1: admin is allowed to read managementIpAddress. ... ok
test_empty_list_values_are_not_dropped (test_json_search.json_search_test.test_empty_list_values_are_not_dropped)
SR-5: falsy matches such as ``[]`` are real matches and must be kept. ... ok
test_is_a_list (test_json_search.json_search_test.test_is_a_list)
SR-4: every call returns a list, whatever the key, the data or the role. ... ok
test_nested_matches_are_aggregated (test_json_search.json_search_test.test_nested_matches_are_aggregated)
SR-5: matches at different depths/lists are aggregated, not dropped. ... ok
test_no_role_cannot_read_secret (test_json_search.json_search_test.test_no_role_cannot_read_secret)
SR-2: omitting the role (role=None) returns no protected field at all. ... ok
test_non_policy_field_is_readable_by_valid_roles (test_json_search.json_search_test.test_non_policy_field_is_readable_by_valid_roles)
§7: fields absent from POLICY stay readable for every valid role. ... ok
test_operator_can_read_management_ip (test_json_search.json_search_test.test_operator_can_read_management_ip)
SR-1: operator is allowed to read managementIpAddress. ... ok
test_operator_cannot_read_api_key (test_json_search.json_search_test.test_operator_cannot_read_api_key)
SR-1: operator is NOT allowed to read the apiKey credential. ... ok
test_parent_key_does_not_leak_secret (test_json_search.json_search_test.test_parent_key_does_not_leak_secret)
SR-3: querying a parent key never returns restricted children. ... ok
test_policy_allow_list_is_enforced_for_every_field (test_json_search.json_search_test.test_policy_allow_list_is_enforced_for_every_field)
SR-1: for every protected field and every role, access == POLICY allow-list. ... ok
test_policy_matches_security_spec (test_json_search.json_search_test.test_policy_matches_security_spec)
The POLICY table must still match the allow-lists of the security spec. ... ok
test_redaction_applies_at_every_depth (test_json_search.json_search_test.test_redaction_applies_at_every_depth)
SR-3: a whole container returned to a viewer is sanitised recursively. ... ok
test_redaction_does_not_mutate_input (test_json_search.json_search_test.test_redaction_does_not_mutate_input)
The caller's data store and the returned objects must stay independent. ... ok
test_restricted_subtree_is_not_traversed (test_json_search.json_search_test.test_restricted_subtree_is_not_traversed)
SR-3: no side-door into a restricted subtree through a child key. ... ok
test_search_found (test_json_search.json_search_test.test_search_found)
SR-5: an allowed key must be found and its value returned exactly once. ... ok
test_search_not_found (test_json_search.json_search_test.test_search_not_found)
SR-4: a key that does not exist returns an empty list, without raising. ... ok
test_unknown_role_is_rejected (test_json_search.json_search_test.test_unknown_role_is_rejected)
SR-2/T3: an unknown, malformed or non-string role is refused entirely. ... ok
test_unusual_input_never_crashes (test_json_search.json_search_test.test_unusual_input_never_crashes)
SR-4/T5: malformed, hostile or cyclic input never raises and returns a list. ... ok
test_viewer_can_read_issue_summary (test_json_search.json_search_test.test_viewer_can_read_issue_summary)
SR-1: viewer is allowed to read issueSummary. ... ok
test_viewer_cannot_read_management_ip (test_json_search.json_search_test.test_viewer_cannot_read_management_ip)
SR-1: viewer is NOT allowed to read managementIpAddress. ... ok
test_wrong_role_cannot_read_secret (test_json_search.json_search_test.test_wrong_role_cannot_read_secret)
SR-1/T3: a wrong or self-declared privileged role never leaks the secret. ... ok

----------------------------------------------------------------------
Ran 22 tests in 0.004s

OK
```

**Dòng kết quả cuối (final test result line): `OK` — `Ran 22 tests in 0.004s`.**

### 8.3 Kiểm chứng độc lập ngoài unit test #1 — probe đối kháng (800 lượt gọi)

Mục đích: không tin vào bộ test do chính mình viết; quét **mọi key** có trong `test_data` ∪ `POLICY` (80 key) × **10 biến thể role** (`viewer`, `operator`, `admin`, `None`, `"root"`, `""`, `"Admin"`, `0`, `True`, `["admin"]`) và tấn công:

- tìm field bị hạn chế lọt vào kết quả (SR-1/SR-3),
- tìm literal secret (`SNMP-COMMUNITY-STRING-7f3a9c`, `10.10.20.21`) lọt vào kết quả khi role **không** được phép đọc field tương ứng (SR-1/SR-2),
- role không xác định mà vẫn nhận dữ liệu (SR-2),
- exception / giá trị không phải `list` (SR-4),
- kết quả alias vào fixture (mutate kết quả rồi so lại `data`).

```
$ python3 /tmp/adversarial_probe.py
keys probed         : 80
role variants       : 10
calls               : 800
crashes / non-lists : none
leaks (SR-1/2/3)    : none
aliasing / mutation : none
RESULT              : PASS
```

Ghi chú trung thực: phiên bản probe đầu tiên báo `RESULT: FAIL` với 12 dòng "literal leak". Kiểm tra lại thì đây là **false positive của chính probe**: nó cờ literal `10.10.20.21` khi `operator`/`admin` đọc `managementIpAddress`, và cờ `SNMP-COMMUNITY-STRING-7f3a9c` khi `admin` đọc `apiKey` — tức là các quyền **đúng** theo `POLICY`. Đã sửa probe thành "policy-aware" (chỉ coi là rò rỉ khi role không nằm trong allow-list của field sở hữu literal) và chạy lại ⇒ `PASS`. Bản ghi cả hai lần chạy ở đây để người duyệt thấy rõ quá trình, không giấu lỗi.

### 8.4 Kiểm chứng độc lập #2 — quét rò rỉ theo chính sách (240 lượt gọi)

```
$ (script quét 80 key × 3 role = 240 lượt, kiểm tra field bị hạn chế + literal secret)
policy-aware leak scan over 240 calls: NO LEAK
```

### 8.5 Kiểm chứng #3 — ba file được bảo vệ không bị đụng tới

```
$ git diff --stat -- policy.py test_data.py security-requirements.md
(không có output)
$ git status --short
 M recursive_json_search.py
 M test_json_search.py
```

---

## 9. Kết luận phiên làm việc

- **Số test đã hiện thực: 22** (3 baseline bắt buộc + 19 bảo mật/chức năng; vượt yêu cầu “ít nhất 3 security test”).
- **Số vòng sửa/làm lại: 1** (một lần chạy đỏ ở `test_nested_matches_are_aggregated` do kỳ vọng thiếu match thứ 4 của `message`; đã sửa kỳ vọng và chạy lại xanh).
- **Lệnh kiểm chứng:** `python3 -m unittest -v test_json_search.py`
- **Kết quả cuối:** `Ran 22 tests in 0.004s` / `OK` (exit code 0).
- Không sửa `policy.py`, `test_data.py`, `security-requirements.md`; không chạy lệnh git nào làm đổi trạng thái repo; không tạo file nào ngoài thư mục `unittest/` (probe nằm ở `/tmp`).
- Việc commit do người duyệt thực hiện (agent dừng ở đây và báo cáo).

---

## Vong 2 - Rework theo review cua nguoi kiem duyet

**Ngay:** 2026-09-23 · **Nguoi yeu cau:** nguoi kiem duyet (human reviewer) · **Trang thai:** da sua xong, 24/24 test xanh.
**Luu y pham vi:** muc nay thay the cac ket luan mau thuan o §6, §8, §9 (cac muc do ghi lai vong 1 voi contract "list gia tri tho" va 22 test - nay da doi theo review).

### 10.1 Nguyen van feedback cua nguoi kiem duyet

```text
REVIEW FEEDBACK from the human reviewer - CHANGES REQUESTED. You are still in the sandbox: do NOT run any state-changing git command (no commit / add / checkout / branch / stash / reset / restore / clean / merge).

BLOCKING ISSUE - return contract violation.

Your implementation returns a list of raw VALUES:
    json_search("apiKey", data, role="admin")          ->  ['SNMP-COMMUNITY-STRING-7f3a9c']
    json_search("issueSummary", data, role="viewer")   ->  ['Network Device 10.10.20.82 Is Unreachable From Controller']

The specification for this function is: "json_search(key, input_object) ... tra ve list cac cap key/value" - the reference implementation appends `temp = {k: v}`. Every match MUST therefore be a single-entry dict keyed by the searched key:
    json_search("apiKey", data, role="admin")          ->  [{'apiKey': 'SNMP-COMMUNITY-STRING-7f3a9c'}]
    json_search("issueSummary", data, role="viewer")   ->  [{'issueSummary': 'Network Device 10.10.20.82 Is Unreachable From Controller'}]

Your test suite asserts the wrong shape (for example `assertEqual(json_search("apiKey", data, role="admin"), [SECRET_API_KEY])`), which is why 22/22 tests passed. Fix the tests - do not weaken them.

REQUIRED CHANGES:
1. json_search() must return a list in which EVERY element is a single-entry dict {key: value} (one entry per match), preserving document order, aggregation at every depth, and all current behaviour.
2. Keep every security property intact: role allow-list (SR-1), fail-closed for role=None/unknown roles (SR-2), recursive redaction so that a parent-key query never leaks restricted children and restricted subtrees are never traversed (SR-3), never raises and always returns a list (SR-4), never mutates the input.
3. Update the test suite so that all assertions check the key/value-pair shape, and ADD at least one test that pins the contract explicitly: every element is a dict with exactly one entry whose key is the searched key.
4. Re-run `python3 -m unittest -v test_json_search.py` until everything passes.
5. Append a new section "## Vong 2 - Rework theo review cua nguoi kiem duyet" to AGENT-LOG.md: quote this feedback, describe exactly what you changed, and paste the final test output.
6. FINAL ANSWER: what you changed, the number of test cases, the number of rework rounds in total, and the final test result line.
```

### 10.2 Da thay doi chinh xac nhung gi

**(1) `recursive_json_search.py` - sua contract tra ve (1 dong logic + docstring):**

| | Truoc (vong 1) | Sau (vong 2) |
|---|---|---|
| Dong append trong `_search()` | `results.append(_redact(value, role))` | `results.append({field: _redact(value, role)})` |
| Ket qua `json_search("apiKey", data, role="admin")` | `['SNMP-COMMUNITY-STRING-7f3a9c']` | `[{'apiKey': 'SNMP-COMMUNITY-STRING-7f3a9c'}]` |
| Ket qua `json_search("issueSummary", data, role="viewer")` | `['Network Device 10.10.20.82 Is Unreachable From Controller']` | `[{'issueSummary': 'Network Device 10.10.20.82 Is Unreachable From Controller'}]` |

- `field` chinh la ten field khop (theo dinh nghia match thi `field == key`), dung nhu reference `temp = {k: v}; ret_val.append(temp)`.
- Docstring module va `:return:` cua `json_search()` da cap nhat de ghi ro contract moi (kem vi du).
- **Khong thay doi bat ky logic bao mat nao:** `_may_read()` (allowlist SR-1), short-circuit fail-closed cho `role=None`/role la (SR-2), `_redact()` de quy + khong di vao cay con bi han che (SR-3), luon tra `list` va bat `RecursionError` (SR-4), khong mutate input. Chi doi "hop dung" cua moi match tu `value` sang `{field: value}`.
- Thu tu tai lieu duoc giu nguyen (dict Python giu thu tu chen) → document order khong doi.

**(2) `test_json_search.py` - cap nhat toan bo assertion sang shape moi (khong noi long test):**

- Them helper `assertKeyValuePairs(result, searched_key)`: khang dinh `result` la `list`, moi phan tu la `dict`, `len(item) == 1`, va key duy nhat dung bang key duoc tim (`list(item.keys()) == [searched_key]`); helper tra ve danh sach value de cac assertion ve gia tri van duoc giu nguyen do chat.
- Viet lai assertion cua ca 22 test cu sang dang cap key/value qua helper.
- Mot so cho con **chat hon** vi du: doc bi tu choi phai bang dung `[]` (khong co wrapper rong), doc duoc phep phai dung shape `[{key: value}]`, va `test_policy_allow_list_is_enforced_for_every_field` goi helper cho moi truong hop duoc phep.
- **Them 2 test moi khoa contract:**
  - `test_every_match_is_a_single_entry_key_value_pair`: 10 key × 3 role tren `test_data`, moi phan tu la dict dung 1 entry keyed by key duoc tim; dong thoi kiem tra khong mat du lieu (`message` → 4, `steps` → 3, `errorCode` → 2) va role fail-closed (`None`, `"root"`, `"Admin"`) tra `[]`.
  - `test_pair_contract_on_synthetic_payload`: payload tong hop khong phu thuoc fixture, phu moi do sau, gom ca value `[]`, `None`, dict con; kiem tra ca truong hop key bi han che voi role duoc phep va role khong xac dinh.
- Cap nhat docstring module: ghi ro contract, danh sach test (**24 test**).

**(3) `AGENT-LOG.md`:** them muc nay (10.1-10.5).

**(4) Khong doi** `policy.py`, `test_data.py`, `security-requirements.md`.

### 10.3 Kiem chung lai sau rework

Tai hien dung 2 vi du cua nguoi kiem duyet:

```
$ python3 (goi truc tiep json_search tren test_data)
apiKey / admin          -> [{'apiKey': 'SNMP-COMMUNITY-STRING-7f3a9c'}]
issueSummary / viewer   -> [{'issueSummary': 'Network Device 10.10.20.82 Is Unreachable From Controller'}]
apiKey / operator       -> []
issueSummary / no role  -> []
message / viewer (len)  -> 4
steps / viewer          -> [{'steps': []}, {'steps': []}, {'steps': []}]
deviceDetails / viewer  -> dict con da redact (khong co apiKey, khong co managementIpAddress)
```

Probe doi khang doc lap (ban vong 2, pair-aware: kiem tra luon contract tren tung ket qua):

```
$ python3 /tmp/adversarial_probe_r2.py
keys probed         : 80
role variants       : 10
calls               : 800
crashes / non-lists : none
contract violations : none
leaks (SR-1/2/3)    : none
aliasing / mutation : none
RESULT              : PASS
```

Ba file duoc bao ve khong bi dung toi:

```
$ git diff --stat -- policy.py test_data.py security-requirements.md
(khong co output)
$ git status --short
 M recursive_json_search.py
 M test_json_search.py
?? AGENT-LOG.md
```

### 10.4 Output cuoi cua lenh kiem chung (vong 2)

Command:

```
python3 -m unittest -v test_json_search.py
```

Output day du (exit code = 0):

```
test_admin_can_read_api_key (test_json_search.json_search_test.test_admin_can_read_api_key)
SR-1: admin is allowed to read the apiKey credential. ... ok
test_admin_can_read_management_ip (test_json_search.json_search_test.test_admin_can_read_management_ip)
SR-1: admin is allowed to read managementIpAddress. ... ok
test_empty_list_values_are_not_dropped (test_json_search.json_search_test.test_empty_list_values_are_not_dropped)
SR-5: falsy matches such as ``[]`` are real matches and must be kept. ... ok
test_every_match_is_a_single_entry_key_value_pair (test_json_search.json_search_test.test_every_match_is_a_single_entry_key_value_pair)
Contract: every element is a dict of exactly one entry keyed by the key. ... ok
test_is_a_list (test_json_search.json_search_test.test_is_a_list)
SR-4: every call returns a list, whatever the key, the data or the role. ... ok
test_nested_matches_are_aggregated (test_json_search.json_search_test.test_nested_matches_are_aggregated)
SR-5: matches at different depths/lists are aggregated, not dropped. ... ok
test_no_role_cannot_read_secret (test_json_search.json_search_test.test_no_role_cannot_read_secret)
SR-2: omitting the role (role=None) returns no protected field at all. ... ok
test_non_policy_field_is_readable_by_valid_roles (test_json_search.json_search_test.test_non_policy_field_is_readable_by_valid_roles)
§7: fields absent from POLICY stay readable for every valid role. ... ok
test_operator_can_read_management_ip (test_json_search.json_search_test.test_operator_can_read_management_ip)
SR-1: operator is allowed to read managementIpAddress. ... ok
test_operator_cannot_read_api_key (test_json_search.json_search_test.test_operator_cannot_read_api_key)
SR-1: operator is NOT allowed to read the apiKey credential. ... ok
test_pair_contract_on_synthetic_payload (test_json_search.json_search_test.test_pair_contract_on_synthetic_payload)
Contract: shape holds on synthetic data, at every depth, for any role. ... ok
test_parent_key_does_not_leak_secret (test_json_search.json_search_test.test_parent_key_does_not_leak_secret)
SR-3: querying a parent key never returns restricted children. ... ok
test_policy_allow_list_is_enforced_for_every_field (test_json_search.json_search_test.test_policy_allow_list_is_enforced_for_every_field)
SR-1: for every protected field and every role, access == POLICY allow-list. ... ok
test_policy_matches_security_spec (test_json_search.json_search_test.test_policy_matches_security_spec)
The POLICY table must still match the allow-lists of the security spec. ... ok
test_redaction_applies_at_every_depth (test_json_search.json_search_test.test_redaction_applies_at_every_depth)
SR-3: a whole container returned to a viewer is sanitised recursively. ... ok
test_redaction_does_not_mutate_input (test_json_search.json_search_test.test_redaction_does_not_mutate_input)
The caller's data store and the returned objects must stay independent. ... ok
test_restricted_subtree_is_not_traversed (test_json_search.json_search_test.test_restricted_subtree_is_not_traversed)
SR-3: no side-door into a restricted subtree through a child key. ... ok
test_search_found (test_json_search.json_search_test.test_search_found)
SR-5: an allowed key must be found and returned as {key: value} once. ... ok
test_search_not_found (test_json_search.json_search_test.test_search_not_found)
SR-4: a key that does not exist returns an empty list, without raising. ... ok
test_unknown_role_is_rejected (test_json_search.json_search_test.test_unknown_role_is_rejected)
SR-2/T3: an unknown, malformed or non-string role is refused entirely. ... ok
test_unusual_input_never_crashes (test_json_search.json_search_test.test_unusual_input_never_crashes)
SR-4/T5: malformed, hostile or cyclic input never raises and returns a list. ... ok
test_viewer_can_read_issue_summary (test_json_search.json_search_test.test_viewer_can_read_issue_summary)
SR-1: viewer is allowed to read issueSummary. ... ok
test_viewer_cannot_read_management_ip (test_json_search.json_search_test.test_viewer_cannot_read_management_ip)
SR-1: viewer is NOT allowed to read managementIpAddress. ... ok
test_wrong_role_cannot_read_secret (test_json_search.json_search_test.test_wrong_role_cannot_read_secret)
SR-1/T3: a wrong or self-declared privileged role never leaks the secret. ... ok

----------------------------------------------------------------------
Ran 24 tests in 0.006s

OK
```

### 10.5 Tong ket vong 2

| Muc | Gia tri |
|---|---|
| Contract tra ve | `list` cac cap `{key: value}` (moi match 1 dict 1 entry) |
| So test | **24** (22 cu da cap nhat + 2 test khoa contract moi) |
| Ket qua lan chay dau cua vong 2 | `Ran 24 tests in 0.006s` / `OK` - khong phat sinh loi nao phai sua them |
| So vong rework luy ke | **2** (vong 1: sua ky vong `message`; vong 2: rework contract theo review) |
| Dong ket qua cuoi | `OK` (`Ran 24 tests in 0.006s`) |

### 10.6 Bang chung them: mutation test (chung toi khong "lam yeu" test)

De khong chi tin vao ket qua OK, toi sao chep source sang `/tmp/mutcheck` (repo khong bi cham soc) roi co tinh lam hong implementation:

| Mutation | Ky vong | Ket qua thuc te |
|---|---|---|
| **A** - dao ve contract cu (append gia tri tho, dung loi ma nguoi duyet chi ra) | Test phai DO | `FAILED (failures=91, errors=2)` - toan bo test hinh dang + gia tri bat loi, gom ca `test_every_match_is_a_single_entry_key_value_pair` |
| **B** - tat fail-closed (`FAIL_CLOSED_FOR_UNKNOWN_ROLE = False`) | Security test phai DO | `FAILED (failures=11)` - `test_unknown_role_is_rejected` bat du 11 bien the role la |
| Khong mutation (ban giao noi) | Phai XANH | `Ran 24 tests in 0.006s` / `OK`, exit code 0 |

=> Contract moi that su duoc kiem choat boi test (khong chi pass vi ca test cung ky vong sai nhu vong 1), va cac rang buoc bao mat van con that.
Hai ERROR con lai o mutation A la do test truy cap `result[0][key]` cua kieu du lieu sai - van duoc tinh la that bai, khong phai bo qua.

Luu y ve do tin cay: ba lan chay lien tiep cho ra cung output, chi khac dong thoi gian (`0.006s` / `0.005s`); khong co test nao phu thuoc thu tu chay, nho `tearDown()` doi chieu `_PRISTINE_DATA` sau moi test.

### 10.7 Cap nhat nho trong cung vong 2 (khong phai sua loi)

- Sau khi chay mutation A, toi thay helper bao loi bang `KeyError` (kho doc). Da cau truc lai `assertKeyValuePairs()` de ghi nhan vi pham hinh dang bang assertion that (FAIL sach) thay vi crash khi trich xuat gia tri. Chi la cai thien chan doan, khong noi long bat ky assertion nao; ket qua suite sau khi doi van `OK` (24 test).
