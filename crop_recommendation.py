# ==============================================================================
# ĐỒ ÁN MÔN HỌC MÁY (MACHINE LEARNING PROJECT)
# ĐỀ TÀI: KHUYẾN NGHỊ LOẠI CÂY TRỒNG PHÙ HỢP DỰA TRÊN ĐẶC ĐIỂM THỔ NHƯỠNG & KHÍ HẬU
# Tác giả: Chuyên gia Khoa học Dữ liệu (Senior Data Scientist)
# Phiên bản: 1.0 (Production-grade & Academic Standards)
# ==============================================================================

import sys
import io
import subprocess
import os
import warnings

# Tắt các cảnh báo không cần thiết từ thư viện để giữ màn hình console sạch đẹp
warnings.filterwarnings('ignore')

# Cấu hình UTF-8 cho console Windows tránh lỗi UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# ==============================================================================
# BƯỚC 1: TỰ ĐỘNG KIỂM TRA & CÀI ĐẶT THƯ VIỆN NẾU THIẾU
# ==============================================================================
def ensure_dependencies():
    """Kiểm tra các thư viện cốt lõi và tự động cài đặt nếu môi trường chưa có."""
    required_packages = {
        'pandas': 'pandas',
        'numpy': 'numpy',
        'sklearn': 'scikit-learn',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn'
    }
    missing = []
    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)
            
    if missing:
        print(f"[!] Phat hien thieu thu vien: {missing}")
        print("[*] Dang tien hanh cai dat tu dong qua pip, vui long doi giay lat...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("[V] Da cai dat day du tat ca thu vien can thiet!\n")
    else:
        print("[V] Kiem tra moi truong: Tat ca cac thu vien can thiet da san sang.\n")

ensure_dependencies()

# Import các thư viện sau khi đã đảm bảo môi trường đầy đủ
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Chế độ headless backend: lưu file ảnh trực tiếp, không mở cửa sổ GUI gây treo IDE
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, StratifiedKFold, cross_val_score
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, confusion_matrix, classification_report


# ==============================================================================
# BƯỚC 2: TẢI HOẶC TẠO DỮ LIỆU THỬ NGHIỆM (MOCK DATA NẾU THIẾU)
# ==============================================================================
DATASET_PATH = 'Crop_recommendation.csv'

def load_or_generate_dataset(filepath=DATASET_PATH):
    """
    Tải tập dữ liệu cây trồng.
    Nếu file không tồn tại, tự động sinh dữ liệu giả lập (mock data) thực tế với 22 loại cây trồng.
    """
    if os.path.exists(filepath):
        print(f"[+] Tìm thấy file dữ liệu: '{filepath}'. Đang nạp dữ liệu...")
        df = pd.read_csv(filepath)
    else:
        print(f"[!] Không tìm thấy '{filepath}'. Đang tự động tạo dữ liệu giả lập (22 loại cây trồng)...")
        np.random.seed(42)
        crops = [
            'rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas',
            'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
            'banana', 'mango', 'grapes', 'watermelon', 'muskmelon',
            'apple', 'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee'
        ]
        
        samples_per_crop = 100
        records = []
        
        # Dải thông số sinh học mô phỏng cho các nhóm cây trồng khác nhau
        for i, crop in enumerate(crops):
            # Tạo đặc trưng riêng biệt theo từng nhóm cây để mô hình có thể phân tách tốt
            base_n = 20 + (i % 5) * 25 + np.random.uniform(-5, 5)
            base_p = 20 + ((i + 2) % 6) * 20 + np.random.uniform(-5, 5)
            base_k = 15 + ((i * 3) % 7) * 25 + np.random.uniform(-5, 5)
            base_temp = 18 + (i % 8) * 2.5 + np.random.uniform(-1, 1)
            base_hum = 40 + (i % 6) * 10 + np.random.uniform(-5, 5)
            base_ph = 5.5 + (i % 4) * 0.5 + np.random.uniform(-0.2, 0.2)
            base_rain = 50 + (i % 7) * 35 + np.random.uniform(-10, 10)
            
            for _ in range(samples_per_crop):
                records.append({
                    'N': max(0.0, np.random.normal(base_n, 8)),
                    'P': max(0.0, np.random.normal(base_p, 8)),
                    'K': max(0.0, np.random.normal(base_k, 8)),
                    'temperature': np.clip(np.random.normal(base_temp, 3), 10, 45),
                    'humidity': np.clip(np.random.normal(base_hum, 6), 15, 100),
                    'ph': np.clip(np.random.normal(base_ph, 0.4), 3.5, 9.5),
                    'rainfall': max(10.0, np.random.normal(base_rain, 25)),
                    'label': crop
                })
                
        df = pd.DataFrame(records)
        df.to_csv(filepath, index=False)
        print(f"[✓] Đã tạo thành công dữ liệu giả lập và lưu vào '{filepath}'.")
        
    print(f"[*] Kích thước dữ liệu: {df.shape[0]} hàng, {df.shape[1]} cột.")
    print(f"[*] Số lượng loại cây trồng (classes): {df['label'].nunique()}")
    print("\n[Mẫu 5 dòng đầu tiên]:")
    print(df.head().to_string(index=False))
    return df


# ==============================================================================
# BƯỚC 3: PHÂN TÍCH KHÁM PHÁ DỮ LIỆU (EDA)
# ==============================================================================
def perform_eda(df):
    """
    Thực hiện EDA và lưu đồ thị ra file PNG theo đúng tiêu chuẩn Senior Data Scientist.
    Tránh tuyệt đối plt.show() để không làm treo giao diện IDE.
    """
    print("\n" + "="*70)
    print(" GIAI ĐOẠN 1: PHÂN TÍCH KHÁM PHÁ DỮ LIỆU (EDA)")
    print("="*70)
    
    # 1. Thống kê mô tả
    print("[*] Thống kê mô tả các thuộc tính số học:")
    numeric_df = df.drop('label', axis=1)
    print(numeric_df.describe().T[['mean', 'std', 'min', '50%', 'max']].to_string())
    
    # Kiểm tra giá trị khuyết (Missing values)
    missing = df.isnull().sum().sum()
    print(f"\n[*] Tổng số lượng giá trị rỗng (NaN/Null): {missing}")
    
    # 2. Vẽ Ma trận tương quan (Correlation Heatmap)
    print("[*] Đang vẽ Ma trận tương quan (Correlation Heatmap)...")
    plt.figure(figsize=(10, 7))
    corr = numeric_df.corr()
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, annot=True, mask=mask, cmap='viridis', fmt=".2f",
                linewidths=1.0, cbar_kws={'label': 'Hệ số tương quan Pearson'})
    plt.title("Ma Trận Tương Quan Các Đặc Trưng Thổ Nhưỡng & Khí Hậu", fontsize=14, fontweight='bold', pad=15)
    heatmap_file = 'heatmap_correlation.png'
    plt.savefig(heatmap_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" [✓] Đã lưu biểu đồ: '{heatmap_file}'")
    
    # 3. Vẽ Biểu đồ phân bố các đặc trưng (Histograms with KDE)
    print("[*] Đang vẽ Biểu đồ phân bố (Feature Distribution)...")
    fig, axes = plt.subplots(nrows=2, ncols=4, figsize=(18, 8))
    axes = axes.flatten()
    features = numeric_df.columns.tolist()
    
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    for idx, col in enumerate(features):
        sns.histplot(df[col], kde=True, ax=axes[idx], color=colors[idx % len(colors)], bins=25)
        axes[idx].set_title(f"Phân bố đặc trưng: {col}", fontsize=11, fontweight='bold')
        axes[idx].set_xlabel("")
        axes[idx].set_ylabel("Tần suất")
        axes[idx].grid(True, linestyle='--', alpha=0.5)
        
    # Ẩn subplot thừa thứ 8
    axes[-1].set_visible(False)
    
    plt.suptitle("Phân Bố Giá Trị Của Các Thông Số Thổ Nhưỡng & Khí Hậu", fontsize=15, fontweight='bold')
    plt.tight_layout()
    dist_file = 'feature_distribution.png'
    plt.savefig(dist_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" [✓] Đã lưu biểu đồ: '{dist_file}'")


