import sqlite3

import config


class Database:
    def __init__(self, file):
        self.connection = sqlite3.connect(file)
        self.cursor = self.connection.cursor()

    async def add_user(self, user_id, name):
        if await self.user_exists(user_id):
            raise ValueError
        with self.connection:
            return self.cursor.execute(
                """INSERT INTO users (user_id, name, role) VALUES(?, ?, ?)""",
                (user_id, name, 'admin' if user_id in config.ADMIN_IDS else 'user')
            )

    async def user_exists(self, user_id):
        with self.connection:
            return bool(self.cursor.execute(
                """SELECT 1 FROM users WHERE user_id = (?)""",
                (user_id,)
            ).fetchall())

    async def update_label(self, label, user_id):
        with self.connection:
            return self.cursor.execute(
                """UPDATE users SET label=(?) WHERE user_id=(?)""",
                (label, user_id)
            )

    async def get_payment_status(self, user_id):
        with self.connection:
            return self.cursor.execute(
                """SELECT bought, label FROM users WHERE user_id=(?)""",
                (user_id,)
            ).fetchall()

    async def update_payment_status(self, user_id):
        with self.connection:
            return self.cursor.execute(
                """UPDATE users SET bought=(?) WHERE user_id=(?)""",
                (True, user_id)
            )
