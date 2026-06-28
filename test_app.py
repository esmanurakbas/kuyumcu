from fastapi.testclient import TestClient

import main


def make_client(tmp_path, monkeypatch):
    monkeypatch.setattr(main, "DB_PATH", tmp_path / "test.db")
    main.init_db()
    return TestClient(main.app)


def data(response):
    body = response.json()
    assert body["status"] == "ok"
    return body["data"]


def test_excel_like_flow(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    alis = {
        "tarih": "2026-06-28",
        "tedarikci": "Ali Usta",
        "cinsi": "Bilezik",
        "ayar": "22",
        "adet": "2",
        "gram": "10,5",
        "milyem": "916",
        "has_fiyati": "3000",
        "iscilik": "100",
        "ek_masraf": "50",
        "odenen": "1000",
    }
    response = client.post("/api/alis", json=alis)
    assert response.status_code == 200
    assert data(response)["has"] == 19.236

    satis = {
        "tarih": "2026-06-28",
        "musteri": "Veli Bey",
        "cinsi": "Bilezik",
        "ayar": "22",
        "adet": "1",
        "gram": "5",
        "milyem": "916",
        "has_fiyati": "3300",
        "iscilik": "80",
        "ek_ucret": "20",
        "indirim": "10",
        "alinan": "5000",
    }
    response = client.post("/api/satis", json=satis)
    assert response.status_code == 200
    assert data(response)["has"] == 4.58

    stock = data(client.get("/api/stok"))[0]
    assert stock["kalan_has"] == 14.656
    assert stock["kalan_adet"] == 1

    cari = data(client.get("/api/cari"))
    supplier = next(item for item in cari if item["isim"] == "Ali Usta")
    customer = next(item for item in cari if item["isim"] == "Veli Bey")
    assert supplier["bakiye"] == 56858.0
    assert customer["bakiye"] == 10204.0

    fazla = dict(satis, adet="20", gram="100")
    response = client.post("/api/satis", json=fazla)
    assert response.status_code == 400
    assert response.json()["message"] == "STOK YETERSİZ"

    hurda = {
        "tarih": "2026-06-28",
        "islem_turu": "ALIŞ",
        "kisi": "Hurda Hasan",
        "cinsi": "Bilezik",
        "ayar": "22",
        "adet": "1",
        "gram": "2",
        "milyem": "916",
        "has_fiyati": "2900",
        "iscilik": "0",
        "odenen_veya_alinan": "1000",
    }
    response = client.post("/api/hurda", json=hurda)
    assert response.status_code == 200
    assert data(response)["toplam_tutar"] == 5312.8

    dashboard = data(client.get("/api/dashboard"))
    assert dashboard["hurda_adedi"] == 1
    assert dashboard["uyari_sayisi"] == 0


def test_turkish_and_accentless_product_names_merge(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    first = {
        "tarih": "2026-06-28",
        "tedarikci": "Çağrı Kuyumcu",
        "cinsi": "çeyrek altın",
        "ayar": "22",
        "adet": "1",
        "gram": "1,75",
        "milyem": "916",
        "has_fiyati": "3000",
    }
    second = dict(first, cinsi="ceyrek altin", gram="1.75")
    assert client.post("/api/alis", json=first).status_code == 200
    assert client.post("/api/alis", json=second).status_code == 200

    stock = data(client.get("/api/stok"))
    assert len(stock) == 1
    assert stock[0]["cinsi"] == "Çeyrek Altın"
    assert stock[0]["kalan_has"] == 3.206

    cari = data(client.get("/api/cari"))
    assert len(cari) == 1
    assert cari[0]["isim"] == "Çağrı Kuyumcu"


def test_suggestions_include_products_and_existing_people(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    client.post(
        "/api/alis",
        json={
            "tarih": "2026-06-28",
            "tedarikci": "Mehmet Usta",
            "cinsi": "Gram Altın",
            "ayar": "24",
            "adet": "1",
            "gram": "1",
            "milyem": "995",
            "has_fiyati": "3200",
        },
    )

    suggestions = data(client.get("/api/suggestions"))
    assert "Çeyrek Altın" in suggestions["products"]
    assert "Gram Altın" in suggestions["products"]
    assert "Mehmet Usta" in suggestions["suppliers"]
    assert "Mehmet Usta" in suggestions["people"]


def test_stock_cannot_go_negative(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)

    response = client.post(
        "/api/satis",
        json={
            "tarih": "2026-06-28",
            "musteri": "Ayşe Hanım",
            "cinsi": "Tam Altın",
            "ayar": "22",
            "adet": "1",
            "gram": "7",
            "milyem": "916",
            "has_fiyati": "3000",
        },
    )
    assert response.status_code == 400
    assert response.json()["message"] == "ALIŞ YOK"
    assert data(client.get("/api/satis")) == []
    assert data(client.get("/api/stok")) == []


def test_invalid_and_negative_numbers_are_rejected(tmp_path, monkeypatch):
    client = make_client(tmp_path, monkeypatch)
    payload = {
        "tarih": "2026-06-28",
        "tedarikci": "Test",
        "cinsi": "Bilezik",
        "ayar": "22",
        "adet": "-1",
        "gram": "abc",
        "milyem": "916",
        "has_fiyati": "3000",
    }
    response = client.post("/api/alis", json=payload)
    assert response.status_code == 422
    assert response.json()["status"] == "error"
