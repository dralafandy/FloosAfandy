import streamlit as st
import pandas as pd
import plotly.express as px
from finance_manager import FinanceManager
from datetime import timedelta, datetime

# إعداد الصفحة
st.title("📈 لوحة التحكم المالية")
st.markdown("### 🎯 نظرة شاملة على أدائك المالي")

# إنشاء كائن لإدارة البيانات
fm = FinanceManager()

# فلاتر تفاعلية في الشريط الجانبي
st.sidebar.header("⚙️ خيارات العرض")
time_range = st.sidebar.selectbox("الفترة الزمنية", ["الكل", "آخر 7 أيام", "آخر 30 يومًا", "آخر 90 يومًا"])
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}
selected_account = st.sidebar.selectbox("اختر حسابًا", options=["جميع الحسابات"] + list(account_options.keys()), 
                                       format_func=lambda x: "جميع الحسابات" if x == "جميع الحسابات" else account_options[x])

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

# ملخص الحسابات
st.subheader("🏦 ملخص الحسابات")
if accounts:
    account_data = [{"الاسم": acc[1], "الرصيد": acc[2], "الحد الأدنى": acc[3]} for acc in accounts]
    st.dataframe(account_data, use_container_width=True)

    st.markdown("### 🌟 أعلى 3 حسابات رصيدًا")
    top_accounts = sorted(accounts, key=lambda x: x[2], reverse=True)[:3]
    for acc in top_accounts:
        st.write(f"🏅 {acc[1]}: {acc[2]:,.2f}")

# تحليل المعاملات
st.subheader("📊 تحليل المعاملات")
if not df.empty:
    # رسم بياني خطي لتطور الرصيد
    try:
        df["date"] = pd.to_datetime(df["date"])
        # حساب الرصيد التراكمي باستخدام DataFrame بدلاً من Series مباشرة
        df["balance_change"] = df.apply(lambda x: x["amount"] if x["type"] == "IN" else -x["amount"], axis=1)
        balance_df = df[["date", "balance_change"]].sort_values("date")
        balance_df["cumulative_balance"] = balance_df["balance_change"].cumsum()
        
        fig_line = px.line(balance_df, x="date", y="cumulative_balance", 
                           title="📉 تطور الرصيد بمرور الوقت", 
                           labels={"date": "التاريخ", "cumulative_balance": "الرصيد"})
        st.plotly_chart(fig_line)
    except Exception as e:
        st.error(f"❌ خطأ في إنشاء الرسم البياني: {str(e)}")

    # رسم بياني دائري للوارد والصادر
    fig_pie = px.pie(values=[total_in, total_out], names=["وارد", "صادر"], 
                     title="🥧 نسبة الوارد إلى الصادر", hole=0.3)
    st.plotly_chart(fig_pie)

    # أكثر المعاملات قيمة مع طريقة الدفع
    st.markdown("### 💸 أعلى 5 معاملات")
    top_transactions = df.nlargest(5, "amount")[["date", "type", "amount", "description", "payment_method"]]
    top_transactions["type"] = top_transactions["type"].replace({"IN": "وارد", "OUT": "صادر"})
    st.table(top_transactions)

else:
    st.info("ℹ️ لا توجد معاملات لعرضها في هذه الفترة أو الحساب المحدد.")

# نصائح تفاعلية
st.markdown("### 💡 نصيحة اليوم")
st.write("تابع تطور رصيدك بانتظام لتحديد الأنماط المالية وتحسين قراراتك!")