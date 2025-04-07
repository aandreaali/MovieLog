import tkinter as tk
from tkinter import ttk
import requests
import pandas as pd
import re  # For extracting the first 4 digits of the year

# ------------------------------ MEDIA & MOVIE CLASSES ------------------------------

class Media:
    """
    Base class to represent a general piece of media.
    Demonstrates inheritance: Movie will inherit from Media.
    """

    def __init__(self, title: str, year: int):
        # We use the property setters so we enforce 'not empty' for title, 
        # but no range constraints on year.
        self.title = title
        self.year = year

    @property
    def title(self):
        return self.__title

    @title.setter
    def title(self, value):
        if not value:
            raise ValueError("Title cannot be empty.")
        self.__title = value

    @property
    def year(self):
        return self.__year

    @year.setter
    def year(self, value):
        # No range checks; just store the integer.
        self.__year = value


class Movie(Media):
    """
    A specialized Media that includes genre, rating, and watched status.
    Demonstrates encapsulation via private attributes and getters/setters.
    """

    def __init__(self, title: str, year: int, genre: str, watched=False, rating=None):
        super().__init__(title, year)
        self.__genre = genre
        self.__watched = watched
        self.__rating = rating

    @property
    def genre(self):
        return self.__genre

    @genre.setter
    def genre(self, value):
        self.__genre = value or "Unknown"

    @property
    def watched(self):
        return self.__watched

    @watched.setter
    def watched(self, value):
        self.__watched = bool(value)

    @property
    def rating(self):
        return self.__rating

    @rating.setter
    def rating(self, value):
        if value is not None:
            if not (0 <= value <= 10):
                raise ValueError("Rating must be between 0 and 10.")
        self.__rating = value


# ------------------------------ MOVIE LIBRARY CLASS ------------------------------

class MovieLibrary:
    """
    Holds multiple Movie objects (composition).
    Also demonstrates using multiple lists, a while loop, and for loops.
    """

    def __init__(self):
        # Main list of movies
        self.__movies = []
        # Additional list: let's track unwatched movies separately
        self.__unwatched_movies = []

    def add_movie(self, movie: Movie):
        """Adds a Movie object to the library."""
        self.__movies.append(movie)
        self.__build_unwatched_list()

    def delete_movie_by_title(self, title_to_delete: str):
        """Delete movies matching the given title (case-insensitive)."""
        before_count = len(self.__movies)
        self.__movies = [
            m for m in self.__movies
            if m.title.lower() != title_to_delete.lower()
        ]
        after_count = len(self.__movies)
        self.__build_unwatched_list()
        return before_count - after_count  # number of deleted items

    def get_all_movies(self):
        """Return a list of all Movie objects."""
        return self.__movies

    def get_unwatched_movies(self):
        """Return a list of unwatched Movie objects."""
        return self.__unwatched_movies

    def __build_unwatched_list(self):
        """Rebuilds the self.__unwatched_movies list from self.__movies."""
        self.__unwatched_movies = [m for m in self.__movies if not m.watched]

    def ensure_valid_ratings(self):
        """
        Demonstrates a while loop.
        If any rating is invalid, set it to None.
        """
        i = 0
        while i < len(self.__movies):
            movie = self.__movies[i]
            if movie.rating is not None and (movie.rating < 0 or movie.rating > 10):
                movie.rating = None
            i += 1

    # ----------------- CSV & Pandas Integration -----------------

    def load_from_csv(self, filename="movies.csv"):
        """Load movies from a CSV using pandas, converting rows to Movie objects."""
        try:
            df = pd.read_csv(filename)
        except FileNotFoundError:
            print("No existing CSV found. Starting with an empty library.")
            return

        for _, row in df.iterrows():
            title = row.get("Title", "")
            # default to 2000 if year is missing or invalid
            year = int(row.get("Year", 2000))
            genre = row.get("Genre", "")
            watched = bool(row.get("Watched", False))
            rating = row.get("Rating", None)
            if pd.isnull(rating):
                rating = None
            else:
                rating = float(rating)

            try:
                movie = Movie(title, year, genre, watched, rating)
                self.add_movie(movie)
            except ValueError as e:
                print(f"Skipping invalid movie row: {e}")

    def save_to_csv(self, filename="movies.csv"):
        """Save current movies to a CSV via pandas."""
        data = []
        for m in self.__movies:
            data.append({
                "Title": m.title,
                "Year": m.year,
                "Genre": m.genre,
                "Watched": m.watched,
                "Rating": m.rating
            })
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)

