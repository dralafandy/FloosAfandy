import sqlite3
from datetime import datetime

class FinanceManager:
    def __init__(self, db_file="finance.db"):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            # جدول الحسابات
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    balance REAL DEFAULT 0.0,
                    min_balance REAL DEFAULT 0.0,
                    created_at TEXT
                )
            ''')
            # جدول المعاملات
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    account_id INTEGER,
                    description TEXT,
                    payment_method TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')
            # جدول الميزانيات (معدل مع account_id)
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS budgets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    budget_amount REAL NOT NULL,
                    spent_amount REAL DEFAULT 0.0,
                    account_id INTEGER,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')
            # جدول الفئات (اختياري للتصنيف التلقائي)
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_name TEXT NOT NULL,
                    keywords TEXT NOT NULL
                )
            ''')
            # إضافة فئات افتراضية
            self.conn.execute('INSERT OR IGNORE INTO categories (category_name, keywords) VALUES (?, ?)', 
                              ("طعام", "مطعم, سوبرماركت, بقالة"))
            self.conn.execute('INSERT OR IGNORE INTO categories (category_name, keywords) VALUES (?, ?)', 
                              ("ترفيه", "سينما, تذكرة, لعبة"))
            self.conn.execute('INSERT OR IGNORE INTO categories (category_name, keywords) VALUES (?, ?)', 
                              ("فواتير", "كهرباء, ماء, إنترنت"))

    def add_account(self, account_name, opening_balance=0.0, min_balance=0.0):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO accounts (name, balance, min_balance, created_at)
                VALUES (?, ?, ?, ?)
            ''', (account_name, opening_balance, min_balance, created_at))
            return cursor.lastrowid

    def categorize_transaction(self, description):
        categories = self.conn.execute('SELECT category_name, keywords FROM categories').fetchall()
        for category_name, keywords in categories:
            keyword_list = keywords.split(",")
            if any(keyword.strip() in description.lower() for keyword in keyword_list):
                return category_name
        return description or "غير مصنف"

    def add_transaction(self, account_id, amount, trans_type, description="", payment_method="كاش"):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        category = self.categorize_transaction(description)
        with self.conn:
            account = self.conn.execute('SELECT balance, min_balance FROM accounts WHERE id = ?', (account_id,)).fetchone()
            if not account:
                raise ValueError("الحساب غير موجود")
            if amount <= 0:
                raise ValueError("المبلغ يجب أن يكون موجبًا")
            if trans_type == "OUT" and account[0] < amount:
                raise ValueError("الرصيد غير كافٍ")

            self.conn.execute('''
                INSERT INTO transactions (date, type, amount, account_id, description, payment_method)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (date, trans_type, amount, account_id, description, payment_method))

            new_balance = account[0] + amount if trans_type == "IN" else account[0] - amount
            self.conn.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_balance, account_id))

            if trans_type == "OUT":
                self.update_budget_spent(category, amount, account_id)

            if new_balance < account[1]:
                return "تنبيه: الرصيد أقل من الحد الأدنى"

    def edit_transaction(self, trans_id, account_id, amount, trans_type, description, payment_method):
        with self.conn:
            old_trans = self.conn.execute('SELECT type, amount, account_id, description FROM transactions WHERE id = ?', (trans_id,)).fetchone()
            if not old_trans:
                raise ValueError("المعاملة غير موجودة")
            old_type, old_amount, old_account_id, old_description = old_trans

            account = self.conn.execute('SELECT balance, min_balance FROM accounts WHERE id = ?', (account_id,)).fetchone()
            if not account:
                raise ValueError("الحساب غير موجود")
            current_balance, min_balance = account

            if old_account_id == account_id:
                temp_balance = current_balance - old_amount if old_type == "IN" else current_balance + old_amount
            else:
                self.conn.execute('UPDATE accounts SET balance = balance + ? WHERE id = ?', 
                                  (old_amount if old_type == "IN" else -old_amount, old_account_id))
                temp_balance = current_balance

            if amount <= 0:
                raise ValueError("المبلغ يجب أن يكون موجبًا")
            if trans_type == "OUT" and temp_balance < amount:
                raise ValueError("الرصيد غير كافٍ")

            new_balance = temp_balance + amount if trans_type == "IN" else temp_balance - amount
            self.conn.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_balance, account_id))

            if old_type == "OUT" and old_description:
                old_category = self.categorize_transaction(old_description)
                self.update_budget_spent(old_category, -old_amount, old_account_id)
            if trans_type == "OUT":
                new_category = self.categorize_transaction(description)
                self.update_budget_spent(new_category, amount, account_id)

            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.conn.execute('''
                UPDATE transactions 
                SET date = ?, type = ?, amount = ?, account_id = ?, description = ?, payment_method = ? 
                WHERE id = ?
            ''', (date, trans_type, amount, account_id, description, payment_method, trans_id))

            if new_balance < min_balance:
                return "تنبيه: الرصيد أقل من الحد الأدنى"

    def filter_transactions(self, account_id=None, start_date=None, end_date=None, trans_type=None):
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
        return self.conn.execute(query, params).fetchall()

    def get_all_accounts(self):
        return self.conn.execute('SELECT * FROM accounts').fetchall()

    def get_all_transactions(self):
        return self.conn.execute('SELECT * FROM transactions').fetchall()

    def add_budget(self, category, budget_amount, account_id):
        """إضافة ميزانية جديدة مرتبطة بحساب"""
        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO budgets (category, budget_amount, account_id)
                VALUES (?, ?, ?)
            ''', (category, budget_amount, account_id))
            return cursor.lastrowid

    def update_budget_spent(self, category, amount, account_id):
        """تحديث المبلغ المنفق في الميزانية للحساب المحدد"""
        with self.conn:
            budget = self.conn.execute('SELECT spent_amount FROM budgets WHERE category = ? AND account_id = ?', 
                                       (category, account_id)).fetchone()
            if budget:
                self.conn.execute('''
                    UPDATE budgets SET spent_amount = spent_amount + ? WHERE category = ? AND account_id = ?
                ''', (amount, category, account_id))
            else:
                self.conn.execute('''
                    INSERT INTO budgets (category, budget_amount, spent_amount, account_id)
                    VALUES (?, 0, ?, ?)
                ''', (category, amount, account_id))

    def get_budgets(self, account_id=None):
        """استرجاع الميزانيات مع فلتر اختياري للحساب"""
        if account_id:
            return self.conn.execute('SELECT * FROM budgets WHERE account_id = ?', (account_id,)).fetchall()
        return self.conn.execute('SELECT * FROM budgets').fetchall()

    def check_alerts(self):
        """التحقق من التنبيهات"""
        alerts = []
        accounts = self.get_all_accounts()
        for acc in accounts:
            if acc[2] < acc[3]:
                alerts.append(f"⚠️ الرصيد في حساب {acc[1]} أقل من الحد الأدنى!")
        budgets = self.get_budgets()
        for budget in budgets:
            if budget[3] > budget[2]:
                alerts.append(f"⚠️ تجاوزت الميزانية لفئة {budget[1]} في حساب {budget[4]}!")
        return alerts