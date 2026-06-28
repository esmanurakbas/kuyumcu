from __future__ import annotations

import sqlite3
import unicodedata
import secrets
import hashlib
import time
from contextlib import asynccontextmanager, contextmanager
from datetime import date, datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kuyumcu.db"
STATIC_DIR = BASE_DIR / "static"

ZERO = Decimal("0")
MONEY_Q = Decimal("0.01")
HAS_Q = Decimal("0.001")
NUM_Q = Decimal("0.001")

PRODUCTS = [
    "Çeyrek Altın",
    "Yarım Altın",
    "Tam Altın",
    "Gram Altın",
    "Bilezik",
    "Hurda Altın",
]


def ok(data: Any = None, message: str = "") -> dict[str, Any]:
    return {"status": "ok", "message": message, "data": data}


def fail(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"status": "error", "message": message, "data": None})


def clean_text(value: Any) -> str:
    return str(value or "").strip()


def normalize_text(value: Any) -> str:
    text = clean_text(value).casefold()
    text = text.translate(str.maketrans({"ı": "i", "İ": "i"}))
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize_product(value: Any) -> str:
    text = clean_text(value)
    key = normalize_text(text)
    for product in PRODUCTS:
        if normalize_text(product) == key:
            return product
    return text


def normalize_islem_turu(value: Any) -> str:
    key = normalize_text(value).replace(" ", "")
    if key in {"alis", "al"}:
        return "ALIS"
    if key in {"satis", "sat"}:
        return "SATIS"
    raise ValueError("İşlem türü ALIŞ veya SATIŞ olmalı.")


def display_islem_turu(value: Any) -> str:
    return "ALIŞ" if clean_text(value) == "ALIS" else "SATIŞ"


def d(value: Any) -> Decimal:
    if value is None or value == "":
        return ZERO
    if isinstance(value, Decimal):
        return value
    text = str(value).strip().replace(" ", "").replace(",", ".")
    try:
        return Decimal(text)
    except InvalidOperation as exc:
        raise ValueError(f"Geçersiz sayı: {value}") from exc


def non_negative(value: Any, field_name: str) -> Decimal:
    number = d(value)
    if number < 0:
        raise ValueError(f"{field_name} negatif olamaz.")
    return number


def q(value: Decimal, precision: Decimal) -> Decimal:
    return value.quantize(precision, rounding=ROUND_HALF_UP)


def as_float(value: Any, precision: Decimal = MONEY_Q) -> float:
    return float(q(d(value), precision))


def calc_has(adet: Any, gram: Any, milyem: Any) -> Decimal:
    return q(d(adet) * d(gram) * d(milyem) / Decimal("1000"), HAS_Q)


def purchase_total(row: sqlite3.Row) -> Decimal:
    return q(d(row["has"]) * d(row["has_fiyati"]), MONEY_Q)


def sale_total(row: sqlite3.Row | dict[str, Any]) -> Decimal:
    return q(d(row["has"]) * d(row["has_fiyati"]), MONEY_Q)


def scrap_total(row: sqlite3.Row | dict[str, Any]) -> Decimal:
    return q(d(row["has"]) * d(row["has_fiyati"]), MONEY_Q)


