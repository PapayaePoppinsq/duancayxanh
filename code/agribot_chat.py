# -*- coding: utf-8 -*-
# ==============================================================================
# HỆ THỐNG TRỢ LÝ CHUYÊN GIA NÔNG NGHIỆP THÔNG MINH (AGRIBOT AI CHATBOT)
# Dữ liệu huấn luyện: VietSmartAgri-Dataset (Hugging Face: VanLuan01/VietSmartAgri-Dataset)
# Tác giả dữ liệu: Xích Văn Luận (VanLuan01) - Tích hợp SOFRI, Bộ NN&PTNT & VietGAP
# Module: agribot_chat.py
# ==============================================================================

import os
import re
import json
import unicodedata
from advisor import CROP_DETAILS, CROP_OPTIMAL_REQUIREMENTS

BASE_DIR = os.path.dirname(__file__)
KB_PATH = os.path.join(BASE_DIR, 'data', 'vietsmartagri_knowledge.json')

_knowledge_base = None

def strip_accents(text):
    """Bỏ dấu tiếng Việt để đối sánh mềm (fuzzy search)."""
    if not text:
        return ""
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text.replace('đ', 'd').replace('Đ', 'D').lower()

def load_knowledge_base():
    """Tải và lưu đệm (cache) cơ sở tri thức VietSmartAgri."""
    global _knowledge_base
    if _knowledge_base is None:
        if os.path.exists(KB_PATH):
            with open(KB_PATH, 'r', encoding='utf-8') as f:
                _knowledge_base = json.load(f)
        else:
            _knowledge_base = []
    return _knowledge_base

# Bản đồ ánh xạ đồng nghĩa cây trồng (Synonyms)
CROP_SYNONYMS = {
    'lúa': ['lúa', 'gạo', 'ruộng', 'đài thơm', 'om5451', 'st25', 'nếp', 'rice', 'paddy'],
    'thanh long': ['thanh long', 'ruột đỏ', 'ruột trắng', 'chong đèn', 'dragon fruit'],
    'bắp': ['bắp', 'ngô', 'bắp nếp', 'bắp ngọt', 'nk66', 'dk6919', 'corn', 'maize'],
    'chuối': ['chuối', 'chuối già', 'nam mỹ', 'cavendish', 'panama', 'banana'],
    'sầu riêng': ['sầu riêng', 'monthong', 'ri6', 'sượng cơm', 'cháy múi', 'durian'],
    'cà phê': ['cà phê', 'cafe', 'robusta', 'arabica', 'catimor', 'coffee'],
    'tiêu': ['tiêu', 'hồ tiêu', 'chết nhanh', 'chết chậm', 'black pepper'],
    'đậu xanh': ['đậu xanh', 'đỗ xanh', 'mungbean', 'mung bean'],
    'đậu bắp': ['đậu bắp', 'okra', 'ladyfinger'],
    'dưa hấu': ['dưa hấu', 'héo xanh', 'watermelon'],
    'mít': ['mít', 'mít thái', 'xơ đen', 'jackfruit'],
    'vải': ['vải', 'vải thiều', 'lục ngạn', 'lychee'],
    'bưởi': ['bưởi', 'bưởi diễn', 'pomelo', 'citrus'],
    'rau': ['rau', 'thủy canh', 'xà lách', 'rau cải', 'rau muống', 'nhà màng', 'vegetable'],
    'tôm': ['tôm', 'thẻ chân trắng', 'ems', 'gan tụy', 'shrimp'],
    'cá tra': ['cá tra', 'pangasius', 'xuất huyết', 'tilapia']
}

def extract_crops_and_topics(query):
    """Trích xuất cây trồng và chủ đề từ câu hỏi người dùng."""
    q_norm = strip_accents(query)
    q_lower = query.lower()

    detected_crops = []
    for crop_key, syns in CROP_SYNONYMS.items():
        for s in syns:
            s_norm = strip_accents(s)
            if re.search(r'\b' + re.escape(s_norm) + r'\b', q_norm):
                detected_crops.append(crop_key)
                break

    # Phát hiện chủ đề
    detected_topics = []
    topic_keywords = {
        'sâu bệnh': ['bệnh', 'sâu', 'nấm', 'thán thư', 'đốm nâu', 'rầy', 'đạo ôn', 'héo xanh', 'rỉ sắt', 'úng rễ', 'thối rễ', 'tuyến trùng', 'xơ đen', 'ruồi đục'],
        'phân bón': ['phân', 'bón', 'npk', 'đạm', 'ure', 'lân', 'kali', 'vôi', 'canxi', 'bo', 'humic', 'trichoderma', 'lá', 'dinh dưỡng'],
        'tưới nước': ['tưới', 'nước', 'nhỏ giọt', 'awd', 'ướt khô', 'ngập', 'độ ẩm', 'hạn', 'khô'],
        'đất đai': ['đất', 'ph', 'chua', 'phèn', 'mặn', 'cát', 'sét', 'mùn', 'cải tạo'],
        'kỹ thuật': ['chong đèn', 'cắt cành', 'tỉa', 'ghép', 'hom', 'giống', 'nuôi trái', 'thu hoạch'],
        'kinh tế': ['chi phí', 'giá', 'vietgap', 'globalgap', 'xuất khẩu', 'lợi nhuận', '1 ha', 'đầu tư']
    }

    for top, kws in topic_keywords.items():
        for kw in kws:
            kw_norm = strip_accents(kw)
            if kw_norm in q_norm:
                detected_topics.append(top)
                break

    return detected_crops, detected_topics

