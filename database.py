#!/usr/bin/env python
# coding: utf-8
# ============================================================
# database.py — SQLite Integration
# Handles schema creation, seeding, and all SQL queries
# ============================================================

import sqlite3
import pandas as pd

DB_PATH = "movie_recommendation.db"

# ─────────────────────────────────────────
# SCHEMA CREATION
# ─────────────────────────────────────────
def init_db():
    """Create all tables if they don't already exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Users (
            user_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT NOT NULL,
            email     TEXT UNIQUE NOT NULL,
            age       INTEGER,
            gender    TEXT
        )
    """)

    # Genres table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Genres (
            genre_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT UNIQUE NOT NULL
        )
    """)

    # Movies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Movies (
            movie_id    INTEGER PRIMARY KEY AUTOINCREMENT,
            title       TEXT NOT NULL,
            genre       TEXT NOT NULL,
            year        INTEGER,
            description TEXT,
            avg_rating  REAL DEFAULT 0.0
        )
    """)

    # Ratings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Ratings (
            rating_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id    INTEGER NOT NULL,
            movie_id   INTEGER NOT NULL,
            rating     REAL NOT NULL CHECK(rating >= 1.0 AND rating <= 5.0),
            timestamp  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)  REFERENCES Users(user_id),
            FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
        )
    """)

    # Recommendations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Recommendations (
            rec_id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id      INTEGER NOT NULL,
            movie_id     INTEGER NOT NULL,
            score        REAL,
            generated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id)  REFERENCES Users(user_id),
            FOREIGN KEY (movie_id) REFERENCES Movies(movie_id)
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Tables created/verified successfully.")


# ─────────────────────────────────────────
# SEED DATA
# ─────────────────────────────────────────
MOVIES_DATA = [
    # (title, genre, year, description)
    ("Fitoor",            "Romance Drama",               2016, "A star-crossed love story inspired by Great Expectations."),
    ("Shikara",           "Romance Drama",               2020, "A love story set against the backdrop of the Kashmir conflict."),
    ("Bombay",            "Romance Drama Musical",       1995, "A Hindu-Muslim couple navigate the Bombay riots of 1992."),
    ("Kadhal Kanmani",    "Romance Drama",               2015, "Young couple grapple with commitment in contemporary Chennai."),
    ("Man Love",          "Romance Drama",               2008, "A dramatic exploration of love and relationships."),
    ("Faraway Land",      "Drama Adventure",             2012, "A journey of self-discovery across distant lands."),
    ("Week Ago",          "Romance Comedy Drama",        2019, "A lighthearted look at relationships and second chances."),
    ("Amanda",            "Drama",                       2018, "A man raises his niece after a family tragedy in Paris."),
    ("Tambour Retribut",  "Drama Thriller",              2014, "A gripping tale of justice and retribution."),
    ("Jjie",              "Romance Drama",               2010, "A South Korean romantic drama about enduring love."),
    ("3 Idiots",          "Comedy Drama",                2009, "Three engineering students navigate college life and friendship."),
    ("Taare Zameen Par",  "Drama Family",                2007, "A dyslexic child finds hope through an unconventional teacher."),
    ("Dil Chahta Hai",    "Comedy Drama Romance",        2001, "Three best friends navigate love and life after college."),
    ("Zindagi Na Milegi", "Adventure Drama Comedy",      2011, "Three friends embark on a road trip across Spain."),
    ("Barfi",             "Romance Comedy Drama",        2012, "A deaf-mute man falls in love in 1970s Darjeeling."),
    ("Inception",         "Sci-Fi Thriller Action",      2010, "A thief steals secrets through dream-sharing technology."),
    ("The Dark Knight",   "Action Thriller Crime",       2008, "Batman faces the anarchic Joker in Gotham City."),
    ("Interstellar",      "Sci-Fi Drama Adventure",      2014, "Astronauts travel through a wormhole to save humanity."),
    ("Parasite",          "Thriller Drama",              2019, "A poor family infiltrates the life of a wealthy household."),
    ("Your Name",         "Romance Animation Drama",     2016, "Two teenagers mysteriously swap bodies in Japan."),
    ("La La Land",        "Romance Musical Drama",       2016, "A jazz musician and aspiring actress fall in love in LA."),
    ("Forrest Gump",      "Drama Comedy Romance",        2018, "The life of a kind-hearted man with a low IQ."),
    ("Avengers Endgame",  "Action Sci-Fi Adventure",     2019, "The Avengers assemble to reverse Thanos's actions."),
    ("Coco",              "Animation Adventure Family",  2017, "A boy travels to the Land of the Dead in Mexico."),
    ("Spirited Away",     "Animation Adventure Fantasy", 2001, "A young girl enters a spirit world to save her parents."),
]

USERS_DATA = [
    ("Kushal",  "kushal@mriirs.edu",  20, "M"),
    ("Daksh",   "daksh@mriirs.edu",   20, "M"),
    ("Jayesh",  "jayesh@mriirs.edu",  21, "M"),
    ("Anirudh", "anirudh@mriirs.edu", 20, "M"),
    ("Remant",  "remant@mriirs.edu",  21, "M"),
    ("Priya",   "priya@example.com",  22, "F"),
    ("Rohan",   "rohan@example.com",  23, "M"),
    ("Sneha",   "sneha@example.com",  21, "F"),
    ("Arjun",   "arjun@example.com",  24, "M"),
    ("Meera",   "meera@example.com",  22, "F"),
]

# Ratings: (user_id, movie_id, rating)
RATINGS_DATA = [
    # Kushal (1) — loves Indian romance and sci-fi
    (1, 1, 5.0), (1, 2, 4.5), (1, 3, 4.0), (1, 11, 5.0), (1, 16, 4.5),
    (1, 17, 4.0), (1, 18, 5.0), (1, 21, 4.5),
    # Daksh (2) — similar to Kushal
    (2, 1, 4.5), (2, 2, 5.0), (2, 3, 4.0), (2, 11, 4.5), (2, 16, 5.0),
    (2, 18, 4.5), (2, 22, 4.0),
    # Jayesh (3) — likes comedy drama
    (3, 11, 5.0), (3, 13, 5.0), (3, 14, 4.5), (3, 15, 4.0), (3, 22, 4.5),
    (3, 7, 4.0), (3, 8, 3.5),
    # Anirudh (4) — action and thriller fan
    (4, 16, 5.0), (4, 17, 5.0), (4, 19, 4.5), (4, 23, 5.0), (4, 9, 4.0),
    (4, 18, 4.0),
    # Remant (5) — animation fan
    (5, 24, 5.0), (5, 25, 5.0), (5, 20, 4.5), (5, 12, 4.0), (5, 11, 3.5),
    # Priya (6) — romance fan
    (6, 1, 5.0), (6, 2, 5.0), (6, 4, 4.5), (6, 20, 4.5), (6, 21, 5.0),
    (6, 15, 4.0), (6, 22, 4.5),
    # Rohan (7) — similar to Anirudh
    (7, 16, 4.5), (7, 17, 5.0), (7, 23, 4.5), (7, 19, 5.0), (7, 18, 3.5),
    # Sneha (8) — world cinema
    (8, 19, 5.0), (8, 20, 5.0), (8, 25, 4.5), (8, 21, 4.0), (8, 8, 4.5),
    # Arjun (9) — mixed
    (9, 11, 4.0), (9, 13, 4.5), (9, 16, 4.0), (9, 17, 3.5), (9, 22, 5.0),
    # Meera (10) — family and drama
    (10, 12, 5.0), (10, 24, 5.0), (10, 8, 4.5), (10, 15, 4.0), (10, 13, 4.5),
]


def load_movies_to_db():
    """Seed Users, Movies, and Ratings if tables are empty."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Seed Users
    cursor.execute("SELECT COUNT(*) FROM Users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO Users (username, email, age, gender) VALUES (?, ?, ?, ?)",
            USERS_DATA
        )
        print(f"[DB] Seeded {len(USERS_DATA)} users.")

    # Seed Movies
    cursor.execute("SELECT COUNT(*) FROM Movies")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO Movies (title, genre, year, description) VALUES (?, ?, ?, ?)",
            MOVIES_DATA
        )
        print(f"[DB] Seeded {len(MOVIES_DATA)} movies.")

    # Seed Ratings
    cursor.execute("SELECT COUNT(*) FROM Ratings")
    if cursor.fetchone()[0] == 0:
        cursor.executemany(
            "INSERT INTO Ratings (user_id, movie_id, rating) VALUES (?, ?, ?)",
            RATINGS_DATA
        )
        # Update avg_rating in Movies
        cursor.execute("""
            UPDATE Movies SET avg_rating = (
                SELECT ROUND(AVG(rating), 2)
                FROM Ratings
                WHERE Ratings.movie_id = Movies.movie_id
            )
        """)
        print(f"[DB] Seeded {len(RATINGS_DATA)} ratings and updated avg_ratings.")

    conn.commit()
    conn.close()


# ─────────────────────────────────────────
# QUERY FUNCTIONS
# ─────────────────────────────────────────
def get_all_movies():
    """Return all movies as a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM Movies", conn)
    conn.close()
    return df


def get_all_ratings():
    """Return all ratings as a DataFrame."""
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM Ratings", conn)
    conn.close()
    return df


def save_recommendations(user_id, movie_ids_scores):
    """Persist generated recommendations for a user."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Clear old recommendations for this user
    cursor.execute("DELETE FROM Recommendations WHERE user_id = ?", (user_id,))
    cursor.executemany(
        "INSERT INTO Recommendations (user_id, movie_id, score) VALUES (?, ?, ?)",
        [(user_id, mid, score) for mid, score in movie_ids_scores]
    )
    conn.commit()
    conn.close()
