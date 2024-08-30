# ./main.py
import streamlit as st
import pandas as pd
import urllib.parse
import time

from pytube import Search

st.set_page_config(page_title="Linkify Songs List", page_icon="🎸")

def add_youtube_links_to_df():
    df = st.session_state.edited_df
    unsaved_songs = df[
        df["link"].isna() & ~df["title"].isna() & ~df["artist"].isna()
    ]
    for index, row in unsaved_songs.iterrows():
        try:
            query =f"{row['title']} {row['artist']}"
            search = Search(query)
            video = search.results[0]
            yt_link = f"https://www.youtube.com/watch?v={video.video_id}"
            st.session_state.edited_df.at[index, "link"] = yt_link

        except IndexError:
            raise "No video found"

        except Exception as e:
            st.error(
                body=f"Error: {e}",
                icon=":material/error:"
            )

def add_lyrics_search_links_to_df():
    df = st.session_state.edited_df
    unsaved_songs = df[
        df["lyrics_link"].isna() & ~df["title"].isna() & ~df["artist"].isna()
    ]
    for index, row in unsaved_songs.iterrows():
        try:
            query = f"{row['title']} {row['artist']} lyrics"
            search_query = urllib.parse.quote_plus(query)
            search_link = f"https://www.google.com/search?q={search_query}"
            st.session_state.edited_df.at[index, "lyrics_link"] = search_link

        except Exception as e:
            st.error(
                body=f"Error: {e}",
                icon=":material/error:"
            )

def add_chords_search_links_to_df():
    df = st.session_state.edited_df
    unsaved_songs = df[
        df["chords_link"].isna() & ~df["title"].isna() & ~df["artist"].isna()
    ]
    for index, row in unsaved_songs.iterrows():
        try:
            query = f"{row['title']} {row['artist']}"
            search_query = urllib.parse.quote_plus(query)
            search_link = f"https://www.ultimate-guitar.com/search.php?search_type=title&value={search_query}"
            st.session_state.edited_df.at[index, "chords_link"] = search_link

        except Exception as e:
            st.error(
                body=f"Error: {e}",
                icon=":material/error:"
            )

def handle_save_changes():
    add_youtube_links_to_df()
    add_lyrics_search_links_to_df()
    add_chords_search_links_to_df()

    st.session_state.edited_df.to_csv("./songs.csv", index=False)
    st.success(
        body=f'Saved Changes',
        icon=":material/thumb_up:"
    )
    st.balloons()
    time.sleep(2) #Give the balloons time to fly before dom refresh
    st.rerun()  # Manually re-render with updated data
    

def get_df_from_csv(file):
    return pd.read_csv(file)

def main():
    st.title("Songs List Editor")
    songs_df = get_df_from_csv("./songs.csv")

    # Column order and sort by artist
    columns_order = ["artist", "title", "link", "lyrics_link", "chords_link"]
    songs_df = songs_df[columns_order]
    songs_df = songs_df.sort_values(by="artist")
    # Reset the index to prevent it from showing as a column
    songs_df.reset_index(drop=True, inplace=True)
    

    st.session_state.edited_df = st.data_editor(
        data=songs_df,
        num_rows="dynamic",
        column_config={
            "artist": st.column_config.TextColumn("Artist"),
            "title": st.column_config.TextColumn("Song"),
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
