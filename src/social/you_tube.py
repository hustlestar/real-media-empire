import httplib2
import os
import random
import sys
import time

import httplib
import httplib2

from apiclient.discovery import build
from apiclient.errors import HttpError
from apiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow


class YouTubeUploader:
    def __init__(self, client_secrets_file, oauth2_file):
        self.client_secrets_file = client_secrets_file
        self.oauth2_file = oauth2_file
        self.youtube_api_service_name = "youtube"
        self.youtube_api_version = "v3"
        self.missing_client_secrets_message = """
            WARNING: Please configure OAuth 2.0
        """
        self.valid_privacy_statuses = ("public", "private", "unlisted")
        self.max_retries = 10
        self.retriable_status_codes = [500, 502, 503, 504]
        self.retriable_exceptions = (httplib2.HttpLib2Error, IOError, httplib.NotConnected,
                                                            httplib.IncompleteRead, httplib.ImproperConnectionState,
                                                            httplib.CannotSendRequest, httplib.CannotSendHeader,
                                                            httplib.ResponseNotReady, httplib.BadStatusLine)
        self.flow = flow_from_clientsecrets(
            self.client_secrets_file,
            scope="https://www.googleapis.com/auth/youtube.upload",
            message=self.missing_client_secrets_message,
        )
        self.storage = Storage(self.oauth2_file)
        self.credentials = self.storage.get()
        self.youtube = None

    def get_authenticated_service(self):
        if self.credentials is None or self.credentials.invalid:
            self.credentials = run_flow(self.flow, self.storage, self.args)
        self.youtube = build(
            self.youtube_api_service_name,
            self.youtube_api_version,
            http=self.credentials.authorize(httplib2.Http()),
        )

    def initialize_upload(self):
        tags = None
        if self.args.keywords:
            tags = self.args.keywords.split(",")

        body = dict(
            snippet=dict(
                title=self.args.title,
                description=self.args.description,
                tags=tags,
                categoryId=self.args.category,
            ),
            status=dict(privacyStatus=self.args.privacyStatus),
        )

        # Call the API's videos.insert method to create and upload the video.
        insert_request = self.youtube.videos().insert(
            part=",".join(body.keys()),
            body=body,
            media_body=MediaFileUpload(
                self.args.file, chunksize=-1, resumable=True
            ),
        )

        self.resumable_upload(insert_request)

    # This method implements an exponential backoff strategy to resume a
    # failed upload.
    def resumable_upload(self, insert_request):
        response = None
        error = None
        retry = 0
        while response is None:
            try:
                print("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None:
                    if "id" in response:
                        print(
                            "Video id '%s' was successfully uploaded."
                            % response["id"]
                        )
                    else:
                        exit(
                            "The upload failed with an unexpected response: %s"
                            % response
                        )
            except HttpError as e:
                if e.resp.status in self.retriable_status_codes:
                    error = "A retriable HTTP error %d occurred:\n%s" % (
                        e.resp.status,
                        e.content,
                    )
                else:
                    raise

