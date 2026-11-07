# lequangquyet.com (trang tĩnh)

## Cấu trúc
- index.html: trang chủ. Các vùng nằm giữa dấu <!--HEADER:begin-->, <!--FOOT:begin-->, <!--FLOAT:begin-->, <!--START:begin--> và dấu end tương ứng được tự cập nhật, đừng sửa tay.
- content/mua-1, content/mua-2: mỗi bài một file .md (nội dung bài viết).
- insights/: các trang bài viết do tools/build_site.py tạo ra (không sửa tay).
- assets/: style.css, site.js, avatar.jpg, og-image.jpg.
- tools/header.html, footer.html, float.html: thanh menu, chân trang, nút hotline và nút lên đầu trang dùng chung cho mọi trang. Sửa ở đây rồi chạy lại build_site.py.
- blog/index.html: trang Blog (tự tạo). Danh sách bài trên đó tự cập nhật.
- tools/: import_excel.py (nhập bài từ Excel, chạy một lần), build_site.py (tạo trang).
- content/REVIEW.md: các câu có số liệu hoặc tên khách hàng, nên xem lại trước khi công khai.

## Sửa một bài hoặc đăng bài mới
1. Sửa file .md trong content/ (hoặc copy một file có sẵn, đổi tiêu đề, slug, number, date, nội dung).
2. Đặt published: yes để bài hiện lên trang. Bài để published: no sẽ không xuất hiện.
3. Chạy: python tools/build_site.py
4. Commit và Push lên GitHub.
Khi bài đã đăng trên LinkedIn, dán link vào dòng linkedin: trong file .md để hiện nút "Xem bản gốc trên LinkedIn".

## Định dạng nội dung trong file .md
- Dòng bắt đầu bằng "## " là tiêu đề nhỏ. Các dòng bắt đầu bằng "- " là danh sách. Đoạn văn cách nhau bằng một dòng trống.
- **chữ đậm** và [chữ liên kết](https://...) dùng được.

## Việc cần làm trước khi đưa lên mạng
- Xem content/REVIEW.md và chỉnh các số liệu, tên khách hàng.
- Bật Cloudflare Web Analytics (thêm đoạn mã vào cuối index.html và tools/article_template.html).


## Giao diện Modern Personal Branding
- `assets/style.css`: bộ giao diện Modern Technology (navy/teal), responsive cho desktop và mobile.
- Nội dung trang chủ vẫn được quản lý trong `index.html`; phần menu/chân trang/nút gọi dùng các file trong `tools/`.
- Khi sửa nội dung các vùng có marker `HEADER`, `FOOT`, `FLOAT`, `START`, hãy sửa file nguồn tương ứng trong `tools/` hoặc dữ liệu `content/`, sau đó chạy lại `python tools/build_site.py`.
