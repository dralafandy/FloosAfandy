import streamlit as st
from finance_manager import FinanceManager

st.title("💼 إدارة الميزانيات")

fm = FinanceManager()

# إضافة ميزانية جديدة
st.header("➕ إضافة ميزانية جديدة")
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
account_id = st.selectbox("🏦 اختر الحساب", options=list(account_options.keys()), 
                          format_func=lambda x: account_options[x])
category = st.text_input("الفئة", placeholder="مثال: طعام، ترفيه")
budget_amount = st.number_input("المبلغ المخصص", min_value=0.0, step=100.0)
if st.button("إضافة الميزانية"):
    fm.add_budget(category, budget_amount, account_id)
    st.success(f"✅ تم إضافة ميزانية لـ {category} في حساب {account_options[account_id]}")

# عرض الميزانيات الحالية
st.header("📋 الميزانيات الحالية")
budgets = fm.get_budgets()
if budgets:
    for budget in budgets:
        account_name = account_options[budget[4]]
        st.write(f"**{account_name} - {budget[1]}**: مخصص {budget[2]:,.2f} | منفق {budget[3]:,.2f}")
        if budget[3] > budget[2]:
            st.warning(f"⚠️ تجاوزت الميزانية لـ {budget[1]} في حساب {account_name}")
else:
    st.info("ℹ️ لا توجد ميزانيات بعد")