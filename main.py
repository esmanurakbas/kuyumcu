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
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "kuyumcu.db"
STATIC_DIR = BASE_DIR / "static"

ZERO = Decimal("0")
MONEY_Q = Decimal("0.01")
HAS_Q = Decimal("0.001")
NUM_Q = Decimal("0.001")
PASSWORD_HASH = hashlib.sha256("2526E".encode("utf-8")).hexdigest()
SESSION_TIMEOUT = 60 * 60 * 8
sessions: dict[str, dict[str, Any]] = {}
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 5 * 60
login_attempts: dict[str, list[float]] = {}

PRODUCTS = [
    "B\u0130LEZ\u0130K",
    "Y\u00dcZ\u00dcK",
    "KOLYE",
    "K\u00dcPE",
    "SET",
    "\u00c7EYREK",
    "YARIM",
    "TAM",
    "GRAM ALTIN",
    "D\u0130\u011eER",
]


def ok(data: Any = None, message: str = "") -> dict[str, Any]:
    return {"status": "ok", "message": message, "data": data}


def fail(message: str, status_code: int = 400) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"status": "error", "message": message, "data": None})




def failed_attempts(ip: str) -> list[float]:
    now = time.time()
    attempts = [item for item in login_attempts.get(ip, []) if now - item < LOCKOUT_SECONDS]
    login_attempts[ip] = attempts
    return attempts


def is_login_locked(ip: str) -> bool:
    return len(failed_attempts(ip)) >= MAX_LOGIN_ATTEMPTS


def lock_remaining_seconds(ip: str) -> int:
    attempts = failed_attempts(ip)
    if len(attempts) < MAX_LOGIN_ATTEMPTS:
        return 0
    return max(1, int(LOCKOUT_SECONDS - (time.time() - attempts[0])))


def record_failed_login(ip: str) -> None:
    attempts = failed_attempts(ip)
    attempts.append(time.time())
    login_attempts[ip] = attempts


def clear_failed_logins(ip: str) -> None:
    login_attempts.pop(ip, None)

def client_ip(request: Request) -> str:
    return request.client.host if request.client else "local"


def cleanup_sessions() -> None:
    now = time.time()
    for token, session in list(sessions.items()):
        if now - session["last"] > SESSION_TIMEOUT:
            sessions.pop(token, None)


def require_auth(request: Request) -> None:
    cleanup_sessions()
    token = request.cookies.get("session_token")
    session = sessions.get(token or "")
    if not session or session.get("ip") != client_ip(request):
        raise HTTPException(status_code=401, detail="Oturum yok. Lütfen giriş yapın.")
    session["last"] = time.time()

def clean_text(value: Any) -> str:
    return str(value or "").strip()


def normalize_text(value: Any) -> str:
    text = clean_text(value).casefold()
    text = text.translate(str.maketrans({"\u0131": "i", "\u0130": "i"}))
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in decomposed if not unicodedata.combining(ch))


def normalize_product(value: Any) -> str:
    text = clean_text(value)
    key = normalize_text(text)
    for product in PRODUCTS:
        if normalize_text(product) == key:
            return product
    return text


def is_hurda_product(value: Any) -> bool:
    return "hurda" in normalize_text(value)


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


def purchase_total(row: sqlite3.Row | dict[str, Any]) -> Decimal:
    return q(d(row["has"]) * d(row["has_fiyati"]) + d(row["iscilik"]) + d(row["ek_masraf"]), MONEY_Q)


def sale_total(row: sqlite3.Row | dict[str, Any]) -> Decimal:
    return q(d(row["has"]) * d(row["has_fiyati"]) + d(row["iscilik"]) + d(row["ek_ucret"]) - d(row["indirim"]), MONEY_Q)


def scrap_total(row: sqlite3.Row | dict[str, Any]) -> Decimal:
    return q(d(row["has"]) * d(row["has_fiyati"]) + d(row["iscilik"]), MONEY_Q)


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



def columns(conn: sqlite3.Connection, table: str) -> set[str]:
    return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}


def add_column(conn: sqlite3.Connection, table: str, definition: str) -> None:
    name = definition.split()[0]
    if name not in columns(conn, table):
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {definition}")

