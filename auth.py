from db import get_connection
import hashlib
import uuid

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register(username, name, password):
    conn = get_connection()
    c = conn.cursor()

    try:
        c.execute(
            "INSERT INTO users (username, name, password) VALUES (%s, %s, %s)",
            (username, name,  hash_password(password))
        )
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login(username, password):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT id, name FROM users WHERE username=%s AND password=%s",
        (username, hash_password(password))
    )
    
    user = c.fetchone()
    
    if not user:
        return None

    user_id = user[0]
    # token generálás
    token = str(uuid.uuid4())

    c.execute(
        "INSERT INTO tokens (token, user_id) VALUES (%s, %s)",
        (token, user_id)
    )
    c.execute(
        "INSERT INTO logins (user_id, last_login) VALUES (%s, now())",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return {"user_id": user_id, "token": token}
    
# ------------------------
# TOKEN VALIDÁLÁS
# ------------------------
def get_user_by_token(token):
    conn = get_connection()
    c = conn.cursor()

    c.execute("""
        SELECT users.id, users.username
        FROM tokens
        JOIN users ON users.id = tokens.user_id
        WHERE tokens.token= %s
    """, (token,))

    user = c.fetchone()
    conn.close()

    if user:
        return {"id": user[0], "username": user[1]}

    return None


# ------------------------
# LOGOUT
# ------------------------
def logout(token):
    conn = get_connection()
    c = conn.cursor()

    c.execute("DELETE FROM tokens WHERE token=%s", (token,))

    conn.commit()
    conn.close()
    
def last_login(id):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT max(last_login) FROM logins WHERE user_id=%s ",
        (id,)
    )

    result = c.fetchone()
    conn.close()

    return result[0] if result else None
    
def username(id):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT name FROM users WHERE id=%s",
        (id,)
    )

    result = c.fetchone()
    conn.close()

    return result[0] if result else None