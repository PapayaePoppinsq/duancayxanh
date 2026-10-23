# ==============================================================================
# QUY TRÌNH HUẤN LUYỆN, TỐI ƯU SIÊU THAM SỐ (GRIDSEARCHCV) VÀ ĐÁNH GIÁ OVERFITTING
# Module: train.py
# Nâng cấp toàn diện dựa trên luồng phân tích từ notebook môn học
# ==============================================================================

import os
import sys
import io
import json
import argparse
import warnings
import pandas as pd
import numpy as np
import joblib

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

warnings.filterwarnings('ignore')

# Cấu hình UTF-8 cho Windows console
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

def find_dataset():
    candidates = [
        os.path.join(os.path.dirname(__file__), 'data', 'Crop_recommendation.csv'),
        os.path.join(os.path.dirname(__file__), 'Crop_recommendation.csv'),
        os.path.join(os.path.dirname(__file__), '..', 'Crop_recommendation.csv'),
        'Crop_recommendation.csv'
    ]
    for path in candidates:
        if os.path.exists(path):
            return os.path.abspath(path)
    return None

def train_and_export(mode='full', run_gridsearch=True):
    print("="*70)
    print(" BẮT ĐẦU QUY TRÌNH HUẤN LUYỆN & TỐI ƯU SIÊU THAM SỐ (THEO NOTEBOOK)")
    print("="*70)
    
    csv_path = find_dataset()
    if not csv_path:
        raise FileNotFoundError("[!] Khong tim thay file Crop_recommendation.csv!")
        
    df_raw = pd.read_csv(csv_path)
    
    # 1. Xử lý chế độ dữ liệu (Data Mode)
    if mode == 'noisy4':
        bon_nhan = ['rice', 'jute', 'maize', 'cotton']
        df = df_raw[df_raw['label'].isin(bon_nhan)].reset_index(drop=True)
        # Thêm 25% nhiễu theo đúng kịch bản Cell 0 trong notebook
        np.random.seed(42)
        noise_ratio = 0.25
        mask = np.random.rand(len(df)) < noise_ratio
        df.loc[mask, 'label'] = np.random.choice(bon_nhan, size=mask.sum())
        print(f"⚠️ [CHẾ ĐỘ THỬ NGHIỆM]: Giữ lại 4 nhãn có nhiễu 25% ({len(df)} mẫu)")
    else:
        df = df_raw.copy()
        print(f"✓ [CHẾ ĐỘ CHUẨN]: Toàn bộ 22 loại cây trồng sạch ({len(df)} mẫu)")
        
    feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    X = df[feature_cols]
    y = df['label']
    
    # 2. Train / Test Split (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[*] Tập Train: {len(X_train)} mẫu | Tập Test: {len(X_test)} mẫu.")
    
    # Chuẩn bị Scaler cho mô hình suy luận
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # 3. Tối ưu hóa siêu tham số bằng GridSearchCV theo đúng Notebook
    if run_gridsearch:
        print("\n" + "-"*65)
        print("⏳ Đang chạy GridSearchCV (5-Fold CV) để tìm siêu tham số tối ưu...")
        print("-"*65)
        
        param_grid_dt = {
            'classifier__max_depth': [4, 6, 8, 10, 12],
            'classifier__min_samples_split': [2, 5, 10],
            'classifier__criterion': ['gini', 'entropy']
        }
        param_grid_rf = {
            'classifier__n_estimators': [50, 100, 150],
            'classifier__max_depth': [6, 8, 10, 12, 16],
            'classifier__min_samples_split': [2, 5]
        }
        
        pipe_dt = Pipeline([('scaler', StandardScaler()), ('classifier', DecisionTreeClassifier(random_state=42))])
        pipe_rf = Pipeline([('scaler', StandardScaler()), ('classifier', RandomForestClassifier(random_state=42))])
        
        grid_dt = GridSearchCV(pipe_dt, param_grid_dt, cv=5, scoring='accuracy', n_jobs=-1)
        grid_rf = GridSearchCV(pipe_rf, param_grid_rf, cv=5, scoring='accuracy', n_jobs=-1)
        
        grid_dt.fit(X_train, y_train)
        grid_rf.fit(X_train, y_train)
        
        best_dt = grid_dt.best_estimator_
        best_rf = grid_rf.best_estimator_
        
        print(f"  [Decision Tree] CV Tốt nhất: {grid_dt.best_score_*100:.2f}% | Tham số: {grid_dt.best_params_}")
        print(f"  [Random Forest] CV Tốt nhất: {grid_rf.best_score_*100:.2f}% | Tham số: {grid_rf.best_params_}")
    else:
        best_dt = Pipeline([('scaler', StandardScaler()), ('classifier', DecisionTreeClassifier(max_depth=8, random_state=42))])
        best_rf = Pipeline([('scaler', StandardScaler()), ('classifier', RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42))])
        best_dt.fit(X_train, y_train)
        best_rf.fit(X_train, y_train)
        
    # 4. Kiểm tra độ lệch và đánh giá Overfitting (Gap = Train Acc - Test Acc)
    dt_train_acc = accuracy_score(y_train, best_dt.predict(X_train)) * 100
    dt_test_acc = accuracy_score(y_test, best_dt.predict(X_test)) * 100
    dt_gap = dt_train_acc - dt_test_acc
    
    rf_train_acc = accuracy_score(y_train, best_rf.predict(X_train)) * 100
    rf_test_acc = accuracy_score(y_test, best_rf.predict(X_test)) * 100
    rf_gap = rf_train_acc - rf_test_acc
    
    print("\n" + "="*70)
    print(" BẢNG ĐÁNH GIÁ HIỆU NĂNG & KIỂM ĐỊNH QUÁ KHỚP (OVERFITTING GAP)")
    print("="*70)
    print(f"{'Mô hình':<20} | {'Train Acc':<12} | {'Test Acc':<12} | {'Gap (Train - Test)':<18} | {'Trạng thái'}")
    print("-"*70)
    dt_status = "Good Fit (Tốt)" if dt_gap <= 5.0 else "Overfitting (Quá khớp)"
    rf_status = "Good Fit (Tốt)" if rf_gap <= 5.0 else "Overfitting (Quá khớp)"
    print(f"{'Decision Tree':<20} | {dt_train_acc:>10.2f}% | {dt_test_acc:>10.2f}% | {dt_gap:>16.2f}% | {dt_status}")
    print(f"{'Random Forest':<20} | {rf_train_acc:>10.2f}% | {rf_test_acc:>10.2f}% | {rf_gap:>16.2f}% | {rf_status}")
    print("="*70)
    
    # 5. Vẽ biểu đồ so sánh Train vs Test Accuracy như trong Cell 33 của Notebook
    plot_data = {
        'Mô hình': ['Decision Tree', 'Decision Tree', 'Random Forest', 'Random Forest'],
        'Tập dữ liệu': ['Tập Học (Train)', 'Tập Thi (Test)', 'Tập Học (Train)', 'Tập Thi (Test)'],
        'Độ chính xác (%)': [dt_train_acc, dt_test_acc, rf_train_acc, rf_test_acc]
    }
    df_plot = pd.DataFrame(plot_data)
    
    plt.figure(figsize=(9, 5))
    ax = sns.barplot(x='Mô hình', y='Độ chính xác (%)', hue='Tập dữ liệu', data=df_plot, palette='Set2')
    plt.title('So Sánh Trực Quan Hiệu Năng Mô Hình (Theo Chuẩn Notebook)', fontsize=13, fontweight='bold', pad=15)
    plt.ylabel('Độ chính xác (%)', fontsize=11)
    plt.xlabel('Thuật toán Machine Learning', fontsize=11)
    plt.ylim(0, 115)
    for p in ax.patches:
        height = p.get_height()
        if height > 0:
            ax.annotate(f"{height:.2f}%", (p.get_x() + p.get_width() / 2., height),
                        ha='center', va='center', xytext=(0, 6), textcoords='offset points',
                        fontsize=10, fontweight='bold')
    plt.tight_layout()
    chart_file = os.path.join(os.path.dirname(__file__), 'accuracy_comparison.png')
    plt.savefig(chart_file, dpi=300)
    plt.close()
    print(f"\n[✓] Đã xuất biểu đồ so sánh Train vs Test: '{chart_file}'")
    
    # 6. Đóng gói mô hình Random Forest tốt nhất để phục vụ Web App
    models_dir = os.path.join(os.path.dirname(__file__), 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    # Lấy mô hình classifier nguyên bản bên trong Pipeline để tái sử dụng
    final_rf_classifier = best_rf.named_steps['classifier']
    
    model_file = os.path.join(models_dir, 'crop_model.pkl')
    scaler_file = os.path.join(models_dir, 'scaler.pkl')
    metadata_file = os.path.join(models_dir, 'metadata.json')
    
    joblib.dump(final_rf_classifier, model_file)
    joblib.dump(scaler, scaler_file)
    
    metadata = {
        'model_name': 'Random Forest Classifier (Optimized via GridSearchCV)',
        'data_mode': mode,
        'features': feature_cols,
        'classes': sorted(list(final_rf_classifier.classes_)),
        'num_classes': len(final_rf_classifier.classes_),
        'train_accuracy': float(rf_train_acc),
        'test_accuracy': float(rf_test_acc),
        'overfitting_gap': float(rf_gap)
    }
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
        
    print(f"[✓] Đã cập nhật mô hình tối ưu: '{model_file}'")
    print(f"[✓] Đã cập nhật scaler:          '{scaler_file}'")
    print("\n[✓] HOÀN TẤT HUẤN LUYỆN & TỐI ƯU HÓA!")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Huấn luyện mô hình từ dữ liệu Notebook")
    parser.add_argument('--mode', choices=['full', 'noisy4'], default='full',
                        help="'full' (toàn bộ 22 cây) hoặc 'noisy4' (4 cây tạo nhiễu 25% theo bài tập)")
    parser.add_argument('--fast', action='store_true', help="Bỏ qua GridSearchCV để huấn luyện nhanh")
    args = parser.parse_args()
    
    train_and_export(mode=args.mode, run_gridsearch=(not args.fast))
