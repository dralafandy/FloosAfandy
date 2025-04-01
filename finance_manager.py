import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

class FinanceManager:
    def __init__(self, db_file="finance.db"):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # جدول الحسابات مع إضافة العملة
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    balance REAL DEFAULT 0.0,
                    min_balance REAL DEFAULT 0.0,
                    currency TEXT DEFAULT "EGP",  -- إضافة العملة
                    created_at TEXT
                )
            ''')
            # جدول المعاملات مع تخزين العملة
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    currency TEXT NOT NULL,  -- إضافة العملة لكل معاملة
                    account_id INTEGER,
                    description TEXT,
                    payment_method TEXT,
                    category TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')
            # جدول الفئات المخصصة
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS custom_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    transaction_type TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')

    def add_account(self, name, balance=0.0, min_balance=0.0, currency="EGP"):
        """إضافة حساب جديد مع تحديد العملة"""
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            self.conn.execute('''
                INSERT INTO accounts (name, balance, min_balance, currency, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, balance, min_balance, currency, created_at))

    def add_transaction(self, account_id, amount, trans_type, currency="EGP", description="", payment_method="كاش", category=""):
        """إضافة معاملة جديدة والتحقق من الرصيد"""
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            account = self.conn.execute('SELECT balance, min_balance, currency FROM accounts WHERE id = ?', (account_id,)).fetchone()
            if not account:
                raise ValueError("الحساب غير موجود")
            if amount <= 0:
                raise ValueError("المبلغ يجب أن يكون موجبًا")
            if trans_type == "OUT" and account[0] < amount:
                raise ValueError("الرصيد غير كافٍ")

            self.conn.execute('''
                INSERT INTO transactions (date, type, amount, currency, account_id, description, payment_method, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date, trans_type, amount, currency, account_id, description, payment_method, category))

            new_balance = account[0] + amount if trans_type == "IN" else account[0] - amount
            self.conn.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_balance, account_id))

            # التحقق من التنبيه عند انخفاض الرصيد
            if new_balance < account[1]:
                print(f"⚠️ تحذير: رصيد الحساب ({account_id}) أقل من الحد الأدنى ({account[1]} {account[2]})")

    def filter_transactions(self, account_id=None, start_date=None, end_date=None, trans_type=None, category=None):
        """تصفية المعاملات المالية"""
        query = 'SELECT * FROM transactions WHERE 1=1'
        params = []
        if account_id:
            query += ' AND account_id = ?'
            params.append(account_id)
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        if trans_type:
            query += ' AND type = ?'
            params.append(trans_type)
        if category:
            query += ' AND category = ?'
            params.append(category)
        return self.conn.execute(query, params).fetchall()

    def export_transactions_to_pdf(self, file_name="transactions_report.pdf", account_id=None, start_date=None, end_date=None):
        """تصدير المعاملات إلى تقرير PDF"""
        transactions = self.filter_transactions(account_id, start_date, end_date)
        if not transactions:
            print("⚠️ لا توجد معاملات للتصدير!")
            return

        c = canvas.Canvas(file_name, pagesize=letter)
        c.drawString(100, 750, "📜 تقرير المعاملات المالية")
        c.drawString(100, 730, f"التاريخ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(100, 710, "-" * 50)

        y = 690
        c.drawString(100, y, "ID  |  التاريخ  |  النوع  |  المبلغ  |  العملة  |  الوصف")
        y -= 20
        c.drawString(100, y, "-" * 100)

        for trans in transactions:
            y -= 20
            c.drawString(100, y, f"{trans[0]}  |  {trans[1]}  |  {trans[2]}  |  {trans[3]:.2f}  {trans[4]}  |  {trans[6]}")
            if y < 100:  # إذا امتلأت الصفحة، أضف صفحة جديدة
                c.showPage()
                y = 750

        c.save()
        print(f"✅ تم حفظ التقرير: {file_name}")

    def get_all_accounts(self):
        """جلب جميع الحسابات"""
        return self.conn.execute('SELECT * FROM accounts').fetchall()
