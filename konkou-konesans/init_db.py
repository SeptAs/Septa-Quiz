#!/usr/bin/env python3
"""
init_db.py — SeptaQuiz by Septech
Initialise les tables PostgreSQL avant le démarrage de l'application.
Appelé par la Build Command sur Render.
"""
import os
import sys

def init_db():
    db_url = os.environ.get('DATABASE_URL', '')
    if not db_url:
        print("ERROR: DATABASE_URL not set. Set it in Render environment variables.")
        sys.exit(1)

    # Render gives postgres:// but psycopg2 needs postgresql://
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)

    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()

        # Table scores — résultats de chaque partie
        cur.execute('''
            CREATE TABLE IF NOT EXISTS scores (
                id           SERIAL PRIMARY KEY,
                name         TEXT    NOT NULL,
                score        INTEGER NOT NULL DEFAULT 0,
                total        INTEGER NOT NULL DEFAULT 7,
                category     TEXT    NOT NULL,
                difficulty   TEXT    NOT NULL,
                lang         TEXT    NOT NULL DEFAULT 'ht',
                correct      INTEGER NOT NULL DEFAULT 0,
                wrong        INTEGER NOT NULL DEFAULT 0,
                time_elapsed INTEGER NOT NULL DEFAULT 0,
                played_at    TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')

        # Table sessions — partie en cours (token anti-triche)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                token       TEXT    PRIMARY KEY,
                category    TEXT    NOT NULL,
                difficulty  TEXT    NOT NULL,
                lang        TEXT    NOT NULL DEFAULT 'ht',
                name        TEXT    NOT NULL,
                q_indices   TEXT    NOT NULL,
                current     INTEGER NOT NULL DEFAULT 0,
                score       INTEGER NOT NULL DEFAULT 0,
                correct     INTEGER NOT NULL DEFAULT 0,
                wrong       INTEGER NOT NULL DEFAULT 0,
                created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            )
        ''')

        # Index pour accélérer les requêtes classement
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_scores_played_at
            ON scores (played_at DESC)
        ''')
        cur.execute('''
            CREATE INDEX IF NOT EXISTS idx_scores_score
            ON scores (score DESC)
        ''')

        # Nettoyer les vieilles sessions (> 2h) au démarrage
        cur.execute('''
            DELETE FROM sessions
            WHERE created_at < NOW() - INTERVAL '2 hours'
        ''')

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Database initialized successfully (SeptaQuiz by Septech)")

    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    init_db()
