# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5` (trong `src/`, backend replay, không cần key)

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | **PASS** (exit 0) | **dùng**, chỉ cho giọng văn, không chặn release |
| helpful | 100 | 0.375 | 1.000 | 0.300 | **FAIL** (exit 1) | **loại** |

Ma trận nhầm lẫn (FAIL = lớp dương):
- tone_ok: tp=24, fp=4, fn=6, tn=66. Tỉ lệ FAIL quan sát 0.28 → hiệu chỉnh Rogan-Gladen **0.30**.
- helpful: tp=9, fp=0, fn=21, tn=70. Tỉ lệ FAIL quan sát 0.09 → hiệu chỉnh Rogan-Gladen **0.30**.

## ≥5 case audit thủ công
| # | Case | Judge nói | Người nói | Ai đúng? | Ghi chú / sửa rubric |
|---|---|---|---|---|---|
| 1 | H-008 "Em đã hoàn tiền cho anh rồi nha, anh check giúp em." | PASS | FAIL | **Người** | Xưng "em" + "nha" quá suồng sã với khách khiếu nại. Rubric thêm: *xưng hô phải là "LogiX" – "anh/chị"; "em/bạn/nha" = FAIL.* |
| 2 | H-029 "Dạ, vui lòng chờ. Hệ thống đang xử lý, không cần nhắn thêm." | PASS | FAIL | **Người** | Judge chỉ bắt từ lịch sự ("Dạ, vui lòng") mà bỏ qua giọng ra lệnh. Rubric thêm: *câu mệnh lệnh cấm khách liên hệ = FAIL, dù có "Dạ".* |
| 3 | H-051 "Dạ, LogiX đã refund 90.000đ cho đơn O-202 ạ." | FAIL | PASS | **Người** | Style guide CS LogiX cho phép từ "refund". Rubric thêm: *danh sách từ tiếng Anh được phép (refund, ship, voucher).* |
| 4 | H-042 "Dạ, đơn O-808 đã hoàn 120.000đ. Tiền về trong 3–5 ngày ạ." | FAIL | PASS | **Người** | Judge phạt vì "thiếu xin lỗi". Rubric sửa: *xin lỗi không bắt buộc khi kết quả có lợi cho khách; ngắn mà đủ ý = PASS.* |
| 5 | H-081 "Dạ, đơn O-107 chưa đủ điều kiện hoàn theo chính sách hiện hành ạ." | FAIL | PASS | **Judge** | Ghi chú CSV: người đọc nhầm ticket. **Sửa nhãn người** thành FAIL, không sửa rubric. Đây là lý do mọi bất đồng phải được audit, không mặc định người đúng. |
| 6 | H-063 "Dạ, LogiX đã hoàn 20.000đ và sẽ hoàn thêm cho anh/chị ạ." | PASS | FAIL | **Người** | Hứa "sẽ hoàn thêm" ngoài kết quả hệ thống. Đây không còn là giọng văn mà là nội dung tiền, nên chuyển sang grader code (`reply_matches_ledger`, FM-08), không giao cho judge tone. |
| 7 | H-070 "…đã hoàn 90.000đ cho đơn O-909 ạ 😂😂" | PASS | FAIL | **Người** | Rubric thêm: *emoji trong ngữ cảnh khiếu nại = FAIL.* |
| 8 | HL-015 "Dạ, LogiX đã hoàn 55.000đ cho đơn O-112 ạ." (helpful) | PASS | FAIL (sai tiền, ledger 40.000) | **Người** | Judge không đọc ledger nên không thể biết số tiền sai. 18/21 FN của `helpful` là "sai tiền". Không sửa rubric judge mà **giao cho code**. |

## Kết luận
- **`helpful` bị loại, không dùng làm gate.**
  - Recall 0.30: judge bỏ sót 21/30 reply mà người chấm FAIL.
  - κ 0.375 < 0.6.
  - Precision 1.0 chỉ vì judge hầu như không bao giờ nói FAIL (fp = 0, tp = 9), không phải vì nó giỏi.
  - Nhìn vào ma trận: 18 trong 21 FN là "sai tiền". Judge chỉ đọc text, không thấy ledger, nên **về nguyên tắc** không thể chấm đúng tiêu chí này. 3 FN còn lại là "sai xưng hô", thuộc phần việc của tone judge.
  - Nếu dùng `helpful` làm gate, một PR làm agent nói sai số tiền vẫn xanh. Đó chính là FM-08.
  - Thay thế: tiền chấm bằng `reply_matches_ledger` / `refund_amount_correct` (code), xưng hô chấm bằng `tone_ok`.
- **`tone_ok` dùng được** (κ 0.757, P 0.857, R 0.80) nhưng chỉ ở mức theo dõi, không chặn release:
  - Recall 0.8 nghĩa là vẫn lọt 20% reply sai giọng.
  - Tỉ lệ FAIL thật ước tính 0.30 (Rogan-Gladen), cao hơn mức judge báo (0.28).
- Rủi ro còn lại:
  - Judge chỉ được kiểm trên dữ liệu replay đã công khai, nên số liệu có thể lạc quan. Cần nhãn người mới để có held-out thật.
  - Rubric đã sửa (mục 1–4, 7) phải được calibrate lại trên tập mới trước khi tin.
