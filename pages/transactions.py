import streamlit as st
from finance_manager import FinanceManager

st.title("💸 تسجيل المعاملات")

fm = FinanceManager()

# 🔹 جلب جميع الحسابات
accounts = fm.get_all_accounts()
if not accounts:
    st.warning("⚠️ لا يوجد حسابات مسجلة. يرجى إنشاء حساب أولًا.")
    st.stop()

# 🔹 تحويل الحسابات إلى قاموس {id: name} وإظهار الرصيد بجانب الاسم
account_options = {acc[0]: f"{acc[1]} (💰 {acc[2]:,.2f})" for acc in accounts}
account_id = st.selectbox("🏦 اختر الحساب", options=list(account_options.keys()), 
                          format_func=lambda x: account_options[x])

# 🔹 اختيار نوع المعاملة
trans_type = st.selectbox("📋 نوع المعاملة", ["وارد", "منصرف"])
trans_type_db = "IN" if trans_type == "وارد" else "OUT"

# 🔹 جلب الفئات بناءً على الحساب ونوع المعاملة
categories = fm.get_custom_categories(account_id, trans_type_db)
category_options = [cat[0] for cat in categories] if categories else ["غير مصنف", "➕ إضافة فئة جديدة"]
category = st.selectbox("📂 اختر الفئة", options=category_options)

# إذا اختار المستخدم "إضافة فئة جديدة"، إظهار حقل الإدخال
if category == "➕ إضافة فئة جديدة":
    new_category = st.text_input("✏️ أدخل اسم الفئة الجديدة")
    if new_category:
        category = new_category  # استخدام الفئة الجديدة بدلاً من القائمة السابقة
        fm.add_custom_category(account_id, trans_type_db, new_category)  # حفظ الفئة في قاعدة البيانات
        st.success(f"✅ تمت إضافة الفئة: {new_category}")

# 🔹 إدخال المبلغ والوصف وطريقة الدفع
amount = st.number_input("💵 المبلغ", min_value=0.01, step=0.01)
description = st.text_input("📝 الوصف", placeholder="وصف المعاملة (اختياري)")
payment_method = st.selectbox("💳 طريقة الدفع", ["كاش", "بطاقة ائتمان", "تحويل بنكي"])

# 🔹 زر تسجيل المعاملة
if st.button("✅ تسجيل المعاملة"):
    if category == "غير مصنف":
        st.error("⚠️ الرجاء اختيار فئة أو إضافة فئة جديدة.")
    else:
        try:
            fm.add_transaction(account_id, amount, trans_type_db, description, payment_method, category)
            new_balance = fm.conn.execute("SELECT balance FROM accounts WHERE id = ?", (account_id,)).fetchone()[0]
            st.success(f"✅ تم تسجيل المعاملة بنجاح! 💰 الرصيد الحالي: {new_balance:,.2f}")
        except ValueError as e:
            st.error(f"❌ {str(e)}")