def create_hurda_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE hurda (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hurda_alis_id INTEGER,
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



def migrate_satis_if_needed(conn: sqlite3.Connection) -> None:
    add_column(conn, "satis", "alis_id INTEGER")
    add_column(conn, "satis", "purchase_id INTEGER")


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
                notlar TEXT NOT NULL DEFAULT '',
                purchase_id INTEGER
            );
            """
        )
        migrate_hurda_if_needed(conn)
        migrate_satis_if_needed(conn)
        add_column(conn, "hurda", "hurda_alis_id INTEGER")


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
    def required_text(cls, value: str, info) -> str:
        value = clean_text(value)
        if not value:
            raise ValueError("Bu alan zorunlu.")
        return normalize_product(value) if info.field_name == "cinsi" else value

    @model_validator(mode="after")
    def validate_numbers(self):
        for field_name in ["adet", "gram", "milyem", "has_fiyati", "iscilik"]:
            setattr(self, field_name, non_negative(getattr(self, field_name), field_name))
        self.cinsi = normalize_product(self.cinsi)
        self.ayar = clean_text(self.ayar)
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
        if is_hurda_product(self.cinsi):
            raise ValueError("Hurda ALIS sayfasina girilemez. HURDA sayfasini kullanin.")
        self.ek_masraf = non_negative(self.ek_masraf, "ek_masraf")
        self.odenen = non_negative(self.odenen, "odenen")
        return self


class SatisIn(BaseTransaction):
    musteri: str
    satis_milyem: Any | None = None
    ek_ucret: Any = ZERO
    indirim: Any = ZERO
    alinan: Any = ZERO
    alis_id: int | None = None
    purchase_id: int | None = None

    @field_validator("musteri")
    @classmethod
    def required_customer(cls, value: str) -> str:
        value = clean_text(value)
        if not value:
            raise ValueError("Müşteri zorunlu.")
        return value

    @model_validator(mode="after")
    def validate_satis_numbers(self):
        if self.satis_milyem is not None and clean_text(self.satis_milyem) != "":
            self.milyem = self.satis_milyem
        for field_name in ["ek_ucret", "indirim", "alinan"]:
            setattr(self, field_name, non_negative(getattr(self, field_name), field_name))
        self.alis_id = self.alis_id or self.purchase_id
        if not self.alis_id:
            raise ValueError("Satış için alıştan ürün seçilmeli.")
        return self


class HurdaIn(BaseTransaction):
    islem_turu: str
    kisi: str
    hurda_alis_id: int | None = None
    odenen_veya_alinan: Any = ZERO

    
    @field_validator("hurda_alis_id", mode="before")
    @classmethod
    def empty_hurda_purchase_id(cls, value: Any) -> int | None:
        if value is None or clean_text(value) == "":
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            raise ValueError("Hurda alis secimi gecersiz.")

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


def sale_purchase_id(row: sqlite3.Row | dict[str, Any]) -> int | None:
    keys = row.keys() if hasattr(row, "keys") else row.keys()
    if "purchase_id" in keys and row["purchase_id"]:
        return int(row["purchase_id"])
    if "alis_id" in keys and row["alis_id"]:
        return int(row["alis_id"])
    return None


def purchase_remaining(conn: sqlite3.Connection, alis: sqlite3.Row, exclude_sale_id: int | None = None) -> dict[str, Decimal]:
    params: list[Any] = [alis["id"]]
    extra = ""
    if exclude_sale_id:
        extra = " AND id != ?"
        params.append(exclude_sale_id)
    sold = conn.execute(
        f"SELECT COALESCE(SUM(adet),0) adet, COALESCE(SUM(adet * gram),0) gram, COALESCE(SUM(has),0) has FROM satis WHERE COALESCE(purchase_id, alis_id) = ?{extra}",
        params,
    ).fetchone()
    return {
        "kalan_adet": d(alis["adet"]) - d(sold["adet"]),
        "kalan_gram": d(alis["adet"]) * d(alis["gram"]) - d(sold["gram"]),
        "kalan_has": d(alis["has"]) - d(sold["has"]),
    }


def row_total_gram(row: sqlite3.Row | dict[str, Any]) -> Decimal:
    return d(row["adet"]) * d(row["gram"])


def stock_items(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    items: dict[tuple[str, str], dict[str, Any]] = {}

    def get(cinsi: str, ayar: str) -> dict[str, Any]:
        key = (normalize_text(cinsi), normalize_text(ayar))
        if key not in items:
            items[key] = {
                "cinsi": normalize_product(cinsi),
                "ayar": clean_text(ayar),
                "alis_adet": ZERO,
                "alis_gram": ZERO,
                "alis_has": ZERO,
                "alis_maliyet": ZERO,
                "satis_adet": ZERO,
                "satis_gram": ZERO,
                "satis_has": ZERO,
            }
        return items[key]

    for row in fetch_all(conn, "alis"):
        if is_hurda_product(row["cinsi"]):
            continue
        item = get(row["cinsi"], row["ayar"])
        item["alis_adet"] += d(row["adet"])
        item["alis_gram"] += row_total_gram(row)
        item["alis_has"] += d(row["has"])
        item["alis_maliyet"] += purchase_total(row)

    for row in fetch_all(conn, "satis"):
        if is_hurda_product(row["cinsi"]):
            continue
        item = get(row["cinsi"], row["ayar"])
        item["satis_adet"] += d(row["adet"])
        item["satis_gram"] += row_total_gram(row)
        item["satis_has"] += d(row["has"])

    result = []
    for item in items.values():
        kalan_adet = item["alis_adet"] - item["satis_adet"]
        kalan_gram = item["alis_gram"] - item["satis_gram"]
        kalan_has = item["alis_has"] - item["satis_has"]
        avg = item["alis_maliyet"] / item["alis_has"] if item["alis_has"] > 0 else ZERO
        result.append(
            {
                "cinsi": item["cinsi"],
                "ayar": item["ayar"],
                "alis_adet": as_float(item["alis_adet"], NUM_Q),
                "alis_gram": as_float(item["alis_gram"], NUM_Q),
                "alis_has": as_float(item["alis_has"], HAS_Q),
                "satis_adet": as_float(item["satis_adet"], NUM_Q),
                "satis_gram": as_float(item["satis_gram"], NUM_Q),
                "satis_has": as_float(item["satis_has"], HAS_Q),
                "kalan_adet": as_float(kalan_adet, NUM_Q),
                "kalan_gram": as_float(kalan_gram, NUM_Q),
                "kalan_has": as_float(kalan_has, HAS_Q),
                "ortalama_has_maliyeti": as_float(avg, MONEY_Q),
                "stok_degeri": as_float(kalan_has * avg, MONEY_Q),
                "uyari": "SATI\u015e HASI ALI\u015eTAN Y\u00dcKSEK" if kalan_has < 0 else ("STOK YETERS\u0130Z" if kalan_adet < 0 or kalan_gram < 0 else ""),
            }
        )
    return sorted(result, key=lambda x: (normalize_text(x["cinsi"]), normalize_text(x["ayar"])))


def stock_lookup(conn: sqlite3.Connection) -> dict[tuple[str, str], dict[str, Any]]:
    return {(normalize_text(item["cinsi"]), normalize_text(item["ayar"])): item for item in stock_items(conn)}


def hurda_purchase_remaining(conn: sqlite3.Connection, hurda_alis: sqlite3.Row, exclude_id: int | None = None) -> dict[str, Decimal]:
    params: list[Any] = [hurda_alis["id"]]
    extra = ""
    if exclude_id:
        extra = " AND id != ?"
        params.append(exclude_id)
    sold = conn.execute(
        f"SELECT COALESCE(SUM(adet),0) adet, COALESCE(SUM(adet * gram),0) gram, COALESCE(SUM(has),0) has FROM hurda WHERE islem_turu = 'SATIS' AND hurda_alis_id = ?{extra}",
        params,
    ).fetchone()
    return {
        "kalan_adet": d(hurda_alis["adet"]) - d(sold["adet"]),
        "kalan_gram": row_total_gram(hurda_alis) - d(sold["gram"]),
        "kalan_has": d(hurda_alis["has"]) - d(sold["has"]),
    }


def hurda_stock_items(conn: sqlite3.Connection) -> list[dict[str, Any]]:
    items: dict[tuple[str, str], dict[str, Any]] = {}

    def get(cinsi: str, ayar: str) -> dict[str, Any]:
        key = (normalize_text(cinsi), normalize_text(ayar))
        if key not in items:
            items[key] = {
                "cinsi": normalize_product(cinsi),
                "ayar": clean_text(ayar),
                "hurda_alis_adet": ZERO,
                "hurda_alis_gram": ZERO,
                "hurda_alis_has": ZERO,
                "hurda_alis_tutari": ZERO,
                "hurda_satis_adet": ZERO,
                "hurda_satis_gram": ZERO,
                "hurda_satis_has": ZERO,
                "hurda_satis_tutari": ZERO,
            }
        return items[key]

    for row in fetch_all(conn, "hurda"):
        item = get(row["cinsi"], row["ayar"])
        if row["islem_turu"] == "ALIS":
            item["hurda_alis_adet"] += d(row["adet"])
            item["hurda_alis_gram"] += row_total_gram(row)
            item["hurda_alis_has"] += d(row["has"])
            item["hurda_alis_tutari"] += scrap_total(row)
        else:
            item["hurda_satis_adet"] += d(row["adet"])
            item["hurda_satis_gram"] += row_total_gram(row)
            item["hurda_satis_has"] += d(row["has"])
            item["hurda_satis_tutari"] += scrap_total(row)

    result = []
    for item in items.values():
        kalan_adet = item["hurda_alis_adet"] - item["hurda_satis_adet"]
        kalan_gram = item["hurda_alis_gram"] - item["hurda_satis_gram"]
        kalan_has = item["hurda_alis_has"] - item["hurda_satis_has"]
        avg = item["hurda_alis_tutari"] / item["hurda_alis_has"] if item["hurda_alis_has"] > 0 else ZERO
        result.append(
            {
                "cinsi": item["cinsi"],
                "ayar": item["ayar"],
                "hurda_alis_adet": as_float(item["hurda_alis_adet"], NUM_Q),
                "hurda_alis_gram": as_float(item["hurda_alis_gram"], NUM_Q),
                "hurda_alis_has": as_float(item["hurda_alis_has"], HAS_Q),
                "hurda_alis_tutari": as_float(item["hurda_alis_tutari"], MONEY_Q),
                "hurda_satis_adet": as_float(item["hurda_satis_adet"], NUM_Q),
                "hurda_satis_gram": as_float(item["hurda_satis_gram"], NUM_Q),
                "hurda_satis_has": as_float(item["hurda_satis_has"], HAS_Q),
                "hurda_satis_tutari": as_float(item["hurda_satis_tutari"], MONEY_Q),
                "kalan_adet": as_float(kalan_adet, NUM_Q),
                "kalan_gram": as_float(kalan_gram, NUM_Q),
                "kalan_has": as_float(kalan_has, HAS_Q),
                "ortalama_has_maliyeti": as_float(avg, MONEY_Q),
                "stok_degeri": as_float(kalan_has * avg, MONEY_Q),
                "uyari": "SATI\u015e HASI ALI\u015eTAN Y\u00dcKSEK" if kalan_has < 0 else ("STOK YETERS\u0130Z" if kalan_adet < 0 or kalan_gram < 0 else ""),
            }
        )
    return sorted(result, key=lambda x: (normalize_text(x["cinsi"]), normalize_text(x["ayar"])))


def hurda_stock_lookup(conn: sqlite3.Connection) -> dict[tuple[str, str], dict[str, Any]]:
    return {(normalize_text(item["cinsi"]), normalize_text(item["ayar"])): item for item in hurda_stock_items(conn)}

def ensure_stock(conn: sqlite3.Connection, cinsi: str, ayar: str, needed_has: Decimal) -> None:
    key = (normalize_text(cinsi), normalize_text(ayar))
    stock = stock_lookup(conn).get(key)
    if not stock or d(stock["alis_has"]) <= 0:
        raise HTTPException(status_code=400, detail="ALIŞ YOK")
    if d(stock["kalan_has"]) < needed_has:
        raise HTTPException(status_code=400, detail="STOK YETERSİZ")



def ensure_sale_stock(conn: sqlite3.Connection, payload: SatisIn, sale_has: Decimal, exclude_sale_id: int | None = None) -> sqlite3.Row:
    alis = conn.execute("SELECT * FROM alis WHERE id = ?", (payload.alis_id,)).fetchone()
    if not alis:
        raise HTTPException(status_code=400, detail="ALIŞ KAYDI BULUNAMADI")
    if normalize_text(alis["cinsi"]) != normalize_text(payload.cinsi) or normalize_text(alis["ayar"]) != normalize_text(payload.ayar):
        raise HTTPException(status_code=400, detail="Seçilen alış ile satış ürünü uyuşmuyor.")
    rem = purchase_remaining(conn, alis, exclude_sale_id)
    sale_gram = d(payload.adet) * d(payload.gram)
    if d(payload.adet) > rem["kalan_adet"] or sale_gram > rem["kalan_gram"]:
        raise HTTPException(status_code=400, detail="STOK YETERS\u0130Z")
    return alis

def ensure_hurda_stock(conn: sqlite3.Connection, payload: HurdaIn, has: Decimal, exclude_id: int | None = None) -> sqlite3.Row | None:
    if payload.islem_turu != "SATIS":
        return None
    if not payload.hurda_alis_id:
        raise HTTPException(status_code=400, detail="Hurda satis icin hurda alistan urun secilmeli.")
    alis = conn.execute("SELECT * FROM hurda WHERE id = ? AND islem_turu = 'ALIS'", (payload.hurda_alis_id,)).fetchone()
    if not alis:
        raise HTTPException(status_code=400, detail="Hurda alis kaydi bulunamadi.")
    if normalize_text(alis["cinsi"]) != normalize_text(payload.cinsi) or normalize_text(alis["ayar"]) != normalize_text(payload.ayar):
        raise HTTPException(status_code=400, detail="Secilen hurda alis ile satis urunu uyusmuyor.")
    rem = hurda_purchase_remaining(conn, alis, exclude_id)
    requested_gram = d(payload.adet) * d(payload.gram)
    if d(payload.adet) > rem["kalan_adet"] or requested_gram > rem["kalan_gram"]:
        raise HTTPException(status_code=400, detail="STOK YETERS\u0130Z")
    return alis


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



def cari_data(conn: sqlite3.Connection) -> dict[str, Any]:
    customers: dict[str, dict[str, Any]] = {}
    suppliers: dict[str, dict[str, Any]] = {}
    combined: dict[str, dict[str, Any]] = {}

    def get(bucket: dict[str, dict[str, Any]], name: str) -> dict[str, Any]:
        key = normalize_text(name)
        if key not in bucket:
            bucket[key] = {"isim": clean_text(name), "toplam": ZERO, "odenen_alinan": ZERO, "son_islem_tarihi": ""}
        return bucket[key]

    def get_combined(name: str) -> dict[str, Any]:
        key = normalize_text(name)
        if key not in combined:
            combined[key] = {
                "isim": clean_text(name),
                "toplam_alis": ZERO,
                "odenen": ZERO,
                "toplam_satis": ZERO,
                "alinan": ZERO,
                "son_islem_tarihi": "",
            }
        return combined[key]

    def add_purchase(name: str, total: Decimal, paid: Decimal, tarih: str) -> None:
        supplier = get(suppliers, name)
        supplier["toplam"] += total
        supplier["odenen_alinan"] += paid
        supplier["son_islem_tarihi"] = max(supplier["son_islem_tarihi"], tarih)
        person = get_combined(name)
        person["toplam_alis"] += total
        person["odenen"] += paid
        person["son_islem_tarihi"] = max(person["son_islem_tarihi"], tarih)

    def add_sale(name: str, total: Decimal, received: Decimal, tarih: str) -> None:
        customer = get(customers, name)
        customer["toplam"] += total
        customer["odenen_alinan"] += received
        customer["son_islem_tarihi"] = max(customer["son_islem_tarihi"], tarih)
        person = get_combined(name)
        person["toplam_satis"] += total
        person["alinan"] += received
        person["son_islem_tarihi"] = max(person["son_islem_tarihi"], tarih)

    for row in fetch_all(conn, "alis"):
        add_purchase(row["tedarikci"], purchase_total(row), d(row["odenen"]), row["tarih"])

    for row in fetch_all(conn, "satis"):
        add_sale(row["musteri"], sale_total(row), d(row["alinan"]), row["tarih"])

    for row in fetch_all(conn, "hurda"):
        if row["islem_turu"] == "ALIS":
            add_purchase(row["kisi"], scrap_total(row), d(row["odenen_veya_alinan"]), row["tarih"])
        else:
            add_sale(row["kisi"], scrap_total(row), d(row["odenen_veya_alinan"]), row["tarih"])

    def out(bucket: dict[str, dict[str, Any]], customer: bool) -> list[dict[str, Any]]:
        rows = []
        for cari in bucket.values():
            debt = cari["toplam"] - cari["odenen_alinan"]
            row = {"isim": cari["isim"], "kalan_borc": as_float(debt, MONEY_Q), "son_islem_tarihi": cari["son_islem_tarihi"]}
            if customer:
                row.update({"musteri_adi": cari["isim"], "toplam_satis": as_float(cari["toplam"], MONEY_Q), "alinan": as_float(cari["odenen_alinan"], MONEY_Q), "tip": "M\u00dc\u015eTER\u0130"})
            else:
                row.update({"tedarikci_adi": cari["isim"], "toplam_alis": as_float(cari["toplam"], MONEY_Q), "odenen": as_float(cari["odenen_alinan"], MONEY_Q), "tip": "TEDAR\u0130K\u00c7\u0130"})
            rows.append(row)
        return sorted(rows, key=lambda item: normalize_text(item["isim"]))

    def out_combined() -> list[dict[str, Any]]:
        rows = []
        for cari in combined.values():
            alis_borcu = cari["toplam_alis"] - cari["odenen"]
            satis_borcu = cari["toplam_satis"] - cari["alinan"]
            net_bakiye = satis_borcu - alis_borcu
            rows.append({
                "isim": cari["isim"],
                "toplam_alis": as_float(cari["toplam_alis"], MONEY_Q),
                "odenen": as_float(cari["odenen"], MONEY_Q),
                "alis_borcu": as_float(alis_borcu, MONEY_Q),
                "toplam_satis": as_float(cari["toplam_satis"], MONEY_Q),
                "alinan": as_float(cari["alinan"], MONEY_Q),
                "satis_borcu": as_float(satis_borcu, MONEY_Q),
                "net_bakiye": as_float(net_bakiye, MONEY_Q),
                "son_islem_tarihi": cari["son_islem_tarihi"],
            })
        return sorted(rows, key=lambda item: normalize_text(item["isim"]))

    return {
        "kisiler": out_combined(),
        "musteriler": out(customers, True),
        "tedarikciler": out(suppliers, False),
        "uyari": "Ayn\u0131 ki\u015fi/firma farkl\u0131 yaz\u0131l\u0131rsa ayr\u0131 cari olarak g\u00f6r\u00fcn\u00fcr.",
    }
def sale_profit(conn: sqlite3.Connection, row: sqlite3.Row) -> Decimal:
    purchase_id = sale_purchase_id(row)
    if not purchase_id:
        return ZERO
    alis = conn.execute("SELECT * FROM alis WHERE id = ?", (purchase_id,)).fetchone()
    if not alis:
        return ZERO
    fark = d(row["milyem"]) - d(alis["milyem"])
    return q(d(row["adet"]) * d(row["gram"]) * fark / Decimal("1000"), HAS_Q)


def sale_metrics(conn: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    purchase_id = sale_purchase_id(row)
    alis = conn.execute("SELECT * FROM alis WHERE id = ?", (purchase_id,)).fetchone() if purchase_id else None
    if not alis:
        return {
            "alis_milyem": 0.0, "satis_milyem": as_float(row["milyem"], NUM_Q), "milyem_farki": 0.0,
            "satis_has": as_float(row["has"], HAS_Q), "has_kari": 0.0, "milyem_kari": 0.0, "tahmini_kar": 0.0,
        }
    alis_milyem = d(alis["milyem"])
    satis_milyem = d(row["milyem"])
    fark = satis_milyem - alis_milyem
    has_kari = q(d(row["adet"]) * d(row["gram"]) * fark / Decimal("1000"), HAS_Q)
    return {
        "alis_milyem": as_float(alis_milyem, NUM_Q),
        "satis_milyem": as_float(satis_milyem, NUM_Q),
        "milyem_farki": as_float(fark, NUM_Q),
        "satis_has": as_float(row["has"], HAS_Q),
        "milyem_farki_has_etkisi": as_float(has_kari, HAS_Q),
        "has_kari": as_float(has_kari, HAS_Q),
        "milyem_kari": as_float(has_kari, HAS_Q),
        "has_kari_milyem": as_float(fark, NUM_Q),
        "tahmini_kar": as_float(has_kari, HAS_Q),
    }


def sale_out(conn: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    item = row_dict(row, "toplam_tutar", sale_total(row))
    item["kalan_borc"] = as_float(sale_total(row) - d(row["alinan"]), MONEY_Q)
    item.update(sale_metrics(conn, row))
    purchase_id = sale_purchase_id(row)
    item["purchase_id"] = purchase_id
    item["alis_id"] = purchase_id
    item["milyem_kari"] = item["has_kari"]
    item["kar"] = item["milyem_kari"]
    item["uyari"] = ""
    return item

def hurda_profit(conn: sqlite3.Connection, row: sqlite3.Row) -> Decimal:
    if row["islem_turu"] != "SATIS":
        return ZERO
    alis = conn.execute("SELECT * FROM hurda WHERE id = ? AND islem_turu = 'ALIS'", (row["hurda_alis_id"],)).fetchone() if "hurda_alis_id" in row.keys() and row["hurda_alis_id"] else None
    if alis and d(alis["has"]) > 0:
        unit_cost = scrap_total(alis) / d(alis["has"])
        return q(scrap_total(row) - d(row["has"]) * unit_cost, MONEY_Q)
    stock = hurda_stock_lookup(conn).get((normalize_text(row["cinsi"]), normalize_text(row["ayar"])))
    unit_cost = d(stock["ortalama_has_maliyeti"]) if stock else ZERO
    return q(scrap_total(row) - d(row["has"]) * unit_cost, MONEY_Q)


def hurda_out(conn: sqlite3.Connection, row: sqlite3.Row) -> dict[str, Any]:
    item = row_dict(row, "toplam_tutar", scrap_total(row))
    item["kalan_borc"] = as_float(scrap_total(row) - d(row["odenen_veya_alinan"]), MONEY_Q)
    item["hurda_kar"] = as_float(hurda_profit(conn, row), MONEY_Q) if row["islem_turu"] == "SATIS" else 0.0
    return item

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
def index(request: Request):
    try:
        require_auth(request)
    except HTTPException:
        return RedirectResponse("/login")
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/login")
def login_page() -> FileResponse:
    return FileResponse(STATIC_DIR / "login.html")


class LoginRequest(BaseModel):
    password: str = ""


@app.get("/api/session")
def session(request: Request) -> dict[str, Any]:
    try:
        require_auth(request)
        return ok({"authenticated": True})
    except HTTPException:
        return ok({"authenticated": False})


@app.post("/api/login")
def login(request: Request, response: Response, payload: LoginRequest):
    ip = client_ip(request)
    if is_login_locked(ip):
        remaining = lock_remaining_seconds(ip)
        return fail(f"Çok fazla hatalı deneme. {remaining} saniye sonra tekrar deneyin.", 429)
    password = clean_text(payload.password)
    if not password:
        record_failed_login(ip)
        return fail("Şifre hatalı", 401)
    if hashlib.sha256(password.encode("utf-8")).hexdigest() != PASSWORD_HASH:
        record_failed_login(ip)
        return fail("Şifre hatalı", 401)
    clear_failed_logins(ip)
    token = secrets.token_urlsafe(32)
    sessions[token] = {"ip": ip, "last": time.time()}
    response.set_cookie("session_token", token, max_age=SESSION_TIMEOUT, httponly=True, samesite="lax")
    return ok({"authenticated": True}, "Giriş başarılı")


@app.post("/api/logout")
def logout(request: Request, response: Response):
    sessions.pop(request.cookies.get("session_token") or "", None)
    response.delete_cookie("session_token")
    return ok({"authenticated": False}, "Çıkış yapıldı")

@app.get("/api/suggestions")
def get_suggestions(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        return ok(suggestions(conn))


@app.get("/api/alis")
def list_alis(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        rows = []
        for row in fetch_all(conn, "alis"):
            item = row_dict(row, "toplam_tutar", purchase_total(row))
            item["kalan_borc"] = as_float(purchase_total(row) - d(row["odenen"]), MONEY_Q)
            rows.append(item)
        return ok(rows)


@app.post("/api/alis")
def create_alis(payload: AlisIn, _: None = Depends(require_auth)) -> dict[str, Any]:
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
        item = row_dict(row, "toplam_tutar", purchase_total(row))
        item["kalan_borc"] = as_float(purchase_total(row) - d(row["odenen"]), MONEY_Q)
        return ok(item, "Alış kaydedildi.")



@app.get("/api/satis/urun-secenekleri")
def sale_options(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        rows = []
        for row in fetch_all(conn, "alis"):
            if is_hurda_product(row["cinsi"]):
                continue
            rem = purchase_remaining(conn, row)
            if rem["kalan_adet"] > 0 and rem["kalan_gram"] > 0:
                item = row_dict(row, "toplam_tutar", purchase_total(row))
                item["alis_milyem"] = item["milyem"]
                item["alis_has_maliyeti"] = as_float(purchase_total(row) / d(row["has"]) if d(row["has"]) > 0 else ZERO, MONEY_Q)
                item["kalan_adet"] = as_float(rem["kalan_adet"], NUM_Q)
                item["kalan_gram"] = as_float(rem["kalan_gram"], NUM_Q)
                item["kalan_has"] = as_float(rem["kalan_has"], HAS_Q)
                item["kalan_stok"] = f"{item['kalan_adet']} adet / {item['kalan_gram']} gr / {item['kalan_has']} has"
                rows.append(item)
        return ok(rows)


@app.get("/api/alis/selectable")
def sale_options_alias(_: None = Depends(require_auth)) -> dict[str, Any]:
    return sale_options(_)
@app.get("/api/satis")
def list_satis(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        return ok([sale_out(conn, row) for row in fetch_all(conn, "satis")])


@app.post("/api/satis")
def create_satis(payload: SatisIn, _: None = Depends(require_auth)) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    with db() as conn:
        alis = ensure_sale_stock(conn, payload, has)
        if d(payload.has_fiyati) == 0:
            payload.has_fiyati = d(alis["has_fiyati"])
        cur = conn.execute(
            """
            INSERT INTO satis (tarih, musteri, cinsi, ayar, adet, gram, milyem, has,
                               has_fiyati, iscilik, ek_ucret, indirim, alinan, notlar, alis_id, purchase_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (payload.tarih, payload.musteri, payload.cinsi, payload.ayar, float(payload.adet), float(payload.gram), float(payload.milyem), float(has), float(payload.has_fiyati), float(payload.iscilik), float(payload.ek_ucret), float(payload.indirim), float(payload.alinan), payload.notlar, payload.alis_id, payload.alis_id),
        )
        row = conn.execute("SELECT * FROM satis WHERE id = ?", (cur.lastrowid,)).fetchone()
        return ok(sale_out(conn, row), "Satış kaydedildi.")


