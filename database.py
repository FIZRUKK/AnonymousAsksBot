import sqlite3

class User:
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                question_count INTEGER DEFAULT 0
            )
        """)
        self.connection.commit()

    def user_exists(self, user_id):
        with self.connection:
            result = self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,)).fetchone()
            return bool(result)

    def add_user(self, user_id, username, first_name, last_name):
        with self.connection:
            if not self.user_exists(user_id):
                self.cursor.execute("INSERT INTO users (user_id, username, first_name, last_name) VALUES (?, ?, ?, ?)", (user_id, username, first_name, last_name))
            else:
                self.cursor.execute("UPDATE users SET username = ?, first_name = ?, last_name = ? WHERE user_id = ?", (username, first_name, last_name, user_id))
            self.connection.commit()

    def get_user_by_id(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            return self.cursor.fetchone()

    def increment_question_count(self, user_id):
        self.cursor.execute("""
            UPDATE users
            SET question_count = question_count + 1
            WHERE user_id = ?
        """, (user_id,))
        self.connection.commit()

    def get_question_count(self, user_id):
        with self.connection:
            self.cursor.execute("SELECT question_count FROM users WHERE user_id = ?", (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0
    
    def get_user_count(self):
        self.cursor.execute("SELECT COUNT(*) FROM users")
        return self.cursor.fetchone()[0]

    def get_last_users(self, n):
        self.cursor.execute("SELECT user_id, username FROM users ORDER BY user_id DESC LIMIT ?", (n,))
        rows = self.cursor.fetchall()
        return [User(user_id, username) for user_id, username in rows]

    def get_top_users(self, limit=10):
        self.cursor.execute("""
            SELECT user_id, username, question_count
            FROM users
            ORDER BY question_count DESC
            LIMIT ?
        """, (limit,))
        return self.cursor.fetchall()
    
    def close(self):
        self.connection.close()

