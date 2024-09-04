import streamlit as st
import pandas as pd
import urllib.parse
import time

from pytube import Search

CSV_STORE_PATH = "./songs.csv"

st.set_page_config(page_title="Linkify Songs List", page_icon="🎸")

def update_links_for_unsaved_songs():
    df = st.session_state.edited_df

    # Filter rows with any blank links
    unsaved_songs = df[
        (df["link"].isna()) | (df["lyrics_link"].isna()) | (df["chords_link"].isna()) & 
        ~df["title"].isna() & ~df["artist"].isna()
    ]

    for index, row in unsaved_songs.iterrows():
        try:
            title = row["title"]
            artist = row["artist"]
            query = f"{title} {artist}"

            # Update YouTube link if blank
            if pd.isna(row["link"]):
                search = Search(query)
                video = next((v for v in search.results if v.video_id), None)
                if video:
                    yt_link = f"https://www.youtube.com/watch?v={video.video_id}"
                    st.session_state.edited_df.at[index, "link"] = yt_link
                else:
                    st.error(
                        body=f"No valid video found for query: {query}",
                        icon=":material/error:"
                    )

            # Update Lyrics link if blank
            if pd.isna(row["lyrics_link"]):
                search_query = urllib.parse.quote_plus(f"{query} lyrics")
                search_link = f"https://www.google.com/search?q={search_query}"
                st.session_state.edited_df.at[index, "lyrics_link"] = search_link

            # Update Chords link if blank
            if pd.isna(row["chords_link"]):
                search_query = urllib.parse.quote_plus(query)
                search_link = f"https://www.ultimate-guitar.com/search.php?search_type=title&value={search_query}"
                st.session_state.edited_df.at[index, "chords_link"] = search_link

        except Exception as e:
            st.error(
                body=f"Error: {e}",
                icon=":material/error:"
            )

def clear_links_for_changed_songs():
    df = st.session_state.edited_df
    original_df = st.session_state.original_df

    # Merge the DataFrames to find rows in edited_df that are not in original_df
    merged_df = df.merge(
        original_df,
        on=["artist", "title"],
        how="left",
        indicator=True
    )

    # Identify rows in edited_df that don't exist in original_df
    changed_rows = merged_df[merged_df['_merge'] == 'left_only']

    # Clear the links for these rows
    for index in changed_rows.index:
        df.at[index, "link"] = None
        df.at[index, "lyrics_link"] = None
        df.at[index, "chords_link"] = None

def handle_save_changes():
    clear_links_for_changed_songs()  # Clear links for changed songs
    update_links_for_unsaved_songs()  # Update links for unsaved songs

    st.session_state.edited_df.to_csv(CSV_STORE_PATH, index=False)
    st.success(
        body='Saved Changes',
        icon=":material/thumb_up:"
    )
    st.balloons()
    time.sleep(2) #Give the balloons time to fly before dom refresh
    st.rerun()  # Manually re-render with updated data


def get_df_from_csv(file):
    return pd.read_csv(file)

def main():
    st.title("Songs List Editor")

    # Add search functionality
    search_query = st.text_input("Search songs by artist or title")

    # Load and store the original DataFrame
    original_df = get_df_from_csv(CSV_STORE_PATH)
    st.session_state.original_df = original_df

    songs_df = original_df.copy()

    # Filter the DataFrame based on the search query
    if search_query:
        songs_df = songs_df[
            songs_df['artist'].str.contains(search_query, case=False) |
            songs_df['title'].str.contains(search_query, case=False)
        ]

    # Column order and sort by artist
    columns_order = ["artist", "title", "proficiency", "link", "lyrics_link", "chords_link"]
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
