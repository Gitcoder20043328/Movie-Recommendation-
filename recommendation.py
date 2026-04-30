#!/usr/bin/env python
# coding: utf-8
# ============================================================
# recommendation.py — Core Algorithms
#
#  Content-Based : TF-IDF on genres  + Cosine Similarity
#  Collaborative : KNN (Pearson correlation) on ratings matrix
# ============================================================

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise        import cosine_similarity
from sklearn.neighbors               import NearestNeighbors
from preprocessing import clean_text


# ─────────────────────────────────────────
# CONTENT-BASED FILTERING
# ─────────────────────────────────────────
def build_content_model(movies_df: pd.DataFrame):
    """
    Build a TF-IDF matrix from cleaned genre strings and compute
    pairwise cosine similarity.

    Returns:
        similarity_matrix : ndarray of shape (n_movies, n_movies)
        indices           : pd.Series mapping cleaned_title → DataFrame index
    """
    # Clean genre text using our preprocessing pipeline
    genre_corpus = movies_df["genre"].apply(clean_text).tolist()

    tfidf      = TfidfVectorizer(stop_words="english")
    tfidf_mat  = tfidf.fit_transform(genre_corpus)
    similarity = cosine_similarity(tfidf_mat)

    # Build index on cleaned titles (matches user input after clean_text())
    movies_df = movies_df.copy()
    movies_df["cleaned_title"] = movies_df["title"].apply(clean_text)
    indices = pd.Series(
        movies_df.index,
        index=movies_df["cleaned_title"]
    ).drop_duplicates()

    return similarity, indices


def get_content_recommendations(cleaned_title: str,
                                similarity_matrix,
                                indices: pd.Series,
                                movies_df: pd.DataFrame,
                                top_n: int = 10) -> list:
    """
    Return top_n movie titles most similar to cleaned_title
    based on cosine similarity of genre TF-IDF vectors.
    """
    if cleaned_title not in indices:
        # Partial match fallback
        matches = [idx for idx in indices.index if cleaned_title in idx]
        if not matches:
            print(f"  [WARNING] '{cleaned_title}' not found in database.")
            return []
        cleaned_title = matches[0]

    idx    = indices[cleaned_title]
    scores = list(enumerate(similarity_matrix[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)
    # Skip index 0 (the movie itself)
    scores = scores[1 : top_n + 1]

    movie_indices = [i[0] for i in scores]
    return movies_df["title"].iloc[movie_indices].tolist()


# ─────────────────────────────────────────
# COLLABORATIVE FILTERING
# ─────────────────────────────────────────
def build_ratings_matrix(ratings_df: pd.DataFrame) -> pd.DataFrame:
    """
    Pivot ratings into a user × movie matrix.
    Missing values filled with 0.
    """
    matrix = ratings_df.pivot_table(
        index="user_id",
        columns="movie_id",
        values="rating"
    ).fillna(0)
    return matrix


def get_collaborative_recommendations(user_id: int,
                                      ratings_df: pd.DataFrame,
                                      movies_df: pd.DataFrame,
                                      top_n: int = 10,
                                      k_neighbors: int = 5) -> list:
    """
    KNN collaborative filtering with Pearson correlation metric.

    Steps:
      1. Build user-movie ratings matrix.
      2. Fit KNN model (metric = correlation, i.e. 1 - Pearson r).
      3. Find k nearest neighbours to the target user.
      4. Compute weighted average rating across neighbours.
      5. Recommend unrated movies with highest predicted scores.

    Returns list of movie title strings.
    """
    matrix = build_ratings_matrix(ratings_df)

    if user_id not in matrix.index:
        print(f"  [WARNING] User ID {user_id} has no ratings in the database.")
        return []

    # KNN with correlation distance (= 1 - Pearson r)
    k = min(k_neighbors, len(matrix) - 1)
    model = NearestNeighbors(metric="correlation", algorithm="brute", n_neighbors=k + 1)
    model.fit(matrix.values)

    user_idx     = matrix.index.get_loc(user_id)
    distances, neighbor_idxs = model.kneighbors(
        matrix.iloc[user_idx].values.reshape(1, -1),
        n_neighbors=k + 1
    )

    # Exclude the user themselves (distance ≈ 0)
    neighbor_idxs = neighbor_idxs[0][1:]
    distances     = distances[0][1:]

    # Similarity = 1 - correlation_distance (Pearson r)
    similarities = 1 - distances
    similarities = np.maximum(similarities, 0)   # clip negatives

    # Movies the target user has already rated
    user_ratings   = matrix.iloc[user_idx]
    already_rated  = set(user_ratings[user_ratings > 0].index)

    # Weighted average of neighbour ratings for unseen movies
    predicted_scores = {}
    for movie_id in matrix.columns:
        if movie_id in already_rated:
            continue
        neighbour_ratings = matrix.iloc[neighbor_idxs][movie_id].values
        weight_sum        = similarities[neighbour_ratings > 0].sum()
        if weight_sum == 0:
            continue
        predicted_scores[movie_id] = np.dot(
            similarities, neighbour_ratings
        ) / weight_sum

    if not predicted_scores:
        return []

    # Rank by predicted score
    ranked = sorted(predicted_scores.items(), key=lambda x: x[1], reverse=True)
    top_movie_ids = [mid for mid, _ in ranked[:top_n]]

    # Map movie_id → title
    id_to_title = dict(zip(movies_df["movie_id"], movies_df["title"]))
    return [id_to_title[mid] for mid in top_movie_ids if mid in id_to_title]
