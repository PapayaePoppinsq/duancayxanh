# ==============================================================================
# MÁY CHỦ WEB & API KHUYẾN NGHỊ CÂY TRỒNG (FLASK WEB APPLICATION)
# Module: app.py
# Chạy ứng dụng: python app.py
# ==============================================================================

import os
import sys
import io
import json
import warnings
import pandas as pd
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import (
    init_db, get_user_by_email, create_user, get_user_by_id,
    save_prediction_history, get_user_history, delete_user_history, clear_user_history
)

warnings.filterwarnings('ignore')

# Cấu hình UTF-8 cho Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from predict import predict_crop_recommendation, get_model_and_scaler
from advisor import CROP_DETAILS, CROP_OPTIMAL_REQUIREMENTS

app = Flask(__name__)
# Secret key cố định từ biến môi trường để giữ phiên đăng nhập ổn định trên Cloud
app.secret_key = os.environ.get('SECRET_KEY', 'agribot-super-secret-session-key-2024')

# Initialize SQLite DB and Flask-Login
init_db()
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)

# Đảm bảo nạp trước model và scaler lúc khởi động máy chủ
try:
    get_model_and_scaler()
    print("[✓] Mô hình AI và bộ chuẩn hóa Scaler đã sẵn sàng hoạt động!")
except Exception as e:
    print(f"[!] Cảnh báo khi tải mô hình: {e}")

@app.route('/')
@login_required
def home():
    """Giao diện web người dùng tương tác trực quan."""
    return render_template('index.html', user=current_user)

@app.route('/api/health')
def health():
    return jsonify({'status': 'ok', 'app': 'AgriBot Crop Recommendation AI v3.0 Eco-Green'})

# ---------------- Authentication Routes ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = get_user_by_email(email)
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Email hoặc mật khẩu không đúng.', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        confirm = request.form.get('confirm')
        if password != confirm:
            flash('Mật khẩu xác nhận không khớp.', 'error')
            return redirect(url_for('register'))
        if get_user_by_email(email):
            flash('Email đã được đăng ký.', 'error')
            return redirect(url_for('register'))
        password_hash = generate_password_hash(password)
        create_user(email, password_hash)
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất.', 'success')
    return redirect(url_for('login'))

