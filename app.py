import copy
import json
import os
import uuid
from functools import wraps

from flask import (
    Flask, abort, flash, redirect, render_template, request,
    send_from_directory, session, url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
IMAGE_DIR = os.path.join(DATA_DIR, "images")
# Đặt GCS_BUCKET để lưu dữ liệu và ảnh lên Google Cloud Storage (ổ đĩa local trên Cloud Run/VM không bền).
GCS_BUCKET = os.environ.get("GCS_BUCKET", "dataforgit").strip()
_gcs_bucket = None

ALLOWED_IMAGE_EXT = {"jpg", "jpeg", "png", "webp", "gif", "avif"}
MAX_IMAGE_BYTES = 5 * 1024 * 1024
DEFAULT_ADMIN_USER = "admin"
DEFAULT_ADMIN_PASSWORD = "123admin"

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "trathaomoc-bachphuc-secret")
app.config["MAX_CONTENT_LENGTH"] = 40 * 1024 * 1024

BRAND = "Trà thảo mộc Bách Phục"
SLOGAN = "Mang hơi thở thanh lành của núi rừng vào từng nhịp sống hiện đại"

HINT_BANNER = "Banner: 1920 × 1080 px (tỉ lệ 16:9). Ảnh ngang, chủ thể nằm giữa khung. Tối đa 5 MB."
HINT_STORY = "1200 × 900 px (tỉ lệ 4:3). Ảnh ngang, tránh chi tiết quan trọng sát mép ảnh. Tối đa 5 MB."
HINT_ORIGIN = "1400 × 900 px (tỉ lệ ~3:2). Ảnh ngang. Tối đa 5 MB."
HINT_CARD = "800 × 600 px (tỉ lệ 4:3). Thẻ hiển thị cắt còn cao 240 px, nên để chủ thể ở giữa."
HINT_CERT = "900 × 1125 px (tỉ lệ 4:5). Ảnh dọc, giống giấy chứng nhận."
HINT_GALLERY = "1200 × 1200 px (vuông 1:1)."
HINT_MAP = "1600 × 600 px (tỉ lệ ~8:3). Ảnh nền phía sau khối địa chỉ."


def txt(name, label):
    return {"name": name, "label": label, "type": "text"}


def area(name, label, rows=3):
    return {"name": name, "label": label, "type": "textarea", "rows": rows}


def lines(name, label):
    return {"name": name, "label": label, "type": "lines"}


def img(name, label, help_text):
    return {"name": name, "label": label, "type": "image", "help": help_text}


def scalar(sid, title, fields):
    return {"id": sid, "title": title, "type": "scalar", "fields": fields}


def listing(sid, title, fields):
    return {"id": sid, "title": title, "type": "list", "fields": fields}


def hero_section():
    return scalar("hero", "Banner đầu trang", [
        txt("eyebrow", "Dòng nhỏ phía trên"),
        txt("title", "Tiêu đề"),
        area("lead", "Mô tả ngắn", 2),
        img("image", "Ảnh nền banner", HINT_BANNER),
    ])


