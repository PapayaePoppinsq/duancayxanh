# ==============================================================================
# HỆ THỐNG CHUYÊN GIA NÔNG HỌC AI (AGRI-EXPERT ADVISORY ENGINE)
# Module: advisor.py
# Chức năng: Biên dịch nhãn cây trồng sang tiếng Việt, chẩn đoán chất lượng thổ nhưỡng,
#            và đưa ra khuyến nghị cải tạo đất & canh tác cụ thể.
# ==============================================================================

CROP_DETAILS = {
    'rice': {
        'name_vi': 'Lúa nước',
        'emoji': '🌾',
        'category': 'Cây lương thực',
        'cycle': '3 - 4 tháng',
        'soil_type': 'Đất phù sa, đất sét pha thịt, giữ nước tốt',
        'tips': 'Cần ngập nước ở giai đoạn đẻ nhánh và làm đòng. Duy trì mực nước 3-5cm.'
    },
    'maize': {
        'name_vi': 'Bắp (Ngô)',
        'emoji': '🌽',
        'category': 'Cây lương thực',
        'cycle': '3 - 3.5 tháng',
        'soil_type': 'Đất thịt nhẹ, đất cát pha màu mỡ, thoát nước tốt',
        'tips': 'Cần nhiều đạm và lân ở giai đoạn cây con và trổ cờ. Tránh úng nước.'
    },
    'chickpea': {
        'name_vi': 'Đậu gà (Chickpea)',
        'emoji': '🫘',
        'category': 'Cây họ đậu',
        'cycle': '3 - 4 tháng',
        'soil_type': 'Đất pha cát, đất thịt pha sét nhẹ, pH 6.0 - 7.5',
        'tips': 'Khả năng cố định đạm sinh học tốt. Cần đất tơi xốp, lượng mưa vừa phải.'
    },
    'kidneybeans': {
        'name_vi': 'Đậu tây (Kidney beans)',
        'emoji': '🫘',
        'category': 'Cây họ đậu',
        'cycle': '2.5 - 3 tháng',
        'soil_type': 'Đất tơi xốp giàu mùn, thoát nước tốt',
        'tips': 'Rất nhạy cảm với ngập úng. Bón phân hữu cơ hoai mục để tăng năng suất.'
    },
    'pigeonpeas': {
        'name_vi': 'Đậu triều (Pigeon peas)',
        'emoji': '🌱',
        'category': 'Cây họ đậu chịu hạn',
        'cycle': '5 - 6 tháng',
        'soil_type': 'Chịu được đất nghèo dinh dưỡng, đất thịt pha sỏi',
        'tips': 'Rễ đâm sâu giúp cải tạo cấu trúc đất và chống xói mòn rất tốt.'
    },
    'mothbeans': {
        'name_vi': 'Đậu bướm (Moth beans)',
        'emoji': '🌿',
        'category': 'Cây họ đậu siêu chịu hạn',
        'cycle': '2.5 - 3 tháng',
        'soil_type': 'Đất cát khô cằn, đất khô hạn bán sa mạc',
        'tips': 'Loài cây thích nghi tốt nhất với khí hậu khô nóng, lượng mưa thấp dưới 50mm.'
    },
    'mungbean': {
        'name_vi': 'Đậu xanh',
        'emoji': '🫛',
        'category': 'Cây họ đậu ngắn ngày',
        'cycle': '60 - 70 ngày',
        'soil_type': 'Đất cát pha, đất thịt nhẹ, độ ẩm vừa phải',
        'tips': 'Cây trồng xen canh hoặc luân canh lý tưởng để phục hồi độ phì cho đất.'
    },
    'blackgram': {
        'name_vi': 'Đậu đen (Đậu muồng)',
        'emoji': '🫘',
        'category': 'Cây họ đậu',
        'cycle': '70 - 80 ngày',
        'soil_type': 'Đất thịt pha, đất phù sa cổ',
        'tips': 'Kháng sâu bệnh tốt, nhu cầu phân bón trung bình, hạn chế bón thừa đạm.'
    },
    'lentil': {
        'name_vi': 'Đậu lăng (Lentil)',
        'emoji': '🍲',
        'category': 'Cây lương thực hạt',
        'cycle': '3 - 4 tháng',
        'soil_type': 'Đất cát pha thịt, đất kiềm nhẹ hoặc trung tính',
        'tips': 'Ưa khí hậu mát mẻ, không chịu được đất ngập úng và đất quá chua.'
    },
    'pomegranate': {
        'name_vi': 'Lựu',
        'emoji': '🪴',
        'category': 'Cây ăn quả lâu năm',
        'cycle': 'Cây lâu năm (thu hoạch sau 2-3 năm)',
        'soil_type': 'Đất thịt pha cát sâu, thoát nước tốt',
        'tips': 'Ưa nắng, cần tỉa cành định kỳ để quả đón ánh sáng và to đều.'
    },
    'banana': {
        'name_vi': 'Chuối',
        'emoji': '🍌',
        'category': 'Cây ăn quả nhiệt đới',
        'cycle': '9 - 12 tháng',
        'soil_type': 'Đất phù sa tơi xốp, tầng đất mặt dày, giàu kali và mùn',
        'tips': 'Nhu cầu nước và kali rất cao. Cần che chắn gió bão và bổ sung phân kali.'
    },
    'mango': {
        'name_vi': 'Xoài',
        'emoji': '🥭',
        'category': 'Cây ăn quả nhiệt đới',
        'cycle': 'Cây lâu năm',
        'soil_type': 'Đất cát pha, đất phù sa cổ, đất thịt nhẹ',
        'tips': 'Cần một mùa khô rõ rệt để kích thích phân hóa mầm hoa và đậu trái.'
    },
    'grapes': {
        'name_vi': 'Nho',
        'emoji': '🍇',
        'category': 'Cây ăn quả thân leo',
        'cycle': 'Cây lâu năm',
        'soil_type': 'Đất sỏi, đất pha cát, thoát nước cực tốt, giàu kali',
        'tips': 'Ưa khí hậu khô ráo, nhiều nắng. Mưa nhiều dễ gây nấm bệnh cho chùm quả.'
    },
    'watermelon': {
        'name_vi': 'Dưa hấu',
        'emoji': '🍉',
        'category': 'Cây rau màu ngắn ngày',
        'cycle': '65 - 75 ngày',
        'soil_type': 'Đất cát pha, đất giồng ven biển, thoát nước nhanh',
        'tips': 'Cần nhiều nắng, tưới đủ ẩm giai đoạn phát triển thân lá, giảm tưới khi tạo ngọt.'
    },
    'muskmelon': {
        'name_vi': 'Dưa lưới / Dưa lê',
        'emoji': '🍈',
        'category': 'Cây rau màu cao cấp',
        'cycle': '70 - 85 ngày',
        'soil_type': 'Đất thịt pha cát tơi xốp, giàu chất hữu cơ',
        'tips': 'Cần ánh sáng dồi dào, kiểm soát độ ẩm chặt chẽ để phòng bệnh sương mai.'
    },
    'apple': {
        'name_vi': 'Táo ôn đới',
        'emoji': '🍎',
        'category': 'Cây ăn quả ôn đới',
        'cycle': 'Cây lâu năm',
        'soil_type': 'Đất thịt pha sét sâu, tầng canh tác dày, pH 6.0 - 7.0',
        'tips': 'Cần tích lũy nhiệt độ thấp (chilling hours) trong mùa đông để kích hoa.'
    },
    'orange': {
        'name_vi': 'Cam',
        'emoji': '🍊',
        'category': 'Cây có múi (Citrus)',
        'cycle': 'Cây lâu năm',
        'soil_type': 'Đất thịt tơi xốp, đất đỏ bazan, thoát nước hoàn hảo',
        'tips': 'Nhạy cảm với bệnh vàng lá thối rễ. Cần đắp mô thoát nước và bón vôi định kỳ.'
    },
    'papaya': {
        'name_vi': 'Đu đủ',
        'emoji': '🍈',
        'category': 'Cây ăn quả nhanh thu',
        'cycle': '7 - 9 tháng bắt đầu thu hoạch',
        'soil_type': 'Đất thịt nhẹ, đất phù sa ven sông, giàu hữu cơ',
        'tips': 'Tuyệt đối không để úng nước quá 24h vì rễ đu đủ rất dễ bị thối.'
    },
    'coconut': {
        'name_vi': 'Dừa',
        'emoji': '🥥',
        'category': 'Cây công nghiệp / Cây ăn quả',
        'cycle': 'Cây lâu năm (thu hoạch sau 4-5 năm)',
        'soil_type': 'Đất cát pha ven biển, đất phù sa bãi bồi, chịu mặn nhẹ',
        'tips': 'Nhu cầu nước dồi dào, cần bổ sung muối khoáng và kali để quả ngọt và cùi dày.'
    },
    'cotton': {
        'name_vi': 'Bông vải',
        'emoji': '☁️',
        'category': 'Cây công nghiệp sợi',
        'cycle': '5 - 6 tháng',
        'soil_type': 'Đất thịt sâu, đất đen, đất phù sa thoát nước tốt',
        'tips': 'Cần nhiều nhiệt và ánh sáng trong suốt chu kỳ sinh trưởng, thời kỳ thu hoạch cần khô ráo.'
    },
    'jute': {
        'name_vi': 'Đay (Cây đay lấy sợi)',
        'emoji': '🎋',
        'category': 'Cây lấy sợi',
        'cycle': '4 - 5 tháng',
        'soil_type': 'Đất phù sa bồi hàng năm, chịu ngập úng tốt',
        'tips': 'Phát triển tốt nhất trong điều kiện nóng ẩm nhiệt đới và lượng mưa lớn.'
    },
    'coffee': {
        'name_vi': 'Cà phê (Robusta / Arabica)',
        'emoji': '☕',
        'category': 'Cây công nghiệp xuất khẩu',
        'cycle': 'Cây lâu năm (bắt đầu thu hoạch từ năm thứ 3)',
        'soil_type': 'Đất đỏ bazan màu mỡ, tầng đất mặt sâu trên 70cm',
        'tips': 'Cần mùa khô để siết nước kích hoa đồng loạt, sau đó tưới bão hòa để đậu quả.'
    }
}

