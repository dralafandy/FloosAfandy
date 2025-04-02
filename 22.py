import streamlit as st
import pandas as pd
import plotly.express as px
from finance_manager import FinanceManager
from datetime import timedelta, datetime

st.set_page_config(page_title="FloosAfandy", layout="wide", initial_sidebar_state="expanded")

fm = FinanceManager()

if 'theme' not in st.session_state:
    st.session_state.theme = "فاتح"
theme = st.sidebar.selectbox("اختر الثيم", ["فاتح", "داكن"], index=0 if st.session_state.theme == "فاتح" else 1)
st.session_state.theme = theme

if theme == "داكن":
    st.markdown("""
        <style>
        .stApp {
            background-color: #2b2b2b;
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp {
            background-color: white;
            color: black;
        }
        </style>
    """, unsafe_allow_html=True)

st.title("FloosAfandy")
menu = st.columns(5)
with menu[0]:
    if st.button("🏦 إدارة الحسابات"):
        st.switch_page("pages/accounts.py")
with menu[1]:
    if st.button("💸 تسجيل المعاملات"):
        st.switch_page("pages/transactions.py")
with menu[2]:
    if st.button("📊 التقارير"):
        st.switch_page("pages/reports.py")
with menu[3]:
    if st.button("💼 إدارة الميزانيات"):
        st.switch_page("pages/budgets.py")
with menu[4]:
    st.button("📈 لوحة التحكم", type="primary", disabled=True)

# عرض التنبيهات
alerts = fm.check_alerts()
if alerts:
    for alert in alerts:
        st.warning(alert)

# إدارة الفئات
st.sidebar.header("📂 إدارة الفئات")
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
cat_account_id = st.sidebar.selectbox("اختر الحساب للفئة", options=list(account_options.keys()), 
                                      format_func=lambda x: account_options[x], key="cat_account")
cat_trans_type = st.sidebar.selectbox("نوع المعاملة", ["وارد", "منصرف"], key="cat_type")
cat_name = st.sidebar.text_input("اسم الفئة", key="cat_name")
if st.sidebar.button("إضافة فئة"):
    fm.add_custom_category(cat_account_id, "IN" if cat_trans_type == "وارد" else "OUT", cat_name)
    st.sidebar.success("تم إضافة الفئة!")

st.sidebar.subheader("الفئات الموجودة")
all_categories = fm.get_all_categories()
if all_categories:
    for cat in all_categories:
        col1, col2 = st.sidebar.columns([3, 1])
        col1.write(f"{account_options[cat[1]]} - {'وارد' if cat[2] == 'IN' else 'منصرف'}: {cat[3]}")
        if col2.button("🗑️", key=f"del_cat_{cat[0]}"):
            fm.delete_custom_category(cat[0])
            st.sidebar.success("تم حذف الفئة!")

# لوحة التحكم
st.markdown("### 🎯 نظرة شاملة على أدائك المالي")
st.sidebar.header("⚙️ خيارات العرض")
if st.sidebar.button("🔄 إعادة تعيين الفلاتر"):
    st.session_state.time_range = "الكل"
    st.session_state.selected_account = "جميع الحسابات"
time_range = st.sidebar.selectbox("الفترة الزمنية", ["الكل", "آخر 7 أيام", "آخر 30 يومًا", "آخر 90 يومًا"], 
                                  key="time_range", index=["الكل", "آخر 7 أيام", "آخر 30 يومًا", "آخر 90 يومًا"].index(st.session_state.get("time_range", "الكل")))
options_list = ["جميع الحسابات"] + list(account_options.keys())
default_index = 0
stored_account = st.session_state.get("selected_account", "جميع الحسابات")
if stored_account != "جميع الحسابات" and stored_account in account_options:
    default_index = options_list.index(stored_account)
selected_account = st.sidebar.selectbox("اختر حسابًا", options=options_list, 
                                        format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x], 
                                        key="selected_account", index=default_index)

if time_range == "آخر 7 أيام":
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
elif time_range == "آخر 30 يومًا":
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
elif time_range == "آخر 90 يومًا":
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
else:
    start_date = None

transactions = fm.filter_transactions(
    account_id=selected_account if selected_account != "جميع الحسابات" else None,
    start_date=start_date
)
df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"]) if transactions else pd.DataFrame()

if not df.empty:
    df["amount"] = pd.to_numeric(df["amount"], errors='coerce')
    df = df.dropna(subset=["amount"])

total_balance = sum(acc[2] for acc in accounts)
col1, col2, col3 = st.columns(3)
col1.metric("💰 إجمالي الرصيد", f"{total_balance:,.2f}", delta_color="normal")
if not df.empty:
    total_in = df[df["type"] == "IN"]["amount"].sum()
    total_out = df[df["type"] == "OUT"]["amount"].sum()
    col2.metric("📥 إجمالي الوارد", f"{total_in:,.2f}", delta=f"{total_in - total_out:,.2f}")
    col3.metric("📤 إجمالي الصادر", f"{total_out:,.2f}", delta=f"{total_out - total_in:,.2f}")

# رسم بياني لتوزيع الأرصدة
st.subheader("🏦 توزيع الأرصدة بين الحسابات")
if accounts:
    account_df = pd.DataFrame(accounts, columns=["id", "name", "balance", "min_balance", "created_at"])
    fig = px.pie(account_df, values="balance", names="name", title="توزيع الأرصدة")
    st.plotly_chart(fig)

# ملخص اليوم
st.subheader("📅 ملخص اليوم")
today = datetime.now().strftime("%Y-%m-%d")
today_trans = fm.filter_transactions(start_date=today)
if today_trans:
    today_df = pd.DataFrame(today_trans, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"])
    today_in = today_df[today_df["type"] == "IN"]["amount"].sum()
    today_out = today_df[today_df["type"] == "OUT"]["amount"].sum()
    st.write(f"وارد اليوم: {today_in:,.2f} | صادر اليوم: {today_out:,.2f}")
else:
    st.write("لا توجد معاملات اليوم")