# Cấu trúc trang admin: mỗi page có các section; content[page][section] tương ứng.
PAGES = [
    {"key": "site", "label": "Thông tin chung", "sections": [
        scalar("general", "Thương hiệu & chân trang", [
            txt("brand", "Tên thương hiệu"),
            area("slogan", "Slogan (trang chủ)", 2),
            area("footer_about", "Giới thiệu ngắn (chân trang)", 2),
        ]),
        scalar("contact", "Thông tin liên hệ", [
            txt("hotline", "Hotline"),
            txt("email", "Email"),
            txt("address", "Địa chỉ"),
            txt("hours", "Giờ làm việc"),
        ]),
        listing("badges", "Huy hiệu / chứng nhận nhanh", [
            txt("name", "Tên huy hiệu"),
            txt("desc", "Mô tả"),
        ]),
    ]},
    {"key": "home", "label": "Trang chủ", "sections": [
        scalar("hero", "Banner trang chủ", [
            txt("eyebrow", "Dòng nhỏ phía trên"),
            area("lead", "Mô tả ngắn", 2),
            img("image", "Ảnh nền banner", HINT_BANNER),
            txt("btn1", "Nút 1"),
            txt("btn2", "Nút 2"),
        ]),
        scalar("story", "Câu chuyện thảo mộc", [
            txt("eyebrow", "Dòng nhỏ"),
            txt("title", "Tiêu đề"),
            area("p1", "Đoạn 1", 4),
            area("p2", "Đoạn 2", 4),
            area("quote", "Trích dẫn", 2),
            txt("link_text", "Chữ của liên kết"),
            img("image", "Ảnh minh họa", HINT_STORY),
            txt("badge_num", "Số nổi bật (ảnh)"),
            txt("badge_label", "Nhãn nổi bật (ảnh)"),
        ]),
        scalar("values", "Tiêu đề phần giá trị cốt lõi", [
            txt("eyebrow", "Dòng nhỏ"),
            txt("title", "Tiêu đề"),
        ]),
        listing("value_items", "Các giá trị cốt lõi", [
            txt("icon", "Icon Bootstrap (ví dụ: bi-tree)"),
            txt("title", "Tiêu đề"),
            area("desc", "Mô tả", 2),
        ]),
        listing("stats", "Số liệu nổi bật", [
            txt("num", "Số"),
            txt("label", "Nhãn"),
        ]),
        scalar("featured", "Phần thảo mộc nổi bật", [
            txt("eyebrow", "Dòng nhỏ"),
            txt("title", "Tiêu đề"),
            txt("button", "Chữ nút"),
        ]),
        scalar("cta", "Kêu gọi cuối trang", [
            txt("title", "Tiêu đề"),
            area("desc", "Mô tả", 2),
            txt("button", "Chữ nút"),
        ]),
    ]},
    {"key": "about", "label": "Về chúng tôi", "sections": [
        hero_section(),
        scalar("origin", "Nguồn gốc", [
            txt("eyebrow", "Dòng nhỏ"),
            txt("title", "Tiêu đề"),
            txt("sub1_title", "Tiêu đề phụ 1"),
            area("sub1_text", "Nội dung phụ 1", 3),
            txt("sub2_title", "Tiêu đề phụ 2"),
            area("sub2_text", "Nội dung phụ 2", 3),
            area("quote", "Trích dẫn", 2),
            img("image", "Ảnh minh họa", HINT_ORIGIN),
        ]),
        scalar("process", "Tiêu đề quy trình", [
            txt("eyebrow", "Dòng nhỏ"),
            txt("title", "Tiêu đề"),
        ]),
        listing("steps", "Các bước quy trình", [
            txt("title", "Tên bước"),
            area("desc", "Mô tả", 2),
        ]),
        scalar("commitment", "Cam kết", [
            txt("eyebrow", "Dòng nhỏ"),
            txt("title", "Tiêu đề"),
            txt("sub_title", "Tiêu đề phụ"),
            lines("checklist", "Danh sách cam kết"),
            img("image", "Ảnh minh họa", HINT_STORY),
        ]),
        scalar("sustainability", "Tiêu đề phát triển bền vững", [
            txt("eyebrow", "Dòng nhỏ"),
            txt("title", "Tiêu đề"),
        ]),
        listing("sustain_items", "Các cam kết bền vững", [
            txt("icon", "Icon Bootstrap (ví dụ: bi-flower1)"),
            txt("title", "Tiêu đề"),
            area("desc", "Mô tả", 2),
        ]),
    ]},
    {"key": "ingredients", "label": "Thành phần", "sections": [
        hero_section(),
        listing("items", "Danh sách thảo mộc", [
            txt("name", "Tên"),
            txt("latin", "Tên khoa học"),
            txt("origin", "Nguồn gốc"),
            img("image", "Ảnh", HINT_CARD),
            area("desc", "Mô tả", 4),
            lines("benefits", "Công dụng"),
            txt("quote", "Trích dẫn"),
        ]),
        scalar("notice", "Lưu ý cuối trang", [
            txt("eyebrow", "Dòng nhỏ"),
            txt("title", "Tiêu đề"),
            area("text", "Nội dung", 3),
        ]),
    ]},
    {"key": "certificates", "label": "Chứng nhận", "sections": [
        hero_section(),
        listing("items", "Giấy chứng nhận / kết quả kiểm nghiệm", [
            txt("title", "Tên giấy"),
            txt("issuer", "Đơn vị cấp"),
            txt("year", "Năm"),
            img("image", "Ảnh giấy", HINT_CERT),
        ]),
        scalar("faq", "Tiêu đề hỏi đáp", [
            txt("eyebrow", "Dòng nhỏ"),
            txt("title", "Tiêu đề"),
        ]),
        listing("faq_items", "Câu hỏi thường gặp", [
            txt("q", "Câu hỏi"),
            area("a", "Trả lời", 3),
        ]),
    ]},
    {"key": "gallery", "label": "Thư viện ảnh", "sections": [
        hero_section(),
        listing("items", "Ảnh trong thư viện", [
            img("src", "Ảnh", HINT_GALLERY),
            txt("caption", "Chú thích"),
            txt("category", "Nhóm (ví dụ: Thiên nhiên)"),
        ]),
    ]},
    {"key": "contact", "label": "Liên hệ", "sections": [
        hero_section(),
        scalar("page", "Khối nội dung trang liên hệ", [
            txt("form_title", "Tiêu đề form gửi tin"),
            txt("info_title", "Tiêu đề thông tin liên hệ"),
            img("map_image", "Ảnh nền khối địa chỉ", HINT_MAP),
        ]),
    ]},
]

