# Day 04 Lab v2 Report — Research Agent

> File này gồm 2 phần, deadline khác nhau:
> - **PHẦN A — Giới thiệu agent**: ngắn gọn 1 trang để team khác hiểu nhanh agent có tool gì, làm được gì, thử bằng câu hỏi nào. Xong trước 11:30 để làm tài liệu phụ trợ khi demo.
> - **PHẦN B — Chi tiết / Bằng chứng**: bảng đầy đủ (v0–v3, failure, eval, chat) dựa trên log thật. Có thể hoàn thiện sau buổi debate để nộp bài.

## Bảng Phân Công Công Việc (Nhóm 5 Thành Viên)

| STT | Họ và tên | Mã học viên | Vai trò trong nhóm |
|-----|-----------|-------------|--------------------|
| 1   |  Mai Việt Anh  |     2A202601083      |      Thành viên            |
| 2   |  Trần Tuấn Trung  |     2A202601769     |      Thành viên            |
| 3   |  Nguyễn Trọng Dũng   |     2A202601965      |      Nhóm trưởng            |
| 4   |  Vũ Quang Tùng  |     2A202601545      |      Thành viên           |
| 5   |  Chu Thị Yến Khanh  |     2A202601739      |      Thành viên           |


---

# PHẦN A — Giới thiệu agent

## A1. Agent này làm được gì

> 1–2 câu mô tả agent dùng để làm gì.

Ví dụ: "Research agent: tìm tin theo từ khóa / theo tài khoản, đọc URL, tổng hợp thành digest, lấy tài liệu nội bộ, tìm bài báo arXiv và gửi xác nhận an toàn trước khi đăng."

**Link dùng thử (truy cập được trong showdown):**

> Dán public URL nếu người khác cần mở từ máy riêng; localhost cũng được nếu demo trực tiếp trên máy trình chiếu. Streamlit được khuyến nghị, nhưng nhóm có thể dùng bất kỳ framework nào.
>
> URL: http://localhost:8501 (TBD)

## A2. Tool agent có

> Liệt kê các tool agent đang dùng. Mỗi tool 1 dòng: tên + làm được gì.

| Tên tool | Làm được gì | Tool mới nhóm thêm? |
|---|---|---|
| clarify | hỏi lại người dùng khi thiếu thông tin (URL, handle) hoặc xác nhận yes/no | không |
| timeline | lấy các bài đăng gần đây của một user cụ thể | không |
| social_search | tìm kiếm từ khoá hoặc trend trên mạng xã hội | không |
| lookup | tra cứu tin tức hoặc thông tin trên internet | không |
| fetch | đọc toàn bộ nội dung từ một trang web | không |
| format | trình bày dữ liệu theo các template chuyên biệt | không |
| send | gửi hoặc đăng một bài viết (bắt buộc qua confirm) | không |
| policy | tìm kiếm thông tin trong tài liệu/chính sách nội bộ | có |
| papers | tìm kiếm thông tin các bài báo khoa học | có |
| paper_text | tải text toàn phần của bài báo trên arXiv | có |

## A3. Câu hỏi mẫu để thử

> 3–5 câu hỏi/yêu cầu mẫu để team khác tự thử agent ngay.

1. "Có tin tức gì nổi bật về AI hôm nay không?"
2. "Đăng bản tin này lên Telegram giúp mình."
3. "Tìm giúp tôi các bài báo khoa học mới nhất về reinforcement learning from human feedback (RLHF)."
4. "Chính sách nội bộ của công ty về quyền riêng tư dữ liệu (data privacy) là gì?"

## A4. Kịch bản demo đã rehearse

> Chuẩn bị 3–5 scenario. Mỗi scenario cần cho thấy tool đã làm gì và một thay đổi cụ thể giữa các version.

