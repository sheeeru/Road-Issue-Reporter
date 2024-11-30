import sqlite3
import bcrypt

def initialize_database():
    conn = sqlite3.connect('road_issues.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password TEXT NOT NULL,
                        role TEXT NOT NULL)''')

    # Create issues table
    cursor.execute('''CREATE TABLE IF NOT EXISTS issues (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        issue_type TEXT NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        description TEXT NOT NULL,
                        solved BOOLEAN NOT NULL DEFAULT 0,
                        FOREIGN KEY (user_id) REFERENCES users (id))''')

    # Insert default admin account
    admin_username = "admin"
    admin_password = "admin123"
    hashed_password = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", 
                       (admin_username, hashed_password, 'admin'))
        print(f"Admin account created with username '{admin_username}' and password '{admin_password}'.")
    except sqlite3.IntegrityError:
        print("Admin account already exists.")

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()