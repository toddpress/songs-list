# ./main.py
import streamlit as st
import pandas as pd
import urllib.parse
import time

from pytube import Search
from database import DatabaseManager

st.set_page_config(page_title="Linkify Songs List", page_icon="🎸")

def add_youtube_links_to_df():
    df = st.session_state.edited_df
    unsaved_songs = df[
        (df["link"].isna() | (df["link"] == "")) & 
        ~df["title"].isna() & ~df["artist"].isna()
    ]
    for index, row in unsaved_songs.iterrows():
        try:
            query = f"{row['title']} {row['artist']}"
            search = Search(query)
            video = search.results[0]
            yt_link = f"https://www.youtube.com/watch?v={video.video_id}"
            st.session_state.edited_df.at[index, "link"] = yt_link

        except IndexError:
            st.warning(f"No YouTube video found for {row['title']} by {row['artist']}")

        except Exception as e:
            st.error(
                body=f"Error searching YouTube for {row['title']} by {row['artist']}: {e}",
                icon=":material/error:"
            )

def add_lyrics_search_links_to_df():
    df = st.session_state.edited_df
    unsaved_songs = df[
        (df["lyrics_link"].isna() | (df["lyrics_link"] == "")) & 
        ~df["title"].isna() & ~df["artist"].isna()
    ]
    for index, row in unsaved_songs.iterrows():
        try:
            query = f"{row['title']} {row['artist']} lyrics"
            search_query = urllib.parse.quote_plus(query)
            search_link = f"https://www.google.com/search?q={search_query}"
            st.session_state.edited_df.at[index, "lyrics_link"] = search_link

        except Exception as e:
            st.error(
                body=f"Error creating lyrics link for {row['title']} by {row['artist']}: {e}",
                icon=":material/error:"
            )

def add_chords_search_links_to_df():
    df = st.session_state.edited_df
    unsaved_songs = df[
        (df["chords_link"].isna() | (df["chords_link"] == "")) & 
        ~df["title"].isna() & ~df["artist"].isna()
    ]
    for index, row in unsaved_songs.iterrows():
        try:
            query = f"{row['title']} {row['artist']}"
            search_query = urllib.parse.quote_plus(query)
            search_link = f"https://www.ultimate-guitar.com/search.php?search_type=title&value={search_query}"
            st.session_state.edited_df.at[index, "chords_link"] = search_link

        except Exception as e:
            st.error(
                body=f"Error creating chords link for {row['title']} by {row['artist']}: {e}",
                icon=":material/error:"
            )

def handle_save_changes():
    # Initialize database connection
    db = DatabaseManager()
    
    try:
        add_youtube_links_to_df()
        add_lyrics_search_links_to_df()
        add_chords_search_links_to_df()

        # Sync changes to database
        success = db.sync_dataframe_to_database(st.session_state.edited_df, st.session_state.original_df)
        
        if success:
            st.success(
                body='Saved Changes to Database',
                icon=":material/thumb_up:"
            )
            st.balloons()
            time.sleep(2)  # Give the balloons time to fly before dom refresh
            st.rerun()  # Manually re-render with updated data
        else:
            st.error("Failed to save changes to database")
    
    finally:
        db.disconnect()


def get_df_from_database(search_query=None):
    """Load songs from database and return as DataFrame"""
    db = DatabaseManager()
    
    try:
        if search_query:
            songs_data = db.search_songs(search_query)
        else:
            songs_data = db.get_all_songs()
        
        return db.songs_to_dataframe(songs_data)
    
    finally:
        db.disconnect()

def main():
    st.title("Songs List Editor")

    # Add search functionality
    search_query = st.text_input("Search songs by artist or title")

    # Load and store the original DataFrame from database
    try:
        original_df = get_df_from_database(search_query if search_query else None)
        st.session_state.original_df = original_df
        songs_df = original_df.copy()
    except Exception as e:
        st.error(f"Error connecting to database: {e}")
        st.info("Please ensure MySQL is running and the database is properly configured.")
        return

    # Column order and sort by artist
    columns_order = ["artist", "title", "proficiency", "link", "lyrics_link", "chords_link"]
    
    # Ensure all columns exist
    for col in columns_order:
        if col not in songs_df.columns:
            songs_df[col] = ""
    
    songs_df = songs_df[columns_order]
    
    if not songs_df.empty:
        songs_df = songs_df.sort_values(by="artist")
    
    # Reset the index to prevent it from showing as a column
    songs_df.reset_index(drop=True, inplace=True)

    st.session_state.edited_df = st.data_editor(
        data=songs_df,
        num_rows="dynamic",
        column_config={
            "artist": st.column_config.TextColumn("Artist"),
            "title": st.column_config.TextColumn("Song"),
            "proficiency": st.column_config.SelectboxColumn(
                "Proficiency",
                options=[
                    "☆☆☆☆☆",
                    "★☆☆☆☆",
                    "★★☆☆☆",
                    "★★★☆☆",
                    "★★★★☆",
                    "★★★★★"
                ],
                default="☆☆☆☆☆"
            ),
            "link": st.column_config.LinkColumn(
                "YT Link",
                disabled=True,
                display_text="Listen on YouTube",
            ),
            "lyrics_link": st.column_config.LinkColumn(
                "Lyrics Link",
                disabled=True,
                display_text="Find Lyrics on Google",
            ),
            "chords_link": st.column_config.LinkColumn(
                "Chords Link",
                disabled=True,
                display_text="Find Chords on UG.com",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    if st.button(
        label="Save Changes",
        help="Save the changes made to the songs list",
    ):
        handle_save_changes()

if __name__ == "__main__":
    main()