def search_vietsmartagri(query, top_k=2):
    """
    Thuật toán tìm kiếm thông minh trên cơ sở tri thức VietSmartAgri:
    Kết hợp đối sánh thực thể, điểm từ khóa trọng số và độ khớp ngữ nghĩa.
    """
    kb = load_knowledge_base()
    if not kb:
        return []

    q_norm = strip_accents(query)
    q_words = set(w for w in re.findall(r'\w+', q_norm) if len(w) >= 2)
    detected_crops, detected_topics = extract_crops_and_topics(query)

    scored_items = []

    for item in kb:
        score = 0.0
        prompt_norm = strip_accents(item.get('prompt', ''))
        resp_norm = strip_accents(item.get('response', ''))
        cot_norm = strip_accents(item.get('chain_of_thought', ''))
        en_norm = item.get('en_summary', '').lower()
        crop_norm = strip_accents(item.get('crop', ''))
        topic_norm = strip_accents(item.get('topic', ''))

        # 1. Trùng khớp cây trồng (Bonus cực mạnh)
        for dc in detected_crops:
            syns = CROP_SYNONYMS.get(dc, [dc])
            if any(strip_accents(s) in crop_norm or strip_accents(s) in prompt_norm for s in syns):
                score += 15.0

        # 2. Trùng khớp chủ đề
        for dt in detected_topics:
            if dt in topic_norm or dt in prompt_norm:
                score += 8.0

        # 3. Đối sánh từ khóa (Keyword overlap)
        prompt_words = set(re.findall(r'\w+', prompt_norm))
        resp_words = set(re.findall(r'\w+', resp_norm))
        tag_words = set(strip_accents(t) for t in item.get('tags', []))

        overlap_prompt = len(q_words.intersection(prompt_words))
        overlap_resp = len(q_words.intersection(resp_words))
        overlap_tags = len(q_words.intersection(tag_words))

        score += overlap_prompt * 4.0
        score += overlap_tags * 3.0
        score += overlap_resp * 1.0

        # 4. Trùng cụm từ nguyên văn
        if len(query.strip()) > 8 and q_norm in prompt_norm:
            score += 25.0

        if score > 5.0:
            scored_items.append((score, item))

    scored_items.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored_items[:top_k]]

def format_vietsmartagri_response(item):
    """Định dạng câu trả lời từ dữ liệu chuẩn hóa của VietSmartAgri."""
    crop = item.get('crop', 'Cây trồng')
    topic = item.get('topic', 'Kỹ thuật nông nghiệp')
    region = item.get('region', 'Việt Nam')
    prompt = item.get('prompt', '')
    response = item.get('response', '')
    cot = item.get('chain_of_thought', '')
    source = item.get('source', 'VietSmartAgri Dataset')

    lines = [
        f"### 🌾 **Tư Vấn Nông Học Chuyên Sâu: {crop}**",
        f"🏷️ **Chủ đề:** *{topic}* | 📍 **Vùng canh tác:** *{region}*\n",
        f"**💡 Câu hỏi thường gặp thực tế:** *\"{prompt}\"*\n",
        "---",
        "#### 📋 **Phác Đồ & Giải Pháp Thực Chiến:**",
        f"{response}\n"
    ]

    if cot and len(cot.strip()) > 10:
        lines.append("#### 🧠 **Quy Trình Suy Luận Từng Bước (Chain-of-Thought):**")
        steps = re.split(r'(?:Bước|Tầng)\s*(\d+)[\s:\-]+', cot)
        if len(steps) > 2:
            for i in range(1, len(steps), 2):
                step_num = steps[i]
                step_content = steps[i+1].strip() if i+1 < len(steps) else ""
                lines.append(f"- **Bước {step_num}:** {step_content}")
        else:
            lines.append(f"{cot}\n")

    lines.append("\n---")
    lines.append(f"📌 *Nguồn dữ liệu:* **{source}** (Bộ dữ liệu huấn luyện VietSmartAgri-Dataset)")
    return "\n".join(lines)

