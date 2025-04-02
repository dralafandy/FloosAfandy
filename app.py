import streamlit as st
import pandas as pd
import plotly.express as px
from finance_manager import FinanceManager
from datetime import timedelta, datetime
from styles import apply_sidebar_styles

st.set_page_config(page_title="FloosAfandy", layout="centered", initial_sidebar_state="collapsed")

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

# Main content
st.markdown("<h1 style='text-align: center; color: #1A2525;'>مرحبًا بك في FloosAfandy</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #6b7280;'>إدارة مالياتك بسهولة وأناقة</p>", unsafe_allow_html=True)
st.markdown("---")

if alerts:
    st.warning("📢 تنبيهات مهمة:")
    for alert in alerts:
        st.warning(alert)

st.subheader("📈 نظرة عامة")
if "time_range" not in st.session_state:
    st.session_state.time_range = "الكل"
if "selected_account" not in st.session_state:
    st.session_state.selected_account = "جميع الحسابات"

time_range = st.session_state.time_range
selected_account = st.session_state.selected_account

if time_range == "آخر 7 أيام":
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
elif time_range == "آخر 30 يومًا":
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
elif time_range == "آخر 90 يومًا":
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
else:
    start_date = None

transactions = fm.filter_transactions(account_id=selected_account if selected_account != "جميع الحسابات" else None, start_date=start_date)
df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"]) if transactions else pd.DataFrame()

if not df.empty:
    df["amount"] = pd.to_numeric(df["amount"], errors='coerce')
    df = df.dropna(subset=["amount"])

total_balance = sum(acc[2] for acc in accounts)
st.metric("💰 إجمالي الرصيد", f"{total_balance:,.2f}", delta_color="normal")
st.metric("📥 الوارد", f"{df[df['type'] == 'IN']['amount'].sum():,.2f}" if not df.empty else "0.00", delta_color="normal")
st.metric("📤 الصادر", f"{df[df['type'] == 'OUT']['amount'].sum():,.2f}" if not df.empty else "0.00", delta_color="normal")

st.subheader("🏦 توزيع الأرصدة")
if accounts:
    account_df = pd.DataFrame(accounts, columns=["id", "name", "balance", "min_balance", "created_at"])
    fig = px.pie(account_df, values="balance", names="name", title="توزيع الأرصدة", color_discrete_sequence=px.colors.qualitative.Pastel, height=300)
    st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 توزيع المصروفات حسب الفئات")
if not df.empty and not df[df["type"] == "OUT"].empty:
    expenses_df = df[df["type"] == "OUT"].assign(category=df["category"].str.split(", ")).explode("category")
    category_summary = expenses_df.groupby("category")["amount"].sum().reset_index()
    fig_category = px.pie(category_summary, values="amount", names="category", title="توزيع المصروفات", color_discrete_sequence=px.colors.qualitative.Bold, height=300)
    st.plotly_chart(fig_category, use_container_width=True)
