# Songs List Application

A simple web application for managing your song list with proficiency tracking and play logging.

## Features

- 🎵 Display songs in a clean, non-interactive table
- ➕ Add songs via a modal form
- 🎸 Track proficiency level (1-5 stars)
- 📅 Log when you last played each song
- 🔗 Store links to YouTube, lyrics, and chords
- 🔍 Search songs by artist or title
- 🗑️ Delete songs

## Setup

### 1. Update Database Schema

First, add the `last_played` column to your existing database:

```bash
mysql -u root -p songs_list_db -e "ALTER TABLE songs ADD COLUMN last_played DATE AFTER chords_link, ADD INDEX idx_last_played (last_played);"
```

### 2. Install Dependencies

Activate your virtual environment and install the new dependencies:

```bash
source song_list_env/bin/activate
pip install -r requirements.txt
```

### 3. Run the Application

Start the Flask server:

```bash
python app.py
```

The application will be available at: `http://localhost:5000`

## Usage

### Adding a Song
1. Click the "Add Song" button in the header
2. Fill in the song details (artist and title are required)
3. Click "Add Song" to save

### Logging a Play
- Click the "Log Play" button next to any song to record today's date

### Searching
- Type in the search box to filter songs by artist or title

### Deleting a Song
- Click the "Delete" button next to any song (will ask for confirmation)

## Configuration

Edit `config.py` to update your database connection settings.

## Development

The application uses:
- **Flask** for the web framework
- **MySQL** for data storage
- **Jinja2** for HTML templates
- Pure CSS for styling (no external CSS frameworks)
