import streamlit as st
import pandas as pd
import plotly.express as px
from finance_manager import FinanceManager
from datetime import datetime, timedelta

st.title("📊 التقارير")
fm = FinanceManager()

st.sidebar.header("⚙️ فلاتر التقارير")
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
account_id = st.sidebar.selectbox("🏦 الحساب", options=["جميع الحسابات"] + list(account_options.keys()), 
                                  format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x])
trans_type = st.sidebar.selectbox("📋 النوع", ["الكل", "وارد", "منصرف"])
payment_method = st.sidebar.selectbox("💳 طريقة الدفع", ["الكل", "كاش", "بطاقة ائتمان", "تحويل بنكي"])
start_date = st.sidebar.date_input("📅 من", value=None)
end_date = st.sidebar.date_input("📅 إلى", value=None)

# فلتر الفئات بناءً على نوع المعاملة
if trans_type != "الكل" and account_id != "جميع الحسابات":
    categories = fm.get_custom_categories(account_id, "IN" if trans_type == "وارد" else "OUT")
    category_options = ["الكل"] + [cat[0] for cat in categories]
else:
    category_options = ["الكل"]
category = st.sidebar.selectbox("📂 الفئة", options=category_options)

start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S") if start_date else None
end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S") if end_date else None

transactions = fm.filter_transactions(
    account_id=account_id if account_id != "جميع الحسابات" else None,
    start_date=start_date_str,
    end_date=end_date_str,
    trans_type="IN" if trans_type == "وارد" else "OUT" if trans_type == "منصرف" else None,
    category=category if category != "الكل" else None,
    payment_method=payment_method if payment_method != "الكل" else None
)

st.subheader("📋 جدول المعاملات")
if transactions:
    df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"])
    df["type"] = df["type"].replace({"IN": "وارد", "OUT": "منصرف"})
    df["account"] = df["account_id"].map(account_options)
    st.dataframe(df[["date", "type", "amount", "account", "description", "payment_method", "category"]])
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("💾 تحميل CSV", csv, "transactions_report.csv", "text/csv", use_container_width=True)
else:
    st.info("ℹ️ لا توجد معاملات تطابق الفلاتر.")

st.header("📈 رسوم بيانية")
if transactions:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(df, x="date", y="amount", color="type", title="المعاملات بمرور الوقت")
        st.plotly_chart(fig)
    with col2:
        df_expanded = df.assign(category=df["category"].str.split(", ")).explode("category")
        category_summary = df_expanded.groupby("category")["amount"].sum().reset_index()
        fig_pie = px.pie(category_summary, values="amount", names="category", title="توزيع حسب الفئات")
        st.plotly_chart(fig_pie)
