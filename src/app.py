from flask import Flask, render_template, request, jsonify
import requests

from database import init_db, get_connection

app = Flask(__name__)

# -----------------------------------------------------------------------------
# Работа с БД
# -----------------------------------------------------------------------------

def load_buttons():
    conn = get_connection()

    rows = conn.execute("""
        SELECT *
        FROM buttons
        ORDER BY id
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_button(btn_id):
    conn = get_connection()

    row = conn.execute(
        "SELECT * FROM buttons WHERE id=?",
        (btn_id,)
    ).fetchone()

    conn.close()

    return dict(row) if row else None


# -----------------------------------------------------------------------------
# Главная страница
# -----------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")


# -----------------------------------------------------------------------------
# Получить все кнопки
# -----------------------------------------------------------------------------

@app.route("/api/buttons")
def api_buttons():
    return jsonify(load_buttons())


# -----------------------------------------------------------------------------
# Импульс
# -----------------------------------------------------------------------------

@app.route("/api/button/<int:btn_id>", methods=["POST"])
def trigger(btn_id):

    btn = get_button(btn_id)

    if not btn:
        return jsonify(success=False, error="Кнопка не найдена")

    try:

        url = (
            f"http://{btn['ip']}/relay_cgi.cgi"
            f"?type=2"
            f"&relay={btn['relay']}"
            f"&on=1"
            f"&time={btn['pulse_sec']}"
            f"&pwd={btn['password']}"
        )

        requests.get(url, timeout=5)

        return jsonify(success=True)

    except Exception as e:

        return jsonify(success=False, error=str(e))


# -----------------------------------------------------------------------------
# Включить / выключить
# -----------------------------------------------------------------------------

@app.route("/api/set_relay/<int:btn_id>/<int:state>", methods=["POST"])
def set_relay(btn_id, state):

    btn = get_button(btn_id)

    if not btn:
        return jsonify(success=False, error="Кнопка не найдена")

    try:

        url = (
            f"http://{btn['ip']}/relay_cgi.cgi"
            f"?type=0"
            f"&relay={btn['relay']}"
            f"&on={state}"
            f"&time=0"
            f"&pwd={btn['password']}"
        )

        requests.get(url, timeout=5)

        return jsonify(success=True)

    except Exception as e:

        return jsonify(success=False, error=str(e))


# -----------------------------------------------------------------------------
# Добавить кнопку
# -----------------------------------------------------------------------------

@app.route("/api/add_button", methods=["POST"])
def add_button():

    data = request.json

    conn = get_connection()

    conn.execute("""
        INSERT INTO buttons
        (
            name,
            ip,
            relay,
            password,
            pulse_sec
        )
        VALUES
        (?,?,?,?,?)
    """,
    (
        data["name"],
        data["ip"],
        data["relay"],
        data["password"],
        data["pulse_sec"]
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# -----------------------------------------------------------------------------
# Редактировать кнопку
# -----------------------------------------------------------------------------

@app.route("/api/edit_button", methods=["POST"])
def edit_button():

    data = request.json

    conn = get_connection()

    conn.execute("""
        UPDATE buttons
        SET
            name=?,
            ip=?,
            relay=?,
            password=?,
            pulse_sec=?
        WHERE id=?
    """,
    (
        data["name"],
        data["ip"],
        data["relay"],
        data["password"],
        data["pulse_sec"],
        data["id"]
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)


# -----------------------------------------------------------------------------
# Удалить кнопку
# -----------------------------------------------------------------------------

@app.route("/api/delete_button/<int:btn_id>", methods=["DELETE"])
def delete_button(btn_id):

    conn = get_connection()

    conn.execute(
        "DELETE FROM buttons WHERE id=?",
        (btn_id,)
    )

    conn.commit()
    conn.close()

    return jsonify(success=True)


# -----------------------------------------------------------------------------
# Статус реле
# -----------------------------------------------------------------------------

@app.route("/api/status/<int:btn_id>")
def relay_status(btn_id):

    btn = get_button(btn_id)

    if not btn:
        return jsonify(
            online=False,
            relay=False
        )

    try:

        r = requests.get(
            f"http://{btn['ip']}/relay_cgi_load.cgi",
            timeout=2
        )

        data = r.text.strip("&").split("&")

        relay_count = int(data[1])

        if btn["relay"] >= relay_count:

            return jsonify(
                online=True,
                relay=False
            )

        relay_state = data[2 + btn["relay"]] == "1"

        return jsonify(
            online=True,
            relay=relay_state
        )

    except Exception:

        return jsonify(
            online=False,
            relay=False
        )


@app.route("/api/settings")
def get_settings():

    conn = get_connection()

    row = conn.execute("""
        SELECT *
        FROM settings
        WHERE id=1
    """).fetchone()

    conn.close()

    return jsonify(dict(row))

@app.route("/api/settings", methods=["POST"])
def save_settings():

    data = request.json

    conn = get_connection()

    conn.execute("""
        UPDATE settings
        SET
            theme=?,
            refresh_interval=?,
            timeout=?,
            notifications=?
        WHERE id=1
    """,
    (
        data["theme"],
        data["refresh_interval"],
        data["timeout"],
        data["notifications"]
    ))

    conn.commit()
    conn.close()

    return jsonify(success=True)

# -----------------------------------------------------------------------------
# Запуск
# -----------------------------------------------------------------------------

if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5001,
        debug=True
    )