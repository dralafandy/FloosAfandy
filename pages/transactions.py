import streamlit as st
from finance_manager import FinanceManager

st.title("💸 تسجيل المعاملات")

fm = FinanceManager()

# اختيار الحساب
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
account_id = st.selectbox("🏦 اختر الحساب", options=list(account_options.keys()), 
                          format_func=lambda x: account_options[x])

# اختيار نوع المعاملة
trans_type = st.selectbox("📋 نوع المعاملة", ["وارد", "منصرف"])
trans_type_db = "IN" if trans_type == "وارد" else "OUT"

# جلب الفئات بناءً على الحساب ونوع المعاملة
categories = fm.get_custom_categories(account_id, trans_type_db)
category_options = [cat[0] for cat in categories] if categories else ["غير مصنف"]
category = st.selectbox("📂 اختر الفئة", options=category_options)

# إدخال المبلغ والوصف وطريقة الدفع
amount = st.number_input("💵 المبلغ", min_value=0.01, step=0.01)
description = st.text_input("📝 الوصف", placeholder="وصف المعاملة (اختياري)")
payment_method = st.selectbox("💳 طريقة الدفع", ["كاش", "بطاقة ائتمان", "تحويل بنكي"])

if st.button("✅ تسجيل المعاملة"):
    try:
        fm.add_transaction(account_id, amount, trans_type_db, description, payment_method, category)
        st.success("✅ تم تسجيل المعاملة بنجاح!")
    except ValueError as e:
        st.error(f"❌ {str(e)}")