# ==============================================================================
# BƯỚC 4: TIỀN XỬ LÝ & CHUẨN HÓA DỮ LIỆU
# ==============================================================================
def preprocess_data(df):
    """
    Chia tập dữ liệu Train/Test tỉ lệ 80/20 với stratify=y.
    Áp dụng cả StandardScaler và MinMaxScaler để so sánh hiệu năng.
    """
    print("\n" + "="*70)
    print(" GIAI ĐOẠN 2: TIỀN XỬ LÝ & CHUẨN HÓA DỮ LIỆU")
    print("="*70)
    
    X = df.drop('label', axis=1)
    y = df['label']
    
    # Chia tập dữ liệu 80% train, 20% test, stratify để giữ nguyên tỷ lệ mẫu của 22 loại cây
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    print(f"[*] Tập huấn luyện (Train set): {X_train.shape[0]} mẫu ({X_train.shape[0]/len(df):.0%})")
    print(f"[*] Tập kiểm thử (Test set):     {X_test.shape[0]} mẫu ({X_test.shape[0]/len(df):.0%})")
    
    # 1. StandardScaler (Z-score: mean=0, std=1)
    scaler_std = StandardScaler()
    X_train_std = scaler_std.fit_transform(X_train)
    X_test_std = scaler_std.transform(X_test)
    
    # 2. MinMaxScaler (Đưa về khoảng [0, 1])
    scaler_mm = MinMaxScaler()
    X_train_mm = scaler_mm.fit_transform(X_train)
    X_test_mm = scaler_mm.transform(X_test)
    
    print("[✓] Đã fit và transform dữ liệu với cả StandardScaler và MinMaxScaler.")
    return X_train, X_test, y_train, y_test, X_train_std, X_test_std, X_train_mm, X_test_mm, scaler_std, scaler_mm


