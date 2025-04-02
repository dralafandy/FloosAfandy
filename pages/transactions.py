import streamlit as st
from finance_manager import FinanceManager
import pandas as pd

st.title("💸 إدارة المعاملات")

fm = FinanceManager()
accounts = fm.get_all_accounts()
account_options = {acc[0]: acc[1] for acc in accounts}

# قسم إضافة معاملة جديدة
st.header("➕ إضافة معاملة جديدة")
with st.form(key="add_transaction_form"):
    col1, col2 = st.columns(2)
    with col1:
        account_id = st.selectbox("🏦 الحساب", options=list(account_options.keys()), 
                                  format_func=lambda x: account_options[x], key="add_account")
    with col2:
        trans_type = st.selectbox("📋 نوع المعاملة", ["وارد", "منصرف"], key="add_type")
    trans_type_db = "IN" if trans_type == "وارد" else "OUT"

    # جلب الفئات بناءً على نوع المعاملة والحساب
    categories = fm.get_custom_categories(account_id, trans_type_db)
    category_options = [cat[0] for cat in categories] if categories else ["غير مصنف"]
    category_options.append("إضافة فئة جديدة")
    category = st.selectbox("📂 الفئة", options=category_options, key="add_category")

    # إذا اختير "إضافة فئة جديدة"
    if category == "إضافة فئة جديدة":
        new_category = st.text_input("اسم الفئة الجديدة", key="new_category")
    else:
        new_category = None

    col3, col4 = st.columns(2)
    with col3:
        amount = st.number_input("💵 المبلغ", min_value=0.01, step=0.01, format="%.2f", key="add_amount")
    with col4:
        payment_method = st.selectbox("💳 طريقة الدفع", ["كاش", "بطاقة ائتمان", "تحويل بنكي"], key="add_payment")
    
    description = st.text_area("📝 الوصف", placeholder="وصف المعاملة (اختياري)", key="add_desc")

    submit_button = st.form_submit_button("💾 حفظ المعاملة", type="primary", use_container_width=True)

if submit_button:
    try:
        # إذا تم إدخال فئة جديدة، أضفها أولاً
        if new_category:
            fm.add_custom_category(account_id, trans_type_db, new_category)
            selected_category = new_category
        else:
            selected_category = category

        # حفظ المعاملة
        result = fm.add_transaction(account_id, amount, trans_type_db, description, payment_method, selected_category)
        st.success("✅ تم حفظ المعاملة بنجاح!")
        if result and "تنبيه" in result:
            st.warning(result)
        st.rerun()
    except Exception as e:
        st.error(f"❌ خطأ أثناء الحفظ: {str(e)}")

# قسم عرض وتعديل/حذف المعاملات
st.header("📋 المعاملات الحالية")
transactions = fm.get_all_transactions()
if transactions:
    df = pd.DataFrame(transactions, columns=["id", "date", "type", "amount", "account_id", "description", "payment_method", "category"])
    df["account"] = df["account_id"].map(account_options)
    df["type"] = df["type"].replace({"IN": "وارد", "OUT": "منصرف"})
    st.dataframe(df[["id", "date", "type", "amount", "account", "description", "payment_method", "category"]], use_container_width=True)

    st.subheader("🛠️ تعديل أو حذف معاملة")
    trans_id = st.selectbox("اختر معاملة", options=df["id"].tolist(), 
                            format_func=lambda x: f"معاملة {x} - {df[df['id'] == x]['date'].iloc[0]}")
    selected_trans = df[df["id"] == trans_id].iloc[0]

    with st.form(key="edit_transaction_form"):
        col5, col6 = st.columns(2)
        with col5:
            edit_account = st.selectbox("🏦 الحساب", options=list(account_options.keys()), 
                                        index=list(account_options.keys()).index(selected_trans["account_id"]), key="edit_acc")
        with col6:
            edit_type = st.selectbox("📋 النوع", ["وارد", "منصرف"], 
                                     index=0 if selected_trans["type"] == "وارد" else 1, key="edit_type")
        edit_type_db = "IN" if edit_type == "وارد" else "OUT"

        # جلب الفئات بناءً على الحساب ونوع المعاملة للتعديل
        edit_categories = fm.get_custom_categories(edit_account, edit_type_db)
        edit_category_options = [cat[0] for cat in edit_categories] if edit_categories else ["غير مصنف"]
        edit_category_options.append("إضافة فئة جديدة")
        edit_category = st.selectbox("📂 الفئة", options=edit_category_options, 
                                     index=edit_category_options.index(selected_trans["category"]) if selected_trans["category"] in edit_category_options else 0, 
                                     key="edit_cat")

        # إذا اختير "إضافة فئة جديدة" أثناء التعديل
        if edit_category == "إضافة فئة جديدة":
            edit_new_category = st.text_input("اسم الفئة الجديدة", key="edit_new_category")
        else:
            edit_new_category = None

        col7, col8 = st.columns(2)
        with col7:
            edit_amount = st.number_input("💵 المبلغ", value=float(selected_trans["amount"]), min_value=0.01, step=0.01, format="%.2f", key="edit_amount")
        with col8:
            edit_payment = st.selectbox("💳 طريقة الدفع", ["كاش", "بطاقة ائتمان", "تحويل بنكي"], 
                                        index=["كاش", "بطاقة ائتمان", "تحويل بنكي"].index(selected_trans["payment_method"]), key="edit_payment")
        
        edit_desc = st.text_area("📝 الوصف", value=selected_trans["description"], key="edit_desc")

        col9, col10 = st.columns(2)
        with col9:
            save_button = st.form_submit_button("💾 حفظ التعديل", use_container_width=True)
        with col10:
            delete_button = st.form_submit_button("🗑️ حذف المعاملة", use_container_width=True)

    if save_button:
        try:
            # إذا تم إدخال فئة جديدة أثناء التعديل
            if edit_new_category:
                fm.add_custom_category(edit_account, edit_type_db, edit_new_category)
                final_category = edit_new_category
            else:
                final_category = edit_category

            result = fm.edit_transaction(trans_id, edit_account, edit_amount, edit_type_db, edit_desc, edit_payment, final_category)
            st.success("✅ تم تعديل المعاملة بنجاح!")
            if result and "تنبيه" in result:
                st.warning(result)
            st.rerun()
        except Exception as e:
            st.error(f"❌ خطأ أثناء التعديل: {str(e)}")

    if delete_button:
        try:
            with fm.conn:
                old_trans = fm.conn.execute('SELECT type, amount, account_id FROM transactions WHERE id = ?', (trans_id,)).fetchone()
                if old_trans:
                    old_type, old_amount, old_account_id = old_trans
                    fm.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', 
                                    (old_amount if old_type == "IN" else -old_amount, old_account_id))
                    fm.conn.execute("DELETE FROM transactions WHERE id = ?", (trans_id,))
                    fm.conn.commit()
            st.success("🗑️ تم حذف المعاملة بنجاح!")
            st.rerun()
        except Exception as e:
            st.error(f"❌ خطأ أثناء الحذف: {str(e)}")
else:
    st.info("ℹ️ لا توجد معاملات بعد، أضف واحدة أعلاه!")