def get_crop_profile(crop_label):
    """Lấy thông tin mô tả chi tiết của một loại cây trồng."""
    return CROP_DETAILS.get(crop_label.lower(), {
        'name_vi': crop_label.capitalize(),
        'emoji': '🌱',
        'category': 'Cây trồng nông nghiệp',
        'cycle': 'Đang cập nhật',
        'soil_type': 'Đa dạng',
        'tips': 'Canh tác theo tiêu chuẩn nông nghiệp hiện hành.'
    })

def diagnose_soil_and_climate(N, P, K, temp, humidity, ph, rainfall):
    """
    Chẩn đoán toàn diện tính chất lý hóa thổ nhưỡng & khí hậu,
    đồng thời đưa ra phác đồ cải tạo đất từ Chuyên gia Nông học AI.
    """
    diagnosis = {
        'ph_level': '',
        'ph_badge': '',
        'npk_summary': '',
        'climate_summary': '',
        'action_plan': []
    }
    
    # 1. Đánh giá độ chua / kiềm (pH)
    if ph < 5.0:
        diagnosis['ph_level'] = f"Đất rất chua (pH={ph:.2f}) - Nguy cơ ngộ độc nhôm, sắt"
        diagnosis['ph_badge'] = "danger"
        diagnosis['action_plan'].append("Cần bón vôi nông nghiệp (CaCO3 hoặc CaO) liều lượng 1.5 - 2 tấn/ha để hạ phèn khử chua.")
    elif 5.0 <= ph < 6.0:
        diagnosis['ph_level'] = f"Đất chua nhẹ (pH={ph:.2f}) - Thích hợp cây công nghiệp như chè, cà phê"
        diagnosis['ph_badge'] = "warning"
        diagnosis['action_plan'].append("Nên bổ sung phân lân nung chảy hoặc phân chuồng hoai mục để cân bằng độ pH tự nhiên.")
    elif 6.0 <= ph <= 7.5:
        diagnosis['ph_level'] = f"Đất trung tính lý tưởng (pH={ph:.2f}) - Thích hợp với hầu hết cây trồng"
        diagnosis['ph_badge'] = "success"
    else:
        diagnosis['ph_level'] = f"Đất hơi kiềm (pH={ph:.2f}) - Cần lưu ý khả năng hấp thụ vi lượng"
        diagnosis['ph_badge'] = "warning"
        diagnosis['action_plan'].append("Bổ sung phân hữu cơ sinh học hoặc lưu huỳnh nguyên tố để giảm tính kiềm của đất.")
        
    # 2. Đánh giá dinh dưỡng N-P-K
    npk_notes = []
    if N < 40:
        npk_notes.append("Thiếu Đạm (N thấp)")
        diagnosis['action_plan'].append("Bón thúc phân Urê hoặc phân hữu cơ đạm cá để hỗ trợ phát triển thân lá giai đoạn đầu.")
    elif N > 100:
        npk_notes.append("Đạm rất dồi dào (N cao)")
        diagnosis['action_plan'].append("Cân đối giảm bón đạm hóa học để tránh cây phát triển lốp đổ, giảm sức đề kháng sâu bệnh.")
    else:
        npk_notes.append("Đạm vừa đủ")
        
    if P < 30:
        npk_notes.append("Thiếu Lân (P thấp)")
        diagnosis['action_plan'].append("Bổ sung Super lân hoặc Lân hữu cơ kích thích bộ rễ phát triển mạnh.")
    elif P > 90:
        npk_notes.append("Lân dồi dào")
    else:
        npk_notes.append("Lân ổn định")
        
    if K < 30:
        npk_notes.append("Thiếu Kali (K thấp)")
        diagnosis['action_plan'].append("Cần bổ sung Kali Clorua hoặc Kali Sunfat ở giai đoạn nuôi củ, nuôi hạt và tạo ngọt cho quả.")
    elif K > 100:
        npk_notes.append("Kali rất cao (đặc trưng đất trồng chuối/nho)")
    else:
        npk_notes.append("Kali đầy đủ")
        
    diagnosis['npk_summary'] = " | ".join(npk_notes)
    
    # 3. Đánh giá thời tiết khí hậu
    climate_notes = []
    if temp < 18:
        climate_notes.append("Khí hậu mát/lạnh ôn đới")
    elif 18 <= temp <= 30:
        climate_notes.append("Nhiệt độ nhiệt đới lý tưởng")
    else:
        climate_notes.append("Nắng nóng nhiệt độ cao")
        
    if humidity > 80:
        climate_notes.append("Độ ẩm không khí rất cao")
        diagnosis['action_plan'].append("Chú ý khơi rãnh thoát nước và tỉa cành thông thoáng để phòng ngừa nấm khuẩn phát sinh.")
    elif humidity < 50:
        climate_notes.append("Không khí khô hanh")
        diagnosis['action_plan'].append("Nên phủ màng nông nghiệp hoặc rơm rạ gốc để giữ ẩm đất và chống bốc hơi nước.")
        
    if rainfall > 200:
        climate_notes.append("Lượng mưa rất dồi dào (>200mm)")
    elif rainfall < 60:
        climate_notes.append("Lượng mưa ít, khô hạn (<60mm)")
        diagnosis['action_plan'].append("Cần lắp đặt hệ thống tưới nhỏ giọt tiết kiệm nước.")
    else:
        climate_notes.append("Lượng mưa trung bình")
        
    diagnosis['climate_summary'] = " | ".join(climate_notes)
    
    if not diagnosis['action_plan']:
        diagnosis['action_plan'].append("Điều kiện đất và khí hậu đạt chuẩn xuất sắc, chỉ cần duy trì quy trình chăm sóc hữu cơ bình thường.")
        
    return diagnosis