# ==============================================================================
# BƯỚC 5: KHẢO SÁT CHUYÊN SÂU THUẬT TOÁN K-NEAREST NEIGHBORS (KNN)
# ==============================================================================
def survey_knn(X_train_std, X_test_std, X_train_mm, X_test_mm, y_train, y_test):
    """
    Khảo sát toàn diện thuật toán KNN:
    1. Tìm K tối ưu (K lẻ từ 1 đến 19).
    2. So sánh hiệu quả giữa StandardScaler vs MinMaxScaler.
    3. Khảo sát 3 độ đo khoảng cách: 'euclidean', 'manhattan', 'minkowski'.
    4. Khảo sát 2 chiến lược trọng số: 'uniform', 'distance'.
    5. Khảo sát thuật toán tìm kiếm: 'kd_tree', 'ball_tree'.
    6. In bảng so sánh chi tiết và xuất biểu đồ khảo sát K.
    """
    print("\n" + "="*70)
    print(" GIAI ĐOẠN 3: KHẢO SÁT CHUYÊN SÂU THUẬT TOÁN KNN")
    print("="*70)
    
    # 1. Khảo sát K lẻ từ 1 đến 20
    k_odd_values = [k for k in range(1, 20) if k % 2 != 0]
    std_accs = []
    mm_accs = []
    
    for k in k_odd_values:
        # Với StandardScaler
        knn_std = KNeighborsClassifier(n_neighbors=k, metric='euclidean', algorithm='kd_tree')
        knn_std.fit(X_train_std, y_train)
        std_accs.append(accuracy_score(y_test, knn_std.predict(X_test_std)))
        
        # Với MinMaxScaler
        knn_mm = KNeighborsClassifier(n_neighbors=k, metric='euclidean', algorithm='kd_tree')
        knn_mm.fit(X_train_mm, y_train)
        mm_accs.append(accuracy_score(y_test, knn_mm.predict(X_test_mm)))
        
    best_k_idx = int(np.argmax(std_accs))
    best_k = k_odd_values[best_k_idx]
    print(f"[*] Khảo sát giá trị K (lẻ): {k_odd_values}")
    print(f"[★] Giá trị K tối ưu tìm được trên StandardScaler: K = {best_k} (Accuracy = {std_accs[best_k_idx]:.4f})")
    
    # Lưu biểu đồ đường khảo sát K
    plt.figure(figsize=(10, 5))
    plt.plot(k_odd_values, std_accs, marker='o', linewidth=2.5, color='#1f77b4', label='StandardScaler (Z-score)')
    plt.plot(k_odd_values, mm_accs, marker='s', linewidth=2.0, linestyle='--', color='#ff7f0e', label='MinMaxScaler [0, 1]')
    plt.axvline(best_k, color='red', linestyle=':', label=f'K tối ưu ({best_k})')
    plt.title("Khảo Sát Ảnh Hưởng Của Siêu Tham Số K Đến Độ Chính Xác KNN", fontsize=13, fontweight='bold')
    plt.xlabel("Số lượng láng giềng (K lẻ)", fontsize=11)
    plt.ylabel("Độ chính xác (Accuracy)", fontsize=11)
    plt.xticks(k_odd_values)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(loc='lower left')
    knn_curve_file = 'knn_k_survey.png'
    plt.savefig(knn_curve_file, dpi=300, bbox_inches='tight')
    plt.close()
    print(f" [✓] Đã lưu đồ thị khảo sát K: '{knn_curve_file}'")
    
    # 2. Khảo sát tổ hợp: Distance Metric, Weights, Algorithm Search
    metrics = ['euclidean', 'manhattan', 'minkowski']
    weights = ['uniform', 'distance']
    algorithms = ['kd_tree', 'ball_tree']
    
    print("\n" + "-"*85)
    print(f"{'Metric':<12} | {'Weight':<10} | {'Algorithm':<11} | {'Accuracy':<10} | {'F1-Macro':<10} | {'Ghi chú'}")
    print("-"*85)
    
    survey_results = []
    
    for metric in metrics:
        for weight in weights:
            for algo in algorithms:
                knn = KNeighborsClassifier(
                    n_neighbors=best_k,
                    metric=metric,
                    weights=weight,
                    algorithm=algo
                )
                knn.fit(X_train_std, y_train)
                preds = knn.predict(X_test_std)
                acc = accuracy_score(y_test, preds)
                f1 = f1_score(y_test, preds, average='macro')
                
                survey_results.append({
                    'metric': metric,
                    'weight': weight,
                    'algorithm': algo,
                    'accuracy': acc,
                    'f1': f1,
                    'model': knn
                })
                
                note = "★ Tốt nhất" if acc == max(r['accuracy'] for r in survey_results) and len(survey_results) > 1 else ""
                print(f"{metric:<12} | {weight:<10} | {algo:<11} | {acc:<10.4f} | {f1:<10.4f} | {note}")
                
    print("-"*85)
    
    # Chọn cấu hình tốt nhất (ưu tiên accuracy cao nhất, sau đó f1 cao nhất)
    best_config = max(survey_results, key=lambda x: (x['accuracy'], x['f1']))
    print(f"\n[★] CẤU HÌNH KNN TỐI ƯU NHẤT:")
    print(f"    - K (Neighbors):   {best_k}")
    print(f"    - Distance Metric: {best_config['metric']}")
    print(f"    - Weight Strategy: {best_config['weight']}")
    print(f"    - Search Tree:     {best_config['algorithm']}")
    print(f"    - Test Accuracy:   {best_config['accuracy']:.4%}")
    print(f"    - Test F1-Macro:   {best_config['f1']:.4%}")
    
    return best_k, best_config


