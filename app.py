# ./main.py
import streamlit as st
import pandas as pd

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

def handle_save_changes():
    add_youtube_links_to_df()

    st.session_state.edited_df.to_csv("./songs.csv", index=False)
    st.success(
        body=f'Saved Changes',
        icon=":material/thumb_up:"
    )
    st.balloons()

def get_df_from_csv(file):
    return pd.read_csv(file)

def get_unsaved_songs():
    df = st.session_state.edited_df
    return df[
        df["link"].isna() & ~df["title"].isna() & ~df["artist"].isna()
    ]

def main():
    st.title("Songs List Editor")

    songs_df = get_df_from_csv("./songs.csv")

    st.session_state.edited_df = st.data_editor(
        data=songs_df,
        num_rows="dynamic",
        column_config={
            "title": st.column_config.TextColumn("Song"),
            "artist": st.column_config.TextColumn("Artist"),
            "link": st.column_config.LinkColumn(
                "YT Link",
                disabled=True,
                display_text="Listen on YouTube",
            ),
        },
        hide_index=True,
        use_container_width=True,
    )

    if st.button(
        label="Save Changes",
        help="Save the changes made to the songs list",
        disabled=len(get_unsaved_songs()) == 0,
    ):
        handle_save_changes()


if __name__ == "__main__":
    main()
