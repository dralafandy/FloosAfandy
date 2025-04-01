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
            # جدول المعاملات مع عمود الفئة
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    account_id INTEGER,
                    description TEXT,
                    payment_method TEXT,
                    category TEXT,  -- عمود جديد للفئة
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')
            # جدول الفئات المخصصة
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS custom_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    transaction_type TEXT NOT NULL,  -- "IN" أو "OUT"
                    category_name TEXT NOT NULL,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')

    def add_custom_category(self, account_id, transaction_type, category_name):
        """إضافة فئة مخصصة"""
        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO custom_categories (account_id, transaction_type, category_name)
                VALUES (?, ?, ?)
            ''', (account_id, transaction_type, category_name))
            return cursor.lastrowid

    def get_custom_categories(self, account_id, transaction_type):
        """استرجاع الفئات المخصصة"""
        return self.conn.execute('''
            SELECT category_name FROM custom_categories 
            WHERE account_id = ? AND transaction_type = ?
        ''', (account_id, transaction_type)).fetchall()

    def add_transaction(self, account_id, amount, trans_type, description="", payment_method="كاش", category=""):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            account = self.conn.execute('SELECT balance FROM accounts WHERE id = ?', (account_id,)).fetchone()
            if not account:
                raise ValueError("الحساب غير موجود")
            if amount <= 0:
                raise ValueError("المبلغ يجب أن يكون موجبًا")
            if trans_type == "OUT" and account[0] < amount:
                raise ValueError("الرصيد غير كافٍ")

            self.conn.execute('''
                INSERT INTO transactions (date, type, amount, account_id, description, payment_method, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date, trans_type, amount, account_id, description, payment_method, category))

            new_balance = account[0] + amount if trans_type == "IN" else account[0] - amount
            self.conn.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_balance, account_id))

    def filter_transactions(self, account_id=None, start_date=None, end_date=None, trans_type=None, category=None):
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

    def get_all_accounts(self):
        return self.conn.execute('SELECT * FROM accounts').fetchall()
