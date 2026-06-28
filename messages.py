from db import get_connection

def save_message(user_id, role, chat_type, content):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "INSERT INTO messages (user_id, role, chat_type,  content) VALUES (%s, %s, %s, %s)",
        (user_id, role, chat_type, content)
    )

    conn.commit()
    conn.close()

def load_messages(user_id, chat_type):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT role, content FROM messages WHERE user_id=%s and chat_type=%s ORDER BY id",
        (user_id, chat_type)
    )

    rows = c.fetchall()
    conn.close()

    return [{"role": r[0], "content": r[1]} for r in rows]

def remove_messages(user_id, chat_type):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "delete FROM messages WHERE user_id = %s and chat_type = %s",
        (user_id, chat_type)
    )

    #rows = c.fetchnone()
    conn.commit()
    conn.close()

    #return rows