import json
import logging
import os.path
import random
import time

import httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError, ResumableUploadError
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage

from config import CONFIG

httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError, ResumableUploadError, HttpError)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube",
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.force-ssl",
]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """WARNING: Please configure OAuth 2.0"""

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")
logger = logging.getLogger(__name__)


class YouTubeUploader:
    def __init__(self, client_secrets_file: str, channel_name: str, channel_id: str, oath_storage_dir: str = CONFIG.get("OAUTH_2_DIR")):
        self.client_secrets_file = client_secrets_file
        self.channel_id = channel_id
        self.channel_name = str(channel_name).lower().replace("\\s+", "_").replace("_shorts", "")
        self.credentials_file = os.path.join(oath_storage_dir, f"{self.channel_name}_oauth2.json")
        self.youtube = None

    def authenticate(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, scopes=YOUTUBE_SCOPES)
        credentials = Credentials.from_authorized_user_file(self.credentials_file, []) if os.path.exists(self.credentials_file) else None
        if not credentials or credentials.expired:
            is_refresh_failed = False
            if credentials and credentials.refresh_token:
                logger.info("Trying to refresh token")
                try:
                    credentials.refresh(Request())
                    logger.info("Successfully refreshed token")
                except:
                    logger.info("Failed to refresh token")
                    is_refresh_failed = True
            if credentials and credentials.refresh_token and is_refresh_failed:
                credentials = flow.run_local_server(port=0)
            elif not credentials:
                credentials = flow.run_local_server(port=0)

            if not os.path.exists(self.credentials_file):
                with open(self.credentials_file, 'w') as _:
                    pass

            storage = Storage(self.credentials_file)
            storage.put(credentials)
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)

    def upload_video(
            self,
            file_path,
            title="Test Title",
            description="Test Description",
            category="22",
            tags=None,
            privacy_status=VALID_PRIVACY_STATUSES[1]
    ):
        self.authenticate()
        if isinstance(tags, str):
            tags = tags.split(",")
        elif not tags:
            tags = []
        logger.info(f"Uploading video to channel {self.channel_name} from file {file_path}"
                    f"\nTitle: {title}"
                    f"\nDescription: {description}"
                    f"\nTags: {tags}"
                    f"\nCategory: {category}"
                    f"\nPrivacy: {privacy_status}")
        body = {
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags,
                "categoryId": category
            },
            "status": {
                "privacyStatus": privacy_status
            }
        }

        insert_request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
        )
        return self.resumable_upload(insert_request)

    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                logger.info("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        logger.info(f"Video id '{response['id']}' was successfully uploaded.")
                        return response['id']
                    else:
                        exit(f"The upload failed with an unexpected response: {response}")
            except HttpError as e:
                if e.resp.status in RETRIABLE_STATUS_CODES:
                    error = f"A retriable HTTP error {e.resp.status} occurred:\n{e.content}"
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = "A retriable error occurred: %s" % e

            if error is not None:
                logger.info(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                logger.info(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)

    def upload_thumbnail(self, file_path, video_id):
        self.authenticate()
        logger.info(f"Uploading thumbnail from file {file_path}")
        thumbnail_url = None
        try:
            response = self.youtube.thumbnails().set(
                videoId=video_id,
                media_body=MediaFileUpload(file_path, chunksize=-1, resumable=True)
            ).execute()
            if response and 'items' in response and len(response['items']) > 0:
                thumbnail_url = response['items'][0]['default']['url']
                logger.info(f"Thumbnail successfully uploaded. URL: {thumbnail_url}")
        except HttpError as e:
            logger.info(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return thumbnail_url

    def insert_comment(self, video_id, comment_text, channel_id=None):
        self.authenticate()
        # Call the YouTube API to insert the comment
        comment_insert_response = self.youtube.commentThreads().insert(
            part="snippet",
            body=dict(
                snippet=dict(
                    channelId=channel_id if channel_id else self.channel_id,
                    videoId=video_id,
                    topLevelComment=dict(
                        snippet=dict(
                            textOriginal=comment_text
                        )
                    ),
                    isPublic=True,
                    isPinned=True
                )
            )
        ).execute()

        print("Comment successful!")
        return comment_insert_response['id']


if __name__ == '__main__':
    uploader = YouTubeUploader(
        client_secrets_file=CONFIG.get("YOUTUBE_CHANNEL_API_KEY_PATH"),
        channel_name='daily_mindset',
        channel_id="UCPZrsHvG-XxorsXWtC3i6AA"
    )

    comment = 'test comment new'
    video_id = '9aKOFqVoXic'
    res = uploader.insert_comment(video_id=video_id, comment_text=comment)
    print(res)

    # uploader.authenticate()
    # uploader.upload_video("D:\\Projects\\media-empire\\tmp\\2023-03-10T15-25-33_slide_in_top_all.mp4")
