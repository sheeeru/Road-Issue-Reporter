import sqlite3
import bcrypt
import logging

logging.basicConfig(level=logging.INFO)

def get_db_connection():
    try:
        conn = sqlite3.connect('road_issues.db')
        conn.row_factory = sqlite3.Row  # Allows for column access by name
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {e}")
        return None

def login(username, password):
    conn = get_db_connection()
    if conn is None:
        return None, "Database connection failed."

    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password, role FROM users WHERE username=?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user:
        logging.info(f"User  found: ID={user[0]}, Username={user[1]}, Role={user[3]}")
        if bcrypt.checkpw(password.encode('utf-8'), user[2].encode('utf-8')):
            return user[0], user[3]  # Return user_id and role
        else:
            logging.warning("Invalid password for user: %s", username)
            return None, "Invalid username or password."
    else:
        logging.warning("User  not found: %s", username)
        return None, "Invalid username or password."

def register(username, password, is_admin=False):
    conn = get_db_connection()
    if conn is None:
        return "Database connection failed."

    cursor = conn.cursor()
    role = 'admin' if is_admin else 'user'
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, hashed_password, role))
        conn.commit()
        return f"Registration successful! User {username} is now a {role}."
    except sqlite3.IntegrityError:
        return "Username already taken."
    finally:
        conn.close()

def report_issue(user_id, issue_type, latitude, longitude, description):
    conn = get_db_connection()
    if conn is None:
        logging.error("Database connection failed.")
        return

    cursor = conn.cursor()
    cursor.execute("INSERT INTO issues (user_id, issue_type, latitude, longitude, description, solved) VALUES (?, ?, ?, ?, ?, ?)",
                   (user_id, issue_type, latitude, longitude, description, False))
    conn.commit()
    conn.close()

def view_issues():
    conn = get_db_connection()
    if conn is None:
        logging.error("Database connection failed.")
        return []

    cursor = conn.cursor()
    cursor.execute("SELECT id, issue_type, latitude, longitude, description, solved FROM issues")
    issues = cursor.fetchall()
    conn.close()
    return issues

def get_leaderboard():
    conn = get_db_connection()
    if conn is None:
        logging.error("Database connection failed.")
        return []

    cursor = conn.cursor()
    cursor.execute('''
        SELECT u.username, COUNT(i.id) as points
        FROM users u
        LEFT JOIN issues i ON u.id = i.user_id
        WHERE i.solved = 0
        GROUP BY u.id
        ORDER BY points DESC
    ''')
    leaderboard = cursor.fetchall()
    conn.close()
    return leaderboard

def mark_as_solved(issue_id):
    conn = get_db_connection()
    if conn is None:
        logging.error("Database connection failed.")
        return

    cursor = conn.cursor()
    cursor.execute("UPDATE issues SET solved = 1 WHERE id = ?", (issue_id,))
    conn.commit()
    conn.close()