# Nhu cầu thổ nhưỡng & khí hậu tối ưu trung bình của 22 loại cây trồng (dựa trên 2.200 mẫu dữ liệu thực nghiệm)
CROP_OPTIMAL_REQUIREMENTS = {
    "apple": {"N": 20.8, "P": 134.2, "K": 199.9, "temp": 22.6, "humidity": 92.3, "ph": 5.9, "rainfall": 112.7},
    "banana": {"N": 100.2, "P": 82.0, "K": 50.0, "temp": 27.4, "humidity": 80.4, "ph": 6.0, "rainfall": 104.6},
    "blackgram": {"N": 40.0, "P": 67.5, "K": 19.2, "temp": 30.0, "humidity": 65.1, "ph": 7.1, "rainfall": 67.9},
    "chickpea": {"N": 40.1, "P": 67.8, "K": 79.9, "temp": 18.9, "humidity": 16.9, "ph": 7.3, "rainfall": 80.1},
    "coconut": {"N": 22.0, "P": 16.9, "K": 30.6, "temp": 27.4, "humidity": 94.8, "ph": 6.0, "rainfall": 175.7},
    "coffee": {"N": 101.2, "P": 28.7, "K": 29.9, "temp": 25.5, "humidity": 58.9, "ph": 6.8, "rainfall": 158.1},
    "cotton": {"N": 117.8, "P": 46.2, "K": 19.6, "temp": 24.0, "humidity": 79.8, "ph": 6.9, "rainfall": 80.4},
    "grapes": {"N": 23.2, "P": 132.5, "K": 200.1, "temp": 23.8, "humidity": 81.9, "ph": 6.0, "rainfall": 69.6},
    "jute": {"N": 78.4, "P": 46.9, "K": 40.0, "temp": 25.0, "humidity": 79.6, "ph": 6.7, "rainfall": 174.8},
    "kidneybeans": {"N": 20.8, "P": 67.5, "K": 20.0, "temp": 20.1, "humidity": 21.6, "ph": 5.7, "rainfall": 105.9},
    "lentil": {"N": 18.8, "P": 68.4, "K": 19.4, "temp": 24.5, "humidity": 64.8, "ph": 6.9, "rainfall": 45.7},
    "maize": {"N": 77.8, "P": 48.4, "K": 19.8, "temp": 22.4, "humidity": 65.1, "ph": 6.2, "rainfall": 84.8},
    "mango": {"N": 20.1, "P": 27.2, "K": 29.9, "temp": 31.2, "humidity": 50.2, "ph": 5.8, "rainfall": 94.7},
    "mothbeans": {"N": 21.4, "P": 48.0, "K": 20.2, "temp": 28.2, "humidity": 53.2, "ph": 6.8, "rainfall": 51.2},
    "mungbean": {"N": 21.0, "P": 47.3, "K": 19.9, "temp": 28.5, "humidity": 85.5, "ph": 6.7, "rainfall": 48.4},
    "muskmelon": {"N": 100.3, "P": 17.7, "K": 50.1, "temp": 28.7, "humidity": 92.3, "ph": 6.4, "rainfall": 24.7},
    "orange": {"N": 19.6, "P": 16.6, "K": 10.0, "temp": 22.8, "humidity": 92.2, "ph": 7.0, "rainfall": 110.5},
    "papaya": {"N": 49.9, "P": 59.0, "K": 50.0, "temp": 33.7, "humidity": 92.4, "ph": 6.7, "rainfall": 142.6},
    "pigeonpeas": {"N": 20.7, "P": 67.7, "K": 20.3, "temp": 27.7, "humidity": 48.1, "ph": 5.8, "rainfall": 149.5},
    "pomegranate": {"N": 18.9, "P": 18.8, "K": 40.2, "temp": 21.8, "humidity": 90.1, "ph": 6.4, "rainfall": 107.5},
    "rice": {"N": 79.9, "P": 47.6, "K": 39.9, "temp": 23.7, "humidity": 82.3, "ph": 6.4, "rainfall": 236.2},
    "watermelon": {"N": 99.4, "P": 17.0, "K": 50.2, "temp": 25.6, "humidity": 85.2, "ph": 6.5, "rainfall": 50.8}
}

