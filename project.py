from lyricsgenius import Genius
import json
import os
from progress.bar import Bar


# Format a lyrics string to be usable with our models
def clean_lyrics(lyric):
    return lyric


# Retrieve all the songs that Genius has for a given genre
# Returns a list of cleaned lyrics
def get_songs_by_genre(genius_api_obj, tag, res_max=1000):
    # We can look at 50 pages of documents within a tag, with 20 songs per page
    page = 1
    # This is going to be a list of tuples
    songs = []
    # Keep scrubbing data until there's none left, or we don't need more
    with Bar("Scrubbing", max=res_max) as bar:
        while page and len(songs) <= (res_max - 20):
            # Get all the results for a tag on a given page
            res = genius_api_obj.tag(tag, page=page)
            # Iterate through the hits
            for hit in res['hits']:
                bar.next()
                song_title = hit['title_with_artists'].strip()
                song_lyrics = clean_lyrics(genius_api_obj.lyrics(song_url=hit['url']))
                # Only add append a lyric if its usable
                if song_lyrics:
                    songs.append((song_title, song_lyrics))
            page = res['next_page']
    return songs


# RN this just saves the data to local disk, but this could export
# it to some sort of cloud service in the future
def save_data(genre_tag, genre_songs, data_dir='data/'):
    target_dir = data_dir + genre_tag + "/"
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    for title, lyrics in genre_songs:
        with open(target_dir + title, 'w') as f:
            f.write(lyrics)
    return


if __name__ == "__main__":
    print("Loading API keys...")
    try:
        with open("api_keys.json", 'r') as api_keys_file:
            api_keys = json.load(api_keys_file)
    except FileNotFoundError:
        print("Oops! It looks like you don't have the file describing our API keys!")
        exit()

    # Initialize an API object to do our searching with
    print("Authenticating Genius API...")
    genius = Genius(api_keys['lyricsgenius']['Token'])

    # Sourced from: OOPS THIS PAGE IS DOWN, we might not be able to use tags...
    genre_tags = [
        "pop",
        # "metal",
        # "rap",
        # "country"
    ]

    print("Collecting Genius Data...")
    for genre_tag in genre_tags:
        print("Scrubbing for", genre_tag, "lyrics...")
        # A list of tuples of the form (song_title, song_lyrics)
        genre_songs = get_songs_by_genre(genius, genre_tag, res_max=20)
        save_data(genre_tag, genre_songs)
