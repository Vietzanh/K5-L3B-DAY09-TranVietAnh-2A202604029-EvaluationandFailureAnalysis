# Trace case: từ trace tới quyết định sai đầu tiên

Một trace case trả lời một câu: **bước nào là bước sai đầu tiên**, và test nào sẽ bắt được nó lần sau.

```bash
cd src
python -m lab9.trace_case --shape seeded_regression --claim C-014 --seed 11
python -m lab9.trace_case --shape fixed --claim C-014 --seed 11   # đối chứng
```

## Case: `seeded_regression C-014@11` (FM-05 pre_deducted)

| Trường | Nội dung |
|---|---|
| Trial | `seeded_regression C-014@11`, report `reports/eval_seeded_regression.json`, run ID `E-seeded_regression-20261118-0ac4` (eval set `0ac4668070df`) |
| Triệu chứng | Lab 8 grader: FAIL `proposal_mismatch`. `refund_amount_correct` = False: **ledger 90.000 ≠ label 120.000**. `reply_matches_ledger` = False: reply "Dạ, LogiX đã hoàn 120.000đ cho đơn O-515." trong khi ledger chỉ giữ 90.000. |
| Bước sai đầu tiên | **Bước 5 `proposal`** `{"amount_vnd": 120000}` |
| Vì sao là bước *đầu tiên* | Bước 1 `handoff` (đúng contract, đúng tool). Bước 2 `investigator`: đơn O-515 đúng như DB. Bước 3 `quote`: 150.000 (SHIP-LATE-03 + DMG-04), giống hệt `fixed`. Bước 4 `refund_history`: `refunded_vnd = 30000` là dữ liệu đúng (đọc thêm lịch sử chưa phải là lỗi). Đến bước 5, agent tự lấy 150.000 − 30.000 = 120.000 làm đề xuất. Host vốn tự trừ khoản đã hoàn, nên trừ thêm lần nữa → 90.000. |
| Failure mode | **FM-05** pre_deducted. Hệ quả ở bước 6: **FM-08** (reply nói số agent tự tính, không phải số trong ledger). |
| Đối chứng | `fixed C-014@11`: bước 3 `quote` 150.000, **không có** bước `refund_history`/`proposal`. Agent gửi thẳng 150.000, host trừ 30.000 → ledger 120.000 = label; reply "120.000đ" khớp ledger. PASS mọi grader. |
| Regression test | `src/tests/test_lab9_trace_case.py`: `test_lab9_c014_pre_deducted_is_caught` khẳng định trên variant lỗi `proposal_correct`, `refund_amount_correct`, `reply_matches_ledger`, `pass_rate` đều False và bước 5 là `proposal`. `test_lab9_c014_fixed_passes_every_grader` khẳng định `fixed` qua hết. Cả hai đã chạy: **fail đúng trên variant lỗi, pass trên `fixed`** (test xanh trong `pytest -m student -k "lab9 and not advanced"`). |
| Chưa chắc chắn | Trace không ghi lời gọi `issue_refund` (bước của host nằm ngoài trace), nên "host trừ lần hai" là suy từ ledger (90.000 = 120.000 − 30.000) và code `lab8.durability`, không đọc được trực tiếp từ event. Trace cũng không cho biết agent *định* trừ vì hiểu sai chính sách hay vì prompt; với MockLLM thì đây là công tắc `pre_deducted`. |

## Quy tắc

- Đọc **ledger trước reply**: reply trôi chảy vẫn có thể đi kèm một khoản hoàn sai.
- "Bước sai đầu tiên" phải dẫn số event cụ thể, không phải "agent bị nhầm".
- Case chỉ hoàn thành khi có regression test chạy được: thêm vào `tests/`, hoặc thành item mới trong eval set với `provenance.from_trace`. Case này có cả hai: test ở trên, và item E-014 mang `provenance.from_trace = "seeded_regression C-014@11 step 5 proposal"`.
