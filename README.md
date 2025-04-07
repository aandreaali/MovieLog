# Movie Tracker App

A Python application to track and manage your movie watchlist with a user-friendly GUI interface.

## Features
- Add and manage movies with details (title, year, genre, rating)
- Fetch movie details from OMDB API
- Track watched/unwatched status
- Save data to CSV
- Modern GUI interface with Tkinter
- Data persistence using pandas

## Requirements
- Python 3.x
- pandas
- requests
- python-dotenv
- tkinter (included with Python)

## Installation
1. Clone the repository
```bash
git clone https://github.com/aandreaali/MovieLog.git
cd MovieLog
```

2. Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
- Create a `.env` file in the project root
- Add your OMDB API key:
```
OMDB_API_KEY=your_api_key_here
```

## Usage
Run the application:
```bash
python src/movie_tracker/movie_tracker.py
```

## Features in Detail
- **Movie Management**
  - Add new movies with title, year, genre, and rating
  - Mark movies as watched/unwatched
  - Delete movies from your collection
  - View all movies in a table format

- **OMDB Integration**
  - Fetch movie details automatically
  - Get accurate release years and genres
  - Access IMDB ratings

- **Data Persistence**
  - Save your movie collection to CSV
  - Load existing collection on startup
  - Automatic data backup

## Project Structure
```
MovieLog/
├── src/
│   └── movie_tracker/
│       ├── movie_tracker.py  # Main application file
│       └── __init__.py
├── data/
│   └── movies.csv           # Movie database
├── requirements.txt         # Project dependencies
├── .env                    # Environment variables
└── README.md               # This file
```

## License
MIT License

## Author
Andrea Alivernini 