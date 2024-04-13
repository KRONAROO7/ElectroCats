import sqlite3
import secrets
import pytz
from datetime import datetime
from config import fish_cost


class Database:

    def __init__(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute("""CREATE IF NOT EXISTS users (
                session_id INTEGER PRIMARY KEY,
                coins INTEGER DEFAULT 0,
                wash INTEGER DEFAULT 0,
                timestamp INTEGER
        )""")
        conn.commit()

        cursor.execute("""CREATE IF NOT EXISTS fish (
                fish_id INTEGER PRIMARY KEY,
                fish TEXT,
                hunger INTEGER DEFAULT 0,
                user_id INTEGER,
                is_alive INTEGER DEFAULT 1,
                FOREIGN KEY (user_id) REFERENCES users(session_id)
        )""")
        conn.commit()

    @staticmethod
    def add_fish(session_id, fish):
        if fish not in fish_cost:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        fish_id = secrets.randbelow(10 ** 8)
        fish_id_str = str(fish_id).zfill(8)
        if not cursor.execute("SELECT * FROM fish WHERE fish_id=?",
                              (fish_id_str,)).fetchone():
            cursor.execute("INSERT INTO fish (fish_id, fish, user_id) VALUES (?, ?, ?)",
                           (fish_id_str, fish, session_id))
            conn.commit()
            conn.close()
            return fish_id_str

    def new_session(self):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        timestamp = int(datetime.now(pytz.timezone('Europe/Kiev')).timestamp())
        session_id = secrets.randbelow(10 ** 8)
        session_id_str = str(session_id).zfill(8)
        if not cursor.execute("SELECT * FROM sessions WHERE session_id=?",
                              (session_id_str,)).fetchone():
            cursor.execute("INSERT INTO sessions (session_id, timestamp) VALUES (?, ?)",
                           (session_id_str, timestamp))
            conn.commit()
            conn.close()

            self.add_fish(session_id_str, "fish-3")
            self.add_fish(session_id_str, "fish-3")

            return session_id_str
        conn.close()
        return False

    @staticmethod
    def clear_session():
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        timestamp = int(datetime.now(pytz.timezone('Europe/Kiev')).timestamp()) - 86400
        sessions = cursor.execute("SELECT session_id FROM users WHERE timestamp < ?",
                                  (timestamp,)).fetchall()
        for session in sessions:
            cursor.execute("DELETE FROM users WHERE session_id = ?", session)
        conn.commit()
        conn.close()

    @staticmethod
    def add_hungry(amount: int = 1):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        fishes = cursor.execute("SELECT fish_id, hunger FROM fish").fetchall()
        for fish, hunger in fishes:
            cursor.execute("SET fish UPDATE hunger = ? WHERE fish_id = ?", (hunger + amount, fish))
        conn.commit()
        conn.close()

    @staticmethod
    def add_wash(amount: int = 1):
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        aqua = cursor.execute("SELECT session_id, wash FROM users").fetchall()
        for user, wash in aqua:
            cursor.execute("SET users UPDATE wash = ? WHERE session_id = ?", (wash + amount, user))
        conn.commit()
        conn.close()

    @staticmethod
    def kill_fish():
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        hunger = cursor.execute("SELECT fish_id fish WHERE hunger > 100").fetchall()
        for fish in hunger:
            cursor.execute("DELETE FROM fish WHERE fish_id = ?", fish)
        conn.commit()
        conn.close()

    @staticmethod
    def get_hungry(session_id: int = None):
        if session_id is None:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        fishes = cursor.execute("SELECT fish_id, hungry FROM fish WHERE user_id = ?",
                                (session_id,)).fetchall()
        fish_list = []
        for fish_id, hungry in fishes:
            fish_dict = {
                "fish_id": fish_id,
                "hungry": hungry
            }
            fish_list.append(fish_dict)
        return fish_list

    @staticmethod
    def get_wash(session_id: int = None):
        if session_id is None:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        try:
            wash = cursor.execute("SELECT wash FROM users WHERE session_id = ?",
                                  (session_id,)).fetchone()
            return wash[0]
        except IndexError:
            return None

    @staticmethod
    def feed_fish(fish_id: int = None):
        if fish_id is None:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        fish = cursor.execute("SELECT hunger FROM fish WHERE fish_id = ?",
                              (fish_id,)).fetchone()
        for i in fish:
            amount = i - 20 if i > 20 else 0
            cursor.execute("UPDATE fish SET hunger = ? WHERE fish_id = ?",
                           (amount, fish_id))
        conn.commit()
        conn.close()

    @staticmethod
    def wash_aqua(session_id: int = None):
        if session_id is None:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET wash = 0 WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()

    @staticmethod
    def ready_to_love(session_id: int = None):
        if session_id is None:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        timestamp = int(datetime.now(pytz.timezone('Europe/Kiev')).timestamp()) - 600
        ready = cursor.execute("SELECT fish_id FROM fish WHERE timestamp < ?", (session_id, timestamp))
        conn.close()
        result = []
        for fish in ready:
            result.append(fish[0])
        return result

    @staticmethod
    def love(fish_id1: int = None, fish_id2: int = None):
        if fish_id1 is None or fish_id2 is None:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        fishes = [fish_id1, fish_id2]
        timestamp = int(datetime.now(pytz.timezone('Europe/Kiev')).timestamp()) - 600
        times = []
        for fish in fishes:
            try:
                time = cursor.execute("SELECT timestamp FROM fish WHERE fish_id = ?",
                                      (fish,)).fetchone()
                times.append(time[0])
            except IndexError:
                return None
        for time in times:
            if time + 600 > timestamp:
                return None

    def buy_fish(self, session_id: int = None, fish: str = None):
        if session_id is None or fish not in fish_cost:
            return None
        cost = fish_cost.get(fish, 99999)
        money = self.get_credits(session_id)
        if money < cost:
            return None
        return self.add_fish(session_id, fish)

    @staticmethod
    def get_credits(session_id: int = None):
        if session_id is None:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        money = cursor.execute("SELECT coins FROM users WHERE session_id = ?",
                               (session_id,)).fetchone()
        if money is not None:
            return money[0]
        return None

    @staticmethod
    def sell_fish(fish_id: int = None):
        if fish_id is None:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        fish = cursor.execute("SELECT fish FROM fish WHERE fish_id = ?",
                               (fish_id,)).fetchone()
        if fish is None:
            return None
        player_id = cursor.execute("SELECT user_id FROM fish WHERE fish_id = ?",
                                   (fish_id,)).fetchone()
        player_money = cursor.execute("SELECT coins FROM users WHERE session_id = ?",
                                      (player_id,)).fetchone()
        result = player_money + fish_cost.get(fish) / 2
        return result

    @staticmethod
    def is_alive(fish_id: int = None):
        if fish_id is None:
            return None
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()
        is_alive = cursor.execute("SELECT is_alive FROM fish WHERE fish_id", (fish_id,))
        if fish_id is None:
            return None
        return True if is_alive == 1 else False
