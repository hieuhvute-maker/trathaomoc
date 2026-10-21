[improve 1]
Tôi đã dựng xong bộ khung website Flask. Bây giờ hãy giúp tôi nâng cấp toàn bộ NỘI DUNG (Content/Copywriting), HÌNH ẢNH (Visuals) và NGHỆ THUẬT TRUYỀN THÔNG (Storytelling) cho website "Trà Thảo Mộc Bách Phục" theo các định hướng chuyên sâu sau:

1. Định hướng Thương hiệu & Câu chuyện (Brand Storytelling):
- Thông điệp cốt lõi: "Mang hơi thở thanh lành của núi rừng vào từng nhịp sống hiện đại".
- Giá trị nhân văn: Nhấn mạnh sứ mệnh đồng hành cùng người dân tộc thiểu số miền Trung (tạo việc làm, sinh kế bền vững, bảo tồn tri thức bản địa về cây thuốc nam, hỗ trợ người đồng bào lao động vùng cao).

2. Chi tiết về Dược lý & Nguyên liệu:
- Nhấn mạnh vào nguồn dược liệu tự nhiên quý hiếm từ đại ngàn miền Trung, đặc biệt là Nấm Linh Chi Rừng tự nhiên, Hà thủ đỏ, Sâm dây, Cúc hoa núi...
- Làm nổi bật Dược lý tự nhiên: Sự chắt lọc tinh hoa đất trời, tính bình, giúp phục hồi thể trạng, thanh lọc cơ thể, giảm căng thẳng cho con người thời hiện đại.

3. Kỳ công Chế biến & Tiêu chuẩn khắt khe:
- Quy trình chế biến thủ công kết hợp hiện đại: Từ bước băng rừng tìm kiếm nguyên liệu, thu hái thuận tự nhiên, rửa sạch nguồn nước khoáng núi, sấy lạnh giữ trọn dược tính đến sao trà thủ công tạo hương vị đậm đà.
- Chứng nhận & Đảm bảo: Khắc họa sự khắt khe trong từng khâu kiểm nghiệm đạt chuẩn vệ sinh an toàn thực phẩm, các chứng nhận ISO/HACCP/OCOP (nếu có), cam kết 100% không chất bảo quản, không hương liệu nhân tạo.

4. Nâng cấp Nội dung & Hình ảnh chi tiết cho các phần trên Web:
- Hero Banner (Trang chủ): Viết Slogan cực kỳ truyền cảm hứng, tinh tế, kèm mô tả hình ảnh gợi ý (Ví dụ: sương mù vờn trên đỉnh núi Đại Lộc/Trường Sơn, bàn tay người đồng bào nâng niu cành thuốc).
- Phần "Hành Trình Thảo Mộc" (Story section): Viết bài PR ngắn lôi cuốn về hành trình từ rừng sâu miền Trung đến tách trà thơm trên bàn làm việc.
- Phần "Dược Tính & Sản Phẩm": Viết lại mô tả cho từng loại thảo mộc (đặc biệt là Nấm Linh Chi Rừng) dưới góc độ khoa học kết hợp y học cổ truyền.
- Phần "Tâm Huyết & Bền Vững": Khối nội dung tôn vinh người lao động vùng cao.
- Nguồn hình ảnh (Image Placeholders/URLs): Gợi ý các link ảnh Unsplash/Pexels hoặc mô tả chi tiết từ khóa tìm ảnh (Ví dụ: 'misty mountains central vietnam', 'wild ganoderma lucidum mushroom', 'traditional tea ceremony', 'indigenous farmer harvesting').

5. Yêu cầu sản phẩm đầu ra:
- Cung cấp lại nội dung dạng HTML/Jinja2 hoặc file Python dictionary/JSON chứa dữ liệu bài viết mới để tôi dễ dàng gắn vào Flask App.
- Cấu trúc bài viết cần dùng các Heading (H2, H3), Quote (trích dẫn hay), Badge (nhãn chứng nhận) để hiển thị lên UI trông thật chuyên nghiệp và thu hút.
- Sử dụng nhiều ảnh trên mạng , chủ đề trà , dược liệu


[base]
Bạn là một chuyên gia Full-Stack Web Developer và UI/UX Designer. Hãy giúp tôi xây dựng một ứng dụng web hoàn chỉnh bằng Python Flask với các yêu cầu chi tiết sau:

1. Công nghệ & Kiến trúc:
- Backend: Python Flask (cấu trúc thư mục chuẩn gồm app.py, thư mục templates/ cho HTML, thư mục static/ cho CSS/JS/Images).
- Frontend: HTML5, Bootstrap 5 (kèm Bootstrap Icons hoặc FontAwesome), Google Fonts (phông chữ trang nhã, hiện đại).
- Giao diện (UI/UX): Thiết kế "fancy", hiện đại, sang trọng, mang phong cách thiên nhiên (natural/organic). Phối màu chủ đạo: Xanh lá đậm (deep green), nâu gỗ/vàng đồng và kem/trắng. Hỗ trợ responsive hoàn hảo trên mọi thiết bị (Mobile-first, tablet, desktop).

2. Tên dự án & Nội dung cốt lõi:
- Tên thương hiệu: Trà thảo mộc Bách Phục.
- Mô tả: Website dạng PR / Giới thiệu thương hiệu & sản phẩm (KHÔNG có chức năng giỏ hàng, mua bán, thanh toán trực tuyến).

3. Cấu trúc Menu & Các trang (Sử dụng Flask render templates):
- Trang chủ (Home): Hero section ấn tượng với hình ảnh thiên nhiên/núi non hùng vĩ, câu chuyện thương hiệu ngắn gọn, các giá trị cốt lõi và lợi ích sức khỏe nổi bật.
- Về chúng tôi (About): Giới thiệu nguồn gốc thảo dược từ vùng núi cao, quy trình thu hái và chế biến sạch.
- Thành phần & Sản phẩm (Ingredients/Showcase): Trưng bày các loại thảo mộc (Nấm linh chi, cam thảo, hoa cúc,...) kèm mô tả công dụng dưới dạng các card Bootstrap đẹp mắt.
- Chứng nhận & Công bố (Certificates & Compliance): Hiển thị các giấy chứng nhận chất lượng, kết quả kiểm nghiệm, hồ sơ công bố sản phẩm (trình bày dạng lưới ảnh phóng to khi click hoặc accordion gọn gàng).
- Thư viện ảnh (Gallery): Các hình ảnh đẹp về thiên nhiên, vùng trồng dược liệu, quy trình đóng gói.
- Liên hệ (Contact): Thông tin liên hệ, hotline, địa chỉ, bản đồ giả lập và form gửi tin nhắn liên hệ.

4. Yêu cầu về hình ảnh và dữ liệu mẫu:
- Sử dụng hình ảnh minh họa chất lượng cao từ các nguồn ảnh miễn phí trên mạng (Unsplash/Pexels) với các từ khóa: vùng núi cao, nấm linh chi, ấm trà thảo mộc, thiên nhiên xanh.
- Viết sẵn dữ liệu mẫu (Dummy data) bằng tiếng Việt cho các bài viết, thành phần, chứng nhận để website hiển thị sinh động ngay khi chạy.

5. Sản phẩm đầu ra mong muốn:
- Cung cấp toàn bộ mã nguồn (source code) các file cần thiết: app.py, các file HTML (base.html, index.html, about.html, v.v.), file CSS tùy chỉnh (style.css nếu cần).
- Không cần check GIT , Chỉ thực hiện thay đổi với yêu cầu, không làm thêm, không cần test, ko cần check git history, làm xong báo done không cần giải thích,