def calculate_fertilizer_recommendation(crop_id, N, P, K):
    """
    So sánh giá trị N, P, K đo được với mức chuẩn tối ưu của loại cây Top 1
    để tính toán phác đồ bón phân định lượng chi tiết.
    """
    req = CROP_OPTIMAL_REQUIREMENTS.get(crop_id, {"N": 60, "P": 50, "K": 40, "temp": 25, "humidity": 70, "ph": 6.5, "rainfall": 120})
    
    diff_N = round(req['N'] - N, 1)
    diff_P = round(req['P'] - P, 1)
    diff_K = round(req['K'] - K, 1)
    
    fert_plans = []
    
    # 1. Đạm (N) - Urê có 46% N
    if diff_N > 10:
        urea_kg = round(diff_N / 0.46, 1)
        fert_plans.append({
            'nutrient': 'Đạm (N)',
            'status': 'Thiếu hụt',
            'diff': f"-{diff_N} kg/ha",
            'badge': 'warning',
            'action': f"Bón bổ sung khoảng {urea_kg} kg Urê (46% N) / ha, chia làm 2 đợt bón lót và bón thúc sớm."
        })
    elif diff_N < -25:
        fert_plans.append({
            'nutrient': 'Đạm (N)',
            'status': 'Dư thừa',
            'diff': f"+{abs(diff_N)} kg/ha",
            'badge': 'danger',
            'action': "Đất đang dư đạm. Cần ngưng bón phân đạm hóa học, tưới nước tiêu đạm để tránh nấm rễ và đổ ngã."
        })
    else:
        fert_plans.append({
            'nutrient': 'Đạm (N)',
            'status': 'Cân bằng',
            'diff': f"{'+' if diff_N <= 0 else '-'}{abs(diff_N)} kg/ha",
            'badge': 'success',
            'action': "Hàm lượng đạm đang ở ngưỡng tối ưu lý tưởng cho cây sinh trưởng ổn định."
        })

    # 2. Lân (P) - Supe Lân có ~16% P2O5
    if diff_P > 10:
        super_p_kg = round(diff_P / 0.16, 1)
        fert_plans.append({
            'nutrient': 'Lân (P)',
            'status': 'Thiếu hụt',
            'diff': f"-{diff_P} kg/ha",
            'badge': 'warning',
            'action': f"Bón lót khoảng {super_p_kg} kg Supe Lân (hoặc Lân nung chảy) / ha để kích thích rễ phát triển."
        })
    elif diff_P < -30:
        fert_plans.append({
            'nutrient': 'Lân (P)',
            'status': 'Dư thừa',
            'diff': f"+{abs(diff_P)} kg/ha",
            'badge': 'danger',
            'action': "Lượng lân dư thừa cao, không cần bón thêm lân trong vụ này để tránh chai đất."
        })
    else:
        fert_plans.append({
            'nutrient': 'Lân (P)',
            'status': 'Cân bằng',
            'diff': f"{'+' if diff_P <= 0 else '-'}{abs(diff_P)} kg/ha",
            'badge': 'success',
            'action': "Lượng lân trong đất rất hài hòa với nhu cầu của bộ rễ."
        })

    # 3. Kali (K) - Kali Clorua có ~60% K2O
    if diff_K > 10:
        kcl_kg = round(diff_K / 0.60, 1)
        fert_plans.append({
            'nutrient': 'Kali (K)',
            'status': 'Thiếu hụt',
            'diff': f"-{diff_K} kg/ha",
            'badge': 'warning',
            'action': f"Bón đón đòng/nuôi quả khoảng {kcl_kg} kg Kali Clorua (KCl 60%) / ha để tích lũy đường và chắc hạt."
        })
    elif diff_K < -30:
        fert_plans.append({
            'nutrient': 'Kali (K)',
            'status': 'Dư thừa',
            'diff': f"+{abs(diff_K)} kg/ha",
            'badge': 'danger',
            'action': "Hàm lượng kali trong đất đang dồi dào, tạm ngưng bổ sung kali gốc."
        })
    else:
        fert_plans.append({
            'nutrient': 'Kali (K)',
            'status': 'Cân bằng',
            'diff': f"{'+' if diff_K <= 0 else '-'}{abs(diff_K)} kg/ha",
            'badge': 'success',
            'action': "Độ phì nhiêu kali đạt chuẩn cao cấp, hỗ trợ cây chống chịu sâu bệnh tốt."
        })

    return {
        'optimal': req,
        'diff': {'N': diff_N, 'P': diff_P, 'K': diff_K},
        'plans': fert_plans
    }

