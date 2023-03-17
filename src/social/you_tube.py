import os.path
import random
import sys
import time

import httplib2
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.file import Storage

from config import CONFIG

httplib2.RETRIES = 1

MAX_RETRIES = 10

RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError)

RETRIABLE_STATUS_CODES = [500, 502, 503, 504]

YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

MISSING_CLIENT_SECRETS_MESSAGE = """WARNING: Please configure OAuth 2.0"""

VALID_PRIVACY_STATUSES = ("public", "private", "unlisted")


class YouTubeUploader:
    def __init__(self, client_secrets_file: str, channel_name: str, oath_storage_dir: str = CONFIG.get("OAUTH_2_DIR")):
        self.client_secrets_file = client_secrets_file
        self.channel_name = str(channel_name).lower().replace("\\s+", "_")
        self.credentials_file = os.path.join(oath_storage_dir, f"{self.channel_name}_oauth2.json")
        self.youtube = None

    def upload(
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
        print(f"Uploading video to channel {self.channel_name} from file {file_path}\n"
              f"\tTitle: {title}"
              f"\tDescription: {description}"
              f"\tTags: {tags}"
              f"\tCategory: {category}"
              f"\tPrivacy: {privacy_status}")
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
        self.resumable_upload(insert_request)

    def authenticate(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secrets_file, scopes=[YOUTUBE_UPLOAD_SCOPE])
        credentials = Credentials.from_authorized_user_file(self.credentials_file, []) if os.path.exists(self.credentials_file) else None
        if not credentials:
            credentials = flow.run_local_server(port=0)
            storage = Storage(self.credentials_file)
            storage.put(credentials)
        self.youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, credentials=credentials)

    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if 'id' in response:
                        print(f"Video id '{response['id']}' was successfully uploaded.")
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
                print(error)
                retry += 1
                if retry > MAX_RETRIES:
                    exit("No longer attempting to retry.")

                max_sleep = 2 ** retry
                sleep_seconds = random.random() * max_sleep
                print(f"Sleeping {sleep_seconds} seconds and then retrying...")
                time.sleep(sleep_seconds)


if __name__ == '__main__':
    uploader = YouTubeUploader(client_secrets_file=CONFIG.get("YOUTUBE_CHANNEL_API_KEY_PATH"))

    uploader.upload("D:\\Projects\\media-empire\\tmp\\2023-03-10T15-25-33_slide_in_top_all.mp4")
