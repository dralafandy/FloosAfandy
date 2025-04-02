import streamlit as st
import pandas as pd
from finance_manager import FinanceManager
from styles import apply_sidebar_styles

st.set_page_config(page_title="FloosAfandy - معاملاتي", layout="centered", initial_sidebar_state="collapsed")

# Apply sidebar styles
apply_sidebar_styles()

# Sidebar
with st.sidebar:
    st.image("https://via.placeholder.com/50.png", width=50)
    st.markdown("<h2>💰 FloosAfandy</h2>", unsafe_allow_html=True)
    fm = FinanceManager()
    alerts = fm.check_alerts()
    if alerts:
        st.markdown(f"<p style='text-align: center; color: #f1c40f;'>⚠️ {len(alerts)} تنبيهات</p>", unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<div class='section-title'>الصفحات</div>", unsafe_allow_html=True)
    if st.button("💸 معاملاتي", key="nav_transactions"):
        st.switch_page("pages/transactions.py")
    if st.button("🏦 حساباتي", key="nav_accounts"):
        st.switch_page("pages/accounts.py")
    if st.button("📊 تقاريري", key="nav_reports"):
        st.switch_page("pages/reports.py")
    st.button("📈 لوحة التحكم", key="nav_dashboard", disabled=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='section-title'>الإعدادات</div>", unsafe_allow_html=True)
    with st.expander("⚙️ الفلاتر", expanded=False):
        accounts = fm.get_all_accounts()
        account_options = {acc[0]: acc[1] for acc in accounts}
        options_list = ["جميع الحسابات"] + list(account_options.keys())
        time_range = st.selectbox("⏳ الفترة", ["الكل", "آخر 7 أيام", "آخر 30 يومًا", "آخر 90 يومًا"], key="time_range")
        selected_account = st.selectbox("🏦 الحساب", options=options_list, 
                                        format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x], 
                                        key="selected_account")
        if st.button("🔄 إعادة تعيين", key="reset_filters"):
            st.session_state.time_range = "الكل"
            st.session_state.selected_account = "جميع الحسابات"
            st.rerun()

# Main content (باقي الكود كما هو)

# ... (باقي الكود دون تغيير)
st.title("🏦 حساباتي")
st.markdown("<p style='color: #6b7280;'>تابع وأدر حساباتك المالية بسهولة</p>", unsafe_allow_html=True)
st.markdown("---")

fm = FinanceManager()
accounts = fm.get_all_accounts()

# Mobile-friendly CSS
st.markdown("""
    <style>
    .card {background-color: #ffffff; padding: 10px; border-radius: 8px; margin: 5px 0; box-shadow: 0 1px 3px rgba(0,0,0,0.1);}
    @media (max-width: 768px) {
        .card {padding: 8px; font-size: 12px;}
        .stButton>button {font-size: 12px; padding: 6px;}
    }
    </style>
""", unsafe_allow_html=True)

# Statistics
st.metric("عدد الحسابات", len(accounts))

# Add Account Form
st.subheader("➕ إضافة حساب جديد")
with st.form(key="add_account_form"):
    account_name = st.text_input("🏦 اسم الحساب", key="add_name")
    opening_balance = st.number_input("💵 الرصيد الافتتاحي", min_value=0.0, step=0.01, format="%.2f", key="add_balance")
    min_balance = st.number_input("🚨 الحد الأدنى", min_value=0.0, step=0.01, format="%.2f", key="add_min")
    submit_button = st.form_submit_button("💾 إضافة الحساب", type="primary", use_container_width=True)
if submit_button:
    fm.add_account(account_name, opening_balance, min_balance)
    st.success("✅ تم إضافة الحساب!")
    st.rerun()

# Accounts as Cards
st.subheader("📋 حساباتك")
search_query = st.text_input("🔍 ابحث عن حساب", "")
filtered_accounts = [acc for acc in accounts if search_query.lower() in acc[1].lower()] if search_query else accounts

if filtered_accounts:
    for acc in filtered_accounts:
        bg_color = "#d1fae5" if acc[2] >= acc[3] else "#fee2e2"
        with st.container():
            st.markdown(f"<div class='card' style='background-color: {bg_color};'>"
                        f"<strong>{acc[1]}</strong><br>الرصيد: {acc[2]:,.2f}<br>الحد الأدنى: {acc[3]:,.2f}</div>", 
                        unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 المعاملات", key=f"trans_{acc[0]}"):
                    st.session_state["filter_account"] = acc[0]
                    st.switch_page("pages/transactions.py")
            with col2:
                if st.button("✏️ تعديل", key=f"edit_{acc[0]}"):
                    st.session_state[f"edit_{acc[0]}"] = True
            with col3:
                if st.button("🗑️ حذف", key=f"del_{acc[0]}"):
                    fm.conn.execute("DELETE FROM accounts WHERE id = ?", (acc[0],))
                    fm.conn.commit()
                    st.success("🗑️ تم الحذف!")
                    st.rerun()
            if st.session_state.get(f"edit_{acc[0]}", False):
                with st.form(key=f"edit_form_{acc[0]}"):
                    new_name = st.text_input("اسم جديد", value=acc[1], key=f"edit_name_{acc[0]}")
                    new_balance = st.number_input("الرصيد", value=float(acc[2]), key=f"edit_balance_{acc[0]}")
                    new_min = st.number_input("الحد الأدنى", value=float(acc[3]), key=f"edit_min_{acc[0]}")
                    if st.form_submit_button("💾 حفظ التعديل"):
                        fm.conn.execute("UPDATE accounts SET name = ?, balance = ?, min_balance = ? WHERE id = ?", 
                                        (new_name, new_balance, new_min, acc[0]))
                        fm.conn.commit()
                        st.success("✅ تم التعديل!")
                        st.session_state[f"edit_{acc[0]}"] = False
                        st.rerun()
else:
    st.info("ℹ️ لا توجد حسابات تطابق البحث.")
