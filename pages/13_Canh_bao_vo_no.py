"""Cảnh báo vỡ nợ: chấm rủi ro một hồ sơ vay hoặc hàng loạt từ file CSV."""

import pandas as pd
import streamlit as st

from risk import HIGH_THRESHOLD, MEDIUM_THRESHOLD, load_bundle, predict_default_proba, risk_level
from ui import page_header

EDU = ["High School", "Bachelor's", "Master's", "PhD"]
EMP = ["Full-time", "Part-time", "Self-employed", "Unemployed"]
MARITAL = ["Single", "Married", "Divorced"]
PURPOSE = ["Auto", "Business", "Education", "Home", "Other"]
YN = ["Yes", "No"]


@st.cache_resource
def get_bundle():
    return load_bundle()


bundle = get_bundle()
page_header("Cảnh báo vỡ nợ", "Dự đoán rủi ro vỡ nợ bằng model Random Forest đã huấn luyện")
st.caption(
    f"Ngưỡng: rủi ro **Cao** từ {HIGH_THRESHOLD:.0%}, **Trung bình** từ {MEDIUM_THRESHOLD:.0%}. "
    "Mọi số tiền tính bằng USD, đúng đơn vị dữ liệu huấn luyện. Đây là công cụ tham khảo, không thay thế thẩm định tín dụng."
)

tab_one, tab_batch = st.tabs(["Một hồ sơ", "Chấm hàng loạt (CSV)"])

with tab_one:
    with st.container(border=True):
        with st.form("risk_form"):
            c1, c2, c3 = st.columns(3)
            age = c1.number_input("Tuổi", 18, 100, 35)
            income = c2.number_input("Thu nhập năm (USD)", 0, None, 60000, step=1000)
            loan_amount = c3.number_input("Số tiền vay (USD)", 0, None, 50000, step=1000)
            c4, c5, c6 = st.columns(3)
            credit = c4.number_input("Điểm tín dụng", 300, 850, 650)
            months_emp = c5.number_input("Số tháng làm việc", 0, 600, 36)
            credit_lines = c6.number_input("Số tín dụng đang mở", 0, 50, 2)
            c7, c8, c9 = st.columns(3)
            rate = c7.number_input("Lãi suất (%)", 0.0, 40.0, 10.0, step=0.1)
            term = c8.selectbox("Kỳ hạn (tháng)", [12, 24, 36, 48, 60], index=2)
            dti = c9.number_input("Tỷ lệ nợ/thu nhập (DTI)", 0.0, 1.0, 0.3, step=0.01)
            c10, c11, c12 = st.columns(3)
            education = c10.selectbox("Học vấn", EDU, index=1)
            employment = c11.selectbox("Nghề nghiệp", EMP)
            marital = c12.selectbox("Tình trạng hôn nhân", MARITAL)
            c13, c14, c15, c16 = st.columns(4)
            purpose = c13.selectbox("Mục đích vay", PURPOSE, index=4)
            mortgage = c14.selectbox("Có thế chấp nhà?", YN, index=1)
            dependents = c15.selectbox("Có người phụ thuộc?", YN, index=1)
            cosigner = c16.selectbox("Có người đồng bảo lãnh?", YN, index=1)
            submitted = st.form_submit_button("Chấm rủi ro", type="primary")

    if submitted:
        row = pd.DataFrame([{
            "Age": age, "Income": income, "LoanAmount": loan_amount, "CreditScore": credit,
            "MonthsEmployed": months_emp, "NumCreditLines": credit_lines, "InterestRate": rate,
            "LoanTerm": term, "DTIRatio": dti, "Education": education, "EmploymentType": employment,
            "MaritalStatus": marital, "HasMortgage": mortgage, "HasDependents": dependents,
            "HasCoSigner": cosigner, "LoanPurpose": purpose,
        }])
        p = float(predict_default_proba(row, bundle).iloc[0])
        level = risk_level(p)
        st.metric("Xác suất vỡ nợ", f"{p:.1%}")
        if level == "Cao":
            st.error(f"Mức rủi ro: **{level}**. Nên thẩm định kỹ trước khi cho vay.")
        elif level == "Trung bình":
            st.warning(f"Mức rủi ro: **{level}**. Cân nhắc thêm điều kiện bảo đảm.")
        else:
            st.success(f"Mức rủi ro: **{level}**.")

with tab_batch:
    with st.container(border=True):
        st.write("Tải file CSV có cùng các cột như dữ liệu huấn luyện, số tiền tính bằng USD (có thể có cột `Default`, sẽ bị bỏ qua).")
        up = st.file_uploader("File CSV hồ sơ vay", type=["csv"])
        if up is not None:
            raw = pd.read_csv(up)
            base_cols = ["Age", "Income", "LoanAmount", "CreditScore", "MonthsEmployed", "NumCreditLines",
                         "InterestRate", "LoanTerm", "DTIRatio", "Education", "EmploymentType",
                         "MaritalStatus", "HasMortgage", "HasDependents", "HasCoSigner", "LoanPurpose"]
            missing = [c for c in base_cols if c not in raw.columns]
            if missing:
                st.error(f"Thiếu cột: {', '.join(missing)}")
            else:
                out = raw.copy()
                out["Xác suất vỡ nợ"] = predict_default_proba(raw, bundle).round(4)
                out["Mức rủi ro"] = out["Xác suất vỡ nợ"].map(risk_level)
                st.write(f"Đã chấm **{len(out):,}** hồ sơ. Cao: **{(out['Mức rủi ro'] == 'Cao').sum():,}**")
                st.dataframe(out.head(200), hide_index=True)
                st.download_button(
                    "Tải kết quả CSV",
                    data=out.to_csv(index=False).encode("utf-8-sig"),
                    file_name="ket_qua_canh_bao_no.csv",
                    mime="text/csv",
                )
