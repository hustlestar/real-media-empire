from social.you_tube import VALID_PRIVACY_STATUSES, YouTubeUploader


class SocialTasks:
    def __init__(
            self,
            youtube_api_key_path,
            youtube_channel_name,
            youtube_tags,
            youtube_category
    ):
        self.youtube_tags = youtube_tags
        self.youtube_category = youtube_category
        self.youtube_uploader = YouTubeUploader(
            client_secrets_file=youtube_api_key_path,
            channel_name=str(youtube_channel_name).lower().replace(" ", "_")
        )

    def upload_video_to_youtube(
            self,
            file_path,
            title="Test Title",
            description="Test Description",
            privacy_status=VALID_PRIVACY_STATUSES[1]
    ):
        return self.youtube_uploader.upload_video(
            file_path,
            title=title,
            description=description,
            category=self.youtube_category,
            tags=self.youtube_tags,
            privacy_status=privacy_status
        )

    def upload_thumbnail_for_youtube(self, thumbnail_path, video_id):
        return self.youtube_uploader.upload_thumbnail(thumbnail_path, video_id)
