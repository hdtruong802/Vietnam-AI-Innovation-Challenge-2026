# Prompt tạo kịch bản video demo VNGov AI Copilot

Bạn là chuyên gia viết kịch bản video demo sản phẩm công nghệ cho cuộc thi AI Innovation Challenge.

Hãy viết kịch bản video demo bằng tiếng Việt cho sản phẩm:

- **Tên sản phẩm:** VNGov AI Copilot
- **Thời lượng tối đa:** dưới 5 phút
- **Thời lượng mục tiêu:** 4 phút 15 giây đến 4 phút 40 giây
- **Đối tượng xem:** Ban giám khảo cuộc thi, đại diện cơ quan nhà nước, chuyên gia AI và người dùng phổ thông
- **Mục tiêu:** Chứng minh sản phẩm giải quyết đúng vấn đề, có MVP hoạt động thật, sử dụng AI đúng chỗ và có cơ chế an toàn đối với thông tin hành chính.

## Bối cảnh sản phẩm

VNGov là trợ lý hướng dẫn và tiền kiểm hồ sơ thủ tục hành chính cho công dân Việt Nam.

Người dùng không cần biết chính xác tên thủ tục. Họ có thể mô tả nhu cầu bằng tiếng Việt tự nhiên. Hệ thống sẽ:

1. Nhận diện thủ tục phù hợp.
2. Hỏi những câu làm rõ ảnh hưởng trực tiếp đến hồ sơ.
3. Tạo checklist giấy tờ theo trường hợp.
4. Giải thích vì sao cần từng giấy tờ và hiển thị nguồn tham khảo.
5. Hiển thị biểu mẫu phù hợp.
6. Chạy kiểm tra deterministic để phát hiện trường thiếu, sai định dạng hoặc mâu thuẫn.
7. Hướng dẫn người dùng sửa trước khi nộp qua kênh chính thức.

MVP hỗ trợ ba thủ tục:

- Đăng ký khai sinh.
- Đăng ký thường trú.
- Đăng ký thành lập hộ kinh doanh.

## Nguyên tắc AI và an toàn

- Đây không phải chatbot pháp luật trả lời tự do.
- AI chỉ dùng để hiểu cách diễn đạt của người dân, hỗ trợ hỏi làm rõ và giải thích kết quả dễ hiểu.
- Checklist, biểu mẫu và kết quả tiền kiểm đến từ procedure pack và rule engine deterministic.
- AI không tự thêm giấy tờ, không tự tạo quy định và không quyết định hồ sơ được cơ quan chấp thuận.
- Mọi hướng dẫn quan trọng phải có nguồn tham khảo.
- Khi dữ liệu chưa đủ, ngoài phạm vi hoặc có rủi ro pháp lý, hệ thống phải dừng và hướng người dùng đến kênh chính thức.
- Dữ liệu dùng trong video là dữ liệu synthetic/demo.
- “Đạt kiểm tra sơ bộ” không đồng nghĩa với hồ sơ được phê duyệt.

## Kịch bản demo chính

Sử dụng “Đăng ký khai sinh” làm tình huống demo xuyên suốt.

Tình huống người dùng:

> Tôi vừa sinh con và muốn chuẩn bị hồ sơ đăng ký khai sinh.

Luồng cần thể hiện:

1. Người dùng truy cập VNGov.
2. Vào chế độ demo mà không cần tạo tài khoản thật.
3. Nhập nhu cầu bằng ngôn ngữ tự nhiên.
4. Hệ thống đề xuất thủ tục Đăng ký khai sinh.
5. Người dùng xác nhận thủ tục.
6. Hệ thống hỏi một số câu làm rõ, ví dụ:
   - Hình thức nộp hồ sơ.
   - Cha mẹ đã đăng ký kết hôn chưa.
   - Ai là người trực tiếp đăng ký.
7. Hiển thị checklist và nguồn tham khảo.
8. Người dùng xác nhận checklist và mở biểu mẫu.
9. Cố tình nhập một dữ liệu sai, ví dụ:
   - Số CCCD không đủ 12 chữ số; hoặc
   - Ngày đăng ký trước ngày sinh của trẻ.
10. Rule engine phát hiện lỗi, chỉ đúng trường và đưa cách sửa.
11. Người dùng sửa dữ liệu và chạy lại tiền kiểm.
12. Hệ thống báo dữ liệu mẫu đã vượt qua kiểm tra sơ bộ, kèm cảnh báo đây không phải quyết định của cơ quan có thẩm quyền.
13. Hiển thị nhanh hai thủ tục còn lại để chứng minh MVP dùng chung một kiến trúc, không phải prototype chỉ có một tình huống.

## Cấu trúc video

Hãy tổ chức video theo nhịp sau:

