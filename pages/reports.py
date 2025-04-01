import streamlit as st
import pandas as pd
import plotly.express as px
from finance_manager import FinanceManager
import io

# إعداد الصفحة
st.title("📊 التقارير المالية")

# إنشاء كائن لإدارة البيانات
fm = FinanceManager()

# فلاتر التقرير في الشريط الجانبي
st.sidebar.header("⚙️ فلاتر التقرير")
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
account_id = st.sidebar.selectbox("اختر الحساب", options=["جميع الحسابات"] + list(account_options.keys()), 
                                 format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x])
trans_type = st.sidebar.selectbox("نوع المعاملة", ["الكل", "وارد", "صادر"])
start_date = st.sidebar.date_input("من تاريخ", value=None)
end_date = st.sidebar.date_input("إلى تاريخ", value=None)
min_amount = st.sidebar.number_input("الحد الأدنى للمبلغ", min_value=0.0, step=100.0, value=0.0)
max_amount = st.sidebar.number_input("الحد الأعلى للمبلغ", min_value=0.0, step=100.0, value=0.0)

# تحويل التواريخ إلى تنسيق مناسب
start_date_str = start_date.strftime("%Y-%m-%d %H:%M:%S") if start_date else None
end_date_str = end_date.strftime("%Y-%m-%d %H:%M:%S") if end_date else None
trans_type_en = None if trans_type == "الكل" else ("IN" if trans_type == "وارد" else "OUT")

# جلب المعاملات مع الفلاتر
transactions = fm.filter_transactions(
    account_id=account_id if account_id != "جميع الحسابات" else None,
    start_date=start_date_str,
    end_date=end_date_str,
    trans_type=trans_type_en
)

# تحديث قائمة الأعمدة لتشمل payment_method
if transactions:
    df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method"])
    if min_amount > 0:
        df = df[df["amount"] >= min_amount]
    if max_amount > 0:
        df = df[df["amount"] <= max_amount]
else:
    df = pd.DataFrame()

# عرض التقرير
st.subheader("📈 تقرير المعاملات")
if not df.empty:
    # عرض الجدول مع إضافة payment_method
    df_display = df[["date", "type", "amount", "description", "payment_method"]]
    df_display["type"] = df_display["type"].replace({"IN": "وارد", "OUT": "صادر"})
    st.dataframe(df_display, use_container_width=True)

    # إحصائيات سريعة
    total_in = df[df["type"] == "IN"]["amount"].sum()
    total_out = df[df["type"] == "OUT"]["amount"].sum()
    col1, col2 = st.columns(2)
    col1.metric("💰 إجمالي الوارد", f"{total_in:,.2f}")
    col2.metric("💸 إجمالي الصادر", f"{total_out:,.2f}")

    # خيارات الرسم البياني
    chart_type = st.selectbox("اختر نوع الرسم البياني", ["شريطي", "خطي", "دائري"])
    if chart_type == "شريطي":
        fig = px.bar(df, x="date", y="amount", color="type", title="📅 تحليل المعاملات حسب التاريخ")
    elif chart_type == "خطي":
        fig = px.line(df, x="date", y="amount", color="type", title="📉 تطور المعاملات")
    else:  # دائري
        fig = px.pie(df, values="amount", names="type", title="🥧 نسبة الوارد إلى الصادر")
    st.plotly_chart(fig)

    # تصدير التقرير إلى CSV
    csv = df_display.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 تحميل التقرير كـ CSV",
        data=csv,
        file_name="تقرير_المعاملات.csv",
        mime="text/csv",
    )
else:
    st.info("ℹ️ لا توجد معاملات تطابق المعايير المحددة.")

# نصائح
st.markdown("### 💡 نصيحة")
st.write("استخدم الفلاتر لتحليل المعاملات بدقة أكبر، وحمل التقرير لمشاركته أو أرشفته!")