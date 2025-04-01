import streamlit as st
import pandas as pd
import plotly.express as px
from finance_manager import FinanceManager
from datetime import timedelta, datetime

# إعداد الصفحة
st.set_page_config(page_title="نظام إدارة الماليات", layout="wide", initial_sidebar_state="expanded")

# إنشاء كائن لإدارة البيانات
fm = FinanceManager()

# تخصيص الواجهة
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

# شريط التنقل العلوي
st.title("نظام إدارة الماليات المتقدم")
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

# لوحة التحكم
st.markdown("### 🎯 نظرة شاملة على أدائك المالي")

# فلاتر تفاعلية في الشريط الجانبي
st.sidebar.header("⚙️ خيارات العرض")
if st.sidebar.button("🔄 إعادة تعيين الفلاتر"):
    st.session_state.time_range = "الكل"
    st.session_state.selected_account = "جميع الحسابات"
time_range = st.sidebar.selectbox("الفترة الزمنية", ["الكل", "آخر 7 أيام", "آخر 30 يومًا", "آخر 90 يومًا"], 
                                  key="time_range", index=["الكل", "آخر 7 أيام", "آخر 30 يومًا", "آخر 90 يومًا"].index(st.session_state.get("time_range", "الكل")))
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
options_list = ["جميع الحسابات"] + list(account_options.keys())
# تحديد المؤشر بناءً على القيمة المخزنة
default_index = 0  # افتراضيًا "جميع الحسابات"
stored_account = st.session_state.get("selected_account", "جميع الحسابات")
if stored_account != "جميع الحسابات" and stored_account in account_options:
    default_index = options_list.index(stored_account)
selected_account = st.sidebar.selectbox("اختر حسابًا", options=options_list, 
                                        format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x], 
                                        key="selected_account", index=default_index)

# تحديد الفترة الزمنية
if time_range == "آخر 7 أيام":
    start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d %H:%M:%S")
elif time_range == "آخر 30 يومًا":
    start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
elif time_range == "آخر 90 يومًا":
    start_date = (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d %H:%M:%S")
else:
    start_date = None

# جلب البيانات
transactions = fm.filter_transactions(
    account_id=selected_account if selected_account != "جميع الحسابات" else None,
    start_date=start_date
)
df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method"]) if transactions else pd.DataFrame()

# تنظيف عمود amount
if not df.empty:
    df["amount"] = pd.to_numeric(df["amount"], errors='coerce')
    df = df.dropna(subset=["amount"])

# إجمالي الرصيد والإحصائيات
total_balance = sum(acc[2] for acc in accounts)
col1, col2, col3 = st.columns(3)
col1.metric("💰 إجمالي الرصيد", f"{total_balance:,.2f}", delta_color="normal")
if not df.empty:
    total_in = df[df["type"] == "IN"]["amount"].sum()
    total_out = df[df["type"] == "OUT"]["amount"].sum()
    col2.metric("📥 إجمالي الوارد", f"{total_in:,.2f}", delta=f"{total_in - total_out:,.2f}")
    col3.metric("📤 إجمالي الصادر", f"{total_out:,.2f}", delta=f"{total_out - total_in:,.2f}")

# ملخص اليوم
st.subheader("📅 ملخص اليوم")
today = datetime.now().strftime("%Y-%m-%d")
today_trans = fm.filter_transactions(start_date=today)
if today_trans:
    today_df = pd.DataFrame(today_trans, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method"])
    today_in = today_df[today_df["type"] == "IN"]["amount"].sum()
    today_out = today_df[today_df["type"] == "OUT"]["amount"].sum()
    st.write(f"وارد اليوم: {today_in:,.2f} | صادر اليوم: {today_out:,.2f}")
else:
    st.write("لا توجد معاملات اليوم")

# ملخص الحسابات
st.subheader("🏦 ملخص الحسابات")
if accounts:
    account_data = [{"الاسم": acc[1], "الرصيد": acc[2], "الحد الأدنى": acc[3]} for acc in accounts]
    st.dataframe(account_data, use_container_width=True)

    st.markdown("### 🌟 أعلى 3 حسابات رصيدًا")
    top_accounts = sorted(accounts, key=lambda x: x[2], reverse=True)[:3]
    for acc in top_accounts:
        st.write(f"🏅 {acc[1]}: {acc[2]:,.2f}")

# ملخص الميزانيات
st.subheader("💼 ملخص الميزانيات")
account_id_filter = selected_account if selected_account != "جميع الحسابات" else None
budgets = fm.get_budgets(account_id=account_id_filter)
if budgets:
    for budget in budgets:
        account_name = account_options[budget[4]]
        st.write(f"{account_name} - {budget[1]}: منفق {budget[3]:,.2f} من {budget[2]:,.2f}")
else:
    st.write("لا توجد ميزانيات حاليًا للحساب المختار")

# تحليل المعاملات
st.subheader("📊 تحليل المعاملات")
if not df.empty:
    try:
        df["date"] = pd.to_datetime(df["date"])
        df["balance_change"] = df.apply(lambda x: x["amount"] if x["type"] == "IN" else -x["amount"], axis=1)
        balance_df = df[["date", "balance_change"]].sort_values("date")
        balance_df["cumulative_balance"] = balance_df["balance_change"].cumsum()
        
        fig_line = px.line(balance_df, x="date", y="cumulative_balance", 
                           title="📉 تطور الرصيد بمرور الوقت", 
                           labels={"date": "التاريخ", "cumulative_balance": "الرصيد"})
        st.plotly_chart(fig_line)
    except Exception as e:
        st.error(f"❌ خطأ في إنشاء الرسم البياني: {str(e)}")

    fig_pie = px.pie(values=[total_in, total_out], names=["وارد", "صادر"], 
                     title="🥧 نسبة الوارد إلى الصادر", hole=0.3)
    st.plotly_chart(fig_pie)

    st.markdown("### 💸 أعلى 5 معاملات")
    top_transactions = df.nlargest(5, "amount")[["date", "type", "amount", "description", "payment_method"]]
    top_transactions["type"] = top_transactions["type"].replace({"IN": "وارد", "OUT": "صادر"})
    st.table(top_transactions)

else:
    st.info("ℹ️ لا توجد معاملات لعرضها في هذه الفترة أو الحساب المحدد.")

# نصائح تفاعلية
st.markdown("### 💡 نصيحة اليوم")
st.write("تابع تطور رصيدك بانتظام لتحديد الأنماط المالية وتحسين قراراتك!")