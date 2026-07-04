# AKBA? Kuyumcu Takip

FastAPI backend ve sade HTML/CSS/JavaScript frontend ile ?al??an kuyumcu takip uygulamas?.

## Yerelde ?al??t?rma

```powershell
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Taray?c?dan a?:

```text
http://127.0.0.1:8000
```

Giri? ?ifresi:

```text
2526E
```

## Windows K?sa Yol

?ift t?klayarak ?al??t?rmak i?in:

```text
start.bat
```

## Veritaban?

Varsay?lan SQLite yolu:

```text
data/kuyumcu.db
```

Farkl? bir yol kullanmak istersen `DB_PATH` ortam de?i?keni verilebilir.

## Deploy

Render gibi ortamlarda ba?lang?? komutu:

```text
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Frontend API ?a?r?lar? relatif `/api/...` yollar?n? kullan?r; deploy ortam?nda `127.0.0.1` ba??ml?l??? yoktur.