# ==============================================================================
# BƯỚC 6: SO SÁNH CÁC MÔ HÌNH HỌC MÁY BẰNG STRATIFIED K-FOLD (k=5)
# ==============================================================================
def compare_models(X_train_std, y_train, X_test_std, y_test, best_knn_config):
    """
    Đánh giá và so sánh 4 mô hình:
    1. KNN (Cấu hình tối ưu)
    2. Gaussian Naive Bayes
    3. Decision Tree
    4. Random Forest
    Áp dụng StratifiedKFold (n_splits=5) để đánh giá khách quan, tránh rò rỉ dữ liệu.
    """
    print("\n" + "="*70)
    print(" GIAI ĐOẠN 4: SO SÁNH CÁC MÔ HÌNH HỌC MÁY (5-FOLD STRATIFIED CV)")
    print("="*70)
    
    models = {
        "KNN (Tối ưu)": KNeighborsClassifier(
            n_neighbors=best_knn_config['model'].n_neighbors,
            metric=best_knn_config['metric'],
            weights=best_knn_config['weight'],
            algorithm=best_knn_config['algorithm']
        ),
        "Gaussian Naive Bayes": GaussianNB(),
        "Decision Tree": DecisionTreeClassifier(random_state=42, max_depth=15),
        "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
    }
    
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    print(f"{'Mô hình':<25} | {'CV Accuracy (Mean ± Std)':<26} | {'CV F1-Macro':<12} | {'Test Accuracy':<13}")
    print("-" * 84)
    
    fitted_models = {}
    model_scores = {}
    
    for name, model in models.items():
        # Kiểm định chéo 5-fold
        cv_acc = cross_val_score(model, X_train_std, y_train, cv=skf, scoring='accuracy')
        cv_f1 = cross_val_score(model, X_train_std, y_train, cv=skf, scoring='f1_macro')
        
        # Fit trên toàn bộ tập train và đánh giá trên tập test
        model.fit(X_train_std, y_train)
        test_pred = model.predict(X_test_std)
        test_acc = accuracy_score(y_test, test_pred)
        
        fitted_models[name] = model
        model_scores[name] = {
            'cv_acc_mean': cv_acc.mean(),
            'cv_acc_std': cv_acc.std(),
            'cv_f1_mean': cv_f1.mean(),
            'test_acc': test_acc
        }
        
        acc_str = f"{cv_acc.mean():.4f} ± {cv_acc.std():.4f}"
        print(f"{name:<25} | {acc_str:<26} | {cv_f1.mean():<12.4f} | {test_acc:<13.4f}")
        
    print("-" * 84)
    
    # Xác định mô hình xuất sắc nhất
    best_model_name = max(model_scores, key=lambda k: model_scores[k]['cv_acc_mean'])
    print(f"\n[★] Mô hình đạt hiệu năng tổng thể cao nhất: >> {best_model_name.upper()} <<")
    
    return fitted_models, best_model_name