@contextmanager
def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("BEGIN")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def create_hurda_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE hurda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tarih TEXT NOT NULL,
            islem_turu TEXT NOT NULL CHECK(islem_turu IN ('ALIS', 'SATIS')),
            kisi TEXT NOT NULL,
            cinsi TEXT NOT NULL,
            ayar TEXT NOT NULL,
            adet REAL NOT NULL DEFAULT 0,
            gram REAL NOT NULL DEFAULT 0,
            milyem REAL NOT NULL DEFAULT 0,
            has REAL NOT NULL DEFAULT 0,
            has_fiyati REAL NOT NULL DEFAULT 0,
            iscilik REAL NOT NULL DEFAULT 0,
            toplam_tutar REAL NOT NULL DEFAULT 0,
            odenen_veya_alinan REAL NOT NULL DEFAULT 0,
            notlar TEXT NOT NULL DEFAULT ''
        )
        """
    )


def migrate_hurda_if_needed(conn: sqlite3.Connection) -> None:
    row = conn.execute("SELECT sql FROM sqlite_master WHERE type = 'table' AND name = 'hurda'").fetchone()
    if not row:
        create_hurda_table(conn)
        return
    if "CHECK(islem_turu IN ('ALIS', 'SATIS'))" in row["sql"]:
        return

    conn.execute("ALTER TABLE hurda RENAME TO hurda_old")
    create_hurda_table(conn)
    old_rows = conn.execute("SELECT * FROM hurda_old").fetchall()
    for old in old_rows:
        try:
            islem_turu = normalize_islem_turu(old["islem_turu"])
        except ValueError:
            islem_turu = "ALIS"
        conn.execute(
            """
            INSERT INTO hurda (id, tarih, islem_turu, kisi, cinsi, ayar, adet, gram, milyem,
                               has, has_fiyati, iscilik, toplam_tutar, odenen_veya_alinan, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                old["id"],
                old["tarih"],
                islem_turu,
                old["kisi"],
                normalize_product(old["cinsi"]),
                old["ayar"],
                old["adet"],
                old["gram"],
                old["milyem"],
                old["has"],
                old["has_fiyati"],
                old["iscilik"],
                old["toplam_tutar"],
                old["odenen_veya_alinan"],
                old["notlar"],
            ),
        )
    conn.execute("DROP TABLE hurda_old")


