from pathlib import Path

import pandas as pd
import streamlit as st


DATA_DIR = Path("archive")
BOOKS_FILE = DATA_DIR / "Books.csv"
RATINGS_FILE = DATA_DIR / "Ratings.csv"
USERS_FILE = DATA_DIR / "Users.csv"

MIN_RATINGS_DEFAULT = 80


st.set_page_config(page_title="Book Recommender System", layout="wide")


@st.cache_data
def load_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    missing_files = [
        str(path) for path in (BOOKS_FILE, RATINGS_FILE, USERS_FILE) if not path.exists()
    ]
    if missing_files:
        raise FileNotFoundError(
            "Missing dataset files: "
            + ", ".join(missing_files)
            + ". Create an archive folder and place Books.csv, Ratings.csv, and Users.csv inside it."
        )

    books = pd.read_csv(BOOKS_FILE, low_memory=False)
    ratings = pd.read_csv(RATINGS_FILE)
    users = pd.read_csv(USERS_FILE)

    books = books.drop_duplicates(subset="ISBN").copy()
    ratings = ratings.dropna(subset=["ISBN", "User-ID", "Book-Rating"]).copy()
    ratings["Book-Rating"] = pd.to_numeric(ratings["Book-Rating"], errors="coerce")
    ratings = ratings.dropna(subset=["Book-Rating"])

    return books, ratings, users


@st.cache_data
def create_book_scores(books: pd.DataFrame, ratings: pd.DataFrame) -> pd.DataFrame:
    rating_summary = (
        ratings.groupby("ISBN")
        .agg(average_rating=("Book-Rating", "mean"), rating_count=("Book-Rating", "count"))
        .reset_index()
    )

    scored_books = books.merge(rating_summary, on="ISBN", how="left")
    scored_books["average_rating"] = scored_books["average_rating"].fillna(0)
    scored_books["rating_count"] = scored_books["rating_count"].fillna(0).astype(int)
    scored_books["Book-Title"] = scored_books["Book-Title"].fillna("Unknown Title")
    scored_books["Book-Author"] = scored_books["Book-Author"].fillna("Unknown Author")
    scored_books["Publisher"] = scored_books["Publisher"].fillna("Unknown Publisher")
    scored_books["Year-Of-Publication"] = scored_books["Year-Of-Publication"].fillna("Unknown")
    return scored_books


def show_dataset_error(error: Exception) -> None:
    st.title("Book Recommender System")
    st.error(str(error))
    st.markdown(
        """
        To run this app, download the Book-Crossing dataset and keep the files like this:

        ```text
        archive/
          Books.csv
          Ratings.csv
          Users.csv
        ```

        After adding the files, restart Streamlit.
        """
    )


def book_image(row: pd.Series, width: int = 95) -> None:
    image_url = row.get("Image-URL-L")
    if isinstance(image_url, str) and image_url.startswith("http"):
        st.image(image_url, width=width)
    else:
        st.caption("No cover")


def show_book_card(row: pd.Series) -> None:
    with st.container(border=True):
        cols = st.columns([1, 4])
        with cols[0]:
            book_image(row)
        with cols[1]:
            st.subheader(row["Book-Title"])
            st.caption(f"by {row['Book-Author']}")
            st.write(f"Publisher: {row.get('Publisher', 'Unknown')}")
            st.write(f"Year: {row.get('Year-Of-Publication', 'Unknown')}")
            st.write(
                f"Average rating: {row['average_rating']:.2f} | Ratings: {int(row['rating_count'])}"
            )


def recommend_books(
    query: str,
    scored_books: pd.DataFrame,
    min_ratings: int,
    limit: int,
) -> pd.DataFrame:
    clean_query = query.strip().lower()
    if not clean_query:
        return scored_books.head(0)

    matches = scored_books[
        scored_books["Book-Title"].str.lower().str.contains(clean_query, na=False)
        | scored_books["Book-Author"].str.lower().str.contains(clean_query, na=False)
    ].copy()

    if matches.empty:
        return matches

    matches = matches[matches["rating_count"] >= min_ratings]
    matches["hybrid_score"] = (
        matches["average_rating"] * 0.7
        + (matches["rating_count"] / max(matches["rating_count"].max(), 1)) * 3
    )
    return matches.sort_values(
        by=["hybrid_score", "average_rating", "rating_count"],
        ascending=False,
    ).head(limit)


try:
    books_df, ratings_df, users_df = load_data()
except Exception as exc:
    show_dataset_error(exc)
    st.stop()

scored_books_df = create_book_scores(books_df, ratings_df)

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Recommend", "Popular Books", "Dataset Summary", "Settings"],
)

st.sidebar.divider()
min_ratings = st.sidebar.slider(
    "Minimum ratings",
    min_value=0,
    max_value=300,
    value=MIN_RATINGS_DEFAULT,
    step=10,
)
show_covers = st.sidebar.toggle("Show book covers", value=True)

if not show_covers:
    book_image = lambda row, width=95: st.caption("Cover hidden")

if page == "Home":
    st.title("Hybrid Filtering Based Book Recommender System")
    st.write(
        "This app recommends books using a simple hybrid idea: it searches by title "
        "or author, then ranks matching books using rating quality and rating count."
    )

    st.subheader("Featured Popular Books")
    featured = scored_books_df[scored_books_df["rating_count"] >= min_ratings].sort_values(
        by=["average_rating", "rating_count"],
        ascending=False,
    )

    cols = st.columns(5)
    for index, (_, book) in enumerate(featured.head(5).iterrows()):
        with cols[index]:
            book_image(book, width=110)
            st.markdown(f"**{book['Book-Title']}**")
            st.caption(f"by {book['Book-Author']}")
            st.write(f"{book['average_rating']:.1f} rating")

elif page == "Popular Books":
    st.title("Popular Books")
    st.write("Books are sorted by average rating and number of ratings.")

    display_count = st.slider("Number of books", 5, 50, 10)
    popular_books = (
        scored_books_df[scored_books_df["rating_count"] >= min_ratings]
        .sort_values(by=["average_rating", "rating_count"], ascending=False)
        .head(display_count)
    )

    for _, row in popular_books.iterrows():
        show_book_card(row)

elif page == "Recommend":
    st.title("Get Book Recommendations")

    user_input = st.text_input("Enter a book title or author you like")
    result_count = st.slider("Recommendations to show", 3, 20, 10)

    if st.button("Recommend"):
        recommendations = recommend_books(
            user_input,
            scored_books=scored_books_df,
            min_ratings=min_ratings,
            limit=result_count,
        )

        if not user_input.strip():
            st.warning("Please enter a book title or author.")
        elif recommendations.empty:
            st.error("No matching books found with the current filters.")
        else:
            st.success(f"Showing {len(recommendations)} recommendations.")
            for _, row in recommendations.iterrows():
                show_book_card(row)

elif page == "Dataset Summary":
    st.title("Dataset Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Books", f"{len(books_df):,}")
    col2.metric("Ratings", f"{len(ratings_df):,}")
    col3.metric("Users", f"{len(users_df):,}")

    st.subheader("Top Authors by Number of Books")
    top_authors = (
        books_df["Book-Author"]
        .fillna("Unknown Author")
        .value_counts()
        .head(10)
        .rename_axis("Author")
        .reset_index(name="Books")
    )
    st.dataframe(top_authors, use_container_width=True)

elif page == "Settings":
    st.title("Settings")
    st.write("These controls are kept simple for learning and demonstration.")
    st.info(
        "Use the sidebar to change minimum ratings and cover visibility. "
        "Lower minimum ratings show more books, while higher values show more trusted books."
    )
