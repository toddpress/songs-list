from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date
import urllib.parse
from database import DatabaseManager

app = Flask(__name__)
app.secret_key = 'your-secret-key-here-change-in-production'  # Change this in production!

def generate_youtube_search_url(artist, title):
    """Generate a YouTube search URL for the song"""
    query = f"{title} {artist}"
    search_query = urllib.parse.quote_plus(query)
    return f"https://www.youtube.com/results?search_query={search_query}"

def generate_lyrics_search_url(artist, title):
    """Generate a Google search URL for lyrics"""
    query = f"{title} {artist} lyrics"
    search_query = urllib.parse.quote_plus(query)
    return f"https://www.google.com/search?q={search_query}"

def generate_chords_search_url(artist, title):
    """Generate an Ultimate Guitar search URL for chords"""
    query = f"{title} {artist}"
    search_query = urllib.parse.quote_plus(query)
    return f"https://www.ultimate-guitar.com/search.php?search_type=title&value={search_query}"

@app.route('/')
def index():
    """Display all songs or search results"""
    search_query = request.args.get('search', '').strip()
    
    db = DatabaseManager()
    try:
        if search_query:
            songs = db.search_songs(search_query)
        else:
            songs = db.get_all_songs()
        
        return render_template('index.html', songs=songs, search_query=search_query)
    except Exception as e:
        flash(f'Database error: {e}', 'error')
        return render_template('index.html', songs=[], search_query=search_query)
    finally:
        db.disconnect()

@app.route('/add_song', methods=['POST'])
def add_song():
    """Add a new song to the database"""
    artist = request.form.get('artist', '').strip()
    title = request.form.get('title', '').strip()
    proficiency = request.form.get('proficiency', '☆☆☆☆☆')
    notes = request.form.get('notes', '').strip() or None
    
    if not artist or not title:
        flash('Artist and title are required!', 'error')
        return redirect(url_for('index'))
    
    # Auto-generate search links
    link = generate_youtube_search_url(artist, title)
    lyrics_link = generate_lyrics_search_url(artist, title)
    chords_link = generate_chords_search_url(artist, title)
    
    db = DatabaseManager()
    try:
        success = db.insert_song(artist, title, proficiency, link, lyrics_link, chords_link, notes)
        if success:
            flash(f'Successfully added "{title}" by {artist}!', 'success')
        else:
            flash('Failed to add song', 'error')
    except Exception as e:
        flash(f'Error adding song: {e}', 'error')
    finally:
        db.disconnect()
    
    return redirect(url_for('index'))

@app.route('/log_play/<int:song_id>', methods=['POST'])
def log_play(song_id):
    """Log a play for a song"""
    db = DatabaseManager()
    try:
        today = date.today()
        success = db.log_play(song_id, today)
        if success:
            flash('Play logged successfully!', 'success')
        else:
            flash('Failed to log play', 'error')
    except Exception as e:
        flash(f'Error logging play: {e}', 'error')
    finally:
        db.disconnect()
    
    return redirect(url_for('index'))

@app.route('/delete_song/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    """Delete a song from the database"""
    db = DatabaseManager()
    try:
        success = db.delete_song(song_id)
        if success:
            flash('Song deleted successfully!', 'success')
        else:
            flash('Failed to delete song', 'error')
    except Exception as e:
        flash(f'Error deleting song: {e}', 'error')
    finally:
        db.disconnect()
    
    return redirect(url_for('index'))

@app.route('/update_proficiency/<int:song_id>', methods=['POST'])
def update_proficiency(song_id):
    """Update the proficiency of a song"""
    proficiency = request.form.get('proficiency', '☆☆☆☆☆')
    
    db = DatabaseManager()
    try:
        # Get the current song data
        query = "SELECT artist, title, link, lyrics_link, chords_link, notes, last_played FROM songs WHERE id = %s"
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute(query, (song_id,))
        song = cursor.fetchone()
        cursor.close()
        
        if song:
            success = db.update_song(
                song_id, 
                song['artist'], 
                song['title'], 
                proficiency,
                song['link'], 
                song['lyrics_link'], 
                song['chords_link'],
                song['notes'],
                song['last_played']
            )
            if success:
                flash('Proficiency updated!', 'success')
            else:
                flash('Failed to update proficiency', 'error')
        else:
            flash('Song not found', 'error')
    except Exception as e:
        flash(f'Error updating proficiency: {e}', 'error')
    finally:
        db.disconnect()
    
    return redirect(url_for('index'))

@app.route('/edit_song/<int:song_id>', methods=['POST'])
def edit_song(song_id):
    """Edit an existing song"""
    artist = request.form.get('artist', '').strip()
    title = request.form.get('title', '').strip()
    proficiency = request.form.get('proficiency', '☆☆☆☆☆')
    link = request.form.get('link', '').strip() or None
    lyrics_link = request.form.get('lyrics_link', '').strip() or None
    chords_link = request.form.get('chords_link', '').strip() or None
    
    if not artist or not title:
        flash('Artist and title are required!', 'error')
        return redirect(url_for('index'))
    
    db = DatabaseManager()
    try:
        # Get the current last_played and notes values
        query = "SELECT notes, last_played FROM songs WHERE id = %s"
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute(query, (song_id,))
        song = cursor.fetchone()
        cursor.close()
        
        if song:
            success = db.update_song(
                song_id, 
                artist, 
                title, 
                proficiency,
                link, 
                lyrics_link, 
                chords_link,
                song['notes'],  # Preserve existing notes
                song['last_played']
            )
            if success:
                flash(f'Successfully updated "{title}" by {artist}!', 'success')
            else:
                flash('Failed to update song', 'error')
        else:
            flash('Song not found', 'error')
    except Exception as e:
        flash(f'Error updating song: {e}', 'error')
    finally:
        db.disconnect()
    
    return redirect(url_for('index'))

@app.route('/update_notes/<int:song_id>', methods=['POST'])
def update_notes(song_id):
    """Update notes for a song"""
    notes = request.form.get('notes', '').strip() or None
    
    db = DatabaseManager()
    try:
        # Get the current song data
        query = "SELECT artist, title, proficiency, link, lyrics_link, chords_link, last_played FROM songs WHERE id = %s"
        cursor = db.connection.cursor(dictionary=True)
        cursor.execute(query, (song_id,))
        song = cursor.fetchone()
        cursor.close()
        
        if song:
            success = db.update_song(
                song_id, 
                song['artist'], 
                song['title'], 
                song['proficiency'],
                song['link'], 
                song['lyrics_link'], 
                song['chords_link'],
                notes,
                song['last_played']
            )
            if success:
                flash('Notes updated successfully!', 'success')
            else:
                flash('Failed to update notes', 'error')
        else:
            flash('Song not found', 'error')
    except Exception as e:
        flash(f'Error updating notes: {e}', 'error')
    finally:
        db.disconnect()
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
