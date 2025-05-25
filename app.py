from flask import Flask, render_template, request, redirect, url_for, session, flash
from RCMIS import RCMIS # keep this if you're running from inside the RCMIS folder
import sqlite3
from RCMIS import RCMIS
system = RCMIS()

app = Flask(__name__)
app.secret_key = "your_secret_key"
system = RCMIS()

def init_db():
    conn = sqlite3.connect('rcmis.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS players (
            player_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            dob TEXT NOT NULL,
            age INTEGER NOT NULL,
            position TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# ... your route definitions go here ...

# Call this once to ensure the table exists
init_db()
def get_db_connection():
    conn = sqlite3.connect('rcmis.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in system.users and system.users[username] == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        flash("Invalid username or password!")
    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    conn = get_db_connection()
    players = conn.execute("SELECT * FROM players").fetchall()
    conn.close()
    return render_template("dashboard.html", players=players)

@app.route("/add_player", methods=["GET", "POST"])
def add_player():
    if request.method == "POST":
        player_id = request.form["player_id"]
        name = request.form["name"]
        dob = request.form["dob"]
        age = request.form["age"]
        position = request.form["position"]

        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO players (player_id, name, dob, age, position) VALUES (?, ?, ?, ?, ?)",
                (player_id, name, dob, age, position)
            )
            conn.commit()
            conn.close()
            return redirect(url_for("dashboard"))
        except sqlite3.IntegrityError:
            flash("Player ID already exists. Please use a unique Player ID.", "error")
            conn.close()
            return render_template("add_player.html")
    return render_template("add_player.html")
@app.route("/log_injury", methods=["GET", "POST"])
def log_injury():
    if request.method == "POST":
        player_id = request.form["player_id"]
        injury_type = request.form["injury_type"]
        body_part = request.form["body_part"]
        severity = request.form["severity"]
        conn = get_db_connection()
        conn.execute(
            "INSERT INTO injuries (player_id, injury_type, body_part, severity) VALUES (?, ?, ?, ?)",
            (player_id, injury_type, body_part, severity)
        )
        conn.commit()
        conn.close()
        flash("Injury logged successfully.", "success")
        return redirect(url_for("dashboard"))
    return render_template("log_injury.html")
@app.route("/update_rehab", methods=["GET", "POST"])
def update_rehab():
    conn = get_db_connection()
    players = conn.execute("SELECT player_id, name FROM players").fetchall()
    injuries = conn.execute("SELECT id, player_id, injury_type FROM injuries").fetchall()
    if request.method == "POST":
        player_id = request.form["player_id"]
        injury_id = request.form["injury_id"]
        notes = request.form["notes"]
        status = request.form["status"]
        conn.execute(
            "INSERT INTO rehab (player_id, injury_id, notes, status) VALUES (?, ?, ?, ?)",
            (player_id, injury_id, notes, status)
        )
        conn.commit()
        conn.close()
        flash("Rehabilitation updated successfully.", "success")
        return redirect(url_for("dashboard"))
    conn.close()
    return render_template("update_rehab.html", players=players, injuries=injuries)
@app.route("/medical_report", methods=["GET", "POST"])
def medical_report():
    conn = get_db_connection()
    players = conn.execute("SELECT player_id, name FROM players").fetchall()
    report = None
    if request.method == "POST":
        player_id = request.form["player_id"]
        report = system.generate_medical_report(player_id)
    conn.close()
    # Use the correct instance 'system' instead of 'rcmis'
    return render_template("medical_report.html", report=report, players=players)
@app.route("/set_availability", methods=["GET", "POST"])
def set_availability():
    conn = get_db_connection()
    players = conn.execute("SELECT player_id, name FROM players").fetchall()
    days = ["Tuesday", "Wednesday", "Thursday"]
    if request.method == "POST":
        player_id = request.form["player_id"]
        for day in days:
            available = 1 if request.form.get(f"available_{day}", "no") == "yes" else 0
            reason = request.form.get(f"reason_{day}", "")
            # Upsert logic: delete old, insert new
            conn.execute(
                "DELETE FROM availability WHERE player_id = ? AND day = ?",
                (player_id, day)
            )
            conn.execute(
                "INSERT INTO availability (player_id, day, available, reason) VALUES (?, ?, ?, ?)",
                (player_id, day, available, reason)
            )
        conn.commit()
        conn.close()
        flash("Availability updated successfully.", "success")
        return redirect(url_for("dashboard"))
    conn.close()
    return render_template("set_availability.html", players=players, days=days)
@app.route("/view_availability", methods=["GET", "POST"])
def view_availability():
    players = []
    day = None
    conn = get_db_connection()
    days = ["Tuesday", "Wednesday", "Thursday"]
    if request.method == "POST":
        day = request.form["day"]
        players = conn.execute("""
            SELECT p.player_id, p.name, a.available, a.reason
            FROM players p LEFT JOIN availability a ON p.player_id = a.player_id AND a.day = ?
        """, (day,)).fetchall()
    conn.close()
    return render_template("view_availability.html", players=players, day=day, days=days)

@app.route("/set_strapping", methods=["GET", "POST"])
def set_strapping():
    conn = get_db_connection()
    players = conn.execute("SELECT player_id, name FROM players").fetchall()
    if request.method == "POST":
        player_id = request.form["player_id"]
        needs = 1 if request.form.get("needs_strapping", "no") == "yes" else 0
        # Upsert logic: delete old, insert new
        conn.execute("DELETE FROM strapping WHERE player_id = ?", (player_id,))
        conn.execute(
            "INSERT INTO strapping (player_id, needs_strapping) VALUES (?, ?)",
            (player_id, needs)
        )
        conn.commit()
        conn.close()
        flash("Strapping status updated.", "success")
        return redirect(url_for("dashboard"))
    conn.close()
    return render_template("set_strapping.html", players=players)

@app.route("/view_strapping")
def view_strapping():
    conn = get_db_connection()
    players = conn.execute("""
        SELECT p.player_id, p.name, p.position
        FROM strapping s
        JOIN players p ON s.player_id = p.player_id
        WHERE s.needs_strapping = 1
    """).fetchall()
    conn.close()
    return render_template("view_strapping.html", players=players)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("login"))

