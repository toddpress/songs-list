import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Establish connection to MySQL database"""
        try:
            self.connection = mysql.connector.connect(**DB_CONFIG)
            if self.connection.is_connected():
                print("Successfully connected to MySQL database")
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None
    
    def disconnect(self):
        """Close database connection"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("MySQL connection closed")
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query and optionally fetch results"""
        if not self.connection or not self.connection.is_connected():
            self.connect()
        
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                cursor.close()
                return result
            else:
                self.connection.commit()
                cursor.close()
                return True
        except Error as e:
            print(f"Database error: {e}")
            return None if fetch else False
    
    def get_all_songs(self):
        """Retrieve all songs from database"""
        query = """
        SELECT id, artist, title, proficiency, link, lyrics_link, chords_link, notes, last_played 
        FROM songs 
        ORDER BY artist, title
        """
        return self.execute_query(query, fetch=True)
    
    def search_songs(self, search_term):
        """Search songs by artist or title"""
        query = """
        SELECT id, artist, title, proficiency, link, lyrics_link, chords_link, notes, last_played 
        FROM songs 
        WHERE artist LIKE %s OR title LIKE %s
        ORDER BY artist, title
        """
        search_pattern = f"%{search_term}%"
        return self.execute_query(query, (search_pattern, search_pattern), fetch=True)
    
    def insert_song(self, artist, title, proficiency="☆☆☆☆☆", link=None, lyrics_link=None, chords_link=None, notes=None, last_played=None):
        """Insert a new song into the database"""
        query = """
        INSERT INTO songs (artist, title, proficiency, link, lyrics_link, chords_link, notes, last_played)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (artist, title, proficiency, link, lyrics_link, chords_link, notes, last_played))
    
    def update_song(self, song_id, artist, title, proficiency, link=None, lyrics_link=None, chords_link=None, notes=None, last_played=None):
        """Update an existing song in the database"""
        query = """
        UPDATE songs 
        SET artist = %s, title = %s, proficiency = %s, link = %s, lyrics_link = %s, chords_link = %s, notes = %s, last_played = %s
        WHERE id = %s
        """
        return self.execute_query(query, (artist, title, proficiency, link, lyrics_link, chords_link, notes, last_played, song_id))
    
    def delete_song(self, song_id):
        """Delete a song from the database"""
        query = "DELETE FROM songs WHERE id = %s"
        return self.execute_query(query, (song_id,))
    
    def log_play(self, song_id, play_date):
        """Update the last_played date for a song"""
        query = "UPDATE songs SET last_played = %s WHERE id = %s"
        return self.execute_query(query, (play_date, song_id))