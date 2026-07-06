# Hybrid Filtering Based Book Recommender System

**Made by:** Darshan Nitin Barhate

This is a Streamlit web app that recommends books using a simple hybrid filtering idea. The app searches books by title or author and then ranks the matching books using both average rating and number of ratings.

The project is based on the Book-Crossing dataset. It includes a notebook for data exploration and a Streamlit app for the final user interface.

## What This Project Does

- Shows popular books from the dataset.
- Recommends books using title or author search.
- Ranks results using a simple hybrid score.
- Shows dataset summary information.
- Handles missing dataset files with a clear message instead of crashing.
- Lets the user change the minimum rating count from the sidebar.
- Lets the user hide or show book covers.

## Improvements Made

- Added a proper `README.md` file for setup and explanation.
- Added `requirements.txt` so dependencies are easy to install.
- Added `.gitignore` to avoid uploading dataset files, cache files, and virtual environments.
- Improved `app.py` so missing dataset files show a helpful instruction screen.
- Cleaned duplicated and missing book data before recommendation.
- Added a simple hybrid ranking formula using average rating and rating count.
- Added a dataset summary page with counts for books, users, and ratings.
- Made the sidebar controls useful for filtering recommendations.
- Kept the code beginner-friendly so it can be explained easily.

## Project Files

| File | Purpose |
| --- | --- |
| `app.py` | Main Streamlit web app. |
| `Book Recommender System.ipynb` | Notebook used for data study and recommender experiments. |
| `requirements.txt` | Python packages needed to run the project. |
| `README.md` | Setup and project explanation. |
| `Book_Recommender_Improvement_Report.tex` | LaTeX report explaining the project and improvements. |
| `.gitignore` | Keeps large/private/generated files out of version control. |

## Dataset Setup

The dataset files are not included inside this zip because they can be large. Create a folder named `archive` in the project directory and place these files inside it:

```text
archive/
  Books.csv
  Ratings.csv
  Users.csv
```

The app expects these exact file names.

## Installation

Use Python 3.10 or newer.

```bash
pip install -r requirements.txt
```

## How to Run

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Simple Explanation

The project loads three CSV files:

- `Books.csv` has book details such as title, author, publisher, year, and cover image.
- `Ratings.csv` has user ratings for books.
- `Users.csv` has user information.

The app first calculates the average rating and total rating count for each book. When the user enters a book title or author, the app finds matching books and ranks them using this simple score:

```text
hybrid_score = average_rating * 0.7 + normalized_rating_count * 3
```

This means a book gets a better rank when it has both a good rating and enough people rating it.

## Pages in the App

- **Home:** Shows the project idea and featured popular books.
- **Recommend:** Lets the user enter a title or author and get recommendations.
- **Popular Books:** Shows top books based on rating and rating count.
- **Dataset Summary:** Shows total books, ratings, users, and top authors.
- **Settings:** Explains the sidebar controls.

## Notes

- If the app says dataset files are missing, check the `archive` folder.
- If images do not load, the image URL in the dataset may be broken.
- Lowering the minimum rating count shows more books.
- Increasing the minimum rating count gives fewer but more trusted results.