# ---------------- Machine Learning & Prediction APIs ----------------
@app.route('/api/predict', methods=['POST'])
@login_required
def api_predict():
    try:
        data = request.get_json(force=True)
        N = float(data.get('N', 90.0))
        P = float(data.get('P', 42.0))
        K = float(data.get('K', 43.0))
        temp = float(data.get('temp', 21.0))
        humidity = float(data.get('humidity', 82.0))
        ph = float(data.get('ph', 6.5))
        rainfall = float(data.get('rainfall', 203.0))

        result = predict_crop_recommendation(
            N=N, P=P, K=K,
            temp=temp, humidity=humidity,
            ph=ph, rainfall=rainfall, top_k=3
        )

        # Lưu tự động vào lịch sử dự đoán của người dùng
        if result.get('top_crops'):
            top1 = result['top_crops'][0]
            try:
                save_prediction_history(
                    user_id=int(current_user.id),
                    crop_name=top1['name_vi'],
                    crop_id=top1['id'],
                    emoji=top1['emoji'],
                    confidence=top1['probability'],
                    n=N, p=P, k=K,
                    temp=temp, humidity=humidity, ph=ph, rainfall=rainfall
                )
            except Exception as hist_err:
                print(f"[!] Lỗi ghi lịch sử: {hist_err}")

        return jsonify({
            'status': 'success',
            'data': result
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400

# ---------------- User Prediction History APIs ----------------
@app.route('/api/history', methods=['GET'])
@login_required
def api_get_history():
    try:
        history = get_user_history(int(current_user.id), limit=30)
        return jsonify({'status': 'success', 'data': history})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/history/<int:history_id>', methods=['DELETE'])
@login_required
def api_delete_history(history_id):
    try:
        delete_user_history(history_id, int(current_user.id))
        return jsonify({'status': 'success', 'message': 'Đã xóa mục lịch sử.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

@app.route('/api/history/clear', methods=['POST'])
@login_required
def api_clear_history():
    try:
        clear_user_history(int(current_user.id))
        return jsonify({'status': 'success', 'message': 'Đã xóa toàn bộ lịch sử.'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

# ---------------- Model Evaluation & Benchmark API ----------------
@app.route('/api/models-benchmark', methods=['GET'])
@login_required
def api_models_benchmark():
    """
    Trả về bảng đánh giá so sánh các thuật toán học máy và trọng số đặc trưng (Feature Importance)
    dựa trên tiêu chí môn học Machine Learning.
    """
    benchmark_data = {
        'models': [
            {
                'name': 'Random Forest Classifier',
                'category': 'Ensemble (Bagging)',
                'train_acc': 99.94,
                'test_acc': 99.55,
                'f1_score': 99.55,
                'gap': 0.40,
                'status': 'Mô hình Tối ưu nhất (Production)',
                'badge': 'success',
                'notes': 'Độ chính xác cao nhất, khử quá khớp tốt nhờ cơ chế kết hợp nhiều cây ngẫu nhiên.'
            },
            {
                'name': 'Gaussian Naive Bayes',
                'category': 'Probabilistic',
                'train_acc': 99.49,
                'test_acc': 99.55,
                'f1_score': 99.54,
                'gap': -0.06,
                'status': 'Rất tốt (Good Fit)',
                'badge': 'success',
                'notes': 'Tốc độ huấn luyện và suy luận cực nhanh, giả định phân phối chuẩn phù hợp cao.'
            },
            {
                'name': 'Support Vector Machine (SVM RBF)',
                'category': 'Kernel Machine',
                'train_acc': 98.58,
                'test_acc': 98.41,
                'f1_score': 98.40,
                'gap': 0.17,
                'status': 'Tốt',
                'badge': 'info',
                'notes': 'Ranh giới phân tách siêu phẳng phi tuyến mạnh mẽ.'
            },
            {
                'name': 'K-Nearest Neighbors (KNN k=5)',
                'category': 'Instance-based',
                'train_acc': 98.47,
                'test_acc': 97.95,
                'f1_score': 97.93,
                'gap': 0.51,
                'status': 'Tốt',
                'badge': 'info',
                'notes': 'Đơn giản, trực quan dựa trên khoảng cách Euclidean trong không gian đặc trưng.'
            },
            {
                'name': 'Decision Tree (CART)',
                'category': 'Tree-based',
                'train_acc': 89.49,
                'test_acc': 87.05,
                'f1_score': 85.21,
                'gap': 2.44,
                'status': 'Mô hình cơ sở (Baseline)',
                'badge': 'warning',
                'notes': 'Dễ diễn giải cây quyết định, nhưng độ chính xác thấp hơn so với Random Forest.'
            }
        ],
        'feature_importance': [
            {'feature': 'Lượng mưa (Rainfall)', 'weight': 22.31, 'desc': 'Ảnh hưởng quan trọng nhất tới phân bố nước sinh trưởng'},
            {'feature': 'Độ ẩm không khí (Humidity)', 'weight': 21.69, 'desc': 'Quyết định tốc độ thoát hơi nước và sự phát triển biểu bì'},
            {'feature': 'Kali trong đất (K)', 'weight': 18.34, 'desc': 'Đặc biệt phân hóa mạnh giữa chuối, nho, táo và các cây khác'},
            {'feature': 'Lân trong đất (P)', 'weight': 14.56, 'desc': 'Kích thích phát triển rễ cây và đậu hoa kết trái'},
            {'feature': 'Đạm trong đất (N)', 'weight': 10.20, 'desc': 'Yếu tố quyết định sinh khối cành lá và phát triển sơ khai'},
            {'feature': 'Nhiệt độ môi trường (Temp)', 'weight': 7.55, 'desc': 'Phân định giữa cây ôn đới lạnh và cây nhiệt đới nóng'},
            {'feature': 'Độ chua của đất (pH)', 'weight': 5.35, 'desc': 'Điều tiết khả năng hòa tan và hấp thu ion khoáng vi lượng'}
        ]
    }
    return jsonify({'status': 'success', 'data': benchmark_data})

# ---------------- Dataset Exploration (EDA) API ----------------
@app.route('/api/dataset-preview', methods=['GET'])
@login_required
def api_dataset_preview():
    """
    Trả về dữ liệu mẫu và thống kê trung bình của 22 cây trồng từ file CSV để người dùng khám phá (EDA).
    """
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'data', 'Crop_recommendation.csv')
        if not os.path.exists(csv_path):
            csv_path = os.path.join(os.path.dirname(__file__), '..', 'Crop_recommendation.csv')
            
        crop_filter = request.args.get('crop', '').strip().lower()
        
        df = pd.read_csv(csv_path)
        total_rows = len(df)
        
        if crop_filter:
            filtered_df = df[df['label'] == crop_filter]
        else:
            filtered_df = df
            
        sample_rows = filtered_df.sample(min(25, len(filtered_df)), random_state=42).to_dict(orient='records')
        for row in sample_rows:
            lbl = str(row.get('label', '')).lower()
            meta = CROP_DETAILS.get(lbl, {})
            row['name_vi'] = meta.get('name_vi', lbl.capitalize())
            row['emoji'] = meta.get('emoji', '🌱')
            row['category'] = meta.get('category', 'Cây trồng')
        
        # Thống kê nhanh theo cây
        crops_list = []
        for crop_id in sorted(df['label'].unique()):
            meta = CROP_DETAILS.get(crop_id, {'name_vi': crop_id, 'emoji': '🌱'})
            req = CROP_OPTIMAL_REQUIREMENTS.get(crop_id, {})
            crops_list.append({
                'id': crop_id,
                'name_vi': meta.get('name_vi', crop_id),
                'emoji': meta.get('emoji', '🌱'),
                'category': meta.get('category', 'Cây trồng'),
                'optimal': req
            })
            
        stats = {
            'N_mean': round(float(filtered_df['N'].mean()), 1),
            'P_mean': round(float(filtered_df['P'].mean()), 1),
            'K_mean': round(float(filtered_df['K'].mean()), 1),
            'temp_mean': round(float(filtered_df['temperature'].mean()), 1),
            'humidity_mean': round(float(filtered_df['humidity'].mean()), 1),
            'ph_mean': round(float(filtered_df['ph'].mean()), 2),
            'rainfall_mean': round(float(filtered_df['rainfall'].mean()), 1),
        }
            
        return jsonify({
            'status': 'success',
            'total_samples': total_rows,
            'filtered_count': len(filtered_df),
            'crops_count': len(crops_list),
            'crops': crops_list,
            'samples': sample_rows,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*65)
    print(" 🌾 HỆ THỐNG KHUYẾN NGHỊ CÂY TRỒNG AGRIBOT AI ECO-GREEN ĐANG KHỞI CHẠY 🌾")
    print("="*65)
    print(f"[*] Máy của bạn truy cập tại:")
    print(f"    👉 http://127.0.0.1:{port}")
    print(f"    👉 http://localhost:{port}")
    print(f"[*] Máy tính / điện thoại khác cùng mạng Wi-Fi truy cập tại:")
    print(f"    👉 http://192.168.1.26:{port}")
    print("="*65)
    print("[*] Nhấn Ctrl + C trong Terminal để dừng máy chủ bất kỳ lúc nào.\n")
    app.run(host='0.0.0.0', port=port, debug=False)


