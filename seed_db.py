import os
import shutil
import sqlite3

def seed():
    artifact_dir = r"C:\Users\Prem\.gemini\antigravity-ide\brain\faf617d5-035d-4a31-a70e-186f45c37637"
    upload_dir = os.path.join(os.path.dirname(__file__), "static", "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    img_map = {
        "stethoscope.jpg": "stethoscope_1792605250151.jpg",
        "car_key.jpg": "toyota_key_fob_1792605270425.jpg",
        "tumbler.jpg": "stanley_tumbler_1792605290396.jpg",
        "headphones.jpg": "sony_headphones_1792605309762.jpg",
        "wallet.jpg": "leather_wallet_1792605330236.jpg",
        "glasses.jpg": "rayban_glasses_1792605353040.jpg",
        "kindle.jpg": "kindle_reader_1792605376654.jpg",
        "umbrella.jpg": "black_umbrella_1792607130617.jpg",
        "keys.jpg": "bike_keys_1792604779607.jpg",
        "backpack.jpg": "campus_backpack_1792604758485.jpg",
        "bottle.jpg": "water_bottle_1792604736024.jpg",
        "airpods.jpg": "airpods_case_1792604709289.jpg",
        "calc.jpg": "casio_calculator_1792604662490.jpg",
    }

    for dest_name, src_name in img_map.items():
        src_path = os.path.join(artifact_dir, src_name)
        dest_path = os.path.join(upload_dir, dest_name)
        if os.path.exists(src_path) and not os.path.exists(dest_path):
            shutil.copy2(src_path, dest_path)
            print(f"Copied photo: {dest_name}")

    entries = [
        ("Casio fx-991EX ClassWiz Calculator", "Black scientific calculator with silver navigation key, name initials 'PK' scratched on back cover.", "Engineering Block, Room 302", "REPORTED", None, None, "calc.jpg"),
        ("Apple AirPods Pro (2nd Gen)", "White charging case in open state, left earbud has faint scratch near mic grill.", "Central Library, 1st Floor Quiet Zone", "MATCHED", "Rohan Sharma", "Engraved with RS on the case, connects with name Rohan AirPods.", "airpods.jpg"),
        ("Navy Blue Hydro Flask (32 oz)", "Wide mouth insulated metal water bottle with boot protector and several stickers.", "Basketball Court bleachers", "REPORTED", None, None, "bottle.jpg"),
        ("Student ID Card & Metro Pass", "Lanyard with college ID card (Dept of Computer Science) and blue metro smart card inside a transparent holder.", "Cafeteria checkout counter", "CLAIMED", "Ananya Patel", "Roll number ends in 042, lanyard has a small NASA pin.", "wallet.jpg"),
        ("Black North Face Backpack", "Borealis backpack containing notebooks, graph paper, and blue umbrella.", "Seminar Hall B", "CLOSED", "David Chen", "Front small pocket contains a red 64GB SanDisk USB with my project resume.", "backpack.jpg"),
        ("Set of Bike Keys with Red Tag", "Honda bike key with two small locker keys on a red woven keychain tag.", "North Parking Lot, Slot 45", "REPORTED", None, None, "keys.jpg"),
        ("Kindle Paperwhite (11th Gen)", "Black e-reader with teal fabric magnetic cover.", "Student Union Lounge, near the sofas", "MATCHED", "Priya Sundaram", "Lock screen shows Atomic Habits, registered under Priya.", "kindle.jpg"),
        ("Ray-Ban Prescription Glasses", "Matte black tortoiseshell frame in a brown hard leather case.", "Chemistry Lab 2, Workbench 4", "REPORTED", None, None, "glasses.jpg"),
        ("Logitech MX Master 3S Mouse", "Pale gray wireless ergonomic mouse with thumb scroll wheel.", "Mac Lab, 3rd Floor", "REPORTED", None, None, "headphones.jpg"),
        ("Grey H&M Zip-up Hoodie (Size L)", "Charcoal heather grey fleece zip hoodie with campus club badge pinned to chest.", "Main Auditorium, Row G Seat 14", "CLAIMED", "Kevin Vance", "Left pocket has a hair tie and campus bookstore receipt from Monday.", "backpack.jpg"),
        ("Anker 20,000mAh Power Bank", "Black textured heavy portable charger with two USB-A and one USB-C port.", "Study Hub, 2nd Floor charging station", "REPORTED", None, None, "kindle.jpg"),
        ("Titan Quartz Wristwatch", "Classic analog men's watch with dark brown leather strap and silver dial.", "Gym Locker Room, Bench 3", "MATCHED", "Aditya Rao", "Back engraving says 'Gift from Dad 2024'.", "car_key.jpg"),
        ("Spiral Sketchbook & Faber-Castell Pencils", "A4 black hardcover spiral sketchbook with 12 drawing pencils in a canvas roll.", "Architecture Studio, Table 8", "REPORTED", None, None, "calc.jpg"),
        ("Brown Leather Bi-fold Wallet", "Genuine brown leather wallet. Private compartments remained closed.", "Campus Shuttle Bus #4", "MATCHED", "Michael Scott", "Contains student discount card and photo of a golden retriever.", "wallet.jpg"),
        ("Black Umbrella with Wooden Handle", "Windproof large 8-rib folding umbrella with curved wooden handle.", "Main Entrance umbrella stand", "CLOSED", "Sarah Jenkins", "Small yellow dot sticker with initials SJ on the bottom tip.", "umbrella.jpg"),
        ("Lab Coat (Size M) with Safety Goggles", "White cotton lab coat with clear UV safety goggles in breast pocket.", "Biochemistry Laboratory coat rack", "REPORTED", None, None, "glasses.jpg"),
        ("Sony WH-1000XM4 Headphones", "Black over-ear noise-cancelling headphones in matching zippered travel case.", "Media Center Editing Suite 2", "CLAIMED", "Vikram Verma", "Case contains airplane adapter and custom braided gold-plated 3.5mm cable.", "headphones.jpg"),
        ("Stanley Quencher Tumbler (40 oz)", "Light pink vacuum insulated travel mug with straw and handle.", "Amphitheatre grass steps", "REPORTED", None, None, "tumbler.jpg"),
        ("Car Key Fob (Toyota)", "3-button black Toyota smart key fob with small silver elephant charm.", "Football Ground walkway", "REPORTED", None, None, "car_key.jpg"),
        ("Littmann Classic III Stethoscope", "Burgundy tube with stainless steel chestpiece.", "Health Center waiting area", "CLOSED", "Dr. Sneha Kulkarni", "Laser-engraved Dr. S. Kulkarni on the binaural metal tube.", "stethoscope.jpg"),
    ]

    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_paths = [
        os.path.join(workspace_root, "lostfound.db"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "lostfound.db")
    ]

    for db_path in db_paths:
        if not os.path.exists(db_path):
            continue
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("""CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT, description TEXT, location TEXT,
            status TEXT DEFAULT 'REPORTED',
            claimant TEXT, proof TEXT,
            image TEXT)""")
        cols = [col[1] for col in conn.execute("PRAGMA table_info(items)").fetchall()]
        if "image" not in cols:
            conn.execute("ALTER TABLE items ADD COLUMN image TEXT")

        for item in entries:
            # Update existing or insert
            exists = conn.execute("SELECT id FROM items WHERE name=?", (item[0],)).fetchone()
            if exists:
                conn.execute("""UPDATE items SET description=?, location=?, status=?, claimant=?, proof=?, image=?
                                WHERE id=?""", (item[1], item[2], item[3], item[4], item[5], item[6], exists["id"]))
            else:
                conn.execute("""INSERT INTO items (name, description, location, status, claimant, proof, image)
                                VALUES (?, ?, ?, ?, ?, ?, ?)""", item)
        conn.commit()
        total = conn.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        with_img = conn.execute("SELECT COUNT(*) FROM items WHERE image IS NOT NULL").fetchone()[0]
        print(f"Database at {db_path}: {with_img} of {total} items have images.")
        conn.close()

if __name__ == "__main__":
    seed()