def init_db() -> None:
    with db() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS alis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT NOT NULL,
                tedarikci TEXT NOT NULL,
                cinsi TEXT NOT NULL,
                ayar TEXT NOT NULL,
                adet REAL NOT NULL DEFAULT 0,
                gram REAL NOT NULL DEFAULT 0,
                milyem REAL NOT NULL DEFAULT 0,
                has REAL NOT NULL DEFAULT 0,
                has_fiyati REAL NOT NULL DEFAULT 0,
                iscilik REAL NOT NULL DEFAULT 0,
                ek_masraf REAL NOT NULL DEFAULT 0,
                odenen REAL NOT NULL DEFAULT 0,
                notlar TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS satis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT NOT NULL,
                musteri TEXT NOT NULL,
                cinsi TEXT NOT NULL,
                ayar TEXT NOT NULL,
                adet REAL NOT NULL DEFAULT 0,
                gram REAL NOT NULL DEFAULT 0,
                milyem REAL NOT NULL DEFAULT 0,
                has REAL NOT NULL DEFAULT 0,
                has_fiyati REAL NOT NULL DEFAULT 0,
                iscilik REAL NOT NULL DEFAULT 0,
                ek_ucret REAL NOT NULL DEFAULT 0,
                indirim REAL NOT NULL DEFAULT 0,
                alinan REAL NOT NULL DEFAULT 0,
                notlar TEXT NOT NULL DEFAULT ''
            );
            """
        )
        migrate_hurda_if_needed(conn)


class BaseTransaction(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    tarih: str = Field(default_factory=lambda: date.today().isoformat())
    cinsi: str
    ayar: str
    adet: Any = ZERO
    gram: Any = ZERO
    milyem: Any = ZERO
    has_fiyati: Any = ZERO
    iscilik: Any = ZERO
    notlar: str = ""

    @field_validator("cinsi", "ayar")
    @classmethod
    def required_text(cls, value: str) -> str:
        value = clean_text(value)
        if not value:
            raise ValueError("Bu alan zorunlu.")
        return normalize_product(value)

    @model_validator(mode="after")
    def validate_numbers(self):
        for field_name in ["adet", "gram", "milyem", "has_fiyati", "iscilik"]:
            setattr(self, field_name, non_negative(getattr(self, field_name), field_name))
        return self


class AlisIn(BaseTransaction):
    tedarikci: str
    ek_masraf: Any = ZERO
    odenen: Any = ZERO

    @field_validator("tedarikci")
    @classmethod
    def required_supplier(cls, value: str) -> str:
        value = clean_text(value)
        if not value:
            raise ValueError("Tedarikçi zorunlu.")
        return value

    @model_validator(mode="after")
    def validate_alis_numbers(self):
        self.ek_masraf = non_negative(self.ek_masraf, "ek_masraf")
        self.odenen = non_negative(self.odenen, "odenen")
        return self


class SatisIn(BaseTransaction):
    musteri: str
    ek_ucret: Any = ZERO
    indirim: Any = ZERO
    alinan: Any = ZERO

    @field_validator("musteri")
    @classmethod
    def required_customer(cls, value: str) -> str:
        value = clean_text(value)
        if not value:
            raise ValueError("Müşteri zorunlu.")
        return value

    @model_validator(mode="after")
    def validate_satis_numbers(self):
        for field_name in ["ek_ucret", "indirim", "alinan"]:
            setattr(self, field_name, non_negative(getattr(self, field_name), field_name))
        return self


class HurdaIn(BaseTransaction):
    islem_turu: str
    kisi: str
    odenen_veya_alinan: Any = ZERO

    @field_validator("islem_turu")
    @classmethod
    def valid_type(cls, value: str) -> str:
        return normalize_islem_turu(value)

    @field_validator("kisi")
    @classmethod
    def required_person(cls, value: str) -> str:
        value = clean_text(value)
        if not value:
            raise ValueError("Kişi zorunlu.")
        return value

    @model_validator(mode="after")
    def validate_hurda_numbers(self):
        self.odenen_veya_alinan = non_negative(self.odenen_veya_alinan, "odenen_veya_alinan")
        return self


def row_dict(row: sqlite3.Row, total_name: str | None = None, total: Decimal | None = None) -> dict[str, Any]:
    data = dict(row)
    if "notlar" in data:
        data["not"] = data.pop("notlar")
    if data.get("islem_turu") in {"ALIS", "SATIS"}:
        data["islem_turu"] = display_islem_turu(data["islem_turu"])
    for key in ["adet", "gram", "milyem", "has"]:
        if key in data:
            data[key] = as_float(data[key], HAS_Q if key == "has" else NUM_Q)
    for key in ["has_fiyati", "iscilik", "ek_masraf", "odenen", "ek_ucret", "indirim", "alinan", "toplam_tutar", "odenen_veya_alinan"]:
        if key in data:
            data[key] = as_float(data[key], MONEY_Q)
    if total_name and total is not None:
        data[total_name] = as_float(total, MONEY_Q)
    return data


def fetch_all(conn: sqlite3.Connection, table: str) -> list[sqlite3.Row]:
    return conn.execute(f"SELECT * FROM {table} ORDER BY tarih DESC, id DESC").fetchall()


def stock_items(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    items: dict[tuple[str, str], dict[str, Any]] = {}

    def get(cinsi: str, ayar: str) -> dict[str, Any]:
        key = (normalize_text(cinsi), normalize_text(ayar))
        if key not in items:
            items[key] = {
                "cinsi": normalize_product(cinsi),
                "ayar": clean_text(ayar),
                "alis_has": ZERO,
                "satis_has": ZERO,
                "kalan_has": ZERO,
                "kalan_adet": ZERO,
                "kalan_gram": ZERO,
                "alis_maliyet": ZERO,
                "hurda_kalan_has": ZERO,
            }
        return items[key]

    for row in fetch_all(conn, "alis"):
        item = get(row["cinsi"], row["ayar"])
        item["alis_has"] += d(row["has"])
        item["kalan_has"] += d(row["has"])
        item["kalan_adet"] += d(row["adet"])
        item["kalan_gram"] += d(row["gram"])
        item["alis_maliyet"] += purchase_total(row)

    for row in fetch_all(conn, "satis"):
        item = get(row["cinsi"], row["ayar"])
        item["satis_has"] += d(row["has"])
        item["kalan_has"] -= d(row["has"])
        item["kalan_adet"] -= d(row["adet"])
        item["kalan_gram"] -= d(row["gram"])

    for row in fetch_all(conn, "hurda"):
        item = get(row["cinsi"], row["ayar"])
        sign = Decimal("1") if row["islem_turu"] == "ALIS" else Decimal("-1")
        item["kalan_has"] += sign * d(row["has"])
        item["kalan_adet"] += sign * d(row["adet"])
        item["kalan_gram"] += sign * d(row["gram"])
        item["hurda_kalan_has"] += sign * d(row["has"])
        if sign > 0:
            item["alis_has"] += d(row["has"])
            item["alis_maliyet"] += scrap_total(row)
        else:
            item["satis_has"] += d(row["has"])

    result = []
    for item in items.values():
        avg = item["alis_maliyet"] / item["alis_has"] if item["alis_has"] > 0 else ZERO
        result.append(
            {
                "cinsi": item["cinsi"],
                "ayar": item["ayar"],
                "alis_has": as_float(item["alis_has"], HAS_Q),
                "satis_has": as_float(item["satis_has"], HAS_Q),
                "kalan_has": as_float(item["kalan_has"], HAS_Q),
                "kalan_adet": as_float(item["kalan_adet"], NUM_Q),
                "kalan_gram": as_float(item["kalan_gram"], NUM_Q),
                "ortalama_has_maliyeti": as_float(avg, MONEY_Q),
                "stok_degeri": as_float(item["kalan_has"] * avg, MONEY_Q),
                "hurda_kalan_has": as_float(item["hurda_kalan_has"], HAS_Q),
                "uyari": "STOK YETERSİZ" if item["kalan_has"] < 0 else "",
            }
        )
    return sorted(result, key=lambda x: (normalize_text(x["cinsi"]), normalize_text(x["ayar"])))


def stock_lookup(conn: sqlite3.Connection) -> dict[tuple[str, str], dict[str, Any]]:
    return {(normalize_text(item["cinsi"]), normalize_text(item["ayar"])): item for item in stock_items(conn)}


def ensure_stock(conn: sqlite3.Connection, cinsi: str, ayar: str, needed_has: Decimal) -> None:
    key = (normalize_text(cinsi), normalize_text(ayar))
    stock = stock_lookup(conn).get(key)
    if not stock or d(stock["alis_has"]) <= 0:
        raise HTTPException(status_code=400, detail="ALIŞ YOK")
    if d(stock["kalan_has"]) < needed_has:
        raise HTTPException(status_code=400, detail="STOK YETERSİZ")


def cari_items(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    cariler: dict[tuple[str, str], dict[str, Any]] = {}

    def get_or_create(isim: str, tip: str) -> dict[str, Any]:
        key = (normalize_text(isim), tip)
        if key not in cariler:
            cariler[key] = {
                "isim": clean_text(isim),
                "tip": tip,
                "alis_has": ZERO,
                "satis_has": ZERO,
                "kalan_has": ZERO,
                "toplam_islem": ZERO,
                "toplam_odeme_alma": ZERO,
                "son_islem_tarihi": "",
            }
        return cariler[key]

    for row in fetch_all(conn, "alis"):
        cari = get_or_create(row["tedarikci"], "TEDARİKÇİ")
        cari["alis_has"] += d(row["has"])
        cari["kalan_has"] += d(row["has"])
        cari["toplam_islem"] += purchase_total(row)
        if row["tarih"] > cari["son_islem_tarihi"]:
            cari["son_islem_tarihi"] = row["tarih"]

    for row in fetch_all(conn, "satis"):
        cari = get_or_create(row["musteri"], "MÜŞTERİ")
        cari["satis_has"] += d(row["has"])
        cari["kalan_has"] -= d(row["has"])
        cari["toplam_odeme_alma"] += sale_total(row)
        if row["tarih"] > cari["son_islem_tarihi"]:
            cari["son_islem_tarihi"] = row["tarih"]

    for row in fetch_all(conn, "hurda"):
        tip = "TEDARİKÇİ" if row["islem_turu"] == "ALIS" else "MÜŞTERİ"
        cari = get_or_create(row["kisi"], tip)
        has_val = d(row["has"])
        if row["islem_turu"] == "ALIS":
            cari["alis_has"] += has_val
            cari["kalan_has"] += has_val
            cari["toplam_islem"] += scrap_total(row)
        else:
            cari["satis_has"] += has_val
            cari["kalan_has"] -= has_val
            cari["toplam_odeme_alma"] += scrap_total(row)
        if row["tarih"] > cari["son_islem_tarihi"]:
            cari["son_islem_tarihi"] = row["tarih"]

    result = []
    for cari in cariler.values():
        bakiye = cari["toplam_islem"] - cari["toplam_odeme_alma"]
        result.append(
            {
                "isim": cari["isim"],
                "tip": cari["tip"],
                "alis_has": as_float(cari["alis_has"], HAS_Q),
                "satis_has": as_float(cari["satis_has"], HAS_Q),
                "kalan_has": as_float(cari["kalan_has"], HAS_Q),
                "toplam_islem": as_float(cari["toplam_islem"], MONEY_Q),
                "toplam_odeme_alma": as_float(cari["toplam_odeme_alma"], MONEY_Q),
                "bakiye": as_float(bakiye, MONEY_Q),
                "son_islem_tarihi": cari["son_islem_tarihi"],
            }
        )
    return sorted(result, key=lambda x: (normalize_text(x["isim"]), x["tip"]))


def sale_profit(conn: sqlite3.Connection, row: sqlite3.Row) -> Decimal:
    key = (normalize_text(row["cinsi"]), normalize_text(row["ayar"]))
    stock = stock_lookup(conn).get(key)
    if not stock or d(stock["alis_has"]) <= 0:
        return ZERO
    avg = d(stock["ortalama_has_maliyeti"])
    return q(sale_total(row) - d(row["has"]) * avg, MONEY_Q)


def suggestions(conn: sqlite3.Connection) -> dict[str, list[str]]:
    products = set(PRODUCTS)
    customers: set[str] = set()
    suppliers: set[str] = set()
    people: set[str] = set()
    for row in conn.execute("SELECT cinsi, tedarikci FROM alis").fetchall():
        products.add(normalize_product(row["cinsi"]))
        suppliers.add(row["tedarikci"])
        people.add(row["tedarikci"])
    for row in conn.execute("SELECT cinsi, musteri FROM satis").fetchall():
        products.add(normalize_product(row["cinsi"]))
        customers.add(row["musteri"])
        people.add(row["musteri"])
    for row in conn.execute("SELECT cinsi, kisi, islem_turu FROM hurda").fetchall():
        products.add(normalize_product(row["cinsi"]))
        people.add(row["kisi"])
        if row["islem_turu"] == "ALIS":
            suppliers.add(row["kisi"])
        else:
            customers.add(row["kisi"])

    def sorted_values(values: set[str]) -> list[str]:
        return sorted((clean_text(v) for v in values if clean_text(v)), key=normalize_text)

    return {
        "products": sorted_values(products),
        "customers": sorted_values(customers),
        "suppliers": sorted_values(suppliers),
        "people": sorted_values(people),
    }


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Kuyumcu Stok Cari Satış", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_: Request, exc: HTTPException):
    return fail(str(exc.detail), exc.status_code)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError):
    first = exc.errors()[0] if exc.errors() else {}
    message = first.get("msg", "Veri doğrulanamadı.")
    return fail(str(message).replace("Value error, ", ""), 422)


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/suggestions")
def get_suggestions() -> dict[str, Any]:
    with db() as conn:
        return ok(suggestions(conn))


@app.get("/api/alis")
def list_alis() -> dict[str, Any]:
    with db() as conn:
        return ok([row_dict(row, "toplam_tutar", purchase_total(row)) for row in fetch_all(conn, "alis")])


@app.post("/api/alis")
def create_alis(payload: AlisIn) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    with db() as conn:
        cur = conn.execute(
            """
            INSERT INTO alis (tarih, tedarikci, cinsi, ayar, adet, gram, milyem, has,
                              has_fiyati, iscilik, ek_masraf, odenen, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.tarih,
                payload.tedarikci,
                payload.cinsi,
                payload.ayar,
                float(payload.adet),
                float(payload.gram),
                float(payload.milyem),
                float(has),
                float(payload.has_fiyati),
                float(payload.iscilik),
                float(payload.ek_masraf),
                float(payload.odenen),
                payload.notlar,
            ),
        )
        row = conn.execute("SELECT * FROM alis WHERE id = ?", (cur.lastrowid,)).fetchone()
        return ok(row_dict(row, "toplam_tutar", purchase_total(row)), "Alış kaydedildi.")


