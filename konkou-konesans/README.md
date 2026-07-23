# 🇭🇹 Konkou Konesans — Quiz Jeneral

App quiz an Kreyòl, kreye pa **Septa**.

## 📁 Estrikti Pwojè

```
konkou-konesans/
├── app.py              ← Flask backend (API)
├── requirements.txt    ← Depandans Python
├── Procfile            ← Kòmand pou Render
├── init_db.py          ← Inisyalizasyon baz done
└── templates/
    └── index.html      ← App konplè (HTML+CSS+JS)
```

## 🚀 Deploy sou Render (GRATIS)

### Etap 1 — Mete kòd la sou GitHub
1. Ale sou [github.com](https://github.com) → kreye yon kont si ou pa gen youn
2. Klike **"New repository"**
3. Non: `konkou-konesans` → klike **Create**
4. Telechaje [GitHub Desktop](https://desktop.github.com/) oswa itilize kòmand sa yo:

```bash
cd konkou-konesans
git init
git add .
git commit -m "Premye vèsyon Konkou Konesans"
git remote add origin https://github.com/USERNAME/konkou-konesans.git
git push -u origin main
```

### Etap 2 — Deploy sou Render
1. Ale sou [render.com](https://render.com) → kreye kont gratis
2. Klike **"New +"** → **"Web Service"**
3. Konekte GitHub ou → chwazi repo `konkou-konesans`
4. Ranpli fòm lan:
   - **Name**: `konkou-konesans`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt && python init_db.py`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: `Free`
5. Klike **"Create Web Service"**

✅ Apre 2-3 minit, ou jwenn yon lyen tankou:
`https://konkou-konesans.onrender.com`

## ⚠️ Nòt sou Render Free
- Sèvè a "dòmi" apre 15 minit san aktivite
- Premye vizit apre lontan ka pran ~30 segond pou reveye
- Baz done SQLite a reyinisyalize si sèvè a redémarre (pou pèsistans total, itilize PostgreSQL)

## 🛠️ Teste Lokalman
```bash
pip install flask flask-cors gunicorn
python init_db.py
python app.py
# Ale sou http://localhost:5000
```