@app.route("/edit_player/<player_id>", methods=["GET", "POST"])
def edit_player(player_id):
    conn = get_db_connection()
    player = conn.execute("SELECT * FROM players WHERE player_id = ?", (player_id,)).fetchone()
    if request.method == "POST":
        name = request.form["name"]
        dob = request.form["dob"]
        age = request.form["age"]
        position = request.form["position"]
        conn.execute(
            "UPDATE players SET name = ?, dob = ?, age = ?, position = ? WHERE player_id = ?",
            (name, dob, age, position, player_id)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("dashboard"))
    conn.close()
    return render_template("edit_player.html", player=player)

@app.route("/delete_player/<player_id>", methods=["POST"])
def delete_player(player_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM players WHERE player_id = ?", (player_id,))
    conn.commit()
    conn.close()
    flash("Player deleted successfully.", "success")
    return redirect(url_for("dashboard")) 

@app.route("/view_injuries")
def view_injuries():
    conn = get_db_connection()
    injuries = conn.execute("""
        SELECT i.id, i.player_id, p.name, i.injury_type, i.body_part, i.severity, i.date_logged
        FROM injuries i
        JOIN players p ON i.player_id = p.player_id
        ORDER BY i.date_logged DESC
    """).fetchall()
    conn.close()
    return render_template("view_injuries.html", injuries=injuries)

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/edit_injury/<int:injury_id>", methods=["GET", "POST"])
def edit_injury(injury_id):
    conn = get_db_connection()
    injury = conn.execute("SELECT * FROM injuries WHERE id = ?", (injury_id,)).fetchone()
    if request.method == "POST":
        injury_type = request.form["injury_type"]
        body_part = request.form["body_part"]
        severity = request.form["severity"]
        conn.execute(
            "UPDATE injuries SET injury_type = ?, body_part = ?, severity = ? WHERE id = ?",
            (injury_type, body_part, severity, injury_id)
        )
        conn.commit()
        conn.close()
        flash("Injury updated successfully.", "success")
        return redirect(url_for("view_injuries"))
    conn.close()
    return render_template("edit_injury.html", injury=injury)

@app.route("/delete_injury/<int:injury_id>", methods=["POST"])
def delete_injury(injury_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM injuries WHERE id = ?", (injury_id,))
    conn.commit()
    conn.close()
    flash("Injury deleted successfully.", "success")
    return redirect(url_for("view_injuries"))

@app.route("/view_rehab")
def view_rehab():
    conn = get_db_connection()
    rehab_records = conn.execute("""
        SELECT r.id, r.player_id, p.name, r.injury_id, i.injury_type, r.notes, r.status, r.date_updated
        FROM rehab r
        JOIN players p ON r.player_id = p.player_id
        JOIN injuries i ON r.injury_id = i.id
        ORDER BY r.date_updated DESC
    """).fetchall()
    conn.close()
    return render_template("view_rehab.html", rehab_records=rehab_records)

@app.route("/select_first_team", methods=["GET", "POST"])
def select_first_team():
    conn = get_db_connection()
    players = conn.execute("SELECT player_id, name, position FROM players").fetchall()
    if request.method == "POST":
        selected_ids = request.form.getlist("player_ids")
        # Remove old selections for 'first'
        conn.execute("DELETE FROM team_selection WHERE team = ?", ("first",))
        # Insert new selections
        for pid in selected_ids:
            conn.execute(
                "INSERT INTO team_selection (player_id, team) VALUES (?, ?)",
                (pid, "first")
            )
        conn.commit()
        conn.close()
        flash("First team selected successfully.", "success")
        return redirect(url_for("dashboard"))
    conn.close()
    return render_template("select_first_team.html", players=players)

@app.route("/view_first_team")
def view_first_team():
    conn = get_db_connection()
    players = conn.execute("""
        SELECT p.player_id, p.name, p.position
        FROM team_selection t
        JOIN players p ON t.player_id = p.player_id
        WHERE t.team = 'first'
    """).fetchall()
    conn.close()
    return render_template("view_first_team.html", players=players)

@app.route("/select_second_team", methods=["GET", "POST"])
def select_second_team():
    conn = get_db_connection()
    players = conn.execute("SELECT player_id, name, position FROM players").fetchall()
    if request.method == "POST":
        selected_ids = request.form.getlist("player_ids")
        # Remove old selections for 'second'
        conn.execute("DELETE FROM team_selection WHERE team = ?", ("second",))
        # Insert new selections
        for pid in selected_ids:
            conn.execute(
                "INSERT INTO team_selection (player_id, team) VALUES (?, ?)",
                (pid, "second")
            )
        conn.commit()
        conn.close()
        flash("Second team selected successfully.", "success")
        return redirect(url_for("dashboard"))
    conn.close()
    return render_template("select_second_team.html", players=players)

@app.route("/view_second_team")
def view_second_team():
    conn = get_db_connection()
    players = conn.execute("""
        SELECT p.player_id, p.name, p.position
        FROM team_selection t
        JOIN players p ON t.player_id = p.player_id
        WHERE t.team = 'second'
    """).fetchall()
    conn.close()
    return render_template("view_second_team.html", players=players)


if __name__ == "__main__":
    app.run(debug=True)