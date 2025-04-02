import streamlit as st
from finance_manager import FinanceManager

st.title("💼 إدارة الميزانيات")

fm = FinanceManager()

# إضافة ميزانية جديدة
st.subheader("إضافة ميزانية جديدة")
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
budget_account_id = st.selectbox("🏦 اختر الحساب", options=list(account_options.keys()), 
                                 format_func=lambda x: account_options[x])
budget_name = st.text_input("اسم الميزانية")
budget_amount = st.number_input("المبلغ", min_value=0.01, step=0.01)
categories = fm.get_custom_categories(budget_account_id, "OUT")
category_options = [cat[0] for cat in categories] if categories else ["غير مصنف"]
budget_category = st.selectbox("📂 اختر الفئة", options=category_options)
if st.button("إضافة الميزانية"):
    fm.add_budget(budget_name, budget_amount, budget_account_id, budget_category)
    st.success("تم إضافة الميزانية بنجاح!")

# عرض الميزانيات
st.subheader("قائمة الميزانيات")
budgets = fm.get_budgets()
if budgets:
    budget_df = pd.DataFrame(budgets, columns=["id", "name", "amount", "spent", "account_id", "category"])
    budget_df["account"] = budget_df["account_id"].map(account_options)
    for idx, row in budget_df.iterrows():
        col1, col2, col3 = st.columns([5, 1, 1])
        col1.write(f"{row['name']} - {row['account']} - الفئة: {row['category']} - منفق: {row['spent']:,.2f}/{row['amount']:,.2f}")
        if col2.button("✏️", key=f"edit_budget_{row['id']}"):
            st.session_state[f"edit_budget_{row['id']}"] = True
        if col3.button("🗑️", key=f"del_budget_{row['id']}"):
            fm.delete_budget(row['id'])
            st.success("تم حذف الميزانية!")

        if st.session_state.get(f"edit_budget_{row['id']}", False):
            with st.form(key=f"form_budget_{row['id']}"):
                edit_name = st.text_input("اسم الميزانية", value=row['name'])
                edit_amount = st.number_input("المبلغ", value=float(row['amount']), min_value=0.01)
                edit_categories = fm.get_custom_categories(row['account_id'], "OUT")
                edit_category_options = [cat[0] for cat in edit_categories] if edit_categories else ["غير مصنف"]
                edit_category = st.selectbox("الفئة", options=edit_category_options, index=edit_category_options.index(row['category']))
                if st.form_submit_button("حفظ التعديلات"):
                    fm.edit_budget(row['id'], edit_name, edit_amount, edit_category)
                    st.success("تم تعديل الميزانية!")
                    st.session_state[f"edit_budget_{row['id']}"] = False
else:
    st.info("لا توجد ميزانيات بعد.")