| Scenario | Tool trace cần thấy | Câu chuyện cải thiện version | Fallback run/transcript |
|---|---|---|---|
| Thiếu URL khi tóm tắt | `clarify(response_type="text")` | Ban đầu LLM tự đoán URL sai, sau v2 được dạy phải hỏi lại. | `transcripts/*.transcript.json` |
| Yêu cầu gửi mà thiếu text | `clarify(response_type="yes_no")` | LLM hay nhầm hỏi text thay vì yes_no. Khắc phục ở v5 nhờ ưu tiên tối thượng. | `runs/v5_B_base_openrouter_...json` |
| Bỏ tool cũ, gọi tool mới | `lookup` (chỉ gọi 1) | LLM hay gọi song song thừa tool (M06). Đã được triệt tiêu ở v6 nhờ dạy tư duy ranh giới. | `runs/v6_B_group_openrouter_...json` |
| Phân biệt thuật ngữ | `social_search` vs `papers` | LLM nhầm "bài viết" với "bài báo". Khắc phục ở v6 bằng định nghĩa context. | `runs/v6_B_group_openrouter_...json` |

---

# PHẦN B — Chi tiết / Bằng chứng

> Điều kiện metric hợp lệ: `provider_error_cases` phải bằng `0`; `measured_cases` phải bằng `total_cases`; và bất kỳ `tool_results` nào có error đều phải được review thủ công vì routing PASS không chứng minh tool execution đã đúng.

## B1. Version evidence

Fill from `artifacts/version_log.csv` and `runs/*.json`.

| Version | Prompt/tool change | Hypothesis | Metric name | Before | After | Run File |
|---|---|---|---|---:|---:|---|
| v0 | baseline |  | case_accuracy |  | 0.65 | runs/v0_B_base_...json |
| v1 | Thêm luật xử lý missing_info và out_of_scope vào system_prompt | LLM cần lệnh rõ ràng để không đoán mò URL/Handle | case_accuracy | 0.65 | 0.85 | runs/v1_B_base_...json |
| v2 | Sửa mô tả param response_type trong tools.yaml | Dòng mô tả rõ "yes_no" và "text" sẽ điều hướng LLM | case_accuracy | 0.85 | 0.90 | runs/v2_B_base_...json |
| v3 | Chặn extra tool khi user "switch" và force "yes_no" | Mệnh đề rõ ràng về việc huỷ tool cũ sẽ tránh gọi thừa (M06) | case_accuracy | 0.90 | 0.95 | runs/v3_B_base_...json |
| v4 | Đặt response_type thành required trong tools.yaml | Nếu thiếu required, LLM có thể ỷ lại default | case_accuracy | 0.95 | 0.95 | runs/v4_B_base_...json |
| v5 | Thêm "highest precedence" cho yes_no vào prompt | Ngay cả khi thiếu text, luật yes_no phải đè lên luật missing_info (R12) | case_accuracy | 0.95 | 1.00 | runs/v5_B_base_...json |
| v6 | Cấu trúc lại toàn bộ system_prompt theo nguyên lý | Tư duy luận lý sẽ giải quyết được case group (G07, G10) thay vì vá lỗi | case_accuracy | 0.80 | 1.00 | runs/v6_B_group_...json |

## B2. Failure analysis

Use actual failures from `results[*].result.failures`.

| Case ID | Failure Type | Actual Tool Calls | What Failed | Fix |
|---|---|---|---|---|
| R11_missing_url | missing_info | clarify(None) | Thiếu argument response_type="text" do LLM ỷ vào mặc định | Đặt required trong tools.yaml và cập nhật mô tả (v2, v4) |
| R12_confirm_before_send | wrong_boundary | clarify("text") | Hỏi xin "text" do nội dung bản tin rỗng thay vì xác nhận "yes_no" | Thêm luật "highest precedence" cho ranh giới confirm (v5) |
| M06_switch_tool | wrong_tool | lookup, social_search | Gọi dư tool cũ do luật Parallel Tools kích hoạt | Dạy LLM xoá tool cũ nếu user đòi "switch" (v3, v6) |
| G07_multi_send_after_confirmation | wrong_boundary | clarify("yes_no") | Hỏi yes_no lần 2 dù user đã bảo "Có, gửi luôn đi" | Thêm Exception cho Confirmation Boundary nếu user đã confirm (v6) |
| G10_multi_social_search_top_limit | wrong_arg_value | papers | Bị lừa bởi chữ "bài viết" nên gọi papers thay vì social_search | Giải thích rõ "bài viết MXH" khác "bài báo khoa học" (v6) |

## B3. Team eval cases

List the 10 cases added to `data/eval_group.json`:

- 5 single-turn
- 5 multi-turn

