from pathlib import Path

from fastapi.testclient import TestClient
import main


def make_client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "test.db")
    main.sessions.clear()
    main.login_attempts.clear()
    main.init_db()
    return TestClient(main.app)


def ok(response):
    body = response.json()
    assert body["status"] == "ok", body
    return body["data"]


def login(client):
    response = client.post("/api/login", json={"password": "2526E"})
    assert response.status_code == 200
    assert "başar" in response.json()["message"].casefold() or "baÅ" in response.json()["message"]


def test_login_rules(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    assert client.get("/").status_code in {200, 307}
    assert client.get("/api/dashboard").status_code == 401
    assert client.get("/api/export").status_code == 401
    assert client.post("/api/login", json={"password": ""}).status_code == 401
    wrong = client.post("/api/login", json={"password": "yanlis"})
    assert wrong.status_code == 401
    login(client)
    assert ok(client.get("/api/session"))["authenticated"] is True
    assert client.get("/api/dashboard").status_code == 200
    client.post("/api/logout")
    assert client.get("/api/dashboard").status_code == 401


def test_login_lockout_after_repeated_wrong_passwords(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    for _ in range(main.MAX_LOGIN_ATTEMPTS):
        response = client.post("/api/login", json={"password": "yanlis"})
        assert response.status_code == 401

    locked = client.post("/api/login", json={"password": "2526E"})
    assert locked.status_code == 429
    assert client.get("/api/dashboard").status_code == 401


def test_pages_and_required_business_flow(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    login(client)

    assert client.get("/").status_code == 200
    assert client.get("/login").status_code == 200
    for path in ["/api/dashboard", "/api/alis", "/api/satis", "/api/stok", "/api/cari", "/api/hurda", "/api/ayarlar"]:
        assert client.get(path).status_code == 200, path

    hurda_blocked = client.post("/api/alis", json={
        "tedarikci": "TEST", "cinsi": "HURDA", "ayar": "22", "adet": 1,
        "gram": 1, "milyem": 916, "has_fiyati": 3000,
    })
    assert hurda_blocked.status_code == 422

    alis = ok(client.post("/api/alis", json={
        "tarih": "2026-06-29", "tedarikci": "TEST TEDARIKCI", "cinsi": "BILEZIK", "ayar": "22",
        "adet": 2, "gram": 10, "milyem": 916, "has_fiyati": 3000, "iscilik": 500,
        "ek_masraf": 0, "odenen": 20000, "notlar": "test alis",
    }))
    assert alis["has"] == 18.320
    assert alis["toplam_tutar"] == 55460.00
    assert alis["kalan_borc"] == 35460.00

    stok = ok(client.get("/api/stok"))
    assert len(stok) == 1
    assert main.normalize_text(stok[0]["cinsi"]) == main.normalize_text("bilezik")
    assert stok[0]["ayar"] == "22"
    assert stok[0]["alis_has"] == 18.320

    options = ok(client.get("/api/satis/urun-secenekleri"))
    assert len(options) == 1
    assert options[0]["id"] == alis["id"]
    assert options[0]["kalan_has"] == 18.320

    satis = ok(client.post("/api/satis", json={
        "tarih": "2026-06-29", "musteri": "TEST MUSTERI", "alis_id": alis["id"],
        "cinsi": "BILEZIK", "ayar": "22", "adet": 1, "gram": 5, "satis_milyem": 940,
        "iscilik": 300, "ek_ucret": 0, "indirim": 0, "alinan": 10000, "notlar": "test satis",
    }))
    assert satis["has"] == 4.700
    assert satis["satis_has"] == 4.700
    assert satis["alis_milyem"] == 916.000
    assert satis["satis_milyem"] == 940.000
    assert satis["milyem_farki"] == 24.000
    assert satis["milyem_farki_has_etkisi"] == 0.120
    assert satis["has_kari"] == 0.120
    assert satis["milyem_kari"] == 0.120
    assert satis["kar"] == 0.120
    assert satis["purchase_id"] == alis["id"]
    assert satis["alis_id"] == alis["id"]
    assert satis["toplam_tutar"] == 14400.00
    assert satis["kalan_borc"] == 4400.00

    stok = ok(client.get("/api/stok"))[0]
    assert stok["satis_has"] == 4.700
    assert stok["kalan_adet"] == 1.000
    assert stok["kalan_gram"] == 15.000
    assert stok["kalan_has"] == 13.620

    fazla = client.post("/api/satis", json={
        "tarih": "2026-06-29", "musteri": "FAZLA", "alis_id": alis["id"],
        "cinsi": "BILEZIK", "ayar": "22", "adet": 20, "gram": 200, "satis_milyem": 940,
    })
    assert fazla.status_code == 400
    assert "STOK" in fazla.json()["message"]

    hurda_alis = ok(client.post("/api/hurda", json={
        "tarih": "2026-06-29", "islem_turu": "ALIS", "kisi": "TEST HURDA TEDARIKCI",
        "cinsi": "HURDA", "ayar": "22", "adet": 1, "gram": 10, "milyem": 916,
        "has_fiyati": 3000, "iscilik": 0, "odenen_veya_alinan": 20000,
    }))
    assert hurda_alis["has"] == 9.160
    assert hurda_alis["toplam_tutar"] == 27480.00
    assert hurda_alis["kalan_borc"] == 7480.00

    hurda_options = ok(client.get("/api/hurda/urun-secenekleri"))
    assert len(hurda_options) == 1
    assert hurda_options[0]["id"] == hurda_alis["id"]

    hurda_satis = ok(client.post("/api/hurda", json={
        "tarih": "2026-06-29", "islem_turu": "SATIS", "hurda_alis_id": hurda_alis["id"],
        "kisi": "TEST HURDA MUSTERI", "cinsi": "HURDA", "ayar": "22", "adet": 1,
        "gram": 4, "milyem": 916, "has_fiyati": 3500, "iscilik": 0, "odenen_veya_alinan": 10000,
    }))
    assert hurda_satis["has"] == 3.664
    assert hurda_satis["toplam_tutar"] == 12824.00
    assert hurda_satis["kalan_borc"] == 2824.00
    assert hurda_satis["hurda_kar"] == 1832.00

    hurda = ok(client.get("/api/hurda"))
    assert hurda["ozet"]["hurda_alis_has"] == 9.160
    assert hurda["ozet"]["hurda_satis_has"] == 3.664
    assert hurda["ozet"]["hurda_kalan_has"] == 5.496
    assert hurda["ozet"]["hurda_alis_tutari"] == 27480.00
    assert hurda["ozet"]["hurda_satis_tutari"] == 12824.00
    assert hurda["ozet"]["hurda_kar"] == 1832.00
    assert hurda["stok"][0]["kalan_has"] == 5.496

    # Hurda normal stok tablosuna karismamali.
    stok = ok(client.get("/api/stok"))
    assert len(stok) == 1
    assert main.normalize_text(stok[0]["cinsi"]) == main.normalize_text("bilezik")

    cari = ok(client.get("/api/cari"))
    suppliers = {row["tedarikci_adi"]: row for row in cari["tedarikciler"]}
    customers = {row["musteri_adi"]: row for row in cari["musteriler"]}
    assert suppliers["TEST TEDARIKCI"]["kalan_borc"] == 35460.00
    assert suppliers["TEST HURDA TEDARIKCI"]["kalan_borc"] == 7480.00
    assert customers["TEST MUSTERI"]["kalan_borc"] == 4400.00
    assert customers["TEST HURDA MUSTERI"]["kalan_borc"] == 2824.00

    dashboard = ok(client.get("/api/dashboard"))
    assert dashboard["toplam_normal_alis"] == 55460.00
    assert dashboard["toplam_normal_satis"] == 14400.00
    assert dashboard["genel_urun_kari"] == 0.120
    assert dashboard["hurda_alis_toplami"] == 27480.00
    assert dashboard["hurda_satis_toplami"] == 12824.00
    assert dashboard["hurda_kar"] == 1832.00
    assert dashboard["normal_stok_has"] == 13.620
    assert dashboard["normal_stok_gram"] == 15.000
    assert dashboard["hurda_kalan_has"] == 5.496
    assert dashboard["hurda_kalan_gram"] == 6.000
    assert dashboard["uyari_sayisi"] == 0

    export = ok(client.get("/api/export"))
    assert export["version"] == "1.0"
    assert "exported_at" in export
    assert len(export["alis"]) == 1
    assert len(export["satis"]) == 1
    assert len(export["hurda"]) == 2
    assert export["stok_normal"][0]["kalan_gram"] == 15.000
    assert export["stok_hurda"][0]["kalan_gram"] == 6.000
    assert export["dashboard"]["genel_urun_kari"] == 0.120
    assert "musteriler" in export["cari"] and "tedarikciler" in export["cari"] and "kisiler" in export["cari"]

    blocked_delete = client.delete(f"/api/alis/{alis['id']}")
    assert blocked_delete.status_code == 400
    assert len(ok(client.get("/api/alis"))) == 1
    assert client.delete(f"/api/satis/{satis['id']}").status_code == 200
    assert client.delete(f"/api/alis/{alis['id']}").status_code == 200
    assert ok(client.get("/api/stok")) == []

def test_purchase_id_and_turkish_char_flow_without_milyem_stock_block(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    login(client)

    alis = ok(client.post("/api/alis", json={
        "tarih": "2026-06-30", "tedarikci": "\u015eAH\u0130N TEDAR\u0130K\u00c7\u0130", "cinsi": "B\u0130LEZ\u0130K", "ayar": "14",
        "adet": 1, "gram": 10, "milyem": 550, "has_fiyati": 1000, "iscilik": 0,
        "ek_masraf": 0, "odenen": 0,
    }))
    assert alis["has"] == 5.500

    selectable = ok(client.get("/api/alis/selectable"))
    assert selectable[0]["id"] == alis["id"]

    satis = ok(client.post("/api/satis", json={
        "tarih": "2026-06-30", "musteri": "\u0130SMA\u0130L M\u00dc\u015eTER\u0130", "purchase_id": alis["id"],
        "cinsi": "bilezik", "ayar": "14", "adet": 1, "gram": 10, "satis_milyem": 560,
        "has_fiyati": 1000, "iscilik": 0, "ek_ucret": 0, "indirim": 0, "alinan": 0,
    }))
    assert satis["purchase_id"] == alis["id"]
    assert satis["alis_id"] == alis["id"]
    assert satis["has"] == 5.600
    assert satis["milyem_farki"] == 10.000
    assert satis["milyem_farki_has_etkisi"] == 0.100
    assert satis["has_kari"] == 0.100
    assert satis["has_kari_milyem"] == 10.000

    stock = ok(client.get("/api/stok"))[0]
    assert stock["kalan_gram"] == 0.000
    assert stock["kalan_has"] == -0.100
    assert "SATI\u015e HASI" in stock["uyari"]

    cari = ok(client.get("/api/cari"))
    assert cari["tedarikciler"][0]["tedarikci_adi"] == "\u015eAH\u0130N TEDAR\u0130K\u00c7\u0130"
    assert cari["musteriler"][0]["musteri_adi"] == "\u0130SMA\u0130L M\u00dc\u015eTER\u0130"
    fazla = client.post("/api/satis", json={
        "tarih": "2026-06-30", "musteri": "FAZLA", "purchase_id": alis["id"],
        "cinsi": "B\u0130LEZ\u0130K", "ayar": "14", "adet": 1.001, "gram": 10, "satis_milyem": 560,
    })
    assert fazla.status_code == 400
    assert "STOK" in fazla.json()["message"]




def test_frontend_layout_tabs_columns_and_confirmations():
    app_js = Path("static/app.js").read_text(encoding="utf-8")
    index_html = Path("static/index.html").read_text(encoding="utf-8")

    assert 'data-view="ayarlar"' not in index_html
    assert "Ayarlar" not in index_html
    assert "T\\u00dcM\\u00dc" in app_js
    assert "M\\u00dc\\u015eTER\\u0130LER" in app_js
    assert "TEDAR\\u0130K\\u00c7\\u0130LER" in app_js
    assert "K\\u0130\\u015e\\u0130 / F\\u0130RMA" in app_js
    assert "HURDA ALI\\u015e" in app_js
    assert "HURDA SATI\\u015e" in app_js
    assert "NORMAL STOK" in app_js
    assert "HURDA STOK" in app_js
    assert "Bu al\\u0131\\u015f kayd\\u0131n\\u0131" in app_js
    assert "Bu sat\\u0131\\u015f kayd\\u0131n\\u0131" in app_js
    assert "Bu hurda kayd\\u0131n\\u0131" in app_js

    forms_block = app_js.split("const forms =", 1)[1].split("const columns =", 1)[0]
    alis_form = forms_block.split("alis:", 1)[1].split("satis:", 1)[0]
    satis_form = forms_block.split("satis:", 1)[1].split("hurda:", 1)[0]
    assert "HURDA" not in app_js.split("suggestions:", 1)[1].split("customers", 1)[0]
    for removed in ["has_fiyati", "iscilik", "ek_masraf", "odenen"]:
        assert removed not in alis_form
    for removed in ["has_fiyati", "iscilik", "ek_ucret", "indirim", "alinan"]:
        assert removed not in satis_form
    assert 'form.elements.satis_milyem.value = ""' in app_js
    assert "form.elements.satis_milyem.value = row.alis_milyem" not in app_js
    assert "form.elements.notlar" in app_js
    assert "icon-btn icon-edit" in app_js
    assert "icon-btn icon-delete" in app_js
    assert "Has K\\u00e2r\\u0131" not in app_js
    assert "Milyem K\\u00e2r\\u0131" in app_js
    assert "top-export-button" in index_html
    assert "exportBtn" in index_html
    assert "/api/export" in app_js
    assert "kuyumcu_backup_" in app_js
    assert 'showConfirm("T\\u00fcm verileri JSON' in app_js

    columns_block = app_js.split("const columns =", 1)[1].split("};", 1)[0]
    assert "kisiCari" in columns_block
    assert "normal_alis_has" in columns_block
    assert "normal_satis_has" in columns_block
    assert "hurda_alis_has" in columns_block
    assert "hurda_satis_has" in columns_block
    assert "toplam_alis_has" in columns_block
    assert "toplam_satis_has" in columns_block
    assert "kalan_has" in columns_block
    assert "milyem_kari" in columns_block
    assert "hurda_alis_adet" in columns_block
    assert "hurda_satis_adet" in columns_block
    assert "purchase_id" not in columns_block
    assert "alis_id" not in columns_block
    assert "hurda_alis_id" not in columns_block


def test_edit_endpoints_update_without_duplicates(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    login(client)

    alis = ok(client.post("/api/alis", json={
        "tarih": "2026-06-30", "tedarikci": "EDIT TEDARIKCI", "cinsi": "BILEZIK", "ayar": "22",
        "adet": 2, "gram": 10, "milyem": 916, "has_fiyati": 3000, "iscilik": 0,
        "ek_masraf": 0, "odenen": 1000,
    }))
    updated_alis = ok(client.put(f"/api/alis/{alis['id']}", json={
        "tarih": "2026-06-30", "tedarikci": "EDIT TEDARIKCI", "cinsi": "BILEZIK", "ayar": "22",
        "adet": 2, "gram": 10, "milyem": 916, "has_fiyati": 3100, "iscilik": 100,
        "ek_masraf": 0, "odenen": 2000,
    }))
    assert updated_alis["toplam_tutar"] == 56892.00
    assert len(ok(client.get("/api/alis"))) == 1

    satis = ok(client.post("/api/satis", json={
        "tarih": "2026-06-30", "musteri": "EDIT MUSTERI", "purchase_id": alis["id"],
        "cinsi": "BILEZIK", "ayar": "22", "adet": 1, "gram": 4, "satis_milyem": 916,
        "has_fiyati": 3300, "iscilik": 50, "ek_ucret": 0, "indirim": 0, "alinan": 1000,
    }))
    updated_satis = ok(client.put(f"/api/satis/{satis['id']}", json={
        "tarih": "2026-06-30", "musteri": "EDIT MUSTERI 2", "purchase_id": alis["id"],
        "cinsi": "BILEZIK", "ayar": "22", "adet": 1, "gram": 5, "satis_milyem": 916,
        "has_fiyati": 3300, "iscilik": 50, "ek_ucret": 0, "indirim": 0, "alinan": 2000,
    }))
    assert updated_satis["purchase_id"] == alis["id"]
    assert updated_satis["has"] == 4.580
    assert len(ok(client.get("/api/satis"))) == 1
    linked_alis_edit = ok(client.put(f"/api/alis/{alis['id']}", json={
        "tarih": "2026-06-30", "tedarikci": "EDIT TEDARIKCI 2", "cinsi": "BILEZIK", "ayar": "22",
        "adet": 2, "gram": 10, "milyem": 917, "notlar": "linked edit",
    }))
    assert linked_alis_edit["tedarikci"] == "EDIT TEDARIKCI 2"
    assert linked_alis_edit["milyem"] == 917.000
    assert linked_alis_edit["has_fiyati"] == 3100.00
    assert linked_alis_edit["iscilik"] == 100.00
    assert linked_alis_edit["odenen"] == 2000.00
    blocked_product_edit = client.put(f"/api/alis/{alis['id']}", json={
        "tarih": "2026-06-30", "tedarikci": "EDIT TEDARIKCI 2", "cinsi": "YUZUK", "ayar": "22",
        "adet": 2, "gram": 10, "milyem": 917,
    })
    assert blocked_product_edit.status_code == 400

    stock = ok(client.get("/api/stok"))[0]
    assert stock["satis_gram"] == 5.000
    dashboard_after_edit = ok(client.get("/api/dashboard"))
    assert dashboard_after_edit["toplam_normal_alis"] == 56954.00
    assert dashboard_after_edit["toplam_normal_satis"] == 15164.00
    assert dashboard_after_edit["normal_stok_gram"] == 15.000

    assert client.delete(f"/api/satis/{satis['id']}").status_code == 200
    after_delete_stock = ok(client.get("/api/stok"))[0]
    assert after_delete_stock["satis_gram"] == 0.000
    assert after_delete_stock["kalan_gram"] == 20.000
    after_delete_dashboard = ok(client.get("/api/dashboard"))
    assert after_delete_dashboard["toplam_normal_satis"] == 0.00
    assert after_delete_dashboard["genel_urun_kari"] == 0.000

    hurda_alis = ok(client.post("/api/hurda", json={
        "tarih": "2026-06-30", "islem_turu": "ALIS", "kisi": "EDIT HURDA TEDARIKCI",
        "cinsi": "HURDA", "ayar": "22", "adet": 1, "gram": 10, "milyem": 916,
        "has_fiyati": 3000, "iscilik": 0, "odenen_veya_alinan": 0,
    }))
    hurda_satis = ok(client.post("/api/hurda", json={
        "tarih": "2026-06-30", "islem_turu": "SATIS", "hurda_alis_id": hurda_alis["id"],
        "kisi": "EDIT HURDA MUSTERI", "cinsi": "HURDA", "ayar": "22", "adet": 1,
        "gram": 2, "milyem": 916, "has_fiyati": 3200, "iscilik": 0, "odenen_veya_alinan": 0,
    }))
    updated_hurda = ok(client.put(f"/api/hurda/{hurda_satis['id']}", json={
        "tarih": "2026-06-30", "islem_turu": "SATIS", "hurda_alis_id": hurda_alis["id"],
        "kisi": "EDIT HURDA MUSTERI", "cinsi": "HURDA", "ayar": "22", "adet": 1,
        "gram": 3, "milyem": 916, "has_fiyati": 3200, "iscilik": 0, "odenen_veya_alinan": 0,
    }))
    assert updated_hurda["has"] == 2.748
    assert updated_hurda["has_fiyati"] == 3200.00
    hurda = ok(client.get("/api/hurda"))
    assert len(hurda["kayitlar"]) == 2
    assert hurda["stok"][0]["kalan_gram"] == 7.000
    assert client.delete(f"/api/hurda/{hurda_satis['id']}").status_code == 200
    hurda_after_delete = ok(client.get("/api/hurda"))
    assert len(hurda_after_delete["kayitlar"]) == 1
    assert hurda_after_delete["stok"][0]["kalan_gram"] == 10.000


def test_hurda_sale_stock_check_uses_adet_and_gram_not_milyem(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    login(client)

    hurda_alis = ok(client.post("/api/hurda", json={
        "tarih": "2026-06-30", "islem_turu": "ALIS", "kisi": "HURDA TEDARIKCI",
        "cinsi": "HURDA", "ayar": "22", "adet": 100, "gram": 1, "milyem": 930,
        "has_fiyati": 0, "iscilik": 0, "odenen_veya_alinan": 0,
    }))

    allowed = ok(client.post("/api/hurda", json={
        "tarih": "2026-06-30", "islem_turu": "SATIS", "hurda_alis_id": hurda_alis["id"],
        "kisi": "HURDA MUSTERI", "cinsi": "HURDA", "ayar": "22", "adet": 100,
        "gram": 1, "milyem": 940, "has_fiyati": 0, "iscilik": 0, "odenen_veya_alinan": 0,
    }))
    assert allowed["has"] == 94.000
    assert allowed["hurda_alis_id"] == hurda_alis["id"]

    stok = ok(client.get("/api/hurda"))["stok"][0]
    assert stok["kalan_adet"] == 0.000
    assert stok["kalan_gram"] == 0.000
    assert stok["kalan_has"] == -1.000

    too_much = client.post("/api/hurda", json={
        "tarih": "2026-06-30", "islem_turu": "SATIS", "hurda_alis_id": hurda_alis["id"],
        "kisi": "FAZLA", "cinsi": "HURDA", "ayar": "22", "adet": 1,
        "gram": 1, "milyem": 940,
    })
    assert too_much.status_code == 400
    assert "STOK" in too_much.json()["message"]


def test_required_routes_are_registered():
    routes = {(tuple(sorted(getattr(route, "methods", []) or [])), getattr(route, "path", "")) for route in main.app.routes}

    def has(method, path):
        return any(path == route_path and method in methods for methods, route_path in routes)

    for table in ["alis", "satis", "hurda"]:
        assert has("GET", f"/api/{table}")
        assert has("POST", f"/api/{table}")
        assert has("PUT", f"/api/{table}/{{item_id}}")
        assert has("DELETE", f"/api/{table}/{{item_id}}")
    for path in [
        "/api/stok", "/api/stok/normal", "/api/stok/hurda", "/api/cari", "/api/dashboard",
        "/api/satis/urun-secenekleri", "/api/hurda/urun-secenekleri",
    ]:
        assert has("GET", path), path


def test_legacy_hurda_like_alis_is_hidden_from_normal_stock(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    login(client)
    with main.db() as conn:
        conn.execute(
            """
            INSERT INTO alis (tarih, tedarikci, cinsi, ayar, adet, gram, milyem, has, has_fiyati, iscilik, ek_masraf, odenen, notlar)
            VALUES ('2026-06-30', 'ESKI', 'B-HURDA', '22', 1, 10, 916, 9.16, 0, 0, 0, 0, '')
            """
        )
        conn.execute(
            """
            INSERT INTO alis (tarih, tedarikci, cinsi, ayar, adet, gram, milyem, has, has_fiyati, iscilik, ek_masraf, odenen, notlar)
            VALUES ('2026-06-30', 'NORMAL', 'BILEZIK', '22', 1, 10, 916, 9.16, 0, 0, 0, 0, '')
            """
        )
    normal = ok(client.get("/api/stok/normal"))
    assert len(normal) == 1
    assert main.normalize_text(normal[0]["cinsi"]) == main.normalize_text("BILEZIK")
    assert "hurda" not in main.normalize_text(normal[0]["cinsi"])


def test_hurda_alis_edit_accepts_empty_hidden_purchase_id(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    login(client)

    hurda_alis = ok(client.post("/api/hurda", json={
        "tarih": "2026-07-02", "islem_turu": "ALIS", "hurda_alis_id": "", "kisi": "NOT EDIT TEDARIKCI",
        "cinsi": "HURDA", "ayar": "22", "adet": 1, "gram": 10, "milyem": 916,
        "notlar": "ilk not", "has_fiyati": 0, "iscilik": 0, "odenen_veya_alinan": 0,
    }))

    updated = ok(client.put(f"/api/hurda/{hurda_alis['id']}", json={
        "tarih": "2026-07-02", "islem_turu": "ALIŞ", "hurda_alis_id": "", "kisi": "NOT EDIT TEDARIKCI",
        "cinsi": "HURDA", "ayar": "22", "adet": 1, "gram": 10, "milyem": 916,
        "notlar": "not duzenlendi", "has_fiyati": 0, "iscilik": 0, "odenen_veya_alinan": 0,
    }))
    assert updated["id"] == hurda_alis["id"]
    assert updated["hurda_alis_id"] is None
    assert updated["not"] == "not duzenlendi"
    assert len(ok(client.get("/api/hurda"))["kayitlar"]) == 1


def test_cari_aggregates_normal_and_hurda_with_same_names_and_recalculates(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    login(client)

    alis_1 = ok(client.post("/api/alis", json={
        "tarih": "2026-07-01", "tedarikci": "ABC TEDARIKCI", "cinsi": "BILEZIK", "ayar": "22",
        "adet": 1, "gram": 10, "milyem": 1000, "has_fiyati": 100, "iscilik": 50,
        "ek_masraf": 25, "odenen": 200,
    }))
    alis_2 = ok(client.post("/api/alis", json={
        "tarih": "2026-07-02", "tedarikci": "abc tedarikci", "cinsi": "BILEZIK", "ayar": "22",
        "adet": 1, "gram": 5, "milyem": 1000, "has_fiyati": 100, "iscilik": 0,
        "ek_masraf": 0, "odenen": 100,
    }))
    satis_1 = ok(client.post("/api/satis", json={
        "tarih": "2026-07-01", "musteri": "XYZ MUSTERI", "purchase_id": alis_1["id"],
        "cinsi": "BILEZIK", "ayar": "22", "adet": 1, "gram": 5, "satis_milyem": 1000,
        "has_fiyati": 100, "iscilik": 20, "ek_ucret": 10, "indirim": 5, "alinan": 100,
    }))
    satis_2 = ok(client.post("/api/satis", json={
        "tarih": "2026-07-02", "musteri": "xyz musteri", "purchase_id": alis_2["id"],
        "cinsi": "BILEZIK", "ayar": "22", "adet": 1, "gram": 1, "satis_milyem": 1000,
        "has_fiyati": 120, "iscilik": 0, "ek_ucret": 0, "indirim": 0, "alinan": 20,
    }))
    hurda_alis = ok(client.post("/api/hurda", json={
        "tarih": "2026-07-03", "islem_turu": "ALIS", "kisi": "ABC TEDARIKCI",
        "cinsi": "HURDA", "ayar": "22", "adet": 1, "gram": 2, "milyem": 1000,
        "has_fiyati": 50, "iscilik": 0, "odenen_veya_alinan": 40,
    }))
    ok(client.post("/api/hurda", json={
        "tarih": "2026-07-03", "islem_turu": "SATIS", "hurda_alis_id": hurda_alis["id"],
        "kisi": "XYZ MUSTERI", "cinsi": "HURDA", "ayar": "22", "adet": 1,
        "gram": 1, "milyem": 1000, "has_fiyati": 150, "iscilik": 0, "odenen_veya_alinan": 50,
    }))

    cari = ok(client.get("/api/cari"))
    suppliers = {main.normalize_text(row["tedarikci_adi"]): row for row in cari["tedarikciler"]}
    customers = {main.normalize_text(row["musteri_adi"]): row for row in cari["musteriler"]}
    supplier = suppliers[main.normalize_text("ABC TEDARIKCI")]
    customer = customers[main.normalize_text("XYZ MUSTERI")]
    people = {main.normalize_text(row["isim"]): row for row in cari["kisiler"]}
    supplier_person = people[main.normalize_text("ABC TEDARIKCI")]
    customer_person = people[main.normalize_text("XYZ MUSTERI")]

    assert len(cari["tedarikciler"]) == 1
    assert supplier["toplam_alis"] == 1675.00
    assert supplier["odenen"] == 340.00
    assert supplier["kalan_borc"] == 1335.00
    assert supplier["son_islem_tarihi"] == "2026-07-03"

    assert len(cari["musteriler"]) == 1
    assert customer["toplam_satis"] == 795.00
    assert customer["alinan"] == 170.00
    assert customer["kalan_borc"] == 625.00
    assert customer["son_islem_tarihi"] == "2026-07-03"

    assert supplier_person["toplam_alis"] == 1675.00
    assert supplier_person["odenen"] == 340.00
    assert supplier_person["alis_borcu"] == 1335.00
    assert supplier_person["toplam_satis"] == 0.00
    assert supplier_person["net_bakiye"] == -1335.00
    assert customer_person["toplam_alis"] == 0.00
    assert customer_person["toplam_satis"] == 795.00
    assert customer_person["alinan"] == 170.00
    assert customer_person["satis_borcu"] == 625.00
    assert customer_person["net_bakiye"] == 625.00

    ok(client.put(f"/api/satis/{satis_2['id']}", json={
        "tarih": "2026-07-02", "musteri": "XYZ MUSTERI", "purchase_id": alis_2["id"],
        "cinsi": "BILEZIK", "ayar": "22", "adet": 1, "gram": 1, "satis_milyem": 1000,
        "has_fiyati": 120, "iscilik": 10, "ek_ucret": 0, "indirim": 0, "alinan": 30,
    }))
    cari_after_edit = ok(client.get("/api/cari"))
    customer_after_edit = {main.normalize_text(row["musteri_adi"]): row for row in cari_after_edit["musteriler"]}[main.normalize_text("XYZ MUSTERI")]
    assert customer_after_edit["toplam_satis"] == 805.00
    assert customer_after_edit["alinan"] == 180.00
    assert customer_after_edit["kalan_borc"] == 625.00

    assert client.delete(f"/api/satis/{satis_1['id']}").status_code == 200
    cari_after_delete = ok(client.get("/api/cari"))
    customer_after_delete = {main.normalize_text(row["musteri_adi"]): row for row in cari_after_delete["musteriler"]}[main.normalize_text("XYZ MUSTERI")]
    assert customer_after_delete["toplam_satis"] == 280.00
    assert customer_after_delete["alinan"] == 80.00
    assert customer_after_delete["kalan_borc"] == 200.00
