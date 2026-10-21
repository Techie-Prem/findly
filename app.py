# Findly - Campus Lost & Found
# Run: python app.py  ->  http://127.0.0.1:5000
import os
import sqlite3
import uuid
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "lab-project"
DB: str = "lostfound.db"

UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}


# State machine: each state lists the states it can move to.
NEXT_STATES = {
    "REPORTED": ["MATCHED"],
    "MATCHED": ["CLAIMED"],
    "CLAIMED": ["CLOSED"],
    "CLOSED": [],
}


def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, description TEXT, location TEXT,
        status TEXT DEFAULT 'REPORTED',
        claimant TEXT, proof TEXT,
        image TEXT)""")
    # Automatically add 'image' column to existing databases
    cols = [col[1] for col in conn.execute("PRAGMA table_info(items)").fetchall()]
    if "image" not in cols:
        conn.execute("ALTER TABLE items ADD COLUMN image TEXT")
        conn.commit()
    return conn


def change_status(item_id, new_status):
    """Move an item to new_status only if the state machine allows it."""
    conn = get_db()
    item = conn.execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    if item is None:
        return "Item not found"
    if new_status not in NEXT_STATES[item["status"]]:
        return f"Cannot go from {item['status']} to {new_status}"
    conn.execute("UPDATE items SET status=? WHERE id=?", (new_status, item_id))
    conn.commit()
    return None


STEPS = ["REPORTED", "MATCHED", "CLAIMED", "CLOSED"]


@app.route("/")
def index():
    q = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip().upper()
    sql, args = "SELECT * FROM items WHERE 1=1", []
    if q:
        sql += " AND (name LIKE ? OR description LIKE ? OR location LIKE ?)"
        args += [f"%{q}%"] * 3
    if status in STEPS:
        sql += " AND status=?"
        args.append(status)
    items = get_db().execute(sql + " ORDER BY id DESC", args).fetchall()
    return render_template("index.html", items=items, q=q, status=status, steps=STEPS)


@app.route("/report", methods=["GET", "POST"])
def report():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        location = request.form.get("location", "").strip()
        if not name or not description or not location:
            flash("All fields are required")
            return render_template("report.html")

        image_filename = None
        if "image" in request.files:
            file = request.files["image"]
            if file and file.filename:
                ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
                if ext in ALLOWED_EXTENSIONS:
                    safe_name = secure_filename(file.filename)
                    image_filename = f"{uuid.uuid4().hex[:8]}_{safe_name}"
                    file.save(os.path.join(UPLOAD_FOLDER, image_filename))

        conn = get_db()
        conn.execute("INSERT INTO items (name, description, location, image) VALUES (?,?,?,?)",
                     (name, description, location, image_filename))
        conn.commit()
        return redirect(url_for("index"))
    return render_template("report.html")


@app.route("/item/<int:item_id>")
def item_page(item_id):
    item = get_db().execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()
    if item is None:
        return "Item not found", 404
    return render_template("item.html", item=item, steps=STEPS)


@app.route("/item/<int:item_id>/claim", methods=["POST"])
def claim(item_id):
    claimant = request.form["claimant"].strip()
    proof = request.form["proof"].strip()
    if not claimant or not proof:
        flash("Name and proof are required")
    else:
        error = change_status(item_id, "MATCHED")
        if error:
            flash(error)
        else:
            conn = get_db()
            conn.execute("UPDATE items SET claimant=?, proof=? WHERE id=?",
                         (claimant, proof, item_id))
            conn.commit()
    return redirect(url_for("item_page", item_id=item_id))


@app.route("/item/<int:item_id>/handover", methods=["POST"])
def handover(item_id):
    error = change_status(item_id, "CLAIMED")
    if error:
        flash(error)
    return redirect(url_for("item_page", item_id=item_id))


@app.route("/item/<int:item_id>/close", methods=["POST"])
def close(item_id):
    error = change_status(item_id, "CLOSED")
    if error:
        flash(error)
    return redirect(url_for("item_page", item_id=item_id))


if __name__ == "__main__":
    app.run(debug=True)
