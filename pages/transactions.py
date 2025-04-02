import streamlit as st
import pandas as pd
from finance_manager import FinanceManager
from styles import apply_sidebar_styles

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

# Main content
st.title("💸 معاملاتي")
st.markdown("<p style='color: #6b7280;'>سجل وتحكم في كل حركة مالية</p>", unsafe_allow_html=True)
st.markdown("---")

accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}

st.markdown("""
    <style>
    .transaction-card {background-color: #ffffff; padding: 8px; border-radius: 5px; margin: 5px 0; box-shadow: 0 1px 2px rgba(0,0,0,0.1);}
    .form-container {background-color: #f9fafb; padding: 10px; border-radius: 8px; margin-bottom: 10px;}
    .category-container {background-color: #e5e7eb; padding: 10px; border-radius: 8px; margin-bottom: 20px;}
    @media (max-width: 768px) {
        .transaction-card {font-size: 12px; padding: 6px;}
        .stButton>button {font-size: 12px; padding: 6px;}
        .form-container, .category-container {padding: 8px;}
        .stTextInput {font-size: 12px;}
    }
    </style>
""", unsafe_allow_html=True)

st.subheader("📂 إدارة الفئات")
with st.container():
    st.markdown("<div class='category-container'>", unsafe_allow_html=True)
    cat_account_id = st.selectbox("🏦 الحساب", options=list(account_options.keys()), 
                                  format_func=lambda x: account_options[x], key="cat_account")
    cat_trans_type = st.selectbox("📋 النوع", ["وارد", "منصرف"], key="cat_type")
    cat_trans_type_db = "IN" if cat_trans_type == "وارد" else "OUT"
    new_category_name = st.text_input("📛 اسم الفئة الجديدة", placeholder="مثال: مكافأة", key="new_category_name")
    
    if st.button("➕ إضافة فئة", key="add_category_button"):
        if new_category_name and new_category_name.strip():
            try:
                fm.add_custom_category(cat_account_id, cat_trans_type_db, new_category_name)
                st.success(f"✅ تمت إضافة الفئة: {new_category_name}")
                st.rerun()
            except Exception as e:
                st.error(f"❌ خطأ أثناء إضافة الفئة: {str(e)}")
        else:
            st.warning("⚠️ يرجى إدخال اسم للفئة!")
    
    categories = fm.get_custom_categories(cat_account_id, cat_trans_type_db)
    if categories:
        st.write("الفئات الحالية:")
        for cat in categories:
            cat_name = cat[0]
            col1, col2 = st.columns([3, 1])
            col1.write(f"{'📥' if cat_trans_type_db == 'IN' else '📤'} {cat_name}")
            if col2.button("🗑️", key=f"del_cat_{cat_name}_{cat_account_id}_{cat_trans_type_db}"):
                try:
                    fm.delete_custom_category_by_name(cat_account_id, cat_trans_type_db, cat_name)
                    st.success(f"🗑️ تم حذف الفئة: {cat_name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ خطأ أثناء الحذف: {str(e)}")
    else:
        st.info("ℹ️ لا توجد فئات لهذا الحساب ونوع المعاملة.")
    st.markdown("</div>", unsafe_allow_html=True)

st.subheader("➕ إضافة معاملة")
if "trans_type" not in st.session_state:
    st.session_state.trans_type = "وارد"
if "account_id" not in st.session_state:
    st.session_state.account_id = list(account_options.keys())[0] if accounts else None

account_id = st.selectbox("🏦 الحساب", options=list(account_options.keys()), 
                          format_func=lambda x: account_options[x], key="pre_add_account",
                          on_change=lambda: st.session_state.update({"account_id": st.session_state.pre_add_account}))
trans_type = st.selectbox("📋 نوع المعاملة", ["وارد", "منصرف"], key="pre_add_type",
                          on_change=lambda: st.session_state.update({"trans_type": st.session_state.pre_add_type}))
trans_type_db = "IN" if trans_type == "وارد" else "OUT"

categories = fm.get_custom_categories(st.session_state.account_id, trans_type_db)
category_options = [cat[0] for cat in categories] if categories else ["غير مصنف"]

with st.form(key="add_transaction_form"):
    st.markdown("<div class='form-container'>", unsafe_allow_html=True)
    st.selectbox("🏦 الحساب", options=list(account_options.keys()), 
                 format_func=lambda x: account_options[x], key="add_account", 
                 index=list(account_options.keys()).index(st.session_state.account_id))
    st.selectbox("📋 نوع المعاملة", ["وارد", "منصرف"], key="add_type", 
                 index=0 if st.session_state.trans_type == "وارد" else 1)
    selected_category = st.selectbox("📂 الفئة", options=category_options, key="add_category")
    amount = st.number_input("💵 المبلغ", min_value=0.01, step=0.01, format="%.2f", key="add_amount")
    payment_method = st.selectbox("💳 طريقة الدفع", ["كاش", "بطاقة ائتمان", "تحويل بنكي"], key="add_payment")
    description = st.text_area("📝 الوصف", placeholder="وصف المعاملة (اختياري)", key="add_desc")
    st.markdown("</div>", unsafe_allow_html=True)
    
    col5, col6 = st.columns(2)
    with col5:
        submit_button = st.form_submit_button("💾 حفظ", type="primary", use_container_width=True)
    with col6:
        submit_add_another = st.form_submit_button("➕ حفظ وإضافة", use_container_width=True)

