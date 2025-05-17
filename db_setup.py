cursor.execute("""
    CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password TEXT NOT NULL
    );
""")

cursor.execute("""
    CREATE TABLE messages (
        id SERIAL PRIMARY KEY,
        sender_id INT REFERENCES users(id),
        receiver_id INT,
        group_chat BOOLEAN DEFAULT FALSE,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
""")

conn.commit()
