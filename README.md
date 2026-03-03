🎬 Movie Recommendation System

This project is a simple Movie Recommendation System built using Python, Pandas, and Scikit-learn.

It recommends movies based on similarity of genres and overview using Content-Based Filtering and Cosine Similarity.

📌 Objective

To build a movie recommendation system that suggests similar movies based on selected movie title.

🛠 Technologies Used

Python

Pandas

NumPy

Scikit-learn

📂 Dataset

TMDB 5000 Movie Dataset
(Downloaded from Kaggle)

The dataset contains:

Movie title

Genres

Overview

⚙️ Working

Load the movie dataset

Select important columns (title, genres, overview)

Convert text data into numerical form

Apply cosine similarity

Recommend top 5 similar movies
