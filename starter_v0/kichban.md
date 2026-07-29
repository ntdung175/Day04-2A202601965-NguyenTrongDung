# Kịch Bản Thuyết Trình: AI Research Agent (Day 04)

> **Lưu ý cho nhóm:** 
> - Kịch bản này được chia cho 3 Speaker chính. Các bạn có thể linh hoạt thay đổi tuỳ theo số lượng thành viên thực tế.
> - **Nguyên tắc khi demo:** Nói đến đâu, thao tác trên màn hình đến đó. Mở sẵn `http://localhost:8501` (Streamlit app) trước khi thuyết trình.
> - **Mục tiêu:** Thể hiện rõ Agent của chúng ta làm được gì, và hành trình tối ưu từ 65% lên 100% (v1 -> v6) diễn ra như thế nào dựa trên tư duy logic chứ không phải vá lỗi mù quáng.

---

## 🎤 Phần 1: Mở đầu & Giới thiệu Agent (Speaker 1)
**Thời lượng dự kiến:** 2-3 phút
**Thao tác màn hình:** Mở trình duyệt, show giao diện trang chủ Streamlit.

**[Speaker 1]**
"Xin chào ban giám khảo và các nhóm. Mình là `[Tên]`, đại diện cho nhóm trình bày về AI Research Agent của bọn mình.

Mục tiêu cốt lõi của Agent này là hỗ trợ nghiên cứu thông tin một cách chủ động và an toàn. Agent của chúng mình được trang bị **10 tools**, trong đó có 6 tool cơ bản (tìm web, đọc URL, tìm MXH, v.v.) và **4 tool nâng cao do nhóm tự thiết kế**: Tìm chính sách nội bộ (`policy`), Tìm kiếm bài báo khoa học trên arXiv (`papers`), Đọc nội dung PDF bài báo (`paper_text`), và Gửi nội dung (`send`).

Điểm nổi bật nhất của Agent này là tư duy logic đa bước. Nó không chỉ biết gọi tool, mà còn biết **ngừng lại để hỏi thêm thông tin nếu thiếu**, phân biệt được ngữ cảnh (báo khoa học vs báo mạng), và quan trọng nhất: **Tuân thủ nghiêm ngặt ranh giới an toàn** (không bao giờ tự ý gửi/đăng bài nếu chưa được user xác nhận)."

---

## 🎤 Phần 2: Demo Kịch Bản Trực Tiếp (Speaker 2)
**Thời lượng dự kiến:** 4-5 phút
**Thao tác màn hình:** Chuyển sang tab **💬 Live Chat** trên Streamlit, sử dụng các nút "Quick Scenarios" bên thanh công cụ.

**[Speaker 2]**
"Sau đây mình xin phép demo trực tiếp cách Agent hoạt động thông qua giao diện Streamlit mà nhóm đã xây dựng.

**(Thao tác: Bấm nút "Thiếu URL")**
**1. Scenario 1: Khả năng chủ động xin thêm thông tin (Missing Info)**
Giả sử user nói: *'Tóm tắt bài viết này giúp mình'*, nhưng lại quên dán link. Ở phiên bản đầu tiên (v0), Agent hay có xu hướng 'đoán bừa' một URL nào đó. Nhưng hiện tại, như các bạn thấy, nó chủ động gọi hàm `clarify` để hỏi lại: *'Bạn hãy cung cấp URL nhé'*. Sau khi mình nhập link OpenAI, nó mới tiến hành `fetch` và tóm tắt.

**(Thao tác: Bấm nút "Multi-turn Switch")**
**2. Scenario 2: Ranh giới đa bước (Tool Switching)**
Mình yêu cầu tìm tweet của Sam Altman, sau đó đổi ý: *'Thôi bỏ Twitter, tìm web thay đi'*. Nhờ được tối ưu prompt ở version 6, Agent hiểu được khái niệm 'huỷ context cũ', lập tức bỏ qua `timeline` và chỉ gọi đúng tool `lookup`. Không bị dư thừa tool như lỗi M06 ở base.

**(Thao tác: Bấm nút "Gửi an toàn")**
**3. Scenario 3: Ranh giới xác nhận an toàn (Confirmation Boundary)**
Mình gõ: *'Đăng bản tin này lên Telegram'*. Dù bản tin đang trống, Agent thay vì hỏi xin nội dung (text), nó lại ưu tiên việc hỏi xác nhận (yes/no): *'Bạn có chắc chắn muốn đăng không?'*. Đây là rule tối thượng nhóm cài đặt để đảm bảo không một lệnh `send` nào lọt ra ngoài mà không có `confirmed=true`."

---

## 🎤 Phần 3: Phân tích Tối ưu hoá & Đánh giá Đội nhóm (Speaker 3)
**Thời lượng dự kiến:** 4 phút
**Thao tác màn hình:** Chuyển sang tab **📊 Version History** và **🗃️ Run Evidence**.

**[Speaker 3]**
"Vậy làm sao nhóm đạt được sự thông minh đó? Mời mọi người xem biểu đồ Accuracy qua từng phiên bản. Nhóm không chỉ chạy 3 phiên bản như yêu cầu, mà đã thực hiện **6 vòng lặp tối ưu thực sự**, nâng điểm Base Eval từ **65% lên tuyệt đối 100%**.

Chiến lược của nhóm là đi từ 'vá lỗi bằng YAML' sang 'dạy nguyên lý bằng Prompt'. 
Ví dụ điển hình nhất là ở Version 5 và 6, nhóm đối mặt với tập `eval_group.json` gồm 10 case do chính nhóm tự thiết kế để bẫy Agent (như nhầm lẫn giữa 'bài viết MXH' và 'bài báo arXiv'). 

Thay vì viết rule if-else lắt nhắt, nhóm đã đập đi xây lại toàn bộ `system_prompt.md`. Nhóm dạy cho LLM 3 nguyên lý:
1. **Lý luận đa bước:** Biết giữ lại timeframe/topic nhưng biết vứt bỏ tool cũ nếu user đổi ý.
2. **Đọc hiểu ngữ cảnh:** Hiểu 'bài viết MXH' thì dùng `social_search`, còn 'nghiên cứu' thì dùng `papers`.
3. **Ngoại lệ uỷ quyền (Confirmation exception):** Bắt buộc hỏi yes/no trước khi gửi, NHƯNG nếu user đã gõ sẵn chữ 'Gửi luôn đi' trong cùng 1 câu thì phải biết tự hiểu là đã được cấp phép.

Kết quả là bộ Eval Team 10 câu khó nhằn cũng đã **Pass 100%** ngay trong lần chạy v6."

---

## 🎤 Phần 4: Tổng kết & Q&A (Speaker 1 hoặc Cả nhóm)
**Thời lượng dự kiến:** 1-2 phút
**Thao tác màn hình:** Mở trang **📋 Scenarios** cho thấy toàn bộ Pre-demo checklist đều xanh.

**[Speaker 1]**
"Tóm lại, dự án không chỉ hoàn thành việc nối API, mà còn thành công trong việc rèn luyện 'tư duy bảo thủ một cách an toàn' cho LLM. Quá trình chia nhỏ các version giúp nhóm audit được từng tham số một và hiểu rõ LLM đang tư duy sai ở đâu.

Tất cả log JSON, transcript hội thoại và evidence đều đã được push lên GitHub và có thể browse trực tiếp ngay trên app này.

Cảm ơn mọi người đã lắng nghe, nhóm xin sẵn sàng nhận câu hỏi từ ban giám khảo!"
