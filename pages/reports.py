import streamlit as st
import pandas as pd
import plotly.express as px
from finance_manager import FinanceManager
from datetime import datetime, timedelta

st.title("📊 التقارير المالية")

fm = FinanceManager()

# 🔹 فلاتر التقارير في الشريط الجانبي
st.sidebar.header("⚙️ فلاتر التقارير")

accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
account_id = st.sidebar.selectbox("🏦 اختر الحساب", options=["جميع الحسابات"] + list(account_options.keys()), 
                                  format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x])

trans_type = st.sidebar.selectbox("📋 نوع المعاملة", ["الكل", "وارد", "منصرف"])
start_date = st.sidebar.date_input("📅 من تاريخ", value=datetime.now() - timedelta(days=30))
end_date = st.sidebar.date_input("📅 إلى تاريخ", value=datetime.now())

# 🔹 فلتر الفئات
if account_id == "جميع الحسابات":
    categories = fm.conn.execute("SELECT DISTINCT category FROM transactions WHERE category IS NOT NULL").fetchall()
else:
    categories = fm.get_custom_categories(account_id, "IN" if trans_type == "وارد" else "OUT" if trans_type == "منصرف" else None)

category_options = ["الكل"] + [cat[0] for cat in categories] if categories else ["الكل"]
category = st.sidebar.selectbox("📂 اختر الفئة", options=category_options)

# 🔹 جلب المعاملات
start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S")
end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S")
transactions = fm.filter_transactions(
    account_id=account_id if account_id != "جميع الحسابات" else None,
    start_date=start_date_str,
    end_date=end_date_str,
    trans_type="IN" if trans_type == "وارد" else "OUT" if trans_type == "منصرف" else None,
    category=category if category != "الكل" else None
)

if transactions:
    df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"])
    df["type"] = df["type"].replace({"IN": "وارد", "OUT": "منصرف"})
    df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d %H:%M")
    df["amount"] = df["amount"].map("{:,.2f}".format)  # تنسيق الأرقام

    # 🔹 عرض ملخص مالي أعلى الصفحة
    total_in = df[df["type"] == "وارد"]["amount"].astype(float).sum() if "وارد" in df["type"].values else 0
    total_out = df[df["type"] == "منصرف"]["amount"].astype(float).sum() if "منصرف" in df["type"].values else 0
    net_cash_flow = total_in - total_out

    col1, col2, col3 = st.columns(3)
    col1.metric("💰 إجمالي الإيرادات", f"{total_in:,.2f} ج.م")
    col2.metric("💸 إجمالي المصروفات", f"{total_out:,.2f} ج.م")
    col3.metric("📉 صافي التدفقات النقدية", f"{net_cash_flow:,.2f} ج.م", delta=f"{net_cash_flow:,.2f}")

    # 🔹 جدول المعاملات
    st.subheader("📋 جدول المعاملات")
    st.dataframe(df[["date", "type", "amount", "description", "payment_method", "category"]])

    # 🔹 الرسم البياني الزمني
    st.subheader("📈 المعاملات بمرور الوقت")
    df["amount"] = df["amount"].astype(float)
    fig = px.bar(df, x="date", y="amount", color="type", title="المعاملات بمرور الوقت")
    fig.update_xaxes(title="التاريخ", tickangle=45)
    fig.update_yaxes(title="المبلغ (ج.م)")
    st.plotly_chart(fig)

    # 🔹 تحليل حسب الفئات
    st.subheader("📊 توزيع المبالغ حسب الفئات")
    category_summary = df.groupby("category")["amount"].sum().reset_index()
    fig_pie = px.pie(category_summary, values="amount", names="category", title="توزيع المبالغ حسب الفئات",
                      hole=0.4, labels={"amount": "المبلغ"})
    fig_pie.update_traces(textinfo="percent+label")
    st.plotly_chart(fig_pie)
else:
    st.info("ℹ️ لا توجد معاملات تطابق الفلاتر.")
