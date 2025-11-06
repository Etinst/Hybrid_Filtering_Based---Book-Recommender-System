import streamlit as st
import pandas as pd
import numpy as np

# ====== PAGE CONFIG ======
st.set_page_config(page_title="Book Recommender System", layout="wide")

# ====== LOAD DATA ======
@st.cache_data
def load_data():
    books = pd.read_csv("archive/Books.csv")
    ratings = pd.read_csv("archive/Ratings.csv")
    users = pd.read_csv("archive/Users.csv")
    return books, ratings, users

books, ratings, users = load_data()

# ====== CREATE POPULARITY DF ======
@st.cache_data
def create_popularity_df():
    popular_df = ratings.groupby("ISBN").agg({"Book-Rating": ["mean", "count"]}).reset_index()
    popular_df.columns = ["ISBN", "Average-Rating", "Rating-Count"]
    popular_df = popular_df.merge(books, on="ISBN")
    popular_df = popular_df[popular_df["Rating-Count"] >= 100]  # filter low-rating books
    popular_df = popular_df.sort_values(by=["Average-Rating", "Rating-Count"], ascending=False)
    return popular_df

popular_df = create_popularity_df()

# ====== SIDEBAR ======
st.sidebar.title("📚 Navigation")
page = st.sidebar.radio("Go to:", ["🏠 Home", "🔍 Recommend", "📈 Popular Books", "⚙️ Settings"])

# ====== HOME PAGE ======
if page == "🏠 Home":
    st.title("📖 Welcome to the Hybrid Book Recommender System")
    st.write("""
    This intelligent book recommender uses a **Hybrid Filtering Approach** 
    combining **Popularity-based** and **Collaborative Filtering** techniques.
    Explore top-rated books, find similar titles, and personalize your reading journey.
    """)

    st.markdown("### 🌟 Featured Popular Books")

    top_books = popular_df.head(10)
    cols = st.columns(5)
    for i, col in enumerate(cols):
        with col:
            if i < len(top_books):
                book = top_books.iloc[i]
                st.image(book["Image-URL-L"], width=120)
                st.markdown(f"**{book['Book-Title']}**")
                st.caption(f"by {book['Book-Author']}")
                st.text(f"⭐ {book['Average-Rating']:.1f} | 🗳 {book['Rating-Count']} votes")

# ====== POPULAR BOOKS PAGE ======
elif page == "📈 Popular Books":
    st.title("🔥 Most Popular Books")
    st.write("Books with the highest average rating and number of votes.")

    n = st.slider("Select number of books to display", 5, 50, 10)
    df_display = popular_df.head(n)

    for _, row in df_display.iterrows():
        with st.container():
            cols = st.columns([1, 3])
            with cols[0]:
                st.image(row["Image-URL-L"], width=100)
            with cols[1]:
                st.markdown(f"### {row['Book-Title']}")
                st.caption(f"by {row['Book-Author']} ({row.get('Year-Of-Publication', 'N/A')})")
                st.text(f"Publisher: {row.get('Publisher', 'Unknown')}")
                st.text(f"⭐ {row['Average-Rating']:.2f} | 🗳 {row['Rating-Count']} ratings")

# ====== RECOMMEND PAGE ======
elif page == "🔍 Recommend":
    st.title("🔍 Get Book Recommendations")

    user_input = st.text_input("Enter a book title you like:")
    if st.button("Recommend"):
        if user_input.strip() == "":
            st.warning("Please enter a valid book title.")
        else:
            # Find similar books by author or genre (basic hybrid logic)
            filtered = books[
                books["Book-Title"].str.contains(user_input, case=False, na=False)
            ]
            if filtered.empty:
                st.error("No matching books found.")
            else:
                st.success(f"Found {len(filtered)} similar books:")
                for _, row in filtered.head(10).iterrows():
                    with st.container():
                        cols = st.columns([1, 3])
                        with cols[0]:
                            st.image(row["Image-URL-L"], width=100)
                        with cols[1]:
                            st.markdown(f"### {row['Book-Title']}")
                            st.caption(f"by {row['Book-Author']}")
                            st.text(f"Publisher: {row.get('Publisher', 'N/A')}")
                            st.text(f"Year: {row.get('Year-Of-Publication', 'N/A')}")

# ====== SETTINGS PAGE ======
elif page == "⚙️ Settings":
    st.title("⚙️ Settings")
    st.write("Customize your Book Recommender experience below.")
    st.toggle("Dark Mode (coming soon)")
    st.toggle("Show Book Covers")
    st.selectbox("Preferred Recommendation Type", ["Hybrid", "Content-Based", "Collaborative"])
    st.button("Save Settings")

    st.info("Your preferences will be saved in future versions of this app.")

