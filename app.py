import streamlit as st
import pandas as pd
import plotly.express as px
from finance_manager import FinanceManager
from datetime import timedelta, datetime

st.set_page_config(page_title="FloosAfandy", layout="wide", initial_sidebar_state="expanded")
fm = FinanceManager()

# Theme setup
if 'theme' not in st.session_state:
    st.session_state.theme = "فاتح"
theme = st.sidebar.selectbox("اختر الثيم", ["فاتح", "داكن"], index=0 if st.session_state.theme == "فاتح" else 1)
st.session_state.theme = theme

if theme == "داكن":
    st.markdown("<style>.stApp {background-color: #2b2b2b; color: white;}</style>", unsafe_allow_html=True)
else:
    st.markdown("<style>.stApp {background-color: white; color: black;}</style>", unsafe_allow_html=True)

st.title("FloosAfandy - إدارة مالياتك بسهولة")
alerts = fm.check_alerts()
if alerts:
    st.warning("📢 التنبيهات:")
    for alert in alerts:
        st.warning(alert)

st.markdown("### اختر الخيار:")
menu = st.columns(4)
with menu[0]:
    if st.button("🏦 إدارة الحسابات", use_container_width=True):
        st.switch_page("pages/accounts.py")
with menu[1]:
    if st.button("💸 تسجيل المعاملات", use_container_width=True):
        st.switch_page("pages/transactions.py")
with menu[2]:
    if st.button("📊 التقارير", use_container_width=True):
        st.switch_page("pages/reports.py")
with menu[3]:
    st.button("📈 لوحة التحكم", type="primary", disabled=True, use_container_width=True)

# إدارة الفئات
st.sidebar.header("📂 إدارة الفئات")
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
cat_account_id = st.sidebar.selectbox("الحساب", options=list(account_options.keys()), 
                                      format_func=lambda x: account_options[x], key="cat_account")
cat_trans_type = st.sidebar.selectbox("نوع المعاملة", ["وارد", "منصرف"], key="cat_type")
cat_name = st.sidebar.text_input("اسم الفئة", key="cat_name")
if st.sidebar.button("💾 إضافة الفئة", use_container_width=True):
    fm.add_custom_category(cat_account_id, "IN" if cat_trans_type == "وارد" else "OUT", cat_name)
    st.sidebar.success("تم إضافة الفئة!")
    st.rerun()

st.sidebar.subheader("الفئات الموجودة")
all_categories = fm.get_all_categories()
if all_categories:
    for cat in all_categories:
        cat_id, cat_acc_id, cat_type, cat_name = cat
        col1, col2, col3 = st.sidebar.columns([3, 1, 1])
        col1.write(f"{account_options[cat_acc_id]} - {'وارد' if cat_type == 'IN' else 'منصرف'}: {cat_name}")
        if col2.button("🗑️", key=f"del_cat_{cat_id}"):
            fm.delete_custom_category(cat_id)
            st.sidebar.success("تم الحذف!")
            st.rerun()
        if col3.button("✏️", key=f"edit_cat_{cat_id}"):
            with st.sidebar.expander(f"تعديل {cat_name}", expanded=True):
                new_name = st.text_input("اسم جديد", value=cat_name, key=f"new_name_{cat_id}")
                new_type = st.selectbox("نوع", ["وارد", "منصرف"], 
                                        index=0 if cat_type == "IN" else 1, key=f"new_type_{cat_id}")
                if st.button("💾 حفظ التعديل", key=f"save_edit_{cat_id}", use_container_width=True):
                    fm.conn.execute('UPDATE custom_categories SET category_name = ?, transaction_type = ? WHERE id = ?',
                                    (new_name, "IN" if new_type == "وارد" else "OUT", cat_id))
                    fm.conn.commit()
                    st.sidebar.success("تم التعديل!")
                    st.rerun()

# باقي الكود (نظرة عامة، رسوم بيانية، إلخ) لم يتغير، لكن الفئات تُستخدم في الرسم البياني للمصروفات
st.markdown("### 📈 نظرة عامة")
st.sidebar.header("⚙️ فلاتر العرض")
if st.sidebar.button("🔄 إعادة تعيين", use_container_width=True):
    st.session_state.time_range = "الكل"
    st.session_state.selected_account = "جميع الحسابات"
time_range = st.sidebar.selectbox("الفترة", ["الكل", "آخر 7 أيام", "آخر 30 يومًا", "آخر 90 يومًا"], key="time_range")
options_list = ["جميع الحسابات"] + list(account_options.keys())
selected_account = st.sidebar.selectbox("الحساب", options=options_list, 
                                        format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x], 
                                        key="selected_account")

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
col1, col2, col3 = st.columns(3)
col1.metric("💰 إجمالي الرصيد", f"{total_balance:,.2f}")
col2.metric("📥 الوارد", f"{df[df['type'] == 'IN']['amount'].sum():,.2f}" if not df.empty else "0.00")
col3.metric("📤 الصادر", f"{df[df['type'] == 'OUT']['amount'].sum():,.2f}" if not df.empty else "0.00")

st.subheader("🏦 توزيع الأرصدة")
if accounts:
    account_df = pd.DataFrame(accounts, columns=["id", "name", "balance", "min_balance", "created_at"])
    fig = px.pie(account_df, values="balance", names="name", title="توزيع الأرصدة")
    st.plotly_chart(fig)

st.subheader("📊 توزيع المصروفات حسب الفئات")
if not df.empty and not df[df["type"] == "OUT"].empty:
    expenses_df = df[df["type"] == "OUT"].assign(category=df["category"].str.split(", ")).explode("category")
    category_summary = expenses_df.groupby("category")["amount"].sum().reset_index()
    fig_category = px.pie(category_summary, values="amount", names="category", title="توزيع المصروفات")
    st.plotly_chart(fig_category)

st.subheader("📅 ملخص اليوم")
today = datetime.now().strftime("%Y-%m-%d")
today_trans = fm.filter_transactions(start_date=today)
if today_trans:
    today_df = pd.DataFrame(today_trans, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"])
    st.write(f"وارد: {today_df[today_df['type'] == 'IN']['amount'].sum():,.2f} | صادر: {today_df[today_df['type'] == 'OUT']['amount'].sum():,.2f}")
else:
    st.write("لا توجد معاملات اليوم")
