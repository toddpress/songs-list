import mysql.connector
from mysql.connector import Error
import pandas as pd
import streamlit as st
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
            st.error(f"Error connecting to MySQL: {e}")
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
            st.error(f"Database error: {e}")
            return None if fetch else False
    
    def get_all_songs(self):
        """Retrieve all songs from database"""
        query = """
        SELECT id, artist, title, proficiency, link, lyrics_link, chords_link 
        FROM songs 
        ORDER BY artist, title
        """
        return self.execute_query(query, fetch=True)
    
    def search_songs(self, search_term):
        """Search songs by artist or title"""
        query = """
        SELECT id, artist, title, proficiency, link, lyrics_link, chords_link 
        FROM songs 
        WHERE artist LIKE %s OR title LIKE %s
        ORDER BY artist, title
        """
        search_pattern = f"%{search_term}%"
        return self.execute_query(query, (search_pattern, search_pattern), fetch=True)
    
    def insert_song(self, artist, title, proficiency="☆☆☆☆☆", link=None, lyrics_link=None, chords_link=None):
        """Insert a new song into the database"""
        query = """
        INSERT INTO songs (artist, title, proficiency, link, lyrics_link, chords_link)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        return self.execute_query(query, (artist, title, proficiency, link, lyrics_link, chords_link))
    
    def update_song(self, song_id, artist, title, proficiency, link=None, lyrics_link=None, chords_link=None):
        """Update an existing song in the database"""
        query = """
        UPDATE songs 
        SET artist = %s, title = %s, proficiency = %s, link = %s, lyrics_link = %s, chords_link = %s
        WHERE id = %s
        """
        return self.execute_query(query, (artist, title, proficiency, link, lyrics_link, chords_link, song_id))
    
    def delete_song(self, song_id):
        """Delete a song from the database"""
        query = "DELETE FROM songs WHERE id = %s"
        return self.execute_query(query, (song_id,))
    
    def songs_to_dataframe(self, songs_data):
        """Convert songs data to pandas DataFrame"""
        if not songs_data:
            # Return empty DataFrame with correct columns
            return pd.DataFrame(columns=['id', 'artist', 'title', 'proficiency', 'link', 'lyrics_link', 'chords_link'])
        
        df = pd.DataFrame(songs_data)
        return df
    
    def dataframe_to_songs(self, df):
        """Convert DataFrame back to songs data for database operations"""
        songs_data = []
        for _, row in df.iterrows():
            song_data = {
                'id': row.get('id'),
                'artist': row['artist'],
                'title': row['title'],
                'proficiency': row['proficiency'],
                'link': row.get('link'),
                'lyrics_link': row.get('lyrics_link'),
                'chords_link': row.get('chords_link')
            }
            songs_data.append(song_data)
        return songs_data
    
    def sync_dataframe_to_database(self, df, original_df):
        """Sync changes from DataFrame back to database"""
        try:
            # Convert DataFrames to sets of tuples for comparison
            if not original_df.empty:
                original_songs = set(original_df[['id', 'artist', 'title', 'proficiency', 'link', 'lyrics_link', 'chords_link']].apply(tuple, axis=1))
            else:
                original_songs = set()
            
            current_songs = set()
            new_songs = []
            updated_songs = []
            
            for _, row in df.iterrows():
                if pd.isna(row.get('id')) or row.get('id') == '':
                    # New song (no ID)
                    new_songs.append(row)
                else:
                    current_songs.add(tuple(row[['id', 'artist', 'title', 'proficiency', 'link', 'lyrics_link', 'chords_link']]))
                    # Check if song was modified
                    original_row = original_df[original_df['id'] == row['id']]
                    if not original_row.empty:
                        original_tuple = tuple(original_row.iloc[0][['id', 'artist', 'title', 'proficiency', 'link', 'lyrics_link', 'chords_link']])
                        current_tuple = tuple(row[['id', 'artist', 'title', 'proficiency', 'link', 'lyrics_link', 'chords_link']])
                        if original_tuple != current_tuple:
                            updated_songs.append(row)
            
            # Find deleted songs
            if not original_df.empty:
                original_ids = set(original_df['id'].dropna())
                current_ids = set(df['id'].dropna()) if 'id' in df.columns else set()
                deleted_ids = original_ids - current_ids
            else:
                deleted_ids = set()
            
            # Perform database operations
            success = True
            
            # Insert new songs
            for _, song in pd.DataFrame(new_songs).iterrows() if new_songs else []:
                result = self.insert_song(
                    song['artist'], song['title'], song['proficiency'],
                    song.get('link'), song.get('lyrics_link'), song.get('chords_link')
                )
                if not result:
                    success = False
            
            # Update modified songs
            for _, song in pd.DataFrame(updated_songs).iterrows() if updated_songs else []:
                result = self.update_song(
                    song['id'], song['artist'], song['title'], song['proficiency'],
                    song.get('link'), song.get('lyrics_link'), song.get('chords_link')
                )
                if not result:
                    success = False
            
            # Delete removed songs
            for song_id in deleted_ids:
                result = self.delete_song(song_id)
                if not result:
                    success = False
            
            return success
            
        except Exception as e:
            st.error(f"Error syncing to database: {e}")
            return False