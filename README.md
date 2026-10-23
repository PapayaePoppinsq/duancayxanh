# 🌾 AgriBot AI — Hệ Thống Khuyến Nghị Cây Trồng Thông Minh

> Ứng dụng Học máy (Machine Learning) hỗ trợ nông nghiệp chính xác: Dự đoán loại cây trồng tối ưu dựa trên 7 chỉ số thổ nhưỡng & vi khí hậu, phân tích cân bằng N-P-K và đưa ra phác đồ bón phân định lượng chi tiết.

---

## 🌟 Tính Năng Nổi Bật

- 🌿 **Giao diện Sinh Thái Hiện Đại (Eco-Green Design)**: Tông màu xanh lá cây sinh thái sang trọng, responsive, mượt mà.
- 🔐 **Hệ thống Tài khoản & Xác thực**: Đăng ký, đăng nhập bảo mật với mã hóa mật khẩu (`werkzeug.security`) và lưu trữ SQLite.
- 🧠 **Mô hình Học Máy Tối Ưu (Random Forest Classifier)**: Đạt độ chính xác kiểm thử **99.55%** (5-Fold Cross Validation), kiểm soát Overfitting Gap chỉ **0.40%**.
- 🌱 **Phác Đồ Bón Phân Định Lượng (NPK Advisory)**: So sánh mẫu đất thực tế với nhu cầu tối ưu của cây trồng để tính toán lượng Urê (46% N), Supe Lân (16% P₂O₅) và Kali Clorua (KCl 60%) cần bón (kg/ha).
- 📊 **Khám Phá Dữ Liệu Thực Nghiệm (EDA & Dataset Explorer)**: Tra cứu nhanh nhu cầu chuẩn của 22 loài cây trồng trên 2.200 mẫu khảo sát.
- ⚡ **So Sánh Mô Hình Học Máy (Model Benchmark)**: Đối sánh trực quan giữa Random Forest, Gaussian Naive Bayes, SVM, KNN và Decision Tree.
- 🎯 **Mức Độ Quan Trọng Của 7 Đặc Trưng (Feature Importance)**: Lượng mưa (22.3%), Độ ẩm (21.7%), Kali (18.3%), Lân (14.6%), Đạm (10.2%), Nhiệt độ (7.6%), Độ pH (5.4%).
- 📜 **Lịch Sử Đo Đạc & Nhật Ký Canh Tác (Field History)**: Tự động lưu trữ lịch sử theo tài khoản, hỗ trợ nạp lại thông số 1-click.

---

## 📁 Cấu Trúc Dự Án

```
├── Crop_recommendation.csv    # Bộ dữ liệu 2.200 mẫu nông nghiệp (22 loại cây)
├── DESIGN.md                  # Tài liệu quy chuẩn thiết kế UI/UX
├── code/                      # Thư mục mã nguồn ứng dụng web Flask
│   ├── app.py                 # Máy chủ Flask chính & các API RESTful
│   ├── database.py            # Quản trị cơ sở dữ liệu SQLite & Users/History
│   ├── train.py               # Quy trình huấn luyện & tối ưu mô hình ML
│   ├── predict.py             # Module suy luận dự đoán
│   ├── advisor.py             # Hệ thống luật chuyên gia nông học & phác đồ phân bón
│   ├── requirements.txt       # Danh sách thư viện phụ thuộc
│   ├── models/                # File mô hình Random Forest (.pkl) & Scaler
│   └── templates/             # Giao diện HTML (Jinja2)
│       ├── index.html         # Bảng điều khiển dự đoán & phân tích chính
│       ├── login.html         # Giao diện Đăng nhập Eco-Green
│       └── register.html      # Giao diện Đăng ký Eco-Green
└── README.md                  # Hướng dẫn dự án
```

---

## 🚀 Hướng Dẫn Cài Đặt & Chạy Ứng Dụng

### 1. Cài đặt môi trường Python
Yêu cầu Python >= 3.9. Di chuyển vào thư mục `code` và cài đặt thư viện:

```bash
cd code
pip install -r requirements.txt
```

### 2. (Tùy chọn) Huấn luyện lại mô hình
Nếu muốn huấn luyện lại mô hình với GridSearchCV:

```bash
python train.py
```

### 3. Khởi chạy máy chủ Web
Chạy ứng dụng Flask:

```bash
python app.py
```

Truy cập trên trình duyệt tại: **http://127.0.0.1:5000** hoặc **http://localhost:5000**

---

## 👥 Tài Khoản Mẫu Trải Nghiệm Nhanh
- **Email**: `nongdan@gmail.com`
- **Mật khẩu**: `password123`
*(Hoặc tạo tài khoản mới tại trang Đăng ký)*
