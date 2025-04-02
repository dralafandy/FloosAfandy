import sqlite3
from datetime import datetime

class FinanceManager:
    def __init__(self, db_file="finance.db"):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.create_tables()

    def create_tables(self):
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    balance REAL DEFAULT 0.0,
                    min_balance REAL DEFAULT 0.0,
                    created_at TEXT
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    account_id INTEGER,
                    description TEXT,
                    payment_method TEXT,
                    category TEXT,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS custom_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    account_id INTEGER,
                    transaction_type TEXT NOT NULL,
                    category_name TEXT NOT NULL,
                    FOREIGN KEY (account_id) REFERENCES accounts (id)
                )
            ''')

    def add_account(self, account_name, opening_balance=0.0, min_balance=0.0):
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO accounts (name, balance, min_balance, created_at)
                VALUES (?, ?, ?, ?)
            ''', (account_name, opening_balance, min_balance, created_at))
            return cursor.lastrowid

    def add_custom_category(self, account_id, transaction_type, category_name):
        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO custom_categories (account_id, transaction_type, category_name)
                VALUES (?, ?, ?)
            ''', (account_id, transaction_type, category_name))
            return cursor.lastrowid

    def get_custom_categories(self, account_id, transaction_type):
        return self.conn.execute('''
            SELECT category_name FROM custom_categories 
            WHERE account_id = ? AND transaction_type = ?
        ''', (account_id, transaction_type)).fetchall()

    def delete_custom_category(self, category_id):
        with self.conn:
            self.conn.execute('DELETE FROM custom_categories WHERE id = ?', (category_id,))

    def get_all_categories(self):
        return self.conn.execute('SELECT id, account_id, transaction_type, category_name FROM custom_categories').fetchall()

    def add_transaction(self, account_id, amount, trans_type, description="", payment_method="كاش", category=""):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        category_str = ", ".join(category) if isinstance(category, list) else category
        with self.conn:
            account = self.conn.execute('SELECT balance, min_balance FROM accounts WHERE id = ?', (account_id,)).fetchone()
            if not account:
                raise ValueError("الحساب غير موجود")
            if amount <= 0:
                raise ValueError("المبلغ يجب أن يكون موجبًا")
            if trans_type == "OUT" and account[0] < amount:
                raise ValueError("الرصيد غير كافٍ")

            self.conn.execute('''
                INSERT INTO transactions (date, type, amount, account_id, description, payment_method, category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (date, trans_type, amount, account_id, description, payment_method, category_str))

            new_balance = account[0] + amount if trans_type == "IN" else account[0] - amount
            self.conn.execute('UPDATE accounts SET balance = ? WHERE id = ?', (new_balance, account_id))

            if new_balance < account[1]:
                return "تنبيه: الرصيد أقل من الحد الأدنى"

    def edit_transaction(self, trans_id, account_id, amount, trans_type, description, payment_method, category):
        with self.conn:
            old_trans = self.conn.execute('SELECT type, amount, account_id FROM transactions WHERE id = ?', (trans_id,)).fetchone()
            if not old_trans:
                raise ValueError("المعاملة غير موجودة")
            old_type, old_amount, old_account_id = old_trans

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

            category_str = ", ".join(category) if isinstance(category, list) else category
            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.conn.execute('''
                UPDATE transactions 
                SET date = ?, type = ?, amount = ?, account_id = ?, description = ?, payment_method = ?, category = ? 
                WHERE id = ?
            ''', (date, trans_type, amount, account_id, description, payment_method, category_str, trans_id))

            if new_balance < min_balance:
                return "تنبيه: الرصيد أقل من الحد الأدنى"

    def filter_transactions(self, account_id=None, start_date=None, end_date=None, trans_type=None, category=None, payment_method=None):
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
            query += ' AND category LIKE ?'
            params.append(f"%{category}%")
        if payment_method:
            query += ' AND payment_method = ?'
            params.append(payment_method)
        return self.conn.execute(query, params).fetchall()

    def get_all_accounts(self):
        return self.conn.execute('SELECT * FROM accounts').fetchall()

    def get_all_transactions(self):
        return self.conn.execute('SELECT * FROM transactions').fetchall()

    def check_alerts(self):
        alerts = []
        accounts = self.get_all_accounts()
        for acc in accounts:
            if acc[2] < acc[3]:
                alerts.append(f"⚠️ الرصيد في حساب {acc[1]} أقل من الحد الأدنى!")
        return alerts