@app.get("/api/hurda/urun-secenekleri")
def hurda_sale_options(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        rows = []
        for row in fetch_all(conn, "hurda"):
            if row["islem_turu"] != "ALIS":
                continue
            rem = hurda_purchase_remaining(conn, row)
            if rem["kalan_adet"] > 0 and rem["kalan_gram"] > 0:
                item = hurda_out(conn, row)
                item["hurda_alis_id"] = item["id"]
                item["alis_milyem"] = item["milyem"]
                item["alis_has_maliyeti"] = as_float(scrap_total(row) / d(row["has"]) if d(row["has"]) > 0 else ZERO, MONEY_Q)
                item["kalan_adet"] = as_float(rem["kalan_adet"], NUM_Q)
                item["kalan_gram"] = as_float(rem["kalan_gram"], NUM_Q)
                item["kalan_has"] = as_float(rem["kalan_has"], HAS_Q)
                item["kalan_stok"] = f"{item['kalan_adet']} adet / {item['kalan_gram']} gr / {item['kalan_has']} has"
                rows.append(item)
        return ok(rows)


@app.get("/api/hurda")
def list_hurda(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        hurda_rows = fetch_all(conn, "hurda")
        rows = [hurda_out(conn, row) for row in hurda_rows]
        alis_has = sum((d(row["has"]) for row in hurda_rows if row["islem_turu"] == "ALIS"), ZERO)
        satis_has = sum((d(row["has"]) for row in hurda_rows if row["islem_turu"] == "SATIS"), ZERO)
        alis_tutar = sum((scrap_total(row) for row in hurda_rows if row["islem_turu"] == "ALIS"), ZERO)
        satis_tutar = sum((scrap_total(row) for row in hurda_rows if row["islem_turu"] == "SATIS"), ZERO)
        summary = {
            "hurda_alis_has": as_float(alis_has, HAS_Q),
            "hurda_satis_has": as_float(satis_has, HAS_Q),
            "hurda_kalan_has": as_float(alis_has - satis_has, HAS_Q),
            "hurda_alis_tutari": as_float(alis_tutar, MONEY_Q),
            "hurda_satis_tutari": as_float(satis_tutar, MONEY_Q),
            "hurda_kar": as_float(sum((hurda_profit(conn, row) for row in hurda_rows), ZERO), MONEY_Q),
        }
        return ok({"ozet": summary, "stok": hurda_stock_items(conn), "kayitlar": rows})


@app.post("/api/hurda")
def create_hurda(payload: HurdaIn, _: None = Depends(require_auth)) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    total = q(has * payload.has_fiyati + payload.iscilik, MONEY_Q)
    with db() as conn:
        ensure_hurda_stock(conn, payload, has)
        cur = conn.execute(
            """
            INSERT INTO hurda (hurda_alis_id, tarih, islem_turu, kisi, cinsi, ayar, adet, gram, milyem,
                               has, has_fiyati, iscilik, toplam_tutar, odenen_veya_alinan, notlar)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.hurda_alis_id if payload.islem_turu == "SATIS" else None,
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
        return ok(hurda_out(conn, row), "Hurda kaydedildi.")

@app.get("/api/stok")
def list_stock(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        return ok(stock_items(conn))



@app.get("/api/stok/normal")
def list_normal_stock(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        return ok(stock_items(conn))


@app.get("/api/stok/hurda")
def list_hurda_stock(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        return ok(hurda_stock_items(conn))


@app.get("/api/cari")
def list_cari(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        return ok(cari_data(conn))


def dashboard_payload(conn: sqlite3.Connection) -> dict[str, Any]:
    alis_rows = fetch_all(conn, "alis")
    satis_rows = fetch_all(conn, "satis")
    hurda_rows = fetch_all(conn, "hurda")
    stocks = stock_items(conn)
    hurda_stocks = hurda_stock_items(conn)
    cari = cari_data(conn)
    today_text = date.today().isoformat()
    total_profit = sum((sale_profit(conn, row) for row in satis_rows), ZERO)
    today_profit = sum((sale_profit(conn, row) for row in satis_rows if row["tarih"] == today_text), ZERO)
    hurda_profit_total = sum((hurda_profit(conn, row) for row in hurda_rows), ZERO)
    hurda_buy_total = sum((scrap_total(row) for row in hurda_rows if row["islem_turu"] == "ALIS"), ZERO)
    hurda_sale_total = sum((scrap_total(row) for row in hurda_rows if row["islem_turu"] == "SATIS"), ZERO)
    return {
        "toplam_normal_alis": as_float(sum((purchase_total(row) for row in alis_rows), ZERO), MONEY_Q),
        "toplam_normal_satis": as_float(sum((sale_total(row) for row in satis_rows), ZERO), MONEY_Q),
        "toplam_alis": as_float(sum((purchase_total(row) for row in alis_rows), ZERO), MONEY_Q),
        "toplam_satis": as_float(sum((sale_total(row) for row in satis_rows), ZERO), MONEY_Q),
        "gunluk_satis": as_float(sum((sale_total(row) for row in satis_rows if row["tarih"] == today_text), ZERO), MONEY_Q),
        "gunluk_urun_kari": as_float(today_profit, HAS_Q),
        "genel_urun_kari": as_float(total_profit, HAS_Q),
        "gunluk_kar": as_float(today_profit, HAS_Q),
        "toplam_kar": as_float(total_profit, HAS_Q),
        "hurda_alis_toplami": as_float(hurda_buy_total, MONEY_Q),
        "hurda_satis_toplami": as_float(hurda_sale_total, MONEY_Q),
        "hurda_kar": as_float(hurda_profit_total, MONEY_Q),
        "toplam_musteri_borcu": as_float(sum((d(row["kalan_borc"]) for row in cari["musteriler"]), ZERO), MONEY_Q),
        "toplam_tedarikci_borcu": as_float(sum((d(row["kalan_borc"]) for row in cari["tedarikciler"]), ZERO), MONEY_Q),
        "normal_stok_has": as_float(sum((d(item["kalan_has"]) for item in stocks), ZERO), HAS_Q),
        "normal_stok_gram": as_float(sum((d(item["kalan_gram"]) for item in stocks), ZERO), NUM_Q),
        "normal_stok_degeri": as_float(sum((d(item["stok_degeri"]) for item in stocks), ZERO), MONEY_Q),
        "toplam_stok_has": as_float(sum((d(item["kalan_has"]) for item in stocks), ZERO), HAS_Q),
        "stok_degeri": as_float(sum((d(item["stok_degeri"]) for item in stocks), ZERO), MONEY_Q),
        "hurda_kalan_has": as_float(sum((d(item["kalan_has"]) for item in hurda_stocks), ZERO), HAS_Q),
        "hurda_kalan_gram": as_float(sum((d(item["kalan_gram"]) for item in hurda_stocks), ZERO), NUM_Q),
        "uyari_sayisi": sum(1 for item in stocks + hurda_stocks if item["uyari"]),
        "alis_adedi": len(alis_rows),
        "satis_adedi": len(satis_rows),
        "hurda_adedi": len(hurda_rows),
    }


@app.get("/api/dashboard")
def dashboard(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        return ok(dashboard_payload(conn))


@app.get("/api/export")
def export_all(_: None = Depends(require_auth)) -> dict[str, Any]:
    with db() as conn:
        alis_rows = [row_dict(row, "toplam_tutar", purchase_total(row)) for row in fetch_all(conn, "alis")]
        satis_rows = [sale_out(conn, row) for row in fetch_all(conn, "satis")]
        hurda_rows = [hurda_out(conn, row) for row in fetch_all(conn, "hurda")]
        return ok({
            "exported_at": datetime.now().isoformat(timespec="seconds"),
            "version": "1.0",
            "alis": alis_rows,
            "satis": satis_rows,
            "hurda": hurda_rows,
            "stok_normal": stock_items(conn),
            "stok_hurda": hurda_stock_items(conn),
            "cari": cari_data(conn),
            "dashboard": dashboard_payload(conn),
        })


@app.get("/api/ayarlar")
def settings(_: None = Depends(require_auth)) -> dict[str, Any]:
    return ok([{"baslik": "Login", "deger": "Aktif"}, {"baslik": "Stok", "deger": "Otomatik hesaplanir"}, {"baslik": "Hurda", "deger": "Normal stoktan ayridir"}])


@app.put("/api/alis/{item_id}")
def update_alis(item_id: int, payload: AlisIn, _: None = Depends(require_auth)) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    with db() as conn:
        existing = conn.execute("SELECT * FROM alis WHERE id = ?", (item_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Kay\u0131t bulunamad\u0131.")
        sold = conn.execute("SELECT COALESCE(SUM(adet),0) adet, COALESCE(SUM(adet * gram),0) gram FROM satis WHERE COALESCE(purchase_id, alis_id) = ?", (item_id,)).fetchone()
        has_linked_sale = d(sold["adet"]) > 0 or d(sold["gram"]) > 0
        if has_linked_sale and (normalize_text(existing["cinsi"]) != normalize_text(payload.cinsi) or normalize_text(existing["ayar"]) != normalize_text(payload.ayar)):
            raise HTTPException(status_code=400, detail="Bu al\u0131\u015f kayd\u0131na ba\u011fl\u0131 sat\u0131\u015f var; cinsi veya ayar de\u011fi\u015ftirilemez.")
        if d(sold["adet"]) > d(payload.adet) or d(sold["gram"]) > d(payload.adet) * d(payload.gram):
            raise HTTPException(status_code=400, detail="Bu al\u0131\u015f kayd\u0131na ba\u011fl\u0131 sat\u0131\u015f var; adet/gram mevcut sat\u0131\u015f\u0131n alt\u0131na d\u00fc\u015f\u00fcr\u00fclemez.")
        if d(payload.has_fiyati) == 0 and d(payload.iscilik) == 0 and d(payload.ek_masraf) == 0 and d(payload.odenen) == 0:
            payload.has_fiyati = d(existing["has_fiyati"])
            payload.iscilik = d(existing["iscilik"])
            payload.ek_masraf = d(existing["ek_masraf"])
            payload.odenen = d(existing["odenen"])
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
        item = row_dict(row, "toplam_tutar", purchase_total(row))
        item["kalan_borc"] = as_float(purchase_total(row) - d(row["odenen"]), MONEY_Q)
        return ok(item, "Alış güncellendi.")


@app.put("/api/satis/{item_id}")
def update_satis(item_id: int, payload: SatisIn, _: None = Depends(require_auth)) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    with db() as conn:
        existing = conn.execute("SELECT * FROM satis WHERE id = ?", (item_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Kay\u0131t bulunamad\u0131.")
        alis = ensure_sale_stock(conn, payload, has, item_id)
        if d(payload.has_fiyati) == 0 and d(payload.iscilik) == 0 and d(payload.ek_ucret) == 0 and d(payload.indirim) == 0 and d(payload.alinan) == 0:
            payload.has_fiyati = d(existing["has_fiyati"])
            payload.iscilik = d(existing["iscilik"])
            payload.ek_ucret = d(existing["ek_ucret"])
            payload.indirim = d(existing["indirim"])
            payload.alinan = d(existing["alinan"])
        elif d(payload.has_fiyati) == 0:
            payload.has_fiyati = d(alis["has_fiyati"])
        cur = conn.execute(
            """
            UPDATE satis 
            SET tarih = ?, musteri = ?, cinsi = ?, ayar = ?, adet = ?, gram = ?, 
                milyem = ?, has = ?, has_fiyati = ?, iscilik = ?, ek_ucret = ?, 
                indirim = ?, alinan = ?, notlar = ?, alis_id = ?, purchase_id = ?
            WHERE id = ?
            """,
            (payload.tarih, payload.musteri, payload.cinsi, payload.ayar, float(payload.adet), float(payload.gram), float(payload.milyem), float(has), float(payload.has_fiyati), float(payload.iscilik), float(payload.ek_ucret), float(payload.indirim), float(payload.alinan), payload.notlar, payload.alis_id, payload.alis_id, item_id),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Kay\u0131t bulunamad\u0131.")
        row = conn.execute("SELECT * FROM satis WHERE id = ?", (item_id,)).fetchone()
        return ok(sale_out(conn, row), "Sat\u0131\u015f g\u00fcncellendi.")

@app.put("/api/hurda/{item_id}")
def update_hurda(item_id: int, payload: HurdaIn, _: None = Depends(require_auth)) -> dict[str, Any]:
    has = calc_has(payload.adet, payload.gram, payload.milyem)
    with db() as conn:
        existing = conn.execute("SELECT * FROM hurda WHERE id = ?", (item_id,)).fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Kay\u0131t bulunamad\u0131.")
        if d(payload.has_fiyati) == 0 and d(payload.iscilik) == 0 and d(payload.odenen_veya_alinan) == 0:
            payload.has_fiyati = d(existing["has_fiyati"])
            payload.iscilik = d(existing["iscilik"])
            payload.odenen_veya_alinan = d(existing["odenen_veya_alinan"])
        total = q(has * payload.has_fiyati + payload.iscilik, MONEY_Q)
        ensure_hurda_stock(conn, payload, has, item_id)
        cur = conn.execute(
            """
            UPDATE hurda
            SET hurda_alis_id = ?, tarih = ?, islem_turu = ?, kisi = ?, cinsi = ?, ayar = ?, adet = ?,
                gram = ?, milyem = ?, has = ?, has_fiyati = ?, iscilik = ?, toplam_tutar = ?,
                odenen_veya_alinan = ?, notlar = ?
            WHERE id = ?
            """,
            (
                payload.hurda_alis_id if payload.islem_turu == "SATIS" else None,
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
                item_id,
            ),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Kay\u0131t bulunamad\u0131.")
        row = conn.execute("SELECT * FROM hurda WHERE id = ?", (item_id,)).fetchone()
        return ok(hurda_out(conn, row), "Hurda g\u00fcncellendi.")

@app.delete("/api/alis/{item_id}")
def delete_alis_item(item_id: int, _: None = Depends(require_auth)) -> dict[str, Any]:
    return delete_item("alis", item_id, _)


@app.delete("/api/satis/{item_id}")
def delete_satis_item(item_id: int, _: None = Depends(require_auth)) -> dict[str, Any]:
    return delete_item("satis", item_id, _)


@app.delete("/api/hurda/{item_id}")
def delete_hurda_item(item_id: int, _: None = Depends(require_auth)) -> dict[str, Any]:
    return delete_item("hurda", item_id, _)

@app.delete("/api/{table}/{item_id}")
def delete_item(table: str, item_id: int, _: None = Depends(require_auth)) -> dict[str, Any]:
    if table not in {"alis", "satis", "hurda"}:
        raise HTTPException(status_code=404, detail="Tablo bulunamad\u0131.")
    with db() as conn:
        if table == "alis":
            linked = conn.execute("SELECT COUNT(*) count FROM satis WHERE COALESCE(purchase_id, alis_id) = ?", (item_id,)).fetchone()["count"]
            if linked:
                raise HTTPException(status_code=400, detail="Bu al\u0131\u015f kayd\u0131na ba\u011fl\u0131 sat\u0131\u015f var. \u00d6nce ilgili sat\u0131\u015f\u0131 silin.")
        if table == "hurda":
            row = conn.execute("SELECT islem_turu FROM hurda WHERE id = ?", (item_id,)).fetchone()
            if row and row["islem_turu"] == "ALIS":
                linked = conn.execute("SELECT COUNT(*) count FROM hurda WHERE islem_turu = 'SATIS' AND hurda_alis_id = ?", (item_id,)).fetchone()["count"]
                if linked:
                    raise HTTPException(status_code=400, detail="Bu hurda al\u0131\u015f kayd\u0131na ba\u011fl\u0131 hurda sat\u0131\u015f var. \u00d6nce ilgili hurda sat\u0131\u015f\u0131 silin.")
        cur = conn.execute(f"DELETE FROM {table} WHERE id = ?", (item_id,))
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Kay\u0131t bulunamad\u0131.")
        return ok({"deleted": True}, "Kay\u0131t silindi.")