@app.get("/api/satis")
def list_satis() -> dict[str, Any]:
    with db() as conn:
        rows = []
        for row in fetch_all(conn, "satis"):
            item = row_dict(row, "toplam_tutar", sale_total(row))
            item["kar"] = as_float(sale_profit(conn, row), MONEY_Q)
            item["uyari"] = ""
            rows.append(item)
        return ok(rows)


@app.post("/api/satis")
def create_satis(payload: SatisIn) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    with db() as conn:
        ensure_stock(conn, payload.cinsi, payload.ayar, has)
        cur = conn.execute(
            """
            INSERT INTO satis (tarih, musteri, cinsi, ayar, adet, gram, milyem, has,
                               has_fiyati, iscilik, ek_ucret, indirim, alinan, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.tarih,
                payload.musteri,
                payload.cinsi,
                payload.ayar,
                float(payload.adet),
                float(payload.gram),
                float(payload.milyem),
                float(has),
                float(payload.has_fiyati),
                float(payload.iscilik),
                float(payload.ek_ucret),
                float(payload.indirim),
                float(payload.alinan),
                payload.notlar,
            ),
        )
        row = conn.execute("SELECT * FROM satis WHERE id = ?", (cur.lastrowid,)).fetchone()
        item = row_dict(row, "toplam_tutar", sale_total(row))
        item["kar"] = as_float(sale_profit(conn, row), MONEY_Q)
        item["uyari"] = ""
        return ok(item, "Satış kaydedildi.")


@app.get("/api/hurda")
def list_hurda() -> dict[str, Any]:
    with db() as conn:
        return ok([row_dict(row) for row in fetch_all(conn, "hurda")])


@app.post("/api/hurda")
def create_hurda(payload: HurdaIn) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    total = q(has * payload.has_fiyati + payload.iscilik, MONEY_Q)
    with db() as conn:
        if payload.islem_turu == "SATIS":
            ensure_stock(conn, payload.cinsi, payload.ayar, has)
        cur = conn.execute(
            """
            INSERT INTO hurda (tarih, islem_turu, kisi, cinsi, ayar, adet, gram, milyem,
                               has, has_fiyati, iscilik, toplam_tutar, odenen_veya_alinan, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.tarih,
                payload.islem_turu,
                payload.kisi,
                payload.cinsi,
                payload.ayar,
                float(payload.adet),
                float(payload.gram),
                float(payload.milyem),
                float(has),
                float(payload.has_fiyati),
                float(payload.iscilik),
                float(total),
                float(payload.odenen_veya_alinan),
                payload.notlar,
            ),
        )
        row = conn.execute("SELECT * FROM hurda WHERE id = ?", (cur.lastrowid,)).fetchone()
        return ok(row_dict(row), "Hurda kaydedildi.")


