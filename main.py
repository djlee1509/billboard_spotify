import requests
from bs4 import BeautifulSoup
import config
from spotipy.oauth2 import SpotifyOAuth
import spotipy
import datetime


API_KEY = config.api_key
API_SECRET = config.api_secret


def get_date():
    date_str = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")
    return date_str


def scrape_tracks(date_str):
    billboard_url = f"https://www.billboard.com/charts/hot-100/{date_str}"
    page = requests.get(billboard_url)

    soup = BeautifulSoup(page.content, 'html.parser')

    title_tags = soup.find_all('span', class_='chart-element__information__song text--truncate color--primary')
    titles = [title.get_text() for title in title_tags]

    return titles


def authenticate_spotify():
    auth_manager = SpotifyOAuth(client_id=API_KEY,
                                client_secret=API_SECRET,
                                show_dialog=True,
                                cache_path="token.txt",
                                scope="playlist-modify-private",
                                redirect_uri="http://localhost:8888/callback")

    sp = spotipy.Spotify(auth_manager=auth_manager)
    user_id = sp.current_user()["id"]

    return sp, user_id


def create_playlist(date_str, titles, sp, user_id):
    date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    year = date.year

    tracks_uris = []

    for title in titles:
        query = f"track:{title} year:{year}"
        result = sp.search(q=query)

        try:
            uri = result["tracks"]["items"][0]["uri"]
            tracks_uris.append(uri)
        except IndexError:
            print(f"{title} not found.")

    playlist_name = f"{date_str} Billboard 100"

    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)

    sp.playlist_add_items(playlist['id'], tracks_uris)


def main():
    date_str = get_date()
    titles = scrape_tracks(date_str)
    sp, user_id = authenticate_spotify()

    create_playlist(date_str, titles, sp, user_id)


if __name__ == "__main__":
    main()
