#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 20:57:37 2023

@author: tatsamgarg
"""

import streamlit as st
import calendar
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime, timedelta

class PlaylistGeneratorGUI:
    def __init__(self):
        self.username_input = None
        self.start_month_input = None
        self.end_month_input = None
        self.generate_button = None

    def run(self):
        st.title(":green[SpotMyMonth] :fallen_leaf:")
        

        st.markdown("<h2 style='text-align: left; font-size: 30px; color: white;'> Playlist Generator </h2>", unsafe_allow_html=True)
        
        st.write("") # Add a blank line here
        
        # create the username input
        #st.write("Your username", text_size="40x")
        st.markdown("<h2 style='text-align: left; font-size: 20px; color: white;'> Your username </h2>", unsafe_allow_html=True)
        self.username_input = st.text_input("", key = "username_input")
          
        st.write("") # Add a blank line here
        
        # create the start month input
        st.markdown("<h2 style='text-align: left; font-size: 20px; color: white;'> Start month </h2>", unsafe_allow_html=True)
        #self.start_month_input = st.text_input("", key = "start_month_input")
        
        
        start_month_year = st.columns(2)
        with start_month_year[0]:
            months = [calendar.month_name[i] for i in range(1, 13)]
            start_month = st.selectbox("Month", months, key="start_month_input")
        with start_month_year[1]:
            start_year = st.text_input("Year (YYYY)", key="start_year_input")
        self.start_month_input = f"{months.index(start_month) + 1:02d}/{start_year}"
        
        st.write("") # Add a blank line here
        
        # create the end month input
        st.markdown("<h2 style='text-align: left; font-size: 20px; color: white;'> End month </h2>", unsafe_allow_html=True)
        #self.end_month_input = st.text_input("", key = "end_month_input")
        
        end_month_year = st.columns(2)
        with end_month_year[0]:
            months = [calendar.month_name[i] for i in range(1, 13)]
            end_month = st.selectbox("Month", months, key="end_month_input")
        with end_month_year[1]:
            end_year = st.text_input("Year (YYYY)", key="end_year_input")
        self.end_month_input = f"{months.index(end_month) + 1:02d}/{end_year}"
        
        # create the generate button
        self.generate_button = st.button("Generate Playlists", key = "generate_button")

        if self.generate_button:
            self.generate_playlists()

    def generate_playlists(self):
        # Set up client credentials
        CLIENT_ID = '3b3deafb7d7d406aa51795a98d044546'
        CLIENT_SECRET = 'edf00b855b164f62bcca60cec5ba33c4'
        REDIRECT_URI = 'http://localhost:8889/callback'

        # Define the scope of the permissions you need
        SCOPE = 'user-library-read playlist-modify-public'

        # Replace this with the Spotify username of the user you are making requests on behalf of
        USERNAME = self.username_input

        # Redirect the user to the Spotify authorization page
        token = util.prompt_for_user_token(USERNAME, SCOPE, CLIENT_ID, CLIENT_SECRET, REDIRECT_URI) # this makes a .cache file

        # Use the token to make API requests
        sp = spotipy.Spotify(auth=token)

        # get the start and end months from the inputs
        start_month_str = self.start_month_input
        end_month_str = self.end_month_input

        # convert the start and end months to datetime objects
        start_month = datetime.strptime(start_month_str, "%m/%Y")
        end_month = datetime.strptime(end_month_str, "%m/%Y")
        days_in_month = calendar.monthrange(end_month.year, end_month.month)[1]
        end_month += timedelta(days=days_in_month)

        # get all tracks from your 'liked' songs library
        offset = 0
        liked_tracks = []
        while True:
            results = sp.current_user_saved_tracks(offset=offset)
            liked_tracks.extend(results['items'])
            offset += len(results['items'])
            if len(results['items']) == 0:
                break

        # group the 'liked' songs by month
        tracks_by_month = {}
        for item in liked_tracks:
            added_at = datetime.strptime(item['added_at'], '%Y-%m-%dT%H:%M:%SZ')
            month = datetime(added_at.year, added_at.month, 1)

            if start_month <= month < end_month:
                month_str = datetime.strftime(month, '%b%y')
                if month_str in tracks_by_month:
                    tracks_by_month[month_str].append(item['track']['uri'])
                else:
                    tracks_by_month[month_str] = [item['track']['uri']]

        # create a new playlist for each month
        for month, track_uris in tracks_by_month.items():
            playlist_name = f"{month}"

            # check if playlist already exists for this month
            playlists = sp.current_user_playlists()
            for playlist in playlists['items']:
                if playlist['name'] == playlist_name:
                    existing_playlist = playlist
                    break
            else:
                existing_playlist = None
            
            # create or update the playlist
            if existing_playlist:
                existing_playlist_tracks = [track['track'] for track in sp.playlist_tracks(existing_playlist['id'])['items']]
                existing_track_uris = [track['uri'] for track in existing_playlist_tracks]
                new_track_uris = list(set(track_uris) - set(existing_track_uris))
            
                if len(new_track_uris)==0:
                    st.write(f"Playlist '{playlist_name}' already exists and was updated with {len(new_track_uris)} tracks!")
                else :
                    sp.user_playlist_add_tracks(user=sp.me()['id'], playlist_id=existing_playlist['id'], tracks=new_track_uris)
                    st.write(f"Playlist '{playlist_name}' already exists and was updated with {len(new_track_uris)} tracks!")
            else:
                playlist = sp.user_playlist_create(user=sp.me()['id'], name=playlist_name)
                sp.user_playlist_add_tracks(user=sp.me()['id'], playlist_id=playlist['id'], tracks=track_uris)
                st.write(f"Playlist '{playlist_name}' created with {len(track_uris)} tracks!")

if __name__ == "__main__":
    playlist_generator_gui = PlaylistGeneratorGUI()
    playlist_generator_gui.run()