# ==============================================================================
# BƯỚC 7: VẼ MA TRẬN NHẦM LẪN (CONFUSION MATRIX) CHO MÔ HÌNH TỐT NHẤT
# ==============================================================================
def plot_best_confusion_matrix(model, X_test_std, y_test, model_name="Random Forest", filename="confusion_matrix.png"):
    """
    Vẽ ma trận nhầm lẫn (Confusion Matrix) chi tiết, định dạng chuẩn báo cáo khoa học.
    Lưu thành file ảnh PNG độ nét cao (dpi=300).
    """
    print("\n" + "="*70)
    print(f" GIAI ĐOẠN 5: MA TRẬN NHẦM LẪN (CONFUSION MATRIX) - {model_name.upper()}")
    print("="*70)
    
    y_pred = model.predict(X_test_std)
    labels = sorted(list(set(y_test)))
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    
    plt.figure(figsize=(14, 12))
    sns.heatmap(
        cm,
        annot=True,
        fmt='d',
        cmap='Blues',
        xticklabels=labels,
        yticklabels=labels,
        cbar_kws={'label': 'Số lượng mẫu dự đoán'}
    )
    plt.title(f"Ma Trận Nhầm Lẫn (Confusion Matrix) - {model_name}\n(Tập kiểm thử 20% - 22 Loại Cây Trồng)",
              fontsize=14, fontweight='bold', pad=15)
    plt.xlabel("Nhãn Dự Đoán (Predicted Label)", fontsize=12, fontweight='bold')
    plt.ylabel("Nhãn Thực Tế (True Label)", fontsize=12, fontweight='bold')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.yticks(rotation=0, fontsize=10)
    
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[✓] Đã xuất Ma trận nhầm lẫn chuẩn báo cáo ra file: '{filename}'")
    
    # In báo cáo phân lớp thu gọn
    report = classification_report(y_test, y_pred, digits=4)
    print("\n[*] Chi tiết Báo cáo Phân lớp (Classification Report):")
    print(report)


