
from googleapiclient.discovery import build


class YoutubeService:

    def __init__(self, api_key):
        self.youtube = build(
            "youtube",
            "v3",
            developerKey=api_key
        )

    def search_channels(self, keyword):

        request = self.youtube.search().list(
            part="snippet",
            q=keyword,
            type="channel",
            maxResults=50
        )

        return request.execute()