def get_quick_suggestions():
    """Danh sách các câu hỏi gợi ý nhanh từ VietSmartAgri."""
    return [
        {"icon": "🌾", "text": "Tưới ướt-khô xen kẽ AWD cho lúa tránh úng rễ?"},
        {"icon": "🐉", "text": "Trị thán thư & đốm nâu trên thanh long ruột đỏ?"},
        {"icon": "🐛", "text": "Phòng trừ sâu keo mùa thu hại bắp (ngô)?"},
        {"icon": "🍌", "text": "Bệnh héo rũ Panama trên chuối Cavendish xử lý sao?"},
        {"icon": "🍈", "text": "Quy trình bón phân nuôi trái sầu riêng Monthong chống sượng cơm?"},
        {"icon": "🍉", "text": "Trị bệnh héo xanh vi khuẩn trên dưa hấu?"},
        {"icon": "☕", "text": "Lắp hệ thống tưới thông minh cho cà phê Robusta mùa khô?"},
        {"icon": "🫘", "text": "Kỹ thuật trồng đậu xanh luân canh sau vụ lúa?"}
    ]

def answer_crop_advisor(crop_name):
    """Tư vấn tổng quan từ bộ dữ liệu advisor 22 loại cây trồng."""
    crop_id = None
    crop_info = None

    for cid, meta in CROP_DETAILS.items():
        if crop_name.lower() in meta.get('name_vi', '').lower() or crop_name.lower() in cid.lower():
            crop_id = cid
            crop_info = meta
            break

    if not crop_id:
        return None

    req = CROP_OPTIMAL_REQUIREMENTS.get(crop_id, {})
    lines = [
        f"### {crop_info.get('emoji', '🌱')} **Cẩm Nang Chuyên Sâu: {crop_info.get('name_vi')}**",
        f"- **Nhóm cây:** {crop_info.get('category')}",
        f"- **Chu kỳ sinh trưởng:** {crop_info.get('cycle')}",
        f"- **Loại đất phù hợp nhất:** {crop_info.get('soil_type')}",
        f"- **Lưu ý canh tác cốt lõi:** {crop_info.get('tips')}\n",
        "#### 📊 **Điều Kiện Thổ Nhưỡng & Khí Hậu Tối Ưu:**",
        f"- **Đạm (N):** {req.get('N_min', 0)} - {req.get('N_max', 0)} kg/ha",
        f"- **Lân (P):** {req.get('P_min', 0)} - {req.get('P_max', 0)} kg/ha",
        f"- **Kali (K):** {req.get('K_min', 0)} - {req.get('K_max', 0)} kg/ha",
        f"- **Độ chua đất (pH):** {req.get('ph_min', 0)} - {req.get('ph_max', 0)}",
        f"- **Nhiệt độ:** {req.get('temp_min', 0)} - {req.get('temp_max', 0)} °C",
        f"- **Độ ẩm không khí:** {req.get('humidity_min', 0)} - {req.get('humidity_max', 0)} %",
        f"- **Lượng mưa hàng năm:** {req.get('rainfall_min', 0)} - {req.get('rainfall_max', 0)} mm\n",
        "---",
        "📌 *Dữ liệu: Hệ thống Chuyên gia Nông học AgriBot AI*"
    ]
    return "\n".join(lines)