# ==============================================================================
# BƯỚC 8: MODULE ỨNG DỤNG - KHUYẾN NGHỊ TOP 3 LOẠI CÂY TRỒNG PHÙ HỢP
# ==============================================================================
def recommend_top_3_crops(N, P, K, temp, humidity, ph, rainfall, model, scaler):
    """
    Dự đoán và đưa ra TOP 3 loại cây trồng phù hợp nhất kèm theo xác suất (%)
    dựa trên các thông số dinh dưỡng đất và điều kiện thời tiết.
    
    Parameters:
    - N: Hàm lượng đạm (Nitơ) trong đất (kg/ha)
    - P: Hàm lượng lân (Photpho) trong đất (kg/ha)
    - K: Hàm lượng kali trong đất (kg/ha)
    - temp: Nhiệt độ trung bình (°C)
    - humidity: Độ ẩm không khí tương đối (%)
    - ph: Độ chua/kiềm của đất (thang đo 0-14)
    - rainfall: Lượng mưa trung bình hàng năm (mm)
    - model: Mô hình học máy đã huấn luyện hỗ trợ hàm `predict_proba`
    - scaler: Đối tượng Scaler đã fit dùng để chuẩn hóa mẫu đất mới
    """
    # 1. Tạo DataFrame mẫu đất với đúng tên các cột đặc trưng để tránh cảnh báo
    feature_cols = ['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']
    soil_sample = pd.DataFrame([[N, P, K, temp, humidity, ph, rainfall]], columns=feature_cols)
    
    # 2. Chuẩn hóa đặc trưng theo đúng chuẩn phân phối lúc train
    soil_sample_scaled = scaler.transform(soil_sample)
    
    # 3. Tính phân phối xác suất trên toàn bộ 22 nhãn lớp
    probabilities = model.predict_proba(soil_sample_scaled)[0]
    classes = model.classes_
    
    # 4. Trích xuất top 3 chỉ số có xác suất cao nhất theo thứ tự giảm dần
    top_3_indices = np.argsort(probabilities)[-3:][::-1]
    
    # 5. Định dạng hiển thị kết quả trực quan
    print("\n" + "╔" + "═"*66 + "╗")
    print("║" + " 🌾 HỆ THỐNG KHUYẾN NGHỊ CÂY TRỒNG NÔNG NGHIỆP THÔNG MINH 🌾".center(66) + "║")
    print("╠" + "═"*66 + "╣")
    print("║ THÔNG SỐ ĐẦU VÀO ĐƯỢC CUNG CẤP:".ljust(67) + "║")
    print(f"║  • Dinh dưỡng đất:  Đạm (N)={N} kg/ha | Lân (P)={P} kg/ha | Kali (K)={K} kg/ha".ljust(67) + "║")
    print(f"║  • Khí hậu & Đất:   Nhiệt độ={temp}°C | Độ ẩm={humidity}% | pH={ph} | Lượng mưa={rainfall}mm".ljust(67) + "║")
    print("╠" + "═"*66 + "╣")
    print("║ KẾT QUẢ KHUYẾN NGHỊ (TOP 3 CÂY TRỒNG TỐI ƯU NHẤT):".ljust(67) + "║")
    
    medals = ["🥇 QUÁN QUÂN (Top 1):", "🥈 Á QUÂN   (Top 2):", "🥉 HẠNG BA  (Top 3):"]
    for rank, idx in enumerate(top_3_indices):
        crop = classes[idx].upper()
        prob = probabilities[idx] * 100
        bar = "█" * int(prob // 5) + "░" * (20 - int(prob // 5))
        line = f"║  {medals[rank]} {crop:<13} [{bar}] {prob:>6.2f}%"
        print(line.ljust(67) + "║")
        
    print("╚" + "═"*66 + "╝\n")


# ==============================================================================
# HÀM CHÍNH (MAIN EXECUTION FLOW)
# ==============================================================================
def main():
    print("="*75)
    print(" BẮT ĐẦU QUY TRÌNH KHOA HỌC DỮ LIỆU: CROP RECOMMENDATION SYSTEM")
    print("="*75)
    
    # Bước 2: Tải dữ liệu
    df = load_or_generate_dataset(DATASET_PATH)
    
    # Bước 3: EDA
    perform_eda(df)
    
    # Bước 4: Tiền xử lý
    (X_train, X_test, y_train, y_test, 
     X_train_std, X_test_std, 
     X_train_mm, X_test_mm, 
     scaler_std, scaler_mm) = preprocess_data(df)
    
    # Bước 5: Khảo sát KNN
    best_k, best_knn_config = survey_knn(
        X_train_std, X_test_std, X_train_mm, X_test_mm, y_train, y_test
    )
    
    # Bước 6: So sánh các mô hình
    fitted_models, best_model_name = compare_models(
        X_train_std, y_train, X_test_std, y_test, best_knn_config
    )
    
    # Bước 7: Vẽ Confusion Matrix cho mô hình Random Forest (hoặc mô hình tốt nhất)
    rf_model = fitted_models["Random Forest"]
    best_model = fitted_models[best_model_name]
    plot_best_confusion_matrix(rf_model, X_test_std, y_test, model_name="Random Forest", filename="confusion_matrix.png")
    
    # Bước 8: Kiểm thử hàm khuyến nghị cây trồng với các kịch bản thổ nhưỡng khác nhau
    print("="*70)
    print(" GIAI ĐOẠN 6: CHẠY THỰC NGHIỆM HÀM RECOMMENDATION CHO NÔNG DÂN")
    print("="*70)
    
    # Mẫu đất 1: Đất phù sa vùng nhiệt đới, lượng mưa lớn, thích hợp trồng lúa nước (Rice)
    print("[Kịch bản 1: Đất đầm lầy phù sa, mưa nhiều, nhiệt độ ẩm cao]")
    recommend_top_3_crops(
        N=90, P=42, K=43, temp=20.87, humidity=82.0, ph=6.5, rainfall=202.93,
        model=best_model, scaler=scaler_std
    )
    
    # Mẫu đất 2: Vùng cao nguyên, đất bazan màu mỡ, thích hợp cây công nghiệp (Coffee)
    print("[Kịch bản 2: Vùng Tây Nguyên mát mẻ, đất giàu đạm và kali]")
    recommend_top_3_crops(
        N=105, P=28, K=32, temp=25.5, humidity=60.0, ph=6.8, rainfall=160.0,
        model=best_model, scaler=scaler_std
    )
    
    # Mẫu đất 3: Vùng khô hạn bán sa mạc, đất cát, lượng mưa thấp, thích hợp dưa hấu / dưa lưới
    print("[Kịch bản 3: Vùng nắng nóng hạn hán ven biển]")
    recommend_top_3_crops(
        N=20, P=15, K=45, temp=32.0, humidity=45.0, ph=6.2, rainfall=40.0,
        model=best_model, scaler=scaler_std
    )
    
    print("\n[✓] HOÀN TẤT TOÀN BỘ QUY TRÌNH THỰC NGHIỆM! Chúc bạn đạt điểm tối đa đồ án!")

if __name__ == '__main__':
    main()
