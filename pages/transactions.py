import streamlit as st
import pandas as pd
from finance_manager import FinanceManager

st.title("💸 تسجيل المعاملات")

fm = FinanceManager()

# إضافة معاملة جديدة
st.subheader("إضافة معاملة جديدة")
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
account_id = st.selectbox("🏦 اختر الحساب", options=list(account_options.keys()), 
                          format_func=lambda x: account_options[x])
trans_type = st.selectbox("📋 نوع المعاملة", ["وارد", "منصرف"])
trans_type_db = "IN" if trans_type == "وارد" else "OUT"
categories = fm.get_custom_categories(account_id, trans_type_db)
category_options = [cat[0] for cat in categories] if categories else ["غير مصنف"]
category = st.multiselect("📂 اختر الفئات", options=category_options, default=["غير مصنف"])
amount = st.number_input("💵 المبلغ", min_value=0.01, step=0.01)
description = st.text_input("📝 الوصف", placeholder="وصف المعاملة (اختياري)")
payment_method = st.selectbox("💳 طريقة الدفع", ["كاش", "بطاقة ائتمان", "تحويل بنكي"])
if st.button("✅ تسجيل المعاملة"):
    try:
        fm.add_transaction(account_id, amount, trans_type_db, description, payment_method, category)
        st.success("✅ تم تسجيل المعاملة بنجاح!")
    except ValueError as e:
        st.error(f"❌ {str(e)}")

# عرض المعاملات مع تعديل وحذف
st.subheader("📜 المعاملات المسجلة")
transactions = fm.get_all_transactions()
if transactions:
    df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"])
    df["type"] = df["type"].replace({"IN": "وارد", "OUT": "منصرف"})
    df["account"] = df["account_id"].map(account_options)
    for idx, row in df.iterrows():
        col1, col2, col3 = st.columns([5, 1, 1])
        col1.write(f"{row['date']} - {row['type']} - {row['amount']:,.2f} - {row['account']} - {row['category']}")
        if col2.button("✏️", key=f"edit_trans_{row['id']}"):
            st.session_state[f"edit_trans_{row['id']}"] = True
        if col3.button("🗑️", key=f"del_trans_{row['id']}"):
            fm.delete_transaction(row['id'])
            st.success("تم حذف المعاملة!")

        if st.session_state.get(f"edit_trans_{row['id']}", False):
            with st.form(key=f"form_trans_{row['id']}"):
                edit_account_id = st.selectbox("الحساب", options=list(account_options.keys()), 
                                               format_func=lambda x: account_options[x], index=list(account_options.keys()).index(row['account_id']))
                edit_trans_type = st.selectbox("نوع المعاملة", ["وارد", "منصرف"], index=0 if row['type'] == "وارد" else 1)
                edit_trans_type_db = "IN" if edit_trans_type == "وارد" else "OUT"
                edit_categories = fm.get_custom_categories(edit_account_id, edit_trans_type_db)
                edit_category_options = [cat[0] for cat in edit_categories] if edit_categories else ["غير مصنف"]
                edit_category = st.multiselect("الفئات", options=edit_category_options, default=row['category'].split(", "))
                edit_amount = st.number_input("المبلغ", value=float(row['amount']), min_value=0.01)
                edit_description = st.text_input("الوصف", value=row['description'])
                edit_payment_method = st.selectbox("طريقة الدفع", ["كاش", "بطاقة ائتمان", "تحويل بنكي"], index=["كاش", "بطاقة ائتمان", "تحويل بنكي"].index(row['payment_method']))
                if st.form_submit_button("حفظ التعديلات"):
                    fm.edit_transaction(row['id'], edit_account_id, edit_amount, edit_trans_type_db, edit_description, edit_payment_method, edit_category)
                    st.success("تم تعديل المعاملة!")
                    st.session_state[f"edit_trans_{row['id']}"] = False
else:
    st.info("ℹ️ لا توجد معاملات مسجلة بعد.")
