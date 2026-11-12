# lequangquyet.com (trang tĩnh)

## Cấu trúc
- index.html: trang chủ. Các vùng nằm giữa dấu <!--HEADER:begin-->, <!--FOOT:begin-->, <!--FLOAT:begin-->, <!--START:begin--> và dấu end tương ứng được tự cập nhật, đừng sửa tay.
- content/mua-1, content/mua-2: mỗi bài một file .md (nội dung bài viết).
- blog/: các trang bài viết do tools/build_site.py tạo ra (không sửa tay).
- assets/: style.css, site.js, avatar.jpg, og-image.jpg.
- tools/header.html, footer.html, float.html: thanh menu, chân trang, nút hotline và nút lên đầu trang dùng chung cho mọi trang. Sửa ở đây rồi chạy lại build_site.py.
- blog/index.html: trang Blog (tự tạo). Danh sách bài trên đó tự cập nhật.
- tools/: import_excel.py (nhập bài từ Excel, chạy một lần), build_site.py (tạo trang).
- content/REVIEW.md: ghi chú nội bộ (các câu có số liệu hoặc tên khách hàng), chỉ có trên máy, không đưa lên GitHub nhờ .gitignore.

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

## Thêm ảnh bìa và ảnh minh họa cho bài viết
1. Tạo thư mục assets/blog/TÊN-SLUG/ (TÊN-SLUG là dòng slug: trong file .md của bài) và bỏ ảnh vào đó, tên không dấu, viết thường, ví dụ cover.jpg, hinh-1.jpg.
2. Ảnh bìa: thêm hai dòng vào phần đầu file .md, trước dấu ---:
   cover: assets/blog/TÊN-SLUG/cover.jpg
   cover_alt: Mô tả ngắn nội dung ảnh
   Ảnh bìa cũng được dùng làm ảnh hiển thị khi chia sẻ bài lên LinkedIn, Facebook, Zalo.
3. Ảnh minh họa trong bài: thêm một dòng riêng, cách các đoạn văn một dòng trống:
   ![Mô tả ảnh](assets/blog/TÊN-SLUG/hinh-1.jpg)
   Muốn có chú thích dưới ảnh: ![Mô tả ảnh](assets/blog/TÊN-SLUG/hinh-1.jpg "Chú thích hiển thị dưới ảnh")
4. Chạy python tools/build_site.py, rồi Commit và Push.
Gợi ý: ảnh JPG hoặc WebP, rộng khoảng 1200 đến 1280 px, mỗi ảnh nên dưới 300 KB. Tên file phải đúng từng chữ (GitHub Pages phân biệt chữ hoa chữ thường).
Lưu ý: không chạy lại tools/import_excel.py sau khi đã thêm ảnh hoặc sửa bài, vì file này tạo lại các file .md từ Excel và sẽ ghi đè.

## Đăng hoạt động và sự kiện
Hoạt động hoạt động giống blog: mỗi hoạt động là một file .md trong content/hoat-dong/ (đã có 3 file mẫu), ảnh để trong assets/hoat-dong/TÊN-SLUG/.
1. Copy một file mẫu, đặt tên dạng NĂM-THÁNG-ten-khong-dau.md, ví dụ 2026-11-hoi-thao-abc.md.
2. Sửa phần đầu file: title (tiêu đề), slug (đường dẫn, viết thường không dấu, chỉ dùng chữ, số và dấu gạch ngang), date (ngày, dạng 2026-11-20), place (địa điểm), tag (nhãn, ví dụ Hoạt động hoặc Sự kiện ngành, các nhãn khác nhau sẽ thành nút lọc), summary (tóm tắt 1 đến 2 câu, hiện trên thẻ và khi chia sẻ), cover (ảnh bìa), cover_alt (mô tả ảnh), published (yes hoặc no), linkedin (link bài đăng gốc nếu có).
3. Thêm ảnh vào assets/hoat-dong/TÊN-SLUG/ (cover.jpg, anh-1.jpg, ...). Ảnh bìa nên tỉ lệ 16:9, rộng khoảng 1280 px.
4. Phần nội dung phía dưới viết giống bài blog: ## là tiêu đề nhỏ, - là danh sách, ![Mô tả](đường-dẫn-ảnh) là ảnh. Nhiều dòng ảnh đặt liền nhau (mỗi ảnh một dòng, cách nhau một dòng trống) sẽ tự thành lưới ảnh 2 cột.
5. Chạy python tools/build_site.py, rồi Commit và Push.
Hoạt động mới nhất hiện trên trang chủ (tối đa 3 thẻ) và trong trang Hoạt động (hoat-dong/). Đặt published: no để ẩn một hoạt động.
Ba file mẫu đang dùng ảnh mẫu và chữ mẫu: thay nội dung thật hoặc đặt published: no trước khi đưa lên mạng.

## Số năm kinh nghiệm tự cộng mỗi năm
Trong index.html, các chỗ có data-since="2016" (năm bắt đầu đi làm) tự tính số năm = năm hiện tại trừ 2016, nên sang 2027 tự thành 11, 2028 thành 12. Muốn đổi năm bắt đầu thì sửa số 2016 ở các thuộc tính đó.
