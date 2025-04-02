import streamlit as st
import pandas as pd
from finance_manager import FinanceManager
from styles import apply_sidebar_styles
import plotly.express as px

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

# ... (باقي الكود دون تغيير)
st.title("📊 تقاريري")
st.markdown("<p style='color: #6b7280;'>رؤية واضحة لأدائك المالي</p>", unsafe_allow_html=True)
st.markdown("---")

fm = FinanceManager()
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}

# Mobile-friendly CSS
st.markdown("""
    <style>
    .filter-box {background-color: #e5e7eb; padding: 10px; border-radius: 8px; margin-bottom: 10px;}
    @media (max-width: 768px) {
        .filter-box {padding: 8px;}
        .stButton>button {font-size: 12px; padding: 6px;}
    }
    </style>
""", unsafe_allow_html=True)

# Filters
st.subheader("⚙️ فلاتر التقرير")
with st.container():
    st.markdown("<div class='filter-box'>", unsafe_allow_html=True)
    account_id = st.selectbox("🏦 الحساب", ["جميع الحسابات"] + list(account_options.keys()), 
                              format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x])
    trans_type = st.selectbox("📋 النوع", ["الكل", "وارد", "منصرف"])
    category = st.selectbox("📂 الفئة", ["الكل"] + [cat[0] for cat in fm.get_custom_categories(account_id, "IN" if trans_type == "وارد" else "OUT")] if trans_type != "الكل" and account_id != "جميع الحسابات" else ["الكل"])
    start_date = st.date_input("📅 من", value=None)
    end_date = st.date_input("📅 إلى", value=None)
    st.markdown("</div>", unsafe_allow_html=True)

start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S") if start_date else None
end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S") if end_date else None
transactions = fm.filter_transactions(
    account_id=account_id if account_id != "جميع الحسابات" else None,
    start_date=start_date_str,
    end_date=end_date_str,
    trans_type="IN" if trans_type == "وارد" else "OUT" if trans_type == "منصرف" else None,
    category=category if category != "الكل" else None
)

# Transactions Table
st.subheader("📋 جدول المعاملات")
if transactions:
    df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"])
    df["type"] = df["type"].replace({"IN": "وارد", "OUT": "منصرف"})
    df["account"] = df["account_id"].map(account_options)
    st.dataframe(df[["date", "type", "amount", "account", "description", "payment_method", "category"]], height=200)
    col1, col2 = st.columns(2)
    with col1:
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("💾 تحميل CSV", csv, "report.csv", "text/csv", use_container_width=True)
    with col2:
        st.button("📑 تصدير PDF", disabled=True, help="قيد التطوير", use_container_width=True)
else:
    st.info("ℹ️ لا توجد معاملات تطابق الفلاتر.")

# Charts
st.subheader("📈 تحليل بياني")
if transactions:
    col1, col2 = st.columns([1, 1])
    with col1:
        fig = px.bar(df, x="date", y="amount", color="type", title="المعاملات بمرور الوقت", color_discrete_map={"وارد": "#34d399", "منصرف": "#f87171"}, height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        df_expanded = df.assign(category=df["category"].str.split(", ")).explode("category")
        category_summary = df_expanded.groupby("category")["amount"].sum().reset_index()
        fig_pie = px.pie(category_summary, values="amount", names="category", title="توزيع حسب الفئات", color_discrete_sequence=px.colors.qualitative.Bold, height=300)
        st.plotly_chart(fig_pie, use_container_width=True)