DEFAULT_CONTENT = {
    "site": {
        "general": {
            "brand": BRAND,
            "slogan": SLOGAN,
            "footer_about": "Thảo dược từ núi cao, chế biến sạch, giữ trọn tinh túy thiên nhiên trong từng tách trà.",
        },
        "contact": {
            "hotline": "1900 6868",
            "email": "contact@bachphuc.vn",
            "address": "Thôn Bản Cao, xã Tả Van, huyện Sa Pa, tỉnh Lào Cai",
            "hours": "Thứ 2 - Thứ 7: 08:00 - 17:30",
        },
        "badges": [
            {"name": "ISO 22000", "desc": "Quản lý an toàn thực phẩm"},
            {"name": "HACCP", "desc": "Kiểm soát mối nguy trọng yếu"},
            {"name": "OCOP", "desc": "Sản phẩm nông thôn tiêu biểu"},
            {"name": "0% Chất bảo quản", "desc": "Không hương liệu nhân tạo"},
        ],
    },
    "home": {
        "hero": {
            "eyebrow": "Thảo dược đại ngàn miền Trung · Tinh khiết tự nhiên",
            "lead": "Từ những triền núi sương phủ miền Trung, mỗi búp thảo mộc được băng rừng tìm kiếm, chế biến thủ công và gửi trọn hương vị đại ngàn đến bạn.",
            "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1920&q=80",
            "btn1": "Khám phá sản phẩm",
            "btn2": "Câu chuyện của chúng tôi",
        },
        "story": {
            "eyebrow": "Hành trình thảo mộc",
            "title": "Từ rừng sâu miền Trung đến tách trà trên bàn làm việc của bạn",
            "p1": "Có những cây thuốc chỉ mọc nơi đại ngàn đã qua nhiều mùa mưa nắng. Người đồng bào vùng cao vẫn nhớ từng gốc cây, từng mùa thu hái, như cách họ nhớ đường về nhà.",
            "p2": "Bách Phục bắt đầu từ chính những câu chuyện ấy. Chúng tôi đi cùng người dân tộc thiểu số miền Trung để đưa dược liệu quý từ rừng về, giữ nguyên tinh túy và đưa đến từng ấm trà của bạn.",
            "quote": "Mang hơi thở thanh lành của núi rừng vào từng nhịp sống hiện đại.",
            "link_text": "Đọc hành trình của chúng tôi",
            "image": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1200&q=80",
            "badge_num": "100%",
            "badge_label": "Thảo mộc tự nhiên",
        },
        "values": {"eyebrow": "Giá trị cốt lõi", "title": "Điều chúng tôi cam kết"},
        "value_items": [
            {"icon": "bi-tree", "title": "Đại ngàn nguyên bản", "desc": "Dược liệu được thu hái từ rừng sâu và triền núi đá miền Trung, không trồng ép."},
            {"icon": "bi-shield-check", "title": "Khắt khe từng khâu", "desc": "Kiểm nghiệm đạt chuẩn vệ sinh an toàn thực phẩm, 100% không chất bảo quản."},
            {"icon": "bi-cup-hot", "title": "Thủ công kết hợp hiện đại", "desc": "Sấy lạnh giữ dược tính, sao trà thủ công tạo hương vị đậm đà."},
            {"icon": "bi-people", "title": "Đồng hành cùng bản làng", "desc": "Tạo sinh kế bền vững cho người đồng bào, bảo tồn tri thức cây thuốc nam."},
        ],
        "stats": [
            {"num": "15+", "label": "Năm kinh nghiệm"},
            {"num": "20+", "label": "Loại thảo mộc"},
            {"num": "5.000+", "label": "Khách hàng tin dùng"},
            {"num": "100%", "label": "Kiểm nghiệm đạt chuẩn"},
        ],
        "featured": {"eyebrow": "Nổi bật", "title": "Dược liệu quý của đại ngàn", "button": "Xem tất cả thảo mộc"},
        "cta": {
            "title": "Hương vị của đại ngàn, trong từng tách trà",
            "desc": "Mỗi tách trà là một lời mời trở về với thiên nhiên và với những người đã giữ rừng xanh suốt bao đời.",
            "button": "Liên hệ ngay",
        },
    },
    "about": {
        "hero": {
            "eyebrow": "Về chúng tôi",
            "title": "Nguồn gốc từ núi cao",
            "lead": "Hành trình từ đỉnh núi sương mờ đến chén trà thơm ngon.",
            "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1920&q=80",
        },
        "origin": {
            "eyebrow": "Nguồn gốc",
            "title": "Vùng đất của dược liệu quý",
            "sub1_title": "Khí hậu và đất rừng nuôi dưỡng dược tính",
            "sub1_text": "Những triền núi miền Trung có sương sớm, nắng dịu và đất rừng giàu khoáng chất. Thảo mộc ở đây sinh trưởng chậm, tích lũy trọn vẹn tinh dầu và dưỡng chất.",
            "sub2_title": "Người giữ rừng là người giữ tri thức",
            "sub2_text": "Chúng tôi làm việc cùng các hộ dân tộc thiểu số, lắng nghe kinh nghiệm thu hái và cách chăm rừng của họ. Mỗi cây thuốc được lấy có chừng mực, để rừng luôn xanh cho mùa sau.",
            "quote": "Rừng cho ta cây thuốc, ta giữ rừng để con cháu còn có cây thuốc.",
            "image": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1400&q=80",
        },
        "process": {"eyebrow": "Quy trình", "title": "Từ thu hái đến đóng gói"},
        "steps": [
            {"title": "Thu hái", "desc": "Chọn lọc thời điểm thu hái phù hợp, thủ công để tránh dập nát."},
            {"title": "Sơ chế", "desc": "Rửa sạch bằng nước suối, loại bỏ tạp chất và phân loại kỹ lưỡng."},
            {"title": "Phơi sấy", "desc": "Sấy ở nhiệt độ thấp, kiểm soát chặt chẽ để giữ hương và dưỡng chất."},
            {"title": "Đóng gói", "desc": "Đóng gói trong môi trường sạch, bảo quản kín để giữ độ tươi."},
        ],
        "commitment": {
            "eyebrow": "Cam kết",
            "title": "Sạch từ gốc đến ngọn",
            "sub_title": "Minh bạch từng lô sản phẩm",
            "checklist": [
                "Vùng trồng được kiểm soát và ghi nhận nhật ký canh tác.",
                "Không chất bảo quản, không phẩm màu nhân tạo.",
                "Kiểm nghiệm định kỳ tại đơn vị được cấp phép.",
                "Truy xuất nguồn gốc theo từng lô sản phẩm.",
            ],
            "image": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=1200&q=80",
        },
        "sustainability": {"eyebrow": "Phát triển bền vững", "title": "Giữ rừng, nuôi người"},
        "sustain_items": [
            {"icon": "bi-house-heart", "title": "Việc làm cho người đồng bào", "desc": "Hợp tác trực tiếp với hộ dân tộc thiểu số miền Trung, tạo thu nhập ổn định ngay tại làng."},
            {"icon": "bi-flower1", "title": "Sinh kế bền vững", "desc": "Chỉ thu hái theo mùa, để lại đủ cây non để rừng tự tái sinh và phục hồi."},
            {"icon": "bi-book", "title": "Bảo tồn tri thức bản địa", "desc": "Ghi chép và lưu giữ kinh nghiệm dùng cây thuốc nam của các thế hệ người dân vùng cao."},
        ],
    },
    "ingredients": {
        "hero": {
            "eyebrow": "Thành phần & Sản phẩm",
            "title": "Thảo mộc của núi rừng",
            "lead": "Mỗi loại thảo mộc mang một công dụng riêng cho sức khỏe.",
            "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1920&q=80",
        },
        "items": [
            {
                "name": "Nấm Linh Chi Rừng",
                "latin": "Ganoderma lucidum",
                "origin": "Rừng nguyên sinh miền Trung",
                "image": "https://images.unsplash.com/photo-1606914469633-bd39206ea739?auto=format&fit=crop&w=800&q=80",
                "desc": "Được mệnh danh là 'nấm của bậc trường thọ', linh chi rừng sinh trưởng chậm trên thân cây mục giữa đại ngàn, tích tụ triterpenoid và polysaccharide. Theo y học cổ truyền, nấm có tính bình, vị ngọt, quy kinh tâm, can, phế.",
                "benefits": ["Tăng cường sức đề kháng", "Hỗ trợ giấc ngủ, giảm căng thẳng", "Chống oxy hóa, thanh lọc cơ thể"],
                "quote": "Chậm rãi như núi rừng, bền bỉ như thời gian.",
            },
            {
                "name": "Hà Thủ Đỏ",
                "latin": "Polygonum multiflorum",
                "origin": "Triền núi đá vôi miền Trung",
                "image": "https://images.unsplash.com/photo-1597318181409-cf64d0b5d8a2?auto=format&fit=crop&w=800&q=80",
                "desc": "Củ hà thủ đỏ là vị thuốc quý của y học dân gian, được dùng để bồi bổ khí huyết, nuôi dưỡng sức khỏe gan thận và giúp cơ thể tràn đầy sinh lực sau những ngày mệt mỏi.",
                "benefits": ["Bồi bổ khí huyết", "Hỗ trợ chức năng gan thận", "Nuôi dưỡng sức khỏe bền lâu"],
                "quote": "Ẩn mình dưới lòng đất, nuôi dưỡng cả một đời người.",
            },
            {
                "name": "Sâm Dây",
                "latin": "Tetrastigma hemsleyanum",
                "origin": "Rừng già vùng cao",
                "image": "https://images.unsplash.com/photo-1518531933037-91b2f5f229cc?auto=format&fit=crop&w=800&q=80",
                "desc": "Sâm dây mọc hoang trên các triền núi đá, vị đắng dịu, hậu ngọt, giàu flavonoid tự nhiên. Được dùng để thanh nhiệt, giải độc và hỗ trợ tăng cường thể trạng.",
                "benefits": ["Thanh nhiệt, giải độc", "Hỗ trợ tăng cường thể trạng", "Giàu flavonoid tự nhiên"],
                "quote": "Vị đắng đầu môi, hậu ngọt nơi cuống họng.",
            },
            {
                "name": "Cúc Hoa Núi",
                "latin": "Chrysanthemum indicum",
                "origin": "Sườn đồi sương mù",
                "image": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?auto=format&fit=crop&w=800&q=80",
                "desc": "Cúc hoa núi nở vàng trên sườn đồi sương phủ, hương thơm dịu nhẹ, tính mát. Trà cúc giúp giải nhiệt, thanh lọc gan và mang đến cảm giác thư thái cho tinh thần.",
                "benefits": ["Giải nhiệt, thanh mát", "Hỗ trợ thanh lọc gan", "Giúp thư thái tinh thần"],
                "quote": "Một đóa hoa núi, một buổi chiều bình yên.",
            },
            {
                "name": "Cam Thảo Núi",
                "latin": "Glycyrrhiza glabra",
                "origin": "Đồi núi khô ráo miền Trung",
                "image": "https://images.unsplash.com/photo-1515586838455-8f8f940d6853?auto=format&fit=crop&w=800&q=80",
                "desc": "Rễ cam thảo mọc hoang trên đồi núi, vị ngọt tự nhiên, êm dịu. Cam thảo giúp làm dịu cổ họng, hỗ trợ tiêu hóa và hài hòa hương vị cho từng ấm trà.",
                "benefits": ["Làm dịu cổ họng", "Hỗ trợ tiêu hóa", "Vị ngọt tự nhiên, không đường"],
                "quote": "Ngọt từ đất, lành từ rễ.",
            },
            {
                "name": "Đinh Lăng Rừng",
                "latin": "Polyscias fruticosa",
                "origin": "Đại ngàn Trường Sơn",
                "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=800&q=80",
                "desc": "Đinh lăng là vị thuốc quen thuộc của núi rừng, hỗ trợ tăng cường sinh lực, giảm mệt mỏi và giúp cơ thể ăn ngon, ngủ sâu hơn trong nhịp sống bận rộn.",
                "benefits": ["Tăng cường sinh lực", "Giảm mệt mỏi", "Hỗ trợ ăn ngon, ngủ sâu"],
                "quote": "Lá xanh của đại ngàn, nhịp sống bình thản của hôm nay.",
            },
        ],
        "notice": {
            "eyebrow": "Lưu ý",
            "title": "Thông tin mang tính tham khảo",
            "text": "Công dụng được nêu mang tính tham khảo dân gian và không thay thế cho chẩn đoán, điều trị của bác sĩ. Vui lòng tham khảo ý kiến chuyên gia y tế trước khi sử dụng, đặc biệt với phụ nữ có thai, người đang điều trị bệnh.",
        },
    },
    "certificates": {
        "hero": {
            "eyebrow": "Chứng nhận & Công bố",
            "title": "Minh bạch về chất lượng",
            "lead": "Giấy chứng nhận, kết quả kiểm nghiệm và hồ sơ công bố sản phẩm.",
            "image": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=1920&q=80",
        },
        "items": [
            {"title": "Giấy chứng nhận VietGAP dược liệu", "issuer": "Cục Trồng trọt và Bảo vệ thực vật", "year": "2024", "image": "https://images.unsplash.com/photo-1586075010923-2dd4570fb338?auto=format&fit=crop&w=900&q=80"},
            {"title": "Kết quả kiểm nghiệm vi sinh", "issuer": "Trung tâm Kiểm nghiệm An toàn thực phẩm", "year": "2025", "image": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?auto=format&fit=crop&w=900&q=80"},
            {"title": "Kết quả kiểm nghiệm kim loại nặng", "issuer": "Viện Kiểm nghiệm An toàn vệ sinh thực phẩm", "year": "2025", "image": "https://images.unsplash.com/photo-1579154204601-01588f351e67?auto=format&fit=crop&w=900&q=80"},
            {"title": "Bản công bố sản phẩm", "issuer": "Bộ Y tế", "year": "2024", "image": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?auto=format&fit=crop&w=900&q=80"},
        ],
        "faq": {"eyebrow": "Hỏi đáp", "title": "Câu hỏi thường gặp"},
        "faq_items": [
            {"q": "Sản phẩm có đạt tiêu chuẩn an toàn thực phẩm không?", "a": "Toàn bộ sản phẩm được kiểm nghiệm định kỳ tại đơn vị được cấp phép, đáp ứng quy chuẩn an toàn thực phẩm hiện hành."},
            {"q": "Hồ sơ công bố sản phẩm có thể xem ở đâu?", "a": "Quý khách có thể yêu cầu bản sao hồ sơ công bố qua mục Liên hệ trên website."},
            {"q": "Nguồn dược liệu có được truy xuất nguồn gốc?", "a": "Mỗi lô dược liệu đều có mã truy xuất, ghi nhận vùng trồng, thời điểm thu hái và quy trình sơ chế."},
        ],
    },
    "gallery": {
        "hero": {
            "eyebrow": "Thư viện ảnh",
            "title": "Khoảnh khắc từ núi rừng",
            "lead": "Thiên nhiên, vùng trồng, quy trình và sản phẩm của chúng tôi.",
            "image": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1920&q=80",
        },
        "items": [
            {"src": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?auto=format&fit=crop&w=1400&q=80", "caption": "Sương mù vờn đỉnh núi miền Trung", "category": "Thiên nhiên"},
            {"src": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1400&q=80", "caption": "Băng rừng tìm dược liệu", "category": "Thiên nhiên"},
            {"src": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?auto=format&fit=crop&w=1400&q=80", "caption": "Bình minh trên đại ngàn", "category": "Thiên nhiên"},
            {"src": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1400&q=80", "caption": "Vùng trồng dược liệu tự nhiên", "category": "Vùng trồng"},
            {"src": "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?auto=format&fit=crop&w=1400&q=80", "caption": "Thu hái thuận theo tự nhiên", "category": "Quy trình"},
            {"src": "https://images.unsplash.com/photo-1544787219-7f47ccb76574?auto=format&fit=crop&w=1400&q=80", "caption": "Sấy lạnh giữ trọn dược tính", "category": "Quy trình"},
            {"src": "https://images.unsplash.com/photo-1563911302283-d2bc129e7570?auto=format&fit=crop&w=1400&q=80", "caption": "Đóng gói trong môi trường sạch", "category": "Đóng gói"},
            {"src": "https://images.unsplash.com/photo-1564890369478-c89ca6d9cde9?auto=format&fit=crop&w=1400&q=80", "caption": "Ấm trà thảo mộc đậm đà hương núi", "category": "Sản phẩm"},
        ],
    },
    "contact": {
        "hero": {
            "eyebrow": "Liên hệ",
            "title": "Kết nối cùng chúng tôi",
            "lead": "Chúng tôi luôn sẵn lòng lắng nghe và hỗ trợ bạn.",
            "image": "https://images.unsplash.com/photo-1441974231531-c6227db76b6e?auto=format&fit=crop&w=1920&q=80",
        },
        "page": {
            "form_title": "Gửi tin nhắn cho chúng tôi",
            "info_title": "Thông tin liên hệ",
            "map_image": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1600&q=80",
        },
    },
}


def gcs():
    global _gcs_bucket
    if _gcs_bucket is None:
        from google.cloud import storage
        _gcs_bucket = storage.Client().bucket(GCS_BUCKET)
    return _gcs_bucket


def data_exists(name):
    if GCS_BUCKET:
        return gcs().blob(f"data/{name}").exists()
    return os.path.exists(os.path.join(DATA_DIR, name))


def save_json(name, data):
    text = json.dumps(data, ensure_ascii=False, indent=2)
    if GCS_BUCKET:
        gcs().blob(f"data/{name}").upload_from_string(text, content_type="application/json")
        return
    with open(os.path.join(DATA_DIR, name), "w", encoding="utf-8") as f:
        f.write(text)


def load_json(name):
    if GCS_BUCKET:
        return json.loads(gcs().blob(f"data/{name}").download_as_text(encoding="utf-8"))
    with open(os.path.join(DATA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def merge_defaults(default, data):
    """Bổ sung các khóa còn thiếu trong file JSON bằng giá trị mặc định."""
    if isinstance(default, dict) and isinstance(data, dict):
        return {k: merge_defaults(v, data[k]) if k in data else copy.deepcopy(v) for k, v in default.items()}
    return data if data is not None else copy.deepcopy(default)


def ensure_data():
    if not GCS_BUCKET:
        os.makedirs(IMAGE_DIR, exist_ok=True)
    if not data_exists("content.json"):
        save_json("content.json", DEFAULT_CONTENT)
    if not data_exists("admin.json"):
        save_json("admin.json", {
            "username": DEFAULT_ADMIN_USER,
            "password_hash": generate_password_hash(DEFAULT_ADMIN_PASSWORD),
        })


def load_content():
    return merge_defaults(DEFAULT_CONTENT, load_json("content.json"))


def save_image_upload(file_storage):
    ext = os.path.splitext(file_storage.filename)[1].lower().lstrip(".")
    if ext not in ALLOWED_IMAGE_EXT:
        flash(f"Định dạng .{ext} không được hỗ trợ. Hãy dùng JPG, PNG, WEBP, GIF hoặc AVIF.", "warning")
        return None
    file_storage.stream.seek(0, os.SEEK_END)
    size = file_storage.stream.tell()
    file_storage.stream.seek(0)
    if size > MAX_IMAGE_BYTES:
        flash(f"Ảnh {file_storage.filename} vượt quá 5 MB.", "warning")
        return None
    name = f"{uuid.uuid4().hex}.{ext}"
    if GCS_BUCKET:
        gcs().blob(f"images/{name}").upload_from_file(file_storage.stream, content_type=file_storage.mimetype)
        return f"https://storage.googleapis.com/{GCS_BUCKET}/images/{name}"
    file_storage.save(os.path.join(IMAGE_DIR, name))
    return f"/media/{name}"


def resolve_image(url_text, upload, current):
    if upload and upload.filename:
        saved = save_image_upload(upload)
        if saved:
            return saved
    url = (url_text or "").strip()
    return url or current


def parse_field(field, key, current):
    if field["type"] == "image":
        return resolve_image(request.form.get(key), request.files.get(key + "|file"), current or "")
    raw = request.form.get(key, "")
    if field["type"] == "lines":
        return [line.strip() for line in raw.splitlines() if line.strip()]
    return raw.strip()


def parse_scalar(section, current):
    result = dict(current)
    for field in section["fields"]:
        key = f"{section['id']}|{field['name']}"
        result[field["name"]] = parse_field(field, key, current.get(field["name"]))
    return result


def parse_list(section):
    prefix = section["id"] + "|"
    row_ids = []
    for key in list(request.form.keys()) + list(request.files.keys()):
        if key.startswith(prefix):
            parts = key.split("|")
            if len(parts) >= 3 and parts[1] not in row_ids:
                row_ids.append(parts[1])
    items = []
    for row_id in row_ids:
        item = {}
        for field in section["fields"]:
            key = f"{section['id']}|{row_id}|{field['name']}"
            item[field["name"]] = parse_field(field, key, "")
        if any(item.values()):
            items.append(item)
    return items


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapper


def find_page(key):
    for page in PAGES:
        if page["key"] == key:
            return page
    return None


@app.context_processor
def inject_globals():
    content = load_content()
    return {
        "c": content,
        "brand": content["site"]["general"]["brand"],
        "contact": content["site"]["contact"],
        "current_year": 2026,
    }


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/ve-chung-toi")
def about():
    return render_template("about.html")


@app.route("/thanh-phan")
def ingredients():
    return render_template("ingredients.html")


@app.route("/chung-nhan")
def certificates():
    return render_template("certificates.html")


@app.route("/thu-vien-anh")
def gallery():
    return render_template("gallery.html")


@app.route("/lien-he", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()
        if not name or not email or not message:
            flash("Vui lòng điền đầy đủ họ tên, email và nội dung.", "danger")
        else:
            flash(f"Cảm ơn {name}! Chúng tôi đã nhận tin nhắn và sẽ phản hồi sớm.", "success")
        return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/media/<path:filename>")
def media(filename):
    return send_from_directory(IMAGE_DIR, filename)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        admin = load_json("admin.json")
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == admin["username"] and check_password_hash(admin["password_hash"], password):
            session["admin"] = True
            return redirect(url_for("admin_index"))
        flash("Sai tài khoản hoặc mật khẩu.", "danger")
    return render_template("admin/login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("Bạn đã đăng xuất.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_index():
    return render_template("admin/index.html", pages=PAGES)


@app.route("/admin/<page_key>", methods=["GET", "POST"])
@login_required
def admin_page(page_key):
    page = find_page(page_key)
    if page is None:
        abort(404)
    content = load_content()
    if request.method == "POST":
        for section in page["sections"]:
            if section["type"] == "list":
                content[page_key][section["id"]] = parse_list(section)
            else:
                content[page_key][section["id"]] = parse_scalar(section, content[page_key][section["id"]])
        save_json("content.json", content)
        flash("Đã lưu nội dung thành công.", "success")
        return redirect(url_for("admin_page", page_key=page_key))
    return render_template("admin/page.html", page=page, data=content[page_key], pages=PAGES)


@app.errorhandler(413)
def too_large(_):
    return "Dữ liệu gửi lên quá lớn. Hãy giảm dung lượng ảnh rồi lưu lại.", 413


ensure_data()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