@app.get("/api/stok")
def list_stock() -> dict[str, Any]:
    with db() as conn:
        return ok(stock_items(conn))


@app.get("/api/cari")
def list_cari() -> dict[str, Any]:
    with db() as conn:
        return ok(cari_items(conn))


@app.get("/api/dashboard")
def dashboard() -> dict[str, Any]:
    with db() as conn:
        alis_rows = fetch_all(conn, "alis")
        satis_rows = fetch_all(conn, "satis")
        hurda_rows = fetch_all(conn, "hurda")
        stocks = stock_items(conn)
        cariler = cari_items(conn)
        today_text = date.today().isoformat()

        total_profit = sum((sale_profit(conn, row) for row in satis_rows), ZERO)
        daily_sales = sum((sale_total(row) for row in satis_rows if row["tarih"] == today_text), ZERO)
        warning_count = sum(1 for item in stocks if item["uyari"])
        total_customer_debt = sum((d(c["bakiye"]) for c in cariler if c["tip"] == "MÜŞTERİ"), ZERO)
        total_supplier_debt = sum((d(c["bakiye"]) for c in cariler if c["tip"] == "TEDARİKÇİ"), ZERO)

        return ok(
            {
                "toplam_alis": as_float(sum((purchase_total(r) for r in alis_rows), ZERO), MONEY_Q),
                "toplam_satis": as_float(sum((sale_total(r) for r in satis_rows), ZERO), MONEY_Q),
                "gunluk_satis": as_float(daily_sales, MONEY_Q),
                "toplam_kar": as_float(total_profit, MONEY_Q),
                "toplam_cari": as_float(total_customer_debt + total_supplier_debt, MONEY_Q),
                "toplam_musteri_borcu": as_float(total_customer_debt, MONEY_Q),
                "toplam_tedarikci_borcu": as_float(total_supplier_debt, MONEY_Q),
                "toplam_stok_has": as_float(sum((d(s["kalan_has"]) for s in stocks), ZERO), HAS_Q),
                "stok_degeri": as_float(sum((d(s["stok_degeri"]) for s in stocks), ZERO), MONEY_Q),
                "hurda_kalan_has": as_float(sum((d(s["hurda_kalan_has"]) for s in stocks), ZERO), HAS_Q),
                "uyari_sayisi": warning_count,
                "alis_adedi": len(alis_rows),
                "satis_adedi": len(satis_rows),
                "hurda_adedi": len(hurda_rows),
            }
        )


