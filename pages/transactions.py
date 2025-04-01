import streamlit as st
from finance_manager import FinanceManager
import pandas as pd

# إعداد الصفحة
st.title("💸 تسجيل المعاملات")

# إنشاء كائن لإدارة البيانات
fm = FinanceManager()

# جلب الحسابات
accounts = fm.get_all_accounts()
if not accounts:
    st.warning("⚠️ يرجى إضافة حساب أولاً من صفحة إدارة الحسابات.")
else:
    account_options = {acc[0]: acc[1] for acc in accounts}

    # قسم إضافة معاملة جديدة
    st.header("➕ إضافة معاملة جديدة")
    col1, col2 = st.columns(2)
    with col1:
        account_id = st.selectbox("🏦 اختر الحساب", options=list(account_options.keys()), 
                                 format_func=lambda x: account_options[x], key="add_account")
        trans_type = st.radio("📋 نوع المعاملة", ["وارد", "صادر"], key="add_type")
    with col2:
        amount = st.number_input("💰 المبلغ", min_value=0.0, step=100.0, key="add_amount")
        description = st.text_input("📝 وصف المعاملة (اختياري)", placeholder="مثال: دفعة فاتورة", key="add_desc")
        payment_method = st.selectbox("💳 طريقة الدفع", ["كاش", "فيزاكارت", "إنستاباي", "أخرى"], key="add_payment")

    if st.button("📤 تسجيل المعاملة", type="primary", key="add_button"):
        try:
            trans_type_en = "IN" if trans_type == "وارد" else "OUT"
            result = fm.add_transaction(account_id, amount, trans_type_en, description, payment_method)
            st.success(f"✅ تم تسجيل المعاملة بنجاح لـ {account_options[account_id]} باستخدام {payment_method}!")
            if result:
                st.warning(f"⚠️ {result}")
        except ValueError as e:
            st.error(f"❌ خطأ: {str(e)}")

    # قسم تعديل معاملة
    st.header("✏️ تعديل معاملة")
    transactions = fm.get_all_transactions()
    if transactions:
        trans_options = {t[0]: f"{account_options[t[4]]} - {t[2]} - {t[3]} - {t[6]}" for t in transactions}
        trans_id = st.selectbox("اختر المعاملة للتعديل", options=list(trans_options.keys()), 
                                format_func=lambda x: trans_options[x])
        
        # عرض تفاصيل المعاملة المختارة للتعديل
        selected_trans = [t for t in transactions if t[0] == trans_id][0]
        col3, col4 = st.columns(2)
        with col3:
            edit_account_id = st.selectbox("🏦 الحساب", options=list(account_options.keys()), 
                                          format_func=lambda x: account_options[x], 
                                          index=list(account_options.keys()).index(selected_trans[4]), key="edit_account")
            edit_trans_type = st.radio("📋 نوع المعاملة", ["وارد", "صادر"], 
                                      index=0 if selected_trans[2] == "IN" else 1, key="edit_type")
        with col4:
            edit_amount = st.number_input("💰 المبلغ", min_value=0.0, step=100.0, 
                                         value=float(selected_trans[3]), key="edit_amount")
            edit_description = st.text_input("📝 الوصف", value=selected_trans[5], key="edit_desc")
            edit_payment_method = st.selectbox("💳 طريقة الدفع", ["كاش", "فيزاكارت", "إنستاباي", "أخرى"], 
                                              index=["كاش", "فيزاكارت", "إنستاباي", "أخرى"].index(selected_trans[6]), 
                                              key="edit_payment")

        if st.button("💾 حفظ التعديلات", type="secondary", key="edit_button"):
            try:
                edit_trans_type_en = "IN" if edit_trans_type == "وارد" else "OUT"
                result = fm.edit_transaction(trans_id, edit_account_id, edit_amount, edit_trans_type_en, 
                                            edit_description, edit_payment_method)
                st.success(f"✅ تم تعديل المعاملة بنجاح!")
                if result:
                    st.warning(f"⚠️ {result}")
            except ValueError as e:
                st.error(f"❌ خطأ: {str(e)}")
    else:
        st.info("ℹ️ لا توجد معاملات للتعديل بعد.")

    # عرض آخر المعاملات
    st.subheader("📅 آخر المعاملات")
    transactions = fm.filter_transactions(account_id=account_id)
    if transactions:
        df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method"])
        df["type"] = df["type"].replace({"IN": "وارد", "OUT": "صادر"})
        df["account_name"] = df["account_id"].map(account_options)
        st.dataframe(df[["date", "type", "amount", "account_name", "description", "payment_method"]].tail(5), use_container_width=True)
    else:
        st.info("ℹ️ لا توجد معاملات مسجلة لهذا الحساب بعد.")

# نصائح
st.markdown("### 💡 نصيحة")
st.write("تأكد من مراجعة التعديلات قبل الحفظ لضمان دقة السجلات!")