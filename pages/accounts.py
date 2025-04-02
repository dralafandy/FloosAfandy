import streamlit as st
from finance_manager import FinanceManager

st.title("🏦 إدارة الحسابات")

fm = FinanceManager()

# إضافة حساب جديد
st.subheader("إضافة حساب جديد")
account_name = st.text_input("اسم الحساب")
opening_balance = st.number_input("الرصيد الافتتاحي", min_value=0.0, step=0.01)
min_balance = st.number_input("الحد الأدنى للرصيد", min_value=0.0, step=0.01)
if st.button("إضافة الحساب"):
    fm.add_account(account_name, opening_balance, min_balance)
    st.success("تم إضافة الحساب بنجاح!")

# عرض الحسابات
st.subheader("قائمة الحسابات")
accounts = fm.get_all_accounts()
if accounts:
    account_df = pd.DataFrame(accounts, columns=["id", "name", "balance", "min_balance", "created_at"])
    for idx, row in account_df.iterrows():
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.write(f"{row['name']} - الرصيد: {row['balance']:,.2f} (الحد الأدنى: {row['min_balance']:,.2f})")
        if col2.button("✏️ تعديل", key=f"edit_{row['id']}"):
            st.session_state[f"edit_account_{row['id']}"] = True
        if col3.button("🗑️ حذف", key=f"del_{row['id']}"):
            fm.delete_account(row['id'])
            st.success("تم حذف الحساب!")

        if st.session_state.get(f"edit_account_{row['id']}", False):
            with st.form(key=f"form_{row['id']}"):
                new_name = st.text_input("اسم الحساب", value=row['name'])
                new_min_balance = st.number_input("الحد الأدنى للرصيد", value=row['min_balance'], min_value=0.0)
                if st.form_submit_button("حفظ التعديلات"):
                    fm.edit_account(row['id'], new_name, new_min_balance)
                    st.success("تم تعديل الحساب!")
                    st.session_state[f"edit_account_{row['id']}"] = False
else:
    st.info("لا توجد حسابات بعد.")
