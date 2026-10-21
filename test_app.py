# Black box test cases for the Lost & Found app (TC numbers match the project report)
import io
import os
import pytest
import app as lf

lf.DB = "test.db"
lf.app.config["TESTING"] = True


@pytest.fixture(autouse=True)
def fresh_db():
    conn = lf.get_db()
    conn.execute("DROP TABLE IF EXISTS items")
    conn.commit()
    conn.close()
    yield
    try:
        conn = lf.get_db()
        conn.execute("DROP TABLE IF EXISTS items")
        conn.commit()
        conn.close()
    except Exception:
        pass


client = lf.app.test_client()


def report(name="Wallet", desc="Black leather", loc="Library"):
    return client.post("/report", data={"name": name, "description": desc, "location": loc},
                       follow_redirects=True)


def claim(item_id=1, who="Ravi", proof="Has my ID card inside"):
    return client.post(f"/item/{item_id}/claim", data={"claimant": who, "proof": proof},
                       follow_redirects=True)


def handover(item_id=1):
    return client.post(f"/item/{item_id}/handover", follow_redirects=True)


def close(item_id=1):
    return client.post(f"/item/{item_id}/close", follow_redirects=True)


def row(item_id=1):
    return lf.get_db().execute("SELECT * FROM items WHERE id=?", (item_id,)).fetchone()


def count():
    return lf.get_db().execute("SELECT COUNT(*) FROM items").fetchone()[0]


def test_tc01_report_with_all_details():
    r = report()
    assert b"Wallet" in r.data and row()["status"] == "REPORTED"


def test_tc02_report_empty_name():
    r = report(name="")
    assert b"All fields are required" in r.data and count() == 0


def test_tc03_report_empty_description():
    report(desc="")
    assert count() == 0


def test_tc04_report_empty_location():
    report(loc="")
    assert count() == 0


def test_tc05_report_only_spaces():
    report(name="   ")
    assert count() == 0


def test_tc06_home_page_with_no_items():
    assert client.get("/").status_code == 200


def test_tc07_newest_item_listed_first():
    report(name="Wallet")
    report(name="Umbrella")
    html = client.get("/").data.decode()
    assert html.index("Umbrella") < html.index("Wallet")


def test_tc08_view_item_details():
    report()
    r = client.get("/item/1")
    assert r.status_code == 200 and b"Black leather" in r.data and b"REPORTED" in r.data


def test_tc09_view_missing_item():
    assert client.get("/item/99").status_code == 404


def test_tc10_claim_reported_item():
    report()
    claim()
    assert row()["status"] == "MATCHED" and row()["claimant"] == "Ravi"


def test_tc11_claim_with_empty_name():
    report()
    r = claim(who="")
    assert b"Name and proof are required" in r.data and row()["status"] == "REPORTED"


def test_tc12_claim_with_empty_proof():
    report()
    claim(proof="")
    assert row()["status"] == "REPORTED"


def test_tc13_claim_already_matched_item():
    report()
    claim(who="Ravi")
    r = claim(who="Sam")
    assert b"Cannot go from MATCHED to MATCHED" in r.data and row()["claimant"] == "Ravi"


def test_tc14_handover_matched_item():
    report()
    claim()
    handover()
    assert row()["status"] == "CLAIMED"


def test_tc15_handover_reported_item():
    report()
    r = handover()
    assert b"Cannot go from REPORTED to CLAIMED" in r.data and row()["status"] == "REPORTED"


def test_tc16_close_claimed_item():
    report()
    claim()
    handover()
    close()
    assert row()["status"] == "CLOSED"


def test_tc17_close_matched_item():
    report()
    claim()
    r = close()
    assert b"Cannot go from MATCHED to CLOSED" in r.data and row()["status"] == "MATCHED"


def test_tc18_closed_item_cannot_change():
    report()
    claim()
    handover()
    close()
    assert b"Cannot go from CLOSED to CLOSED" in close().data
    assert b"Cannot go from CLOSED to CLAIMED" in handover().data
    assert row()["status"] == "CLOSED"


def test_tc19_complete_lifecycle():
    report()
    seen = [row()["status"]]
    claim()
    seen.append(row()["status"])
    handover()
    seen.append(row()["status"])
    close()
    seen.append(row()["status"])
    assert seen == ["REPORTED", "MATCHED", "CLAIMED", "CLOSED"]


def test_tc20_change_status_of_missing_item():
    assert lf.change_status(99, "MATCHED") == "Item not found"


# ---- Unit tests: call the state machine function directly (no web page involved) ----
def test_tc21_every_allowed_change_works():
    add = lambda: lf.get_db().execute(
        "INSERT INTO items (name, description, location) VALUES ('Pen','Blue','Lab')").connection.commit()
    add()
    for new in ["MATCHED", "CLAIMED", "CLOSED"]:
        assert lf.change_status(1, new) is None


def test_tc22_skipping_a_state_is_rejected():
    lf.get_db().execute("INSERT INTO items (name, description, location) VALUES ('Pen','Blue','Lab')").connection.commit()
    assert lf.change_status(1, "CLOSED") == "Cannot go from REPORTED to CLOSED"
    assert row()["status"] == "REPORTED"


def test_tc23_closed_has_no_next_state():
    assert lf.NEXT_STATES["CLOSED"] == []


def test_tc24_report_with_image():
    img_data = (io.BytesIO(b"fake image content"), "wallet.jpg")
    r = client.post("/report", data={
        "name": "Leather Wallet",
        "description": "Brown with coins",
        "location": "Library",
        "image": img_data
    }, content_type="multipart/form-data", follow_redirects=True)
    assert r.status_code == 200
    item = row(1)
    assert item["image"] is not None
    assert "wallet.jpg" in item["image"]
    assert item["image"].encode() in r.data
    saved_path = os.path.join(lf.UPLOAD_FOLDER, item["image"])
    if os.path.exists(saved_path):
        os.remove(saved_path)

