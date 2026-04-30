#!/usr/bin/env python
# coding: utf-8
# ============================================================
# Movie Recommendation System
# Team: Kushal Mohan (1/24/SET/BCS/509) & Daksh Ahuja (1/24/SET/BCS/514)
# Subject: Python [5.0CE202E02H]
# Manav Rachna International Institute of Research and Studies
# ============================================================

from database import init_db, load_movies_to_db, get_all_movies, get_all_ratings
from preprocessing import clean_text
from recommendation import (
    build_content_model,
    get_content_recommendations,
    get_collaborative_recommendations
)

# ─────────────────────────────────────────
# DISPLAY HELPERS
# ─────────────────────────────────────────
def print_banner():
    print("\n" + "=" * 55)
    print("      🎬  MOVIE RECOMMENDATION SYSTEM  🎬")
    print("  Kushal Mohan (509) | Daksh Ahuja (514)")
    print("=" * 55)

def print_menu():
    print("\n┌─────────────────────────────────────┐")
    print("│           MAIN MENU                 │")
    print("├─────────────────────────────────────┤")
    print("│  1. Content-Based Recommendation    │")
    print("│  2. Collaborative Recommendation    │")
    print("│  3. Hybrid Recommendation           │")
    print("│  4. View All Movies in Database     │")
    print("│  5. Exit                            │")
    print("└─────────────────────────────────────┘")

def display_recommendations(title, movies, mode):
    print(f"\n{'─'*50}")
    print(f"  [{mode}] Recommendations for: '{title}'")
    print(f"{'─'*50}")
    if not movies:
        print("  No recommendations found.")
        return
    for i, movie in enumerate(movies, 1):
        print(f"  {i:>2}. {movie}")
    print(f"{'─'*50}\n")

# ─────────────────────────────────────────
# MAIN APPLICATION
# ─────────────────────────────────────────
def main():
    print_banner()
    print("\n[INFO] Initializing database...")
    init_db()
    load_movies_to_db()

    print("[INFO] Loading data from database...")
    movies_df = get_all_movies()
    ratings_df = get_all_ratings()

    print("[INFO] Building content-based model (TF-IDF + Cosine Similarity)...")
    similarity_matrix, indices = build_content_model(movies_df)
    print("[INFO] System ready!\n")

    while True:
        print_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            title = input("\nEnter a movie title: ").strip()
            cleaned = clean_text(title)
            recs = get_content_recommendations(cleaned, similarity_matrix, indices, movies_df)
            display_recommendations(title, recs, "Content-Based")

        elif choice == "2":
            try:
                user_id = int(input("\nEnter your User ID (1-10): ").strip())
                recs = get_collaborative_recommendations(user_id, ratings_df, movies_df)
                display_recommendations(f"User {user_id}", recs, "Collaborative (KNN + Pearson)")
            except ValueError:
                print("[ERROR] Please enter a valid numeric User ID.")

        elif choice == "3":
            title = input("\nEnter a movie title: ").strip()
            try:
                user_id = int(input("Enter your User ID (1-10): ").strip())
            except ValueError:
                print("[ERROR] Invalid User ID.")
                continue

            cleaned = clean_text(title)
            content_recs = get_content_recommendations(cleaned, similarity_matrix, indices, movies_df, top_n=5)
            collab_recs  = get_collaborative_recommendations(user_id, ratings_df, movies_df, top_n=5)

            # Merge: content first, then collab (deduped)
            seen = set(content_recs)
            hybrid = list(content_recs)
            for r in collab_recs:
                if r not in seen:
                    hybrid.append(r)
                    seen.add(r)

            display_recommendations(f"{title} | User {user_id}", hybrid[:10], "Hybrid")

        elif choice == "4":
            print(f"\n{'─'*55}")
            print(f"  {'ID':<6} {'Title':<35} {'Genre'}")
            print(f"{'─'*55}")
            for _, row in movies_df.iterrows():
                print(f"  {row['movie_id']:<6} {str(row['title']):<35} {row['genre']}")
            print(f"{'─'*55}")

        elif choice == "5":
            print("\n  Thank you for using the Movie Recommendation System!")
            print("  Goodbye 👋\n")
            break

        else:
            print("[ERROR] Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
