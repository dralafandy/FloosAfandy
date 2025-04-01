import streamlit as st
from finance_manager import FinanceManager

# إعداد الصفحة
st.title("🏦 إدارة الحسابات")

# إنشاء كائن لإدارة البيانات
fm = FinanceManager()

# قسم إضافة حساب جديد
st.header("➕ إضافة حساب جديد")
col1, col2, col3 = st.columns(3)
with col1:
    account_name = st.text_input("اسم الحساب", placeholder="مثال: حساب توفير")
with col2:
    opening_balance = st.number_input("الرصيد الافتتاحي", min_value=0.0, step=100.0)
with col3:
    min_balance = st.number_input("الحد الأدنى للرصيد", min_value=0.0, step=100.0)

if st.button("إضافة الحساب", key="add", type="primary"):
    account_id = fm.add_account(account_name, opening_balance, min_balance)
    st.success(f"✅ تم إضافة الحساب! معرف الحساب: {account_id}")

# قسم قائمة الحسابات
st.header("📋 قائمة الحسابات")
accounts = fm.get_all_accounts()
if accounts:
    account_data = [{"معرف": acc[0], "الاسم": acc[1], "الرصيد": acc[2], "الحد الأدنى": acc[3], "تاريخ الإنشاء": acc[4]} 
                    for acc in accounts]
    st.table(account_data)

    # خيار تعديل أو حذف حساب
    st.subheader("🛠️ تعديل أو حذف حساب")
    account_options = {acc[0]: acc[1] for acc in accounts}
    selected_account = st.selectbox("اختر حسابًا", options=list(account_options.keys()), 
                                   format_func=lambda x: account_options[x])
    
    # تعديل الحساب
    with st.expander("✏️ تعديل الحساب"):
        new_name = st.text_input("اسم جديد", value=account_options[selected_account])
        new_balance = st.number_input("رصيد جديد", value=float(accounts[selected_account-1][2]), step=100.0)
        new_min_balance = st.number_input("حد أدنى جديد", value=float(accounts[selected_account-1][3]), step=100.0)
        if st.button("حفظ التعديلات", key="edit"):
            with fm.conn:
                fm.conn.execute('''
                    UPDATE accounts SET name = ?, balance = ?, min_balance = ? WHERE id = ?
                ''', (new_name, new_balance, new_min_balance, selected_account))
            st.success(f"✅ تم تعديل الحساب {account_options[selected_account]} بنجاح!")

    # حذف الحساب
    if st.button("🗑️ حذف الحساب", key="delete", type="secondary"):
        with fm.conn:
            fm.conn.execute('DELETE FROM accounts WHERE id = ?', (selected_account,))
            fm.conn.execute('DELETE FROM transactions WHERE account_id = ?', (selected_account,))
        st.success(f"🗑️ تم حذف الحساب {account_options[selected_account]} بنجاح!")

else:
    st.info("ℹ️ لا توجد حسابات بعد، أضف حسابًا جديدًا أعلاه!")

# نصائح سريعة
st.markdown("### 💡 نصيحة")
st.write("تأكد من تحديد حد أدنى للرصيد لتلقي تنبيهات عند انخفاض الرصيد.")