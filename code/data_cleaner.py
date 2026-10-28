# -*- coding: utf-8 -*-
"""
Bộ tiền xử lý và chuẩn hóa dữ liệu VietSmartAgri Dataset
Nguồn: https://huggingface.co/datasets/VanLuan01/VietSmartAgri-Dataset
Tác giả dataset: Xích Văn Luận (VanLuan01)
"""

import os
import re
import json

BASE_DIR = os.path.dirname(__file__)
RAW_PATH = os.path.join(BASE_DIR, 'data', 'vietsmartagri_raw.json')
CLEAN_PATH = os.path.join(BASE_DIR, 'data', 'vietsmartagri_knowledge.json')

# Bảng từ điển sửa lỗi font/ký tự hỏi chấm (?) phổ biến trong nông nghiệp tiếng Việt
REPLACEMENTS = [
    # Lúa & gạo
    (r'\bRu\?ng\b', 'Ruộng'),
    (r'\bla\b', 'lúa'),
    (r'\bLa\b', 'Lúa'),
    (r'\b\?\?t\b', 'đất'),
    (r'\bh\?i\b', 'hơi'),
    (r'\bv\?\b', 'vụ'),
    (r'\bn\?ng nng\b', 'nắng nóng'),
    (r'\bn\?ng\b', 'nắng'),
    (r'\bgi\?ng\b', 'giống'),
    (r'\b\?i Th\?m 8\b', 'Đài Thơm 8'),
    (r'\bt\?\?i n\?\?c\b', 'tưới nước'),
    (r'\bt\?\?i\b', 'tưới'),
    (r'\bn\?\?c\b', 'nước'),
    (r'\bbn phn\b', 'bón phân'),
    (r'\bphn\b', 'phân'),
    (r'\bbn\b', 'bón'),
    (r'\bth\? no\b', 'thế nào'),
    (r'\b\?\? trnh\b', 'để tránh'),
    (r'\b\?ng r\?\b', 'úng rễ'),
    (r'\bt\?ng n\?ng su\?t\b', 'tăng năng suất'),
    (r'\bn\?ng su\?t\b', 'năng suất'),
    (r'\bp d\?ng\b', 'Áp dụng'),
    (r'\bNng-L\?-Ph\?i\b', 'Nông-Lộ-Phơi (AWD)'),
    (r'\b4 \?\?t cn \?\?i\b', '4 đợt cân đối'),
    (r'\bbn lt\b', 'bón lót'),
    (r'\bBn lt\b', 'Bón lót'),
    (r'\bln nung ch\?y\b', 'lân nung chảy'),
    (r'\bh\?u c\?\b', 'hữu cơ'),
    (r'\bThc \?\? nhnh\b', 'Thúc đẻ nhánh'),
    (r'\b\?\? nhnh\b', 'đẻ nhánh'),
    (r'\b\?n \?ng\b', 'Đón đòng'),
    (r'\blm \?ng\b', 'làm đòng'),
    (r'\bsi\?t n\?\?c ph\?i ru\?ng\b', 'siết nước phơi ruộng'),
    (r'\br\?y nu\b', 'rầy nâu'),
    (r'\b\?u tin\b', 'Ưu tiên'),
    (r'\bb\?y \?n\b', 'bẫy đèn'),
    (r'\bthin \?\?ch\b', 'thiên địch'),
    (r'\bthn c\?ng\b', 'thân cứng'),
    (r'\bh\?t ch\?c\b', 'hạt chắc'),
    (r'\b\?\?o n\b', 'đạo ôn'),
    (r'\bc\? bng\b', 'cổ bông'),

    # Thanh long
    (r'\bBnh Thu\?n\b', 'Bình Thuận'),
    (r'\bnh\? gi\?t\b', 'nhỏ giọt'),
    (r'\bl\?ch t\?\?i\b', 'lịch tưới'),
    (r'\bko di\b', 'kéo dài'),
    (r'\bcy ki\?n thi\?t\b', 'cây kiến thiết'),
    (r'\bnui tri\b', 'nuôi trái'),
    (r'\btri\b', 'trái'),
    (r'\bPh\? g\?c r\?m r\?\b', 'Phủ gốc rơm rạ'),
    (r'\b\?\?m nu\b', 'đốm nâu'),
    (r'\bn\?m t\?c k\b', 'nấm tắc kè'),
    (r'\bthn th\?\b', 'thán thư'),
    (r'\bC\?t b\? cnh b\?nh\b', 'Cắt bỏ cành bệnh'),
    (r'\bcnh b\?nh\b', 'cành bệnh'),
    (r'\bkch r\?\b', 'kích rễ'),
    (r'\bvng cnh\b', 'vàng cành'),
    (r'\bth\?i r\?\b', 'thối rễ'),
    (r'\b\?c sn\b', 'ốc sên'),
    (r'\bru\?i \?\?c qu\?\b', 'ruồi đục quả'),
    (r'\bchong \?n\b', 'chong đèn'),
    (r'\bhom gi\?ng\b', 'hom giống'),

    # Bắp / Ngô
    (r'\bB\?p\b', 'Bắp (Ngô)'),
    (r'\bb\?p\b', 'bắp'),
    (r'\blp h\?t\b', 'lép hạt'),
    (r'\bsu keo ma thu\b', 'sâu keo mùa thu'),
    (r'\bsu keo\b', 'sâu keo'),
    (r'\bchy l\b', 'cháy lá'),
    (r'\br\? s\?t\b', 'rỉ sắt'),
    (r'\bchu\?t\b', 'chuột'),

    # Chuối, Sầu riêng, Tiêu, Cà phê
    (r'\bho r\? Panama\b', 'héo rũ Panama'),
    (r'\btuy\?n trng\b', 'tuyến trùng'),
    (r'\bch\?t nhanh\b', 'chết nhanh'),
    (r'\bch\?t ch\?m\b', 'chết chậm'),
    (r'\bx m\?\b', 'xì mủ'),
    (r'\bx \?en\b', 'xơ đen'),
    (r'\bs\?\?ng c\?m\b', 'sượng cơm'),
    (r'\bvng c\?m\b', 'vàng cơm'),
    (r'\bho xanh\b', 'héo xanh vi khuẩn'),
    (r'\bB??c (\d)\b', r'Bước \1'),
    (r'\bT\?ng (\d)\b', r'Tầng \1'),
]

