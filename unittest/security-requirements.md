# Security Requirements & Threat Model — `json_search()`

> Tài liệu này là đầu vào (input) cho security test ở `test_json_search.py`.
> Framework dùng để phân tích: **STRIDE**.

## 1. Bối cảnh sử dụng

`json_search(key, input_object, role=None)` là hàm thư viện dùng để tra cứu **đệ quy**
các cặp `key/value` bên trong một JSON object lồng nhiều cấp. Dữ liệu điển hình là
payload trả về từ API giám sát hạ tầng mạng (xem `test_data.py`: một bản ghi sự cố
`issueSummary = "Network Device 10.10.20.82 Is Unreachable From Controller"` kèm
thông tin chi tiết về thiết bị mạng).

Hàm này phục vụ **nhiều loại người dùng khác nhau** (admin, operator, viewer) nên
kết quả trả về phải phụ thuộc vào **vai trò (role)** của người gọi.

## 2. Actor / Role và mục đích gọi hàm (a)

| Actor / Role | Mục đích gọi `json_search()` | Được phép đọc giá trị của |
|---|---|---|
| `viewer` | Xem tình trạng sự cố để theo dõi vận hành (read-only, mức thấp nhất) | `issueSummary` |
| `operator` | Xử lý sự cố: cần thêm địa chỉ quản trị của thiết bị để thao tác | `issueSummary`, `managementIpAddress` |
| `admin` | Quản trị hạ tầng: cần cả thông tin xác thực thiết bị để cấu hình lại | `issueSummary`, `managementIpAddress`, `apiKey` |
| **không xác định** (`role=None`) | Không có phiên làm việc hợp lệ | **không đọc được trường nào nằm trong `POLICY`** |
| **threat actor** (ngoài ý định thiết kế) | Viewer/operator/kẻ tấn công tìm cách đọc vượt quyền | — (đây là đối tượng của threat model) |

Nguồn quyết định quyền: `POLICY` trong `policy.py` (allowlist theo từng trường):

```python
POLICY = {
    "apiKey": ["admin"],
    "managementIpAddress": ["admin", "operator"],
    "issueSummary": ["admin", "operator", "viewer"],
}
```

## 3. Asset nhạy cảm có thể xuất hiện trong dữ liệu trả về (b)

| Asset | Vị trí trong `test_data.py` | Vì sao nhạy cảm |
|---|---|---|
| `apiKey` | `...connectedDevice[0].deviceDetails.apiKey` = `SNMP-COMMUNITY-STRING-7f3a9c` | Là **thông tin xác thực** (community string SNMP) dùng để quản trị thiết bị mạng. Lộ khoá ⇒ kẻ tấn công đọc/ghi cấu hình thiết bị ⇒ chiếm quyền quản trị hạ tầng. |
| `managementIpAddress` | `...deviceDetails.managementIpAddress` = `10.10.20.21` | Địa chỉ quản trị: cho phép trinh sát và tấn công trực tiếp vào thiết bị; kèm `actualServiceId = 10.10.20.82`. |
| Thông tin định danh thiết bị | `serialNumber`, `macAddress`, `instanceUuid`, `hostname`, `platformId` | Nhận dạng duy nhất thiết bị; hỗ trợ dò quét, giả mạo, tra cứu ngoài luồng. |
| Thông tin vận hành nội bộ | `issueSummary`, `issueDescription`, `impactedHosts.location` | Lộ topology/mức độ ảnh hưởng của hạ tầng (thấp hơn nhưng vẫn là dữ liệu nội bộ). |

## 4. Trust boundary (c)

1. **Boundary #1 — Caller → `json_search()`.** Ranh giới tin cậy quan trọng nhất của
   bài toán: dữ liệu đã ở trong bộ nhớ của tiến trình, nhưng **quyền được phép đọc
   lại phụ thuộc vào `role` của caller**.
2. **Boundary #2 — `json_search()` → nguồn JSON/API giám sát.** Hàm tin tưởng cấu
   trúc dữ liệu đầu vào.

**Trust boundary bị bỏ qua:** nếu hàm **không kiểm tra `role` trước khi trả kết quả**,
thì mọi caller — kể cả `viewer` hoặc caller không xác thực — đều đọc được toàn bộ
trường, bao gồm `apiKey`. Việc xác thực/phân quyền ở tầng trên (web API, CLI) **không
thay thế** được kiểm tra bên trong hàm, vì `json_search()` là điểm vào dùng chung của
thư viện và có thể bị gọi trực tiếp (ví dụ: từ một module khác, từ REPL, từ test).

## 5. Threat model (STRIDE) (d)

