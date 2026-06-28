from db import get_connection

def load_plans(user_id):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT plan_label ,plan FROM plans WHERE user_id=%s",
        (user_id,)
    )

    rows = c.fetchall()
    conn.close()

    return [{"plan_label": r[0], "plan": r[1]} for r in rows]


def save_plan(user_id, plan_label, plan,  hotel, travel_mode):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "INSERT INTO plans (user_id, plan_label, plan, create_date, hotel, travel_mode ) VALUES (%s, %s, %s, now(), %s, %s)",
        (user_id, plan_label ,plan, hotel, travel_mode)
    )

    conn.commit()
    conn.close()

def load_plan(user_id, plan_label):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "SELECT plan, hotel, travel_mode FROM plans WHERE user_id=%s and plan_label=%s ",
        (user_id, plan_label)
    )

    rows = c.fetchall()
    conn.close()

    return [{"plan": r[0], "hotel": r[1], "travel_mode": r[2]} for r in rows]

def remove_plan(user_id, plan_label):
    conn = get_connection()
    c = conn.cursor()

    c.execute(
        "delete FROM plans WHERE user_id = %s and plan_label = %s",
        (user_id, plan_label)
    )

    #rows = c.fetchnone()
    conn.commit()
    conn.close()

    #return rows