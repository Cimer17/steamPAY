import sqlite3

class DataBase():

    def __init__(self):
        self.conn = sqlite3.connect('baza.db', check_same_thread=False)
        self.cursor = self.conn.cursor()

    def register_new_user(self, id):
        self.cursor.execute('INSERT INTO users VALUES (?, 0, 0, 0);', [id])
        self.conn.commit()
    
    def chek(self, id, param):
        self.cursor.execute(f'SELECT "{param}" FROM users WHERE id = {id}')
        return self.cursor.fetchone()
    
    def update_rulle(self, id):
        self.cursor.execute(f'UPDATE users SET rulle="1" WHERE id={id}')
        self.conn.commit()

    def update_login(self, id, login):
        self.cursor.execute(f'UPDATE users SET login_steam="{login}" WHERE id={id}')
        self.conn.commit()
    
    def get_sum(self, id):
        self.cursor.execute(f'SELECT SUM_PAYMENTS FROM users WHERE id = {id}')
        return self.cursor.fetchone()

    def sum_update(self, id, sum):
        result = str(float(self.get_sum(id)[0]) + float(sum))
        self.cursor.execute(f'UPDATE users SET SUM_PAYMENTS="{result}" WHERE id={id}')
        self.conn.commit()