| # | Nhóm STRIDE | Threat | Asset bị ảnh hưởng | Biện pháp giảm thiểu |
|---|---|---|---|---|
| T1 | **Information Disclosure** | `viewer` (hoặc caller không có quyền) gọi `json_search("apiKey", data)` và nhận về SNMP community string ⇒ lộ bí mật thiết bị | `apiKey` | Allowlist theo `POLICY` trước khi append kết quả |
| T2 | **Information Disclosure** | Caller **bỏ qua tham số `role`** (`role=None`) để bypass kiểm soát truy cập ⇒ lấy trọn dữ liệu nhạy cảm | mọi trường trong `POLICY` | **Fail-closed**: `role=None`/role không hợp lệ ⇒ không trả về trường nằm trong `POLICY` |
| T3 | **Elevation of Privilege** | `operator`/`viewer` tự khai `role="admin"` và được tin tưởng tuyệt đối (client-side trust) ⇒ nâng quyền đọc secret | `apiKey`, `managementIpAddress` | Hàm chỉ nhận `role` **đã được xác thực ở tầng server**; tài liệu hoá yêu cầu này và kiểm thử rằng role lạ bị từ chối |
| T4 | **Information Disclosure** (bypass theo key cha) | `viewer` không hỏi thẳng `apiKey` mà hỏi **key cha** (`deviceDetails`, `connectedDevice`) ⇒ nhận về cả cây con chứa `apiKey` | `apiKey` nằm sâu trong cây con | **Lọc (redaction) đệ quy** mọi trường trong `POLICY` mà role không được phép, ở mọi độ sâu của kết quả |
| T5 | **Tampering / DoS** | Dữ liệu JSON dị dạng (kiểu lạ, nhánh lồng sâu) làm hàm crash hoặc đệ quy vô hạn ⇒ treo dịch vụ | Availability | Luôn trả về `list`, không crash với kiểu dữ liệu bất thường; ghi nhận giới hạn độ sâu đệ quy là khuyến nghị mở rộng |
| T6 | **Repudiation** | Không có vết log khi một role bị từ chối truy cập trường nhạy cảm ⇒ không truy vết được | Auditability | Khuyến nghị log sự kiện từ chối (ngoài phạm vi bài lab) |

**Threat thuộc đúng nhóm yêu cầu:** T1, T2, T4 → *Information Disclosure*;
T3 → *Elevation of Privilege*.

## 6. Security Requirements

| ID | Security Requirement | Threat | Security test tương ứng |
|---|---|---|---|
| SR-1 | Hệ thống **chỉ trả về** giá trị của trường X nếu `role` của caller nằm trong danh sách được phép đọc trường X (`POLICY[X]`). | T1, T3 | `test_wrong_role_cannot_read_secret`, `test_operator_cannot_read_api_key`, `test_admin_can_read_api_key`, `test_viewer_can_read_issue_summary`, `test_viewer_cannot_read_management_ip`, `test_operator_can_read_management_ip` |
| SR-2 | **Fail-closed**: nếu caller không cung cấp `role` (`role=None`) hoặc role không xác định, hàm **không được trả về** bất kỳ trường nào nằm trong `POLICY`. | T2 | `test_no_role_cannot_read_secret` |
| SR-3 | Kết quả trả về **không được chứa** trường bị hạn chế ở **bất kỳ độ sâu nào**, kể cả khi caller truy vấn bằng key cha. | T4 | `test_parent_key_does_not_leak_secret` |
| SR-4 | Hàm **không được crash** với dữ liệu đầu vào bất thường/không tìm thấy key và **luôn trả về một `list`**. | T5 | `test_search_not_found`, `test_is_a_list` |
| SR-5 | (Chức năng) Tìm kiếm đệ quy phải **gộp kết quả ở mọi cấp**, không được bỏ sót giá trị nằm trong dict/list con. | — (đúng chức năng) | `test_search_found`, `test_nested_matches_are_aggregated` |

## 7. Giới hạn còn lại (residual risk)

- Hàm tin tưởng giá trị `role` do caller truyền vào. Việc **xác thực** role phải do
  tầng gọi (server/API gateway) thực hiện; nếu tầng đó bị lỗi thì `json_search()`
  không thể tự phát hiện. Đây là giới hạn thiết kế đã biết (T3).
- `POLICY` chỉ liệt kê 3 trường; các trường còn lại (ví dụ `serialNumber`,
  `macAddress`) được xem là dữ liệu mức vận hành và được phép đọc với mọi role hợp lệ.
  Muốn siết chặt hơn thì cần chuyển sang cơ chế **default-deny** cho toàn bộ trường.
- Chưa giới hạn độ sâu đệ quy (T5) và chưa ghi log từ chối truy cập (T6).
