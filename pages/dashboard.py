import streamlit as st
import pandas as pd
import plotly.express as px
from finance_manager import FinanceManager
from datetime import datetime, timedelta

st.title("📈 لوحة التحكم المالية")
st.markdown("### 🎯 نظرة شاملة")
fm = FinanceManager()

st.sidebar.header("⚙️ خيارات العرض")
time_range = st.sidebar.selectbox("الفترة الزمنية", ["الكل", "آخر 7 أيام", "آخر 30 يومًا", "آخر 90 يومًا"])
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
selected_account = st.sidebar.selectbox("اختر حسابًا", options=["جميع الحسابات"] + list(account_options.keys()), 
                                        format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x])

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
    df["date"] = pd.to_datetime(df["date"])

total_balance = sum(acc[2] for acc in accounts)
col1, col2, col3 = st.columns(3)
col1.metric("💰 إجمالي الرصيد", f"{total_balance:,.2f}")
col2.metric("📥 الوارد", f"{df[df['type'] == 'IN']['amount'].sum():,.2f}" if not df.empty else "0.00")
col3.metric("📤 الصادر", f"{df[df['type'] == 'OUT']['amount'].sum():,.2f}" if not df.empty else "0.00")

st.subheader("🏦 ملخص الحسابات")
if accounts:
    account_data = [{"الاسم": acc[1], "الرصيد": acc[2], "الحد الأدنى": acc[3]} for acc in accounts]
    st.dataframe(account_data, use_container_width=True)

st.subheader("📊 تحليل المعاملات")
if not df.empty:
    col1, col2 = st.columns(2)
    with col1:
        df["balance_change"] = df.apply(lambda x: x["amount"] if x["type"] == "IN" else -x["amount"], axis=1)
        balance_df = df[["date", "balance_change"]].sort_values("date")
        balance_df["cumulative_balance"] = balance_df["balance_change"].cumsum()
        fig_line = px.line(balance_df, x="date", y="cumulative_balance", title="تطور الرصيد", color_discrete_sequence=["#FFD700"])
        st.plotly_chart(fig_line)
    with col2:
        fig_pie = px.pie(values=[df[df["type"] == "IN"]["amount"].sum(), df[df["type"] == "OUT"]["amount"].sum()], 
                         names=["وارد", "صادر"], title="نسبة الوارد/الصادر", hole=0.3,
                         color_discrete_map={"وارد": "green", "صادر": "red"})
        st.plotly_chart(fig_pie)
else:
    st.info("ℹ️ لا توجد معاملات.")
