"""Dự đoán rủi ro vỡ nợ bằng model Random Forest đã huấn luyện (models/loan_default_model.pkl).

Tiền xử lý phải giống lúc huấn luyện: mã hóa học vấn theo edu_order, nhị phân Yes/No,
one-hot cho nghề nghiệp, tình trạng hôn nhân và mục đích vay (bỏ nhóm tham chiếu).
"""

from pathlib import Path

import joblib
import pandas as pd

MODEL_PATH = Path(__file__).parent / "models" / "loan_default_model.pkl"

# Nhóm tham chiếu bị bỏ khi one-hot (khớp với lúc huấn luyện)
EMPLOYMENT_CATS = ["Part-time", "Self-employed", "Unemployed"]
MARITAL_CATS = ["Married", "Single"]
PURPOSE_CATS = ["Business", "Education", "Home", "Other"]
YES_NO = ["HasMortgage", "HasDependents", "HasCoSigner"]


def load_bundle() -> dict:
    """Tải model và thông tin tiền xử lý. Chỉ tải file model tin cậy."""
    return joblib.load(MODEL_PATH)


def build_features(raw: pd.DataFrame, bundle: dict) -> pd.DataFrame:
    """Chuyển bảng hồ sơ vay thô thành đúng các cột model cần."""
    df = raw.copy()
    df["Education"] = df["Education"].map(bundle["edu_order"]).astype(float)
    for col in YES_NO:
        df[col] = df[col].map({"Yes": 1, "No": 0, 1: 1, 0: 0}).astype(int)
    for cat in EMPLOYMENT_CATS:
        df[f"EmploymentType_{cat}"] = (df["EmploymentType"] == cat).astype(int)
    for cat in MARITAL_CATS:
        df[f"MaritalStatus_{cat}"] = (df["MaritalStatus"] == cat).astype(int)
    for cat in PURPOSE_CATS:
        df[f"LoanPurpose_{cat}"] = (df["LoanPurpose"] == cat).astype(int)
    return df[bundle["feature_columns"]].astype(float)


def predict_default_proba(raw: pd.DataFrame, bundle: dict) -> pd.Series:
    """Xác suất vỡ nợ (lớp 1) cho từng hồ sơ."""
    X = build_features(raw, bundle)
    model = bundle["model"]
    proba = model.predict_proba(X)[:, list(model.classes_).index(1)]
    return pd.Series(proba, index=raw.index)


# Ngưỡng chọn theo F1 tối ưu trên 20.000 hồ sơ mẫu (precision ~38%, recall ~56%)
HIGH_THRESHOLD = 0.60
MEDIUM_THRESHOLD = 0.45


def risk_level(p: float) -> str:
    if p >= HIGH_THRESHOLD:
        return "Cao"
    if p >= MEDIUM_THRESHOLD:
        return "Trung bình"
    return "Thấp"
