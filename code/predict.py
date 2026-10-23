# ==============================================================================
# MODULE SUY LUẬN & DỰ ĐOÁN CÂY TRỒNG (INFERENCE MODULE)
# Module: predict.py
# ==============================================================================

import os
import sys
import io
import warnings
import argparse
import pandas as pd
import numpy as np
import joblib

warnings.filterwarnings('ignore')

# Cấu hình UTF-8 cho Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from advisor import get_crop_profile, diagnose_soil_and_climate, calculate_fertilizer_recommendation

# Tải model và scaler một lần (Caching)
BASE_DIR = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'crop_model.pkl')
SCALER_PATH = os.path.join(BASE_DIR, 'models', 'scaler.pkl')

_model = None
_scaler = None

def get_model_and_scaler():
    global _model, _scaler
    if _model is None or _scaler is None:
        if not os.path.exists(MODEL_PATH) or not os.path.exists(SCALER_PATH):
            raise FileNotFoundError(
                "[!] Chưa tìm thấy file mô hình (.pkl). Vui lòng chạy `python train.py` trước!"
            )
        _model = joblib.load(MODEL_PATH)
        _scaler = joblib.load(SCALER_PATH)
    return _model, _scaler

def predict_crop_recommendation(N, P, K, temp, humidity, ph, rainfall, top_k=3):
    """
    Hàm dự đoán chính:
    Nhận các thông số dinh dưỡng đất và khí hậu, trả về Top K cây trồng phù hợp
    kèm phân tích chuyên sâu từ Chuyên gia Nông học AI và phác đồ bón phân.
    """
    model, scaler = get_model_and_scaler()
    
    # Chuẩn bị dữ liệu đầu vào với tên cột chuẩn
    feature_names = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    input_df = pd.DataFrame([[N, P, K, temp, humidity, ph, rainfall]], columns=feature_names)
    
    # Chuẩn hóa và dự đoán phân phối xác suất
    input_scaled = scaler.transform(input_df)
    probabilities = model.predict_proba(input_scaled)[0]
    classes = model.classes_
    
    # Lấy top K chỉ số cao nhất
    top_indices = np.argsort(probabilities)[-top_k:][::-1]
    
    top_crops = []
    for rank, idx in enumerate(top_indices, 1):
        crop_id = classes[idx]
        prob = float(probabilities[idx] * 100)
        profile = get_crop_profile(crop_id)
        
        top_crops.append({
            'rank': rank,
            'id': crop_id,
            'name_vi': profile['name_vi'],
            'emoji': profile['emoji'],
            'category': profile['category'],
            'probability': round(prob, 2),
            'cycle': profile['cycle'],
            'soil_type': profile['soil_type'],
            'tips': profile['tips']
        })
        
    # Chẩn đoán thổ nhưỡng và khí hậu
    diagnosis = diagnose_soil_and_climate(N, P, K, temp, humidity, ph, rainfall)
    
    # Tính toán khuyến nghị phân bón theo cây Top 1
    top1_id = top_crops[0]['id'] if top_crops else 'rice'
    fertilizer_advice = calculate_fertilizer_recommendation(top1_id, N, P, K)
    
    return {
        'input_data': {
            'N': N, 'P': P, 'K': K,
            'temperature': temp, 'humidity': humidity,
            'ph': ph, 'rainfall': rainfall
        },
        'top_crops': top_crops,
        'diagnosis': diagnosis,
        'fertilizer_advice': fertilizer_advice
    }


def print_cli_report(res):
    """In báo cáo kết quả ra màn hình dòng lệnh."""
    data = res['input_data']
    print("\n" + "="*70)
    print(" 🌾 KẾT QUẢ KHUYẾN NGHỊ TỪ CHUYÊN GIA NÔNG HỌC AI 🌾".center(70))
    print("="*70)
    print(f"[*] Thông số thổ nhưỡng: N={data['N']} | P={data['P']} | K={data['K']} | pH={data['ph']}")
    print(f"[*] Thông số khí hậu:    Nhiệt độ={data['temperature']}°C | Độ ẩm={data['humidity']}% | Lượng mưa={data['rainfall']}mm")
    print("\n[★] TOP LOẠI CÂY TRỒNG PHÙ HỢP NHẤT:")
    for crop in res['top_crops']:
        bar = "█" * int(crop['probability'] // 5) + "░" * (20 - int(crop['probability'] // 5))
        print(f"  Top {crop['rank']}: {crop['emoji']} {crop['name_vi']:<18} [{bar}] {crop['probability']:>6.2f}% ({crop['category']})")
        print(f"         Thời vụ: {crop['cycle']} | Đất: {crop['soil_type']}")
        print(f"         Lưu ý:   {crop['tips']}")
        print()
        
    print("[★] CHẨN ĐOÁN THỔ NHƯỠNG:")
    print(f"  • Độ pH:      {res['diagnosis']['ph_level']}")
    print(f"  • Dinh dưỡng: {res['diagnosis']['npk_summary']}")
    print(f"  • Khí hậu:    {res['diagnosis']['climate_summary']}")
    print("\n[★] KẾ HOẠCH HÀNH ĐỘNG & LỜI KHUYÊN CANH TÁC:")
    for i, plan in enumerate(res['diagnosis']['action_plan'], 1):
        print(f"  {i}. {plan}")
    print("="*70 + "\n")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="AI Khuyến nghị Cây trồng Thổ nhưỡng & Khí hậu")
    parser.add_argument('--N', type=float, default=90.0, help="Hàm lượng đạm N (kg/ha)")
    parser.add_argument('--P', type=float, default=42.0, help="Hàm lượng lân P (kg/ha)")
    parser.add_argument('--K', type=float, default=43.0, help="Hàm lượng kali K (kg/ha)")
    parser.add_argument('--temp', type=float, default=21.0, help="Nhiệt độ trung bình (°C)")
    parser.add_argument('--humid', type=float, default=82.0, help="Độ ẩm không khí (%)")
    parser.add_argument('--ph', type=float, default=6.5, help="Độ chua của đất (pH 0-14)")
    parser.add_argument('--rain', type=float, default=203.0, help="Lượng mưa (mm)")
    
    args = parser.parse_args()
    result = predict_crop_recommendation(
        N=args.N, P=args.P, K=args.K,
        temp=args.temp, humidity=args.humid,
        ph=args.ph, rainfall=args.rain
    )
    print_cli_report(result)
