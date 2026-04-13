import sqlite3
import os


DB_FILE = "challenge_progress.db"

def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS challenges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            language VARCHAR(50),
            level VARCHAR(50),
            subject VARCHAR(100),
            description TEXT,
            user_solution TEXT,
            feedback TEXT,
            score INTEGER,
            completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
    """)
    
    conn.commit()
    conn.close()

def get_or_create_user(name):
    conn = get_connection()
    cursor = conn.cursor()

    # Check if user exists
    cursor.execute("SELECT * FROM users WHERE name = ?", (name,))
    user = cursor.fetchone()

    if user:
        conn.close()
        return user["user_id"]
    
    # Create new user
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def save_challenge(user_id, language, level, subject, description, solution, feedback, score):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO challenges 
        (user_id, language, level, subject, description, user_solution, feedback, score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, language, level, subject, description, solution, feedback, score))
    
    conn.commit()
    conn.close()
    return "Challenge saved!"

def get_user_progress(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT language, level, subject, score, completed_at 
        FROM challenges 
        WHERE user_id = ?
        ORDER BY completed_at DESC
    """, (user_id,))
    
    challenges = cursor.fetchall()
    conn.close()
    
    if not challenges:
        return "No challenges completed yet!"
    
    total = len(challenges)
    avg_score = sum(c["score"] for c in challenges) / total
    
    result = f"Completed {total} challenges. Average score: {avg_score:.1f}/10\n\n"
    result += "Recent challenges:\n"
    for c in challenges[:5]:
        result += f"- **{c['language']}** | {c['subject']} | Score: **{c['score']}/10**\n"
    
    return result

if __name__== "__main__":
    create_tables()
    print("Database created successfully!")

if __name__ == "__main__":
    create_tables()
    print("Database created!")
    
    # Test get_or_create_user
    user_id = get_or_create_user("Amir")
    print(f"User ID: {user_id}")
    
    # Test save_challenge
    save_challenge(
        user_id=user_id,
        language="Python",
        level="beginner",
        subject="lists",
        description="Filter odd numbers from a list",
        solution="def filter_odds(lst): return [x for x in lst if x % 2 != 0]",
        feedback="Clean solution, good use of list comprehension",
        score=8
    )
    print("Challenge saved!")
    
    # Test get_user_progress
    progress = get_user_progress(user_id)
    print(progress)