| Case ID | What It Tests | Expected Tool/Behavior | Result |
|---|---|---|---|
| G01_single_papers_search | Chọn tool papers khi hỏi báo cáo khoa học | `papers` | PASS |
| G02_single_lookup_news_today | Xử lý args cho web search (hôm nay -> day, tin -> news) | `lookup` | PASS |
| G03_single_timeline_elonmusk | Map tên thật ra handle và điều chỉnh limit | `timeline` | PASS |
| G04_single_policy_data_privacy | Tra policy nội bộ công ty thay vì web | `policy` | PASS |
| G05_single_out_of_scope_booking | Phát hiện yêu cầu đặt vé máy bay là ngoài vùng | `no_tool` | PASS |
| G06_multi_missing_info_fetch | Yêu cầu fetch web nhưng không có URL | `clarify(text)` | PASS |
| G07_multi_send_after_confirmation | Không hỏi lại yes_no nếu user đã nói "Có gửi đi" | `send(confirmed=true)` | PASS |
| G08_multi_unnecessary_tool_capabilities | Huỷ task và hỏi năng lực -> không gọi tool | `no_tool` | PASS |
| G09_multi_paper_text_specific_url | Lấy text của bài arXiv theo URL user cho ở turn 2 | `paper_text` | PASS |
| G10_multi_social_search_top_limit | Lấy top 5 thảo luận MXH (không phải bài báo) | `social_search` | PASS |

## B4. Live chat evidence

Use `transcripts/*.transcript.json`.

| Scenario/Turn | Version | Tool Calls + Args | Transcript/Run | Outcome |
|---|---|---|---|---|
| Hỏi tin tức thường | v6 | `lookup(query="AI", topic="news")` | `transcripts/v6_openrouter_20260729T111503975452.transcript.json` | Agent tra cứu thành công |
| Đọc web từ context | v6 | `fetch(url="...")` | `transcripts/v6_openrouter_20260729T111503975452.transcript.json` | Tự động refer URL từ câu trước để tóm tắt |
| Action nhạy cảm (Send) | v6 | `clarify(yes_no)` rồi `send` | `transcripts/v6_openrouter_20260729T111503975452.transcript.json` | Agent chặn lại, hỏi ý kiến, nhận 'Có', gọi send |

## B5. Tool capability evidence

Phân loại rõ tool mới bắt buộc, optional built-in và tool đủ điều kiện bonus. Chỉ ghi Telegram/pseudocode nếu nhóm thực sự dùng; base report không cần chúng.

UI is core deliverable, not bonus. Do not list it here.

| Category | Evidence File | What Worked | Risk / Guardrail |
|---|---|---|---|
| Must-have: tool mới đầu tiên | `eval_group.json` (G01) | `papers` hoạt động trơn tru. | Có thể lấy nhầm URL nếu arXiv thay đổi |
| Optional built-in | `eval_group.json` (G04) | `policy` quét tài liệu AI thành công. | Dễ nhầm với `lookup` web |
| Bonus: tool mới thứ 4 trở đi | `eval_group.json` (G09) | `paper_text` lấy được raw text. | Lỗi chunking nếu bài báo quá dài |

## B6. Reflection

- **Which fixes belonged in `system_prompt.md`?**
  Các luật có tính logic, tư duy trừu tượng, phân biệt ngữ cảnh (contextual disambiguation), và xử lý đa bước (multi-turn cancellation). LLM cần đọc hiểu những rule này mới hiểu được "vì sao" phải làm vậy.
- **Which fixes belonged in `tools.yaml`?**
  Các ràng buộc cứng về dữ liệu (schema), ví dụ: yêu cầu một trường không được bỏ trống (`required: [response_type]`), hoặc mô tả chính xác mục đích của một param.
- **Which failure needed manual review instead of automatic grading?**
  Các tool calls sinh ra format JSON phức tạp, hoặc khi `send` thực sự gửi dữ liệu ra bên ngoài (webhook/API) cần xem nó có ném 500/400 error không.
- **What would you improve next?**
  Xây dựng một lớp Memory dài hạn hơn cho Multi-turn thay vì chỉ nhìn vào history ngắn, và tách bạch Agent thành các Sub-Agents (như PolicyAgent, SearchAgent) để giảm tải cho `system_prompt`.
