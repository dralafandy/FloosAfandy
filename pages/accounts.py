import streamlit as st
from finance_manager import FinanceManager

st.title("🏦 إدارة الحسابات")

fm = FinanceManager()

# إضافة حساب
st.header("➕ إضافة حساب")
col1, col2, col3 = st.columns(3)
with col1:
    account_name = st.text_input("اسم الحساب", placeholder="مثال: حساب توفير")
with col2:
    opening_balance = st.number_input("الرصيد الافتتاحي", min_value=0.0, step=100.0)
with col3:
    min_balance = st.number_input("الحد الأدنى", min_value=0.0, step=100.0)

if st.button("💾 إضافة الحساب", type="primary", use_container_width=True):
    try:
        account_id = fm.add_account(account_name, opening_balance, min_balance)
        st.success(f"✅ تم إضافة الحساب! المعرف: {account_id}")
    except Exception as e:
        st.error(f"❌ خطأ: {str(e)}")

# قائمة الحسابات
st.header("📋 الحسابات")
accounts = fm.get_all_accounts()
if accounts:
    account_options = {acc[0]: acc[1] for acc in accounts}  # Map account IDs to names
    account_data = [{"معرف": acc[0], "الاسم": acc[1], "الرصيد": acc[2], "الحد الأدنى": acc[3], "تاريخ الإنشاء": acc[4]} 
                    for acc in accounts]
    st.table(account_data)

    st.subheader("🛠️ تعديل/حذف حساب")
    selected_account = st.selectbox("اختر حسابًا", options=[acc[0] for acc in accounts], 
                                    format_func=lambda x: account_options[x])
    sel_acc = next(acc for acc in accounts if acc[0] == selected_account)

    with st.expander("✏️ تعديل الحساب", expanded=True):
        new_name = st.text_input("اسم جديد", value=sel_acc[1], key="edit_name")
        new_balance = st.number_input("رصيد جديد", value=float(sel_acc[2]), step=100.0, key="edit_balance")
        new_min_balance = st.number_input("حد أدنى جديد", value=float(sel_acc[3]), step=100.0, key="edit_min")
        
        col4, col5 = st.columns(2)
        with col4:
            if st.button("💾 حفظ التعديل", use_container_width=True):
                try:
                    fm.conn.execute('UPDATE accounts SET name = ?, balance = ?, min_balance = ? WHERE id = ?',
                                    (new_name, new_balance, new_min_balance, selected_account))
                    fm.conn.commit()
                    st.success("✅ تم التعديل!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: {str(e)}")
        with col5:
            if st.button("🗑️ حذف الحساب", use_container_width=True):
                try:
                    fm.conn.execute('DELETE FROM accounts WHERE id = ?', (selected_account,))
                    fm.conn.execute('DELETE FROM transactions WHERE account_id = ?', (selected_account,))
                    fm.conn.commit()
                    st.success("🗑️ تم الحذف!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ: {str(e)}")
else:
    st.info("ℹ️ لا توجد حسابات بعد.")

st.markdown("### 💡 نصيحة")
st.write("حدد حدًا أدنى للرصيد لتلقي التنبيهات.")