@app.put("/api/alis/{item_id}")
def update_alis(item_id: int, payload: AlisIn) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    with db() as conn:
        cur = conn.execute(
            """
            UPDATE alis 
            SET tarih = ?, tedarikci = ?, cinsi = ?, ayar = ?, adet = ?, gram = ?, 
                milyem = ?, has = ?, has_fiyati = ?, iscilik = ?, ek_masraf = ?, 
                odenen = ?, notlar = ?
            WHERE id = ?
            """,
            (
                payload.tarih,
                payload.tedarikci,
                payload.cinsi,
                payload.ayar,
                float(payload.adet),
                float(payload.gram),
                float(payload.milyem),
                float(has),
                float(payload.has_fiyati),
                float(payload.iscilik),
                float(payload.ek_masraf),
                float(payload.odenen),
                payload.notlar,
                item_id,
            ),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Kayıt bulunamadı.")
        row = conn.execute("SELECT * FROM alis WHERE id = ?", (item_id,)).fetchone()
        return ok(row_dict(row, "toplam_tutar", purchase_total(row)), "Alış güncellendi.")


@app.put("/api/satis/{item_id}")
def update_satis(item_id: int, payload: SatisIn) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    with db() as conn:
        ensure_stock(conn, payload.cinsi, payload.ayar, has)
        cur = conn.execute(
            """
            UPDATE satis 
            SET tarih = ?, musteri = ?, cinsi = ?, ayar = ?, adet = ?, gram = ?, 
                milyem = ?, has = ?, has_fiyati = ?, iscilik = ?, ek_ucret = ?, 
                indirim = ?, alinan = ?, notlar = ?
            WHERE id = ?
            """,
            (
                payload.tarih,
                payload.musteri,
                payload.cinsi,
                payload.ayar,
                float(payload.adet),
                float(payload.gram),
                float(payload.milyem),
                float(has),
                float(payload.has_fiyati),
                float(payload.iscilik),
                float(payload.ek_ucret),
                float(payload.indirim),
                float(payload.alinan),
                payload.notlar,
                item_id,
            ),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Kayıt bulunamadı.")
        row = conn.execute("SELECT * FROM satis WHERE id = ?", (item_id,)).fetchone()
        item = row_dict(row, "toplam_tutar", sale_total(row))
        item["kar"] = as_float(sale_profit(conn, row), MONEY_Q)
        return ok(item, "Satış güncellendi.")


@app.put("/api/hurda/{item_id}")
def update_hurda(item_id: int, payload: HurdaIn) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    with db() as conn:
        cur = conn.execute(
            """
            UPDATE hurda 
            SET tarih = ?, islem_turu = ?, kisi = ?, cinsi = ?, ayar = ?, adet = ?, 
                gram = ?, milyem = ?, has = ?, has_fiyati = ?, iscilik = ?, 
                odenen_veya_alinan = ?, notlar = ?
            WHERE id = ?
            """,
            (
                payload.tarih,
                payload.islem_turu,
                payload.kisi,
                payload.cinsi,
                payload.ayar,
                float(payload.adet),
                float(payload.gram),
                float(payload.milyem),
                float(has),
                float(payload.has_fiyati),
                float(payload.iscilik),
                float(payload.odenen_veya_alinan),
                payload.notlar,
                item_id,
            ),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Kayıt bulunamadı.")
        row = conn.execute("SELECT * FROM hurda WHERE id = ?", (item_id,)).fetchone()
        return ok(row_dict(row, "toplam_tutar", scrap_total(row)), "Hurda güncellendi.")


@app.delete("/api/{table}/{item_id}")
def delete_item(table: str, item_id: int) -> dict[str, Any]:
    if table not in {"alis", "satis", "hurda"}:
        raise HTTPException(status_code=404, detail="Tablo bulunamadı.")
    with db() as conn:
        cur = conn.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Kayıt bulunamadı.")
        return ok({"deleted": True}, "Kayıt silindi.")
