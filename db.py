import sqlite3

from attack import Attack
from character import Character

PATH = 'dnd_bot.db'

class DataBase:

    def __init__(self):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()

        c.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, dice_roller TEXT DEFAULT 'normal')''')

        c.execute('''CREATE TABLE IF NOT EXISTS characters (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, class TEXT, username TEXT, FOREIGN KEY(username) REFERENCES users(username))''')

        c.execute('''CREATE TABLE IF NOT EXISTS modificators (character_id INTEGER, parameter TEXT, value INTEGER, FOREIGN KEY(character_id) REFERENCES characters(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS attacks (character_id INTEGER, name TEXT, dice INTEGER, count INTEGER, modificator TEXT, FOREIGN KEY(character_id) REFERENCES characters(id))''')

        conn.commit()
        conn.close()

    def add_user(self, username):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("INSERT OR IGNORE INTO users (username, dice_roller) VALUES (?, ?)", (username, 'normal'))
        conn.commit()
        conn.close()

    def set_dice_roller(self, username, dice_roller):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("UPDATE users SET dice_roller = ? WHERE username = ?", (dice_roller, username))
        conn.commit()
        conn.close()

    def get_dice_roller(self, username):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("SELECT dice_roller FROM users WHERE username = ?", (username,))
        dice_roller = c.fetchone()
        conn.close()
        return dice_roller[0] if dice_roller else 'normal'

    def add_character(self, name, class_, username):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("INSERT INTO characters (name, class, username) VALUES (?, ?, ?)", (name, class_, username))
        conn.commit()
        conn.close()

    def get_character(self, name):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("SELECT id, name, class FROM characters WHERE name = ?", (name,))
        character = c.fetchone()
        if not character:
            conn.close()
            return None

        character_id = character[0]
        c.execute("SELECT parameter, value FROM modificators WHERE character_id = ?", (character_id,))
        modificators = dict(c.fetchall())

        c.execute("SELECT name, dice, count, modificator FROM attacks WHERE character_id = ?", (character_id,))
        attacks = {name:Attack(name, dice, count, modificator) for name, dice, count, modificator in c.fetchall()}

        conn.close()

        return Character(character[1], character[2], modificators, attacks)

    def set_modificator(self, name, parameter, value):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM characters WHERE name = ?", (name,))
        character_id = c.fetchone()[0]
        c.execute("INSERT INTO modificators (character_id, parameter, value) VALUES (?, ?, ?)", (character_id, parameter, value))
        conn.commit()
        conn.close()

    def add_attack(self, name, attack_name, dice, count, modificator):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM characters WHERE name = ?", (name,))
        character_id = c.fetchone()[0]
        c.execute("INSERT INTO attacks (character_id, name, dice, count, modificator) VALUES (?, ?, ?, ?, ?)", (character_id, attack_name, dice, count, modificator))
        conn.commit()
        conn.close()

    def list_characters(self, username):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("SELECT name, class FROM characters WHERE username = ?", (username,))
        characters = c.fetchall()
        conn.close()
        return characters

    def list_attacks(self, name, username):
        conn = sqlite3.connect(PATH)
        c = conn.cursor()
        c.execute("SELECT id FROM characters WHERE name = ? AND username = ?", (name, username))
        character = c.fetchone()

        if character:
            character_id = character[0]
            c.execute("SELECT name, dice, count, modificator FROM attacks WHERE character_id = ?", (character_id,))
            attacks = c.fetchall()
            conn.close()
            return attacks
        else:
            conn.close()
            return []