- **0:00–0:20 — Hook:** nêu vấn đề người dân thường chỉ phát hiện hồ sơ thiếu hoặc sai sau khi đã nộp.
- **0:20–0:45 — Giới thiệu:** VNGov và giá trị cốt lõi.
- **0:45–3:20 — Demo:** trực tiếp luồng Đăng ký khai sinh.
- **3:20–3:45 — Phạm vi MVP:** hiển thị nhanh ba thủ tục.
- **3:45–4:15 — Kiến trúc và an toàn:** giải thích ngắn AI, deterministic rules, citations và fail-closed.
- **4:15–4:35 — Kết:** giá trị triển khai và lời kết.
- Có thể điều chỉnh vài giây nhưng tổng thời lượng tuyệt đối không vượt quá 4 phút 50 giây.

## Yêu cầu về lời thoại

- Tổng lời đọc khoảng 540–610 từ tiếng Việt.
- Giọng tự tin, bình tĩnh, đáng tin cậy và thực dụng.
- Viết để AI voice đọc tự nhiên: câu ngắn, ít mệnh đề, có nhịp nghỉ rõ.
- Không dùng giọng quảng cáo phô trương.
- Không lạm dụng thuật ngữ kỹ thuật.
- Khi phải dùng “deterministic”, hãy giải thích ngay là “kiểm tra theo quy tắc xác định”.
- Không đọc mã nội bộ như U1, U2, U3.
- Không đọc tên biến, endpoint hoặc JSON.
- Không kể lại mọi thao tác chuột; lời nói cần tập trung vào giá trị và lý do của thao tác.
- Khớp chính xác giữa lời đọc và hình ảnh trên màn hình.
- Dành khoảng nghỉ ngắn tại những thời điểm cần để người xem quan sát checklist, citations và finding.
- Kết thúc bằng một câu định vị ngắn, dễ nhớ.

## Các tuyên bố bị cấm

Không được nói hoặc ngụ ý rằng:

- VNGov đã tích hợp chính thức với Cổng Dịch vụ công Quốc gia.
- VNGov có thể tự động nộp hồ sơ.
- VNGov có quyền phê duyệt hoặc bảo đảm hồ sơ được chấp thuận.
- Toàn bộ pháp luật Việt Nam đã được hệ thống hỗ trợ.
- Dữ liệu demo là dữ liệu công dân thật.
- AI tự quyết định giấy tờ hoặc tính hợp lệ của hồ sơ.
- Nội dung đã được K1/pháp lý phê duyệt nếu giao diện demo vẫn hiển thị “Không phải K1” hoặc “Cần cơ quan xem xét”.
- Sản phẩm đã đạt một KPI nếu chưa có evidence tương ứng.

Nếu trạng thái trên giao diện là demo hoặc `official_review_required`, lời thoại phải mô tả đúng là “dữ liệu và kết quả mô phỏng phục vụ demo”, không gọi là “hướng dẫn đã được cơ quan xác minh”.

## Định dạng đầu ra

Trả về đúng bốn phần:

### Phần 1 — Ý tưởng xuyên suốt

- Một câu thông điệp trung tâm.
- Một câu mô tả phong cách kể chuyện.

### Phần 2 — Storyboard chi tiết

Tạo bảng gồm các cột:

| Thời gian | Hình ảnh/thao tác trên màn hình | Lời voice-over | Chữ nhấn trên màn hình | Ghi chú dựng |
| --- | --- | --- | --- | --- |

Mỗi cảnh dài khoảng 10–30 giây. Ghi rõ vị trí nên zoom, highlight, tạm dừng hoặc chuyển cảnh.

### Phần 3 — Voice-over hoàn chỉnh

- Ghép toàn bộ lời đọc thành một bản liên tục.
- Không chứa timestamp, tiêu đề, chỉ dẫn dựng hoặc nội dung trong ngoặc.
- Có dấu câu phù hợp để đưa thẳng vào AI text-to-speech.
- Chia thành các đoạn ngắn, mỗi đoạn 2–4 câu.

### Phần 4 — Checklist quay và dựng

- Danh sách màn hình cần quay.
- Dữ liệu synthetic cần chuẩn bị.
- Các trạng thái lỗi cần tạo trước.
- Những tuyên bố phải kiểm tra lại với build thực tế trước khi xuất video.

## Tự kiểm tra trước khi trả kết quả

1. Tổng thời lượng có dưới 5 phút không?
2. Lời nói có khớp đúng capability hiện có không?
3. Có phân biệt rõ tiền kiểm với phê duyệt hành chính không?
4. Có thể hiện được giá trị của AI nhưng không để AI vượt quyền rule engine không?
5. Có ít nhất một cảnh cho thấy citation hoặc nguồn tham khảo không?
6. Có một lỗi đầu vào, một lần sửa lỗi và một kết quả tiền kiểm lại không?
