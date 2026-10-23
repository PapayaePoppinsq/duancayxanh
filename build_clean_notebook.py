import json
import os

def create_cleaned_notebook():
    with open('notebook.ipynb', 'r', encoding='utf-8') as f:
        nb = json.load(f)

    # Cell 0: Thay thế đường dẫn Kaggle bị lỗi bằng đường dẫn tự động tìm file
    cell_0_code = """# =====================================================================
# BƯỚC 1: ĐỌC DỮ LIỆU TỰ ĐỘNG & TÙY CHỌN CHẾ ĐỘ PHÂN TÍCH
# =====================================================================
import os
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder

# Tự động tìm đường dẫn file dữ liệu (Local Windows, Linux hoặc Kaggle)
def find_dataset():
    candidates = [
        'Crop_recommendation.csv',
        'data/Crop_recommendation.csv',
        '../Crop_recommendation.csv',
        '/kaggle/input/datasets/cong2nghin/inputphanloai/Crop_recommendation.csv'
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return 'Crop_recommendation.csv'

file_path = find_dataset()
print(f"[*] Đang nạp dữ liệu từ: '{file_path}'")
df_raw = pd.read_csv(file_path)

# =====================================================================
# TÙY CHỌN CHẾ ĐỘ DỮ LIỆU (DATA MODE):
# ---------------------------------------------------------------------
# - False: Sử dụng ĐẦY ĐỦ 22 LOẠI CÂY (Dữ liệu sạch chuẩn - Khuyên dùng, 
#          khớp hoàn toàn với các nhận xét và bảng đánh giá trong bài).
# - True:  Chế độ thử nghiệm 4 loại cây tạo nhiễu 25% (để khảo sát Overfitting).
# =====================================================================
CHE_DO_THU_NGHIEM_NHIEU_4_CAY = False

if CHE_DO_THU_NGHIEM_NHIEU_4_CAY:
    bon_nhan_lua_chon = ['rice', 'jute', 'maize', 'cotton']
    df = df_raw[df_raw['label'].isin(bon_nhan_lua_chon)].reset_index(drop=True)
    
    # Tạo nhiễu 25% gán sai nhãn để thử thách mô hình
    np.random.seed(42)
    noise_ratio = 0.25
    mask = np.random.rand(len(df)) < noise_ratio
    df.loc[mask, 'label'] = np.random.choice(bon_nhan_lua_chon, size=mask.sum())
    print(f"⚠️ [CHẾ ĐỘ THỬ NGHIỆM]: Giữ 4 nhãn có nhiễu 25% ({len(df)} mẫu)")
else:
    df = df_raw.copy()
    print(f"✓ [CHẾ ĐỘ CHUẨN]: Sử dụng toàn bộ 22 loại cây trồng ({len(df)} mẫu, dữ liệu sạch)")

df_rut_gon = df.copy()

print(f"Số lượng mẫu dữ liệu: {df_rut_gon.shape[0]} hàng")
print(f"Số lượng thuộc tính:   {df_rut_gon.shape[1]} cột")
print(f"Danh sách nhãn:        {df_rut_gon['label'].unique()}")
display(df_rut_gon.head())
"""

    nb['cells'][0]['source'] = [line + '\n' for line in cell_0_code.splitlines()]

    # Lưu notebook đã sửa lỗi
    output_filename = 'notebook_hoan_chinh.ipynb'
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(nb, f, ensure_ascii=False, indent=2)

    print(f"[V] Da tao thanh cong file: {output_filename}")

if __name__ == '__main__':
    create_cleaned_notebook()
