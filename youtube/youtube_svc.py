#!/usr/bin/env python3
"""
Polyglot v3 plugin for youtube service 
Copyright (C) 2023  Universal Devices
"""
import requests
from udi_interface import LOGGER, Custom, OAuth
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import googleapiclient.discovery
from nls_gen import NLSGenerator
import os
import json
scopes=['https://www.googleapis.com/auth/youtube.download', 'https://www.googleapis.com/auth/youtube.readonly', 'https://www.googleapis.com/auth/youtubepartner-channel-audit']

YT_PLAYLIST_URL="https://www.googleapis.com/youtube/v3/playlists"
YT_PLAYLIST_ITEMS_URL="https://www.googleapis.com/youtube/v3/playlistItems"
YT_VIDEO_URL="https://www.youtube.com/watch"

PLAYLISTS_DIRECTORY="./playlists"

# This class implements the API calls to your external service
# It inherits the OAuth class
class YouTubeService(OAuth):
    global scopes

    def __init__(self, polyglot):
        # Initialize the OAuth class as well
        super().__init__(polyglot)
        self.poly = polyglot
        self.customParams = Custom(polyglot, 'customparams')
        LOGGER.info('External service initialized...')
        self.playlists={}

    def getAuthURL(self, client_id:str, client_secret:str):
        try:
            client_config = {
                "installed": {
                "client_id": client_id,
                "client_secret": client_secret, 
                "redirect_uris":["https://my.isy.io/api/cloudlink/redirect"],
                "auth_uri":"https://accounts.google.com/o/oauth2/auth",
                "token_uri":"https://oauth2.googleapis.com/token",
                }
            }
            flow = InstalledAppFlow.from_client_config(client_config,scopes)
            auth_url, _ = flow.authorization_url(prompt='consent')
            return auth_url
        except Exception as ex:
            LOGGER.error(str(ex))
            return None

        
    # The OAuth class needs to be hooked to these 2 handlers
    def customNsHandler(self, key, data):
        # This provides the oAuth config (key='oauth') and saved oAuth tokens (key='oauthTokens))
        if key == 'oauth':
            try:
               # data['auth_endpoint']=self.getAuthURL(data['client_id'], data['client_secret'])
               # data['scope']=scopes
                super().customNsHandler(key, data)
            except Exception as ex:
                LOGGER.error(ex)

    def oauthHandler(self, token):
        # This provides initial oAuth tokens following user authentication
        super().oauthHandler(token)

    def getPlaylistFile(self, title):
        if title == None:
            return None
        try:
            return os.path.join(PLAYLISTS_DIRECTORY, f'{title}.m3u')
        except Exception as ex:
            LOGGER.error(ex)
            return None

    def makePlaylistFile(self, playlist_id):
        # Create the directory if it doesn't exist
        if not os.path.exists(PLAYLISTS_DIRECTORY):
            os.makedirs(PLAYLISTS_DIRECTORY)
        
        try:
            playlist = self.playlists[playlist_id]
            if playlist == None:
                return False
            title = playlist['title']
            if title == None:
                return False

            with open(os.path.join(PLAYLISTS_DIRECTORY, f'{title}.m3u'), 'w') as f:
                for item in playlist['items']:
                    url=item['url']
                    f.write(f'{url}\n')

        except Exception as ex:
            LOGGER.error(ex)

    def getVideoURL(self, videoId):
        if videoId == None:
            return None
        access_token = self.getAccessToken()
        if access_token == None:
            return None
        #"url" : f'https://www.youtube.com/watch?v={id}&fmt=audio'
        url=f"{YT_VIDEO_URL}?v={videoId}&fmt=audio&access_token={access_token}"
        return url

    def getPlaylistItems(self, playlist_id):
        if playlist_id == None:
            return None
        params = {
                'part': 'snippet',
                'playlistId': playlist_id,
                'maxResults': 50,  # Maximum number of results per page
        }
        items=[]
        try:
            while True:
                playlist_data = self._callApi(url=YT_PLAYLIST_ITEMS_URL, params=params)

                # Process the playlists data
                for item in playlist_data["items"]:
                    id = item['snippet']['resourceId']['videoId']
                    url=self.getVideoURL(id)
                    item = {
                        "id" : id, 
                        "title" : item['snippet']['title'],
                        "url" : url,
                    }
                    items.append(item) 

                # Check if there is another page of results
                if "nextPageToken" in playlist_data:
                    params["pageToken"] = playlist_data["nextPageToken"]
                else:
                    break  # No more pages, exit the loop
            return items
        except Exception as ex:
            LOGGER.error(str(ex))


    def processPlaylists(self):
        params = {
            "part": "snippet",
            "mine": "true",
            "maxResults": 26
        }
        try:
            while True:
                playlists_data = self._callApi(url=YT_PLAYLIST_URL, params=params)

                # Process the playlists data
                for playlist in playlists_data["items"]:
                    id  = playlist["id"] 
                    items = self.getPlaylistItems(id)
                    pl={
                        'title': playlist["snippet"]["title"],
                        'items': items
                    }
                    self.playlists[id] = pl 
                    self.makePlaylistFile(id)

                # Check if there is another page of results
                if "nextPageToken" in playlists_data:
                    params["pageToken"] = playlists_data["nextPageToken"]
                else:
                    break  # No more pages, exit the loop
        except Exception as ex:
            LOGGER.error(ex)

        return self.playlists


    # Call your external service API
    def _callApi(self, method='GET', url=None, params=None, body=None):
        if url is None:
            LOGGER.error('url is required')
            return None

        completeUrl = url

        LOGGER.info(f"Making call to { method } { completeUrl }")

        # When calling an API, get the access token (it will be refreshed if necessary)
        # If user has not authenticated yet, getAccessToken will raise a ValueError exception
        accessToken = self.getAccessToken()

        headers = {
            'Authorization': f"Bearer { accessToken }"
        }

        if method in [ 'PATCH', 'POST'] and body is None:
            LOGGER.error(f"body is required when using { method } { completeUrl }")

        try:
            if method == 'GET':
                response = requests.get(completeUrl, params=params, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(completeUrl, params=params, headers=headers)
            elif method == 'PATCH':
                response = requests.patch(completeUrl, params=params, headers=headers, json=body)
            elif method == 'POST':
                response = requests.post(completeUrl, params=params, headers=headers, json=body)
            elif method == 'PUT':
                response = requests.put(completeUrl, params=params, headers=headers)

            response.raise_for_status()
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return response.text

        except requests.exceptions.HTTPError as error:
            LOGGER.error(f"Call { method } { completeUrl } failed: { error }")
            return None

    def unsubscribe(self):
        return self._callApi(method='DELETE', url='/subscription')

    def getUserInfo(self):
        return self._callApi(url='/user/info')

if __name__ == "__main__":
    try:
        print("ehllo wworld")
    except (KeyboardInterrupt, SystemExit):
        sys.exit(0)
    except Exception as ex:
        LOGGER.error(ex)
        