# ------------------------------ MOVIELOG APP CLASS ------------------------------

class MovieLogApp(tk.Tk):
    """
    Main Tkinter application. Inherits from tk.Tk (demonstrating inheritance).
    Encapsulates the UI logic. Composes a MovieLibrary instance.
    """

    def __init__(self, api_key="YOUR_OMDB_API_KEY"):
        super().__init__()
        self.title("MovieLog")
        self.geometry("800x500")

        # The library is composed here
        self.library = MovieLibrary()
        self.library.load_from_csv("movies.csv")  # Load existing data

        self.api_key = api_key

        # Set up the UI
        self._setup_ui()

    def _setup_ui(self):
        """Create frames, widgets, and layout (no brand bar)."""
        self.main_frame = ttk.Frame(self, padding=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # row=0: Title + Fetch
        ttk.Label(self.main_frame, text="Title").grid(row=0, column=0, padx=5, pady=5, sticky="W")
        self.entry_title = ttk.Entry(self.main_frame, width=30)
        self.entry_title.grid(row=0, column=1, padx=5, pady=5, sticky="W")

        fetch_btn = ttk.Button(self.main_frame, text="Fetch Details", command=self.fetch_movie_details)
        fetch_btn.grid(row=0, column=2, padx=5, pady=5)

        # row=1: Year
        ttk.Label(self.main_frame, text="Year").grid(row=1, column=0, padx=5, pady=5, sticky="W")
        self.entry_year = ttk.Entry(self.main_frame, width=10)
        self.entry_year.grid(row=1, column=1, padx=5, pady=5, sticky="W")

        # row=2: Genre
        ttk.Label(self.main_frame, text="Genre").grid(row=2, column=0, padx=5, pady=5, sticky="W")
        self.entry_genre = ttk.Entry(self.main_frame, width=20)
        self.entry_genre.grid(row=2, column=1, padx=5, pady=5, sticky="W")

        # row=3: Rating
        ttk.Label(self.main_frame, text="Rating (0-10)").grid(row=3, column=0, padx=5, pady=5, sticky="W")
        self.entry_rating = ttk.Entry(self.main_frame, width=5)
        self.entry_rating.grid(row=3, column=1, padx=5, pady=5, sticky="W")

        # row=4: Watched
        self.var_watched = tk.BooleanVar()
        watched_cb = ttk.Checkbutton(self.main_frame, text="Watched", variable=self.var_watched)
        watched_cb.grid(row=4, column=1, padx=5, pady=5, sticky="W")

        # row=5: Buttons
        add_btn = ttk.Button(self.main_frame, text="Add Movie", command=self.add_movie)
        add_btn.grid(row=5, column=0, padx=5, pady=5)

        delete_btn = ttk.Button(self.main_frame, text="Delete Selected", command=self.delete_selected_movie)
        delete_btn.grid(row=5, column=1, padx=5, pady=5)

        refresh_btn = ttk.Button(self.main_frame, text="Refresh List", command=self.refresh_list)
        refresh_btn.grid(row=5, column=2, padx=5, pady=5)

        # row=6: Treeview
        columns = ("Title", "Year", "Genre", "Rating", "Watched")
        self.tree = ttk.Treeview(self.main_frame, columns=columns, show="headings", height=12)
        self.tree.heading("Title", text="Title")
        self.tree.heading("Year", text="Year")
        self.tree.heading("Genre", text="Genre")
        self.tree.heading("Rating", text="Rating")
        self.tree.heading("Watched", text="Watched")

        self.tree.column("Title", width=200)
        self.tree.column("Year", width=50, anchor=tk.CENTER)
        self.tree.column("Genre", width=100)
        self.tree.column("Rating", width=60, anchor=tk.CENTER)
        self.tree.column("Watched", width=70, anchor=tk.CENTER)

        self.tree.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky="nsew")

        # Make the table area expandable
        self.main_frame.rowconfigure(6, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        # Initial display
        self.refresh_list()

    # ------------------------------ BUTTON HANDLERS ------------------------------

    def fetch_movie_details(self):
        """Fetch details from OMDb for the given title and populate fields."""
        title = self.entry_title.get().strip()
        if not title:
            print("Please enter a movie title first.")
            return

        url = f"http://www.omdbapi.com/?apikey={self.api_key}&t={title}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if data.get("Response") == "True":
                # Extract the first 4 digits from the 'Year' (handles '2016–2025' etc.)
                omdb_year = data.get("Year", "")
                match = re.match(r"(\d{4})", omdb_year)  # look for a 4-digit year at start
                if match:
                    omdb_year = match.group(1)
                else:
                    omdb_year = ""

                # Populate the fields
                self.entry_title.delete(0, tk.END)
                self.entry_title.insert(0, data.get("Title", ""))

                self.entry_year.delete(0, tk.END)
                self.entry_year.insert(0, omdb_year)

                self.entry_genre.delete(0, tk.END)
                self.entry_genre.insert(0, data.get("Genre", ""))

                self.entry_rating.delete(0, tk.END)
                self.entry_rating.insert(0, data.get("imdbRating", ""))
            else:
                print("Movie not found:", data.get("Error"))
        else:
            print("HTTP Error:", response.status_code)

    def add_movie(self):
        """Add a new movie to the library, ensuring year is a valid integer but no range limit."""
        title = self.entry_title.get().strip()
        year_str = self.entry_year.get().strip()
        genre = self.entry_genre.get().strip()
        rating_str = self.entry_rating.get().strip()
        watched = self.var_watched.get()

        # Parse year safely using try/except
        try:
            year = int(year_str)
        except ValueError:
            print("Year must be a number.")
            return

        # Conditionals for rating
        if rating_str == "":
            rating = None
        else:
            try:
                rating = float(rating_str)
            except ValueError:
                print("Rating must be a number (0-10).")
                return

            if rating < 0:
                print("Rating cannot be negative.")
                return
            elif rating > 10:
                print("Rating must be <= 10.")
                return

        # Attempt to create and add the Movie
        try:
            movie = Movie(title, year, genre, watched, rating)
            self.library.add_movie(movie)
            self.library.save_to_csv("movies.csv")
        except ValueError as e:
            print("Error adding movie:", e)
            return

        # Clear fields
        self.entry_title.delete(0, tk.END)
        self.entry_year.delete(0, tk.END)
        self.entry_genre.delete(0, tk.END)
        self.entry_rating.delete(0, tk.END)
        self.var_watched.set(False)

        self.refresh_list()

    def delete_selected_movie(self):
        """Delete the selected row(s) from the Treeview and library."""
        selected_items = self.tree.selection()
        if not selected_items:
            print("No movie selected.")
            return

        for item_id in selected_items:
            values = self.tree.item(item_id, "values")
            title_to_delete = values[0]
            deleted_count = self.library.delete_movie_by_title(title_to_delete)
            print(f"Deleted {deleted_count} movie(s) titled '{title_to_delete}'.")

        self.library.save_to_csv("movies.csv")
        self.refresh_list()

    def refresh_list(self):
        """Refresh the Treeview from the MovieLibrary."""
        # Clear existing rows
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert updated rows
        for m in self.library.get_all_movies():
            rating_str = "" if m.rating is None else str(m.rating)
            watched_str = "Yes" if m.watched else "No"
            self.tree.insert(
                "",
                tk.END,
                values=(m.title, m.year, m.genre, rating_str, watched_str)
            )


# ------------------------------ MAIN ENTRY POINT ------------------------------

if __name__ == "__main__":
    # Create a movie library object
    my_library = MovieLibrary()
    
    # Load existing movies from CSV - these are our objects!
    my_library.load_from_csv("movies.csv")
    
    # Create the GUI application object
    app = MovieLogApp(api_key="9763440c")
    
    # Demonstrate object usage with our existing movies
    print("\nCurrent Movie Library:")
    for movie in my_library.get_all_movies():
        print(f"\nMovie Object: {movie.title}")
        print(f"Properties:")
        print(f"- Title: {movie.title}")
        print(f"- Year: {movie.year}")
        print(f"- Genre: {movie.genre}")
        print(f"- Watched: {movie.watched}")
        print(f"- Rating: {movie.rating}")
    
    # Show unwatched movies (demonstrating object methods)
    print("\nUnwatched Movies:")
    for movie in my_library.get_unwatched_movies():
        print(f"Need to watch: {movie.title}")
    
    # Run the GUI application
    app.mainloop()