def clean_text(text):
    if not text:
        return ""
    # Chuẩn hóa khoảng trắng
    text = re.sub(r'\r\n|\r', '\n', str(text))
    for pattern, rep in REPLACEMENTS:
        text = re.sub(pattern, rep, text, flags=re.IGNORECASE)
    # Loại bỏ các ký tự điều khiển rác
    text = text.replace('\x00', '').replace('\ufeff', '')
    return text.strip()

def build_clean_knowledge_base():
    with open(RAW_PATH, 'r', encoding='utf-8') as f:
        raw_rows = json.load(f)

    cleaned_kb = []
    for idx, r in enumerate(raw_rows):
        crop = clean_text(r.get('crop', 'Cây trồng'))
        topic = clean_text(r.get('topic', 'Kỹ thuật nông nghiệp'))
        prompt = clean_text(r.get('vi_prompt', ''))
        response = clean_text(r.get('vi_response', ''))
        cot = clean_text(r.get('chain_of_thought', ''))
        en_summary = clean_text(r.get('en_summary', ''))
        region = clean_text(r.get('region', 'Việt Nam'))
        context = clean_text(r.get('farming_context', 'Hộ nông dân / Hợp tác xã'))
        source = clean_text(r.get('source_type', 'VietSmartAgri Dataset'))

        # Phân loại thẻ tìm kiếm (Tags)
        tags = set()
        for w in [crop, topic, region]:
            for token in re.findall(r'[\w]+', w.lower()):
                if len(token) > 2:
                    tags.add(token)

        # Trích xuất các hoạt chất / phân bón nếu có
        chem_matches = re.findall(r'\b(?:NPK|Ure|Kali|Lân|Vôi|Canxi|Bo|Humic|Trichoderma|Metalaxyl|Azoxystrobin|Spinosad|Bacillus|Metarhizium|Kasugamycin|Nano Bạc|Nano Đồng|K2SO4|KCl|MKP)\b', response, re.IGNORECASE)
        for chem in chem_matches:
            tags.add(chem.lower())

        item = {
            'id': f'vs_{idx+1}',
            'crop': crop,
            'topic': topic,
            'region': region,
            'prompt': prompt,
            'response': response,
            'chain_of_thought': cot,
            'en_summary': en_summary,
            'farming_context': context,
            'source': source,
            'tags': sorted(list(tags))
        }
        cleaned_kb.append(item)

    with open(CLEAN_PATH, 'w', encoding='utf-8') as f:
        json.dump(cleaned_kb, f, ensure_ascii=False, indent=2)

    print(f"[OK] Da tao thanh cong co so tri thuc VietSmartAgri: {len(cleaned_kb)} muc tai {CLEAN_PATH}")

if __name__ == '__main__':
    build_clean_knowledge_base()