def agribot_chat(message, history=None):
    """
    Hàm xử lý hội thoại chính của Chatbot AgriBot AI:
    Ưu tiên tra cứu tri thức thực chiến VietSmartAgri -> Kết hợp Chuyên gia 22 cây trồng -> Dự đoán ML.
    """
    if not message or not message.strip():
        return {
            "status": "error",
            "reply": "Xin chào! Bạn vui lòng nhập câu hỏi về cây trồng, đất đai hoặc kỹ thuật nông nghiệp để tôi hỗ trợ nhé.",
            "suggestions": get_quick_suggestions()[:4]
        }

    msg = message.strip()
    msg_lower = msg.lower()

    # 1. Chào hỏi & Giới thiệu
    greetings = ['chào', 'hello', 'hi', 'bạn là ai', 'mày là ai', 'giới thiệu', 'giúp gì', 'menu']
    if any(g in msg_lower for g in greetings) and len(msg.split()) <= 4:
        reply = (
            "👋 **Xin chào! Tôi là AgriBot AI - Trợ lý Kỹ Sư Nông Nghiệp Thông Minh.**\n\n"
            "Tôi được trang bị bộ dữ liệu thực chiến **VietSmartAgri-Dataset** "
            "(tích hợp khuyến nghị của Viện Cây ăn quả Miền Nam SOFRI, Bộ NN&PTNT và tiêu chuẩn VietGAP/GlobalGAP).\n\n"
            "🌾 **Tôi có thể tư vấn chuyên sâu cho bạn về:**\n"
            "- 💧 **Kỹ thuật tưới nước & độ ẩm** (AWD ngập-khô xen kẽ cho lúa, tưới nhỏ giọt thanh long, béc bù áp cà phê).\n"
            "- 🧪 **Phác đồ bón phân NPK, vôi, vi sinh** (cải tạo đất chua, phèn, mặn, bổ sung Canxi-Bo, Trichoderma).\n"
            "- 🛡️ **Phòng trừ sâu bệnh hại thực tế** (rầy nâu, đạo ôn, thán thư, đốm nâu, héo xanh, sâu keo mùa thu, rệp sáp).\n"
            "- 📊 **Kỹ thuật nuôi trái & kinh tế** (chong đèn thanh long, chống sượng cơm sầu riêng, chi phí đầu tư 1 ha).\n\n"
            "👉 Hãy chọn một câu hỏi gợi ý bên dưới hoặc gõ trực tiếp thắc mắc của bạn!"
        )
        return {
            "status": "success",
            "reply": reply,
            "source": "AgriBot Greeting",
            "suggestions": get_quick_suggestions()[:4]
        }

    # 2. Tìm kiếm trong VietSmartAgri Dataset
    matches = search_vietsmartagri(msg, top_k=2)
    if matches:
        best_match = matches[0]
        reply_text = format_vietsmartagri_response(best_match)

        # Gợi ý thông minh liên quan đến cây trồng này
        crop_name = best_match.get('crop', '')
        dynamic_suggestions = []
        for s in get_quick_suggestions():
            if s['text'] != msg:
                dynamic_suggestions.append(s)

        return {
            "status": "success",
            "reply": reply_text,
            "source": f"VietSmartAgri-Dataset ({best_match.get('source', '')})",
            "crop": crop_name,
            "suggestions": dynamic_suggestions[:3]
        }

    # 3. Tra cứu trong Advisor 22 Cây Trồng
    detected_crops, _ = extract_crops_and_topics(msg)
    if detected_crops:
        for c in detected_crops:
            advisor_info = answer_crop_advisor(c)
            if advisor_info:
                return {
                    "status": "success",
                    "reply": advisor_info,
                    "source": "AgriBot Crop Knowledge Base",
                    "crop": c,
                    "suggestions": get_quick_suggestions()[:3]
                }

    # 4. Tư vấn tổng quát / Phân tích ngữ cảnh nông nghiệp
    reply_fallback = (
        f"🤔 **Kỹ Sư AgriBot đã ghi nhận câu hỏi:** *\"{msg}\"*\n\n"
        "Đối với vấn đề này, để đạt hiệu quả cao nhất theo khuyến nghị **VietSmartAgri & VietGAP**, bạn nên lưu ý:\n\n"
        "1. **Kiểm tra độ pH và độ ẩm đất trước tiên:** Đất chua (pH < 5.5) làm khóa lân và kali, cần bón 300 - 500 kg vôi nông nghiệp/ha trước 10 - 15 ngày.\n"
        "2. **Cân đối tỷ lệ N-P-K theo từng giai đoạn:** Bón nhiều Đạm (N) và Lân (P) ở đầu vụ giúp bén rễ nở bụi; tăng cường Kali (K) và Canxi-Bo khi nuôi hoa và trái để tránh rụng và tăng độ ngọt.\n"
        "3. **Ưu tiên quản lý dịch hại tổng hợp (IPM):** Sử dụng bẫy đèn, thuốc sinh học (Trichoderma, Bacillus, Metarhizium) để bảo vệ thiên địch và giảm dư lượng thuốc BVTV.\n\n"
        "💡 *Gợi ý:* Bạn có thể hỏi cụ thể tên cây trồng (ví dụ: *Lúa, Thanh long, Bắp, Chuối, Sầu riêng, Cà phê...*) để tôi đưa ra phác đồ chi tiết từng bước!"
    )

    return {
        "status": "success",
        "reply": reply_fallback,
        "source": "AgriBot General Advisory",
        "suggestions": get_quick_suggestions()[:3]
    }