if submit_button or submit_add_another:
    try:
        final_account_id = st.session_state.account_id
        final_trans_type_db = "IN" if st.session_state.trans_type == "وارد" else "OUT"
        final_category = selected_category if selected_category in category_options else "غير مصنف"
        result = fm.add_transaction(final_account_id, amount, final_trans_type_db, description, payment_method, final_category)
        st.success(f"✅ تم حفظ المعاملة بالفئة: {final_category}")
        if result and "تنبيه" in result:
            st.warning(result)
        if submit_add_another:
            st.session_state["keep_open"] = True
        else:
            st.rerun()
    except Exception as e:
        st.error(f"❌ خطأ أثناء الحفظ: {str(e)}")

st.subheader("📋 المعاملات")
search_query = st.text_input("🔍 تصفية المعاملات", "")
transactions = fm.get_all_transactions()
if transactions:
    df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"])
    df["account"] = df["account_id"].map(account_options)
    df["type"] = df["type"].replace({"IN": "وارد", "OUT": "منصرف"})
    filtered_df = df[df.apply(lambda row: search_query.lower() in str(row).lower(), axis=1)] if search_query else df
    for i, row in filtered_df.iterrows():
        st.markdown(f"<div class='transaction-card'>{'📥' if row['type'] == 'وارد' else '📤'} {row['date']} - {row['amount']:,.2f} - {row['account']} - {row['category']}</div>", 
                    unsafe_allow_html=True)
else:
    st.info("ℹ️ لا توجد معاملات.")

if transactions:
    st.subheader("🛠️ تعديل أو حذف")
    trans_id = st.selectbox("اختر معاملة", options=df["id"].tolist(), 
                            format_func=lambda x: f"معاملة {x} - {df[df['id'] == x]['date'].iloc[0]} - {df[df['id'] == x]['category'].iloc[0]}")
    selected_trans = df[df["id"] == trans_id].iloc[0]
    with st.form(key="edit_transaction_form"):
        st.markdown("<div class='form-container'>", unsafe_allow_html=True)
        edit_account = st.selectbox("🏦 الحساب", options=list(account_options.keys()), 
                                    index=list(account_options.keys()).index(selected_trans["account_id"]), key="edit_account")
        edit_type = st.selectbox("📋 النوع", ["وارد", "منصرف"], 
                                 index=0 if selected_trans["type"] == "وارد" else 1, key="edit_type")
        edit_type_db = "IN" if edit_type == "وارد" else "OUT"
        edit_categories = fm.get_custom_categories(edit_account, edit_type_db)
        edit_category_options = [cat[0] for cat in edit_categories] if edit_categories else ["غير مصنف"]
        edit_selected_category = st.selectbox("📂 الفئة", options=edit_category_options, 
                                              index=edit_category_options.index(selected_trans["category"]) if selected_trans["category"] in edit_category_options else 0, 
                                              key="edit_category")
        edit_amount = st.number_input("💵 المبلغ", value=float(selected_trans["amount"]), min_value=0.01, step=0.01, format="%.2f", key="edit_amount")
        edit_payment = st.selectbox("💳 طريقة الدفع", ["كاش", "بطاقة ائتمان", "تحويل بنكي"], 
                                    index=["كاش", "بطاقة ائتمان", "تحويل بنكي"].index(selected_trans["payment_method"]), key="edit_payment")
        edit_desc = st.text_area("📝 الوصف", value=selected_trans["description"], key="edit_desc")
        st.markdown("</div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            save_button = st.form_submit_button("💾 حفظ التعديل", use_container_width=True)
        with col2:
            delete_button = st.form_submit_button("🗑️ حذف", use_container_width=True)

    if save_button:
        try:
            final_edit_category = edit_selected_category if edit_selected_category in edit_category_options else "غير مصنف"
            result = fm.edit_transaction(trans_id, edit_account, edit_amount, edit_type_db, edit_desc, edit_payment, final_edit_category)
            st.success(f"✅ تم تعديل المعاملة بالفئة: {final_edit_category}")
            if result and "تنبيه" in result:
                st.warning(result)
            st.rerun()
        except Exception as e:
            st.error(f"❌ خطأ أثناء التعديل: {str(e)}")

    if delete_button:
        try:
            with fm.conn:
                old_trans = fm.conn.execute('SELECT type, amount, account_id FROM transactions WHERE id = ?', (trans_id,)).fetchone()
                old_type, old_amount, old_account_id = old_trans
                fm.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', 
                                (old_amount if old_type == "IN" else -old_amount, old_account_id))
                fm.conn.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
                fm.conn.commit()
            st.success("🗑️ تم الحذف!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ خطأ أثناء الحذف: {str(e)}")
