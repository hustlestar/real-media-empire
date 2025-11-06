
# Multi-Platform Publishing System

Professional multi-platform video publishing system with account management, scheduling, batch operations, and comprehensive validation.

## Features

- **Multi-Platform Support**: TikTok, Instagram, Facebook, LinkedIn, YouTube
- **Multi-Account Management**: Manage multiple accounts per platform
- **Scheduled Publishing**: Queue system with priority and retry logic
- **Batch Operations**: Publish multiple videos simultaneously
- **Video Validation**: Pre-publish validation against platform requirements
- **Webhook Notifications**: Get notified when publishing completes
- **Error Handling**: Automatic retries with exponential backoff
- **Cost Tracking**: Track publishing costs (future feature)

## Architecture

```
Publishing System
├── Manager (PublishingManager)
│   ├── Account Management
│   ├── Multi-Platform Publishing
│   └── Validation
├── Queue (PublishingQueue)
│   ├── Job Scheduling
│   ├── Priority Processing
│   ├── Retry Logic
│   └── Status Tracking
└── Platforms
    ├── TikTok
    ├── Instagram
    ├── Facebook
    ├── LinkedIn
    └── YouTube
```

## Platform Support

### TikTok
- **Max Duration**: 10 minutes (600s)
- **Max File Size**: 287MB
- **Formats**: MP4, MOV, WEBM
- **Aspect Ratios**: 9:16 (preferred), 16:9, 1:1
- **Recommended Resolution**: 1080x1920 (vertical)
- **Features**: Scheduled publishing, privacy settings, engagement controls

### Instagram
- **Max Duration**: 90s (Reels), 60s (Stories), 60min (Feed)
- **Max File Size**: 100MB
- **Formats**: MP4, MOV
- **Aspect Ratios**: 9:16 (Reels/Stories), 4:5, 1:1 (Feed)
- **Recommended Resolution**: 1080x1920 (Reels)
- **Features**: Post types (Reels/Stories/Feed), location tagging, user tagging

### Facebook
- **Max Duration**: 120 minutes (7200s)
- **Max File Size**: 4GB
- **Formats**: MP4, MOV
- **Aspect Ratios**: 16:9, 9:16, 1:1, 4:5
- **Recommended Resolution**: 1080x1920
- **Features**: Page publishing, scheduled posts, privacy settings

### LinkedIn
- **Max Duration**: 10 minutes (600s)
- **Max File Size**: 5GB
- **Formats**: MP4
- **Aspect Ratios**: 16:9, 9:16, 1:1
- **Recommended Resolution**: 1920x1080
- **Note**: Does not support scheduled posts via API

### YouTube
- **Max Duration**: 12 hours (verified accounts)
- **Max File Size**: 256GB
- **Formats**: MP4, MOV, AVI, FLV, WMV
- **Aspect Ratios**: 16:9, 9:16, 1:1, 4:3, 21:9
- **Recommended Resolution**: 1920x1080
- **Features**: Custom thumbnails, playlists, comments, scheduled publishing

## Quick Start

### 1. Setup Publishing Manager

```python
from features.publishing.manager import PublishingManager
from features.publishing.platforms.base import PublishConfig

manager = PublishingManager()

# Add accounts for each platform
manager.add_account(
    account_id="my_tiktok",
    platform="tiktok",
    credentials={
        "api_key": "your_upload_post_api_key",
        "user": "your_upload_post_user"
    }
)

manager.add_account(
    account_id="my_youtube",
    platform="youtube",
    credentials={
        "client_secrets_file": "/path/to/client_secrets.json",
        "channel_name": "MyChannel",
        "channel_id": "UCxxxxxxxxx"
    }
)
```

### 2. Publish to Single Platform

```python
config = PublishConfig(
    title="My Awesome Video",
    description="Check out this content!",
    tags=["viral", "trending"],
    platform_specific={
        "tiktok": {
            "privacy": "public",
            "allow_comments": True
        }
    }
)

result = await manager.publish_to_platform(
    account_id="my_tiktok",
    platform="tiktok",
    video_path="/path/to/video.mp4",
    config=config
)

print(f"Success: {result.success}")
print(f"Video URL: {result.url}")
```

### 3. Multi-Platform Publishing

```python
results = await manager.publish_multi_platform(
    account_id="my_account",
    platforms=["tiktok", "instagram", "youtube"],
    video_path="/path/to/video.mp4",
    config=config
)

for platform, result in results.items():
    print(f"{platform}: {result.status}")
```

### 4. Scheduled Publishing

```python
from features.publishing.queue import PublishingQueue, QueuedPublishConfig
from datetime import datetime, timedelta

queue = PublishingQueue(db_session, manager)

scheduled_time = datetime.utcnow() + timedelta(hours=2)

queued_config = QueuedPublishConfig(
    account_id="my_account",
    platforms=["tiktok", "instagram"],
    video_path="/path/to/video.mp4",
    config=config,
    scheduled_time=scheduled_time,
    priority=8,
    webhook_url="https://myapp.com/webhook"
)

job = queue.add_job("job_123", queued_config)

# Start queue workers
await queue.start()
```

### 5. Video Validation

```python
results = manager.validate_video_for_platforms(
    video_path="/path/to/video.mp4",
    platforms=["tiktok", "instagram", "youtube"]
)

for platform, validation in results.items():
    if validation['valid']:
        print(f"{platform}: ✅ Valid")
    else:
        print(f"{platform}: ❌ {', '.join(validation['errors'])}")
```

## REST API Usage

### Add Account

```bash
POST /api/publishing/accounts
Content-Type: application/json

{
  "account_id": "my_tiktok",
  "platform": "tiktok",
  "credentials": {
    "api_key": "...",
    "user": "..."
  }
}
```

### Publish Immediately

```bash
POST /api/publishing/publish/immediate
Content-Type: application/json

{
  "account_id": "my_tiktok",
  "platforms": ["tiktok", "instagram"],
  "video_path": "/path/to/video.mp4",
  "title": "My Video",
  "description": "Check this out!",
  "tags": ["viral", "trending"],
  "platform_specific": {
    "tiktok": {
      "privacy": "public"
    }
  }
}
```

### Schedule Publishing

```bash
POST /api/publishing/publish/scheduled
Content-Type: application/json

{
  "account_id": "my_account",
  "platforms": ["tiktok", "youtube"],
  "video_path": "/path/to/video.mp4",
  "title": "Scheduled Video",
  "description": "Coming soon!",
  "scheduled_time": "2025-11-07T10:00:00Z",
  "priority": 8,
  "max_retries": 3
}
```

### Check Job Status

```bash
GET /api/publishing/jobs/{job_id}
```

### List Jobs

```bash
GET /api/publishing/jobs?status=pending&limit=50
```

### Validate Video

```bash
POST /api/publishing/validate
Content-Type: application/json

{
  "video_path": "/path/to/video.mp4",
  "platforms": ["tiktok", "instagram", "youtube"]
}
```

## Platform-Specific Configuration

### TikTok Options

```python
platform_specific = {
    "tiktok": {
        "privacy": "public",  # public, friends_only, private
        "allow_comments": True,
        "allow_duet": True,
        "allow_stitch": True,
        "brand_content": False,
        "brand_organic": False
    }
}
```

### Instagram Options

```python
platform_specific = {
    "instagram": {
        "post_type": "reels",  # reels, stories, feed
        "location": "New York, NY",
        "tag_users": ["@username1", "@username2"],
        "share_to_feed": True  # For Reels
    }
}
```

### Facebook Options

```python
platform_specific = {
    "facebook": {
        "privacy": "public",  # public, friends, only_me
        "place": "123456789",  # Place ID
        "backdated_time": "2025-11-06T12:00:00Z"
    }
}
```

### LinkedIn Options

```python
platform_specific = {
    "linkedin": {
        "visibility": "public",  # public, connections
        "commentary": "Professional content for LinkedIn"
    }
}
```

### YouTube Options

```python
platform_specific = {
    "youtube": {
        "category": "22",  # Category ID (22 = People & Blogs)
        "privacy_status": "private"  # public, private, unlisted
    }
}
```

## Credentials Configuration

### upload-post.com (TikTok, Instagram, Facebook, LinkedIn)

Get API credentials from [upload-post.com](https://upload-post.com):

```python
credentials = {
    "api_key": "your_api_key",
    "user": "your_user_id"
}
```

Additional for Facebook:
```python
credentials = {
    "api_key": "...",
    "user": "...",
    "page_id": "your_facebook_page_id"
}
```

### YouTube

YouTube requires OAuth2 credentials:

```python
credentials = {
    "client_secrets_file": "/path/to/client_secrets.json",
    "channel_name": "YourChannelName",
    "channel_id": "UCxxxxxxxxxxxxxxxxx",
    "oauth_storage_dir": "/path/to/oauth/storage"
}
```

Get credentials from [Google Cloud Console](https://console.cloud.google.com).

## Queue System

### Job Lifecycle

1. **PENDING**: Job created, ready to process
2. **SCHEDULED**: Job scheduled for future time
3. **PROCESSING**: Currently uploading
4. **COMPLETED**: Successfully published
5. **FAILED**: Failed (may retry if retries remaining)
6. **CANCELLED**: Manually cancelled
7. **RETRYING**: Failed, will retry

### Priority System

- Jobs are processed by priority (1-10, higher = more urgent)
- Same priority processed FIFO (first in, first out)
- High priority jobs (8-10) jump the queue

### Retry Logic

- Configurable max retries (default: 3)
- Exponential backoff delay (default: 5 minutes)
- Failed jobs automatically retry if under max attempts

### Webhooks

Register webhook URL to get notifications:

```python
queued_config = QueuedPublishConfig(
    ...,
    webhook_url="https://myapp.com/webhook/publish",
    callback_data={"custom": "data"}
)
```

Webhook payload:
```json
{
  "job_id": "job_123",
  "account_id": "my_account",
  "platforms": ["tiktok", "instagram"],
  "title": "Video Title",
  "success": true,
  "status": "completed",
  "created_at": "2025-11-06T10:00:00Z",
  "completed_at": "2025-11-06T10:05:30Z",
  "results": {
    "tiktok": {
      "success": true,
      "video_id": "123456",
      "url": "https://tiktok.com/@user/video/123456"
    }
  },
  "callback_data": {"custom": "data"}
}
```

## Error Handling

### Validation Errors

```python
validation = manager.validate_video_for_platforms(video_path, platforms)

for platform, result in validation.items():
    if not result['valid']:
        for error in result['errors']:
            print(f"❌ {platform}: {error}")

    for warning in result['warnings']:
        print(f"⚠️  {platform}: {warning}")
```

### Publishing Errors

```python
result = await manager.publish_to_platform(...)

if not result.success:
    print(f"Error: {result.error}")

    if "authentication" in result.error.lower():
        # Re-authenticate
        await manager.authenticate_account(account_id, platform)
```

### Queue Errors

Failed jobs automatically retry with exponential backoff. Monitor failures:

```python
stats = queue.get_queue_stats()
print(f"Failed jobs: {stats['failed']}")

failed_jobs = queue.list_jobs(status=QueueStatus.FAILED)
for job in failed_jobs:
    print(f"{job.id}: {job.error_message}")
```

## Best Practices

1. **Validate Before Publishing**
   ```python
   validation = manager.validate_video_for_platforms(video_path, platforms)
   if not all(v['valid'] for v in validation.values()):
       # Fix issues before publishing
       return
   ```

2. **Use Scheduled Publishing for Off-Peak Times**
   ```python
   # Schedule for 2 PM when engagement is high
   scheduled_time = datetime.utcnow().replace(hour=14, minute=0)
   ```

3. **Monitor Queue Stats**
   ```python
   stats = queue.get_queue_stats()
   if stats['failed'] > 10:
       # Alert admin
       send_alert("High failure rate in publishing queue")
   ```

4. **Handle Platform-Specific Limits**
   ```python
   # TikTok video
   if duration > 600:  # 10 minutes
       platforms.remove("tiktok")

   # Instagram Reels
   if duration > 90:
       platforms.remove("instagram")
   ```

5. **Use Webhooks for Long-Running Jobs**
   ```python
   queued_config = QueuedPublishConfig(
       ...,
       webhook_url=f"{BASE_URL}/webhook/publish/{user_id}"
   )
   ```

6. **Batch Similar Content**
   ```python
   # Batch publish all daily content at once
   batch = [
       create_publish_spec(video)
       for video in daily_videos
   ]
   await manager.publish_batch(batch)
   ```

## Monitoring & Analytics

### Queue Statistics

```python
stats = queue.get_queue_stats()

print(f"Pending: {stats['pending']}")
print(f"Processing: {stats['processing']}")
print(f"Completed: {stats['completed']}")
print(f"Failed: {stats['failed']}")
print(f"Scheduled (future): {stats['scheduled_future']}")
```

### Success Rate by Platform

```python
completed_jobs = queue.list_jobs(status=QueueStatus.COMPLETED, limit=1000)

platform_stats = {}
for job in completed_jobs:
    results = json.loads(job.results_json)
    for platform, result in results.items():
        if platform not in platform_stats:
            platform_stats[platform] = {"success": 0, "total": 0}

        platform_stats[platform]["total"] += 1
        if result["success"]:
            platform_stats[platform]["success"] += 1

for platform, stats in platform_stats.items():
    rate = stats["success"] / stats["total"] * 100
    print(f"{platform}: {rate:.1f}% success rate")
```

## Troubleshooting

### Authentication Failures

**TikTok/Instagram/Facebook/LinkedIn:**
- Verify upload-post.com API key and user ID
- Check account is connected on upload-post.com dashboard
- Ensure platform account is properly linked

**YouTube:**
- Verify client_secrets.json is valid
- Check OAuth credentials haven't expired
- Re-run authentication flow if needed

### Upload Failures

1. **File Not Found**
   - Verify video_path exists and is absolute
   - Check file permissions

2. **Validation Errors**
   - Run validation before publishing
   - Fix file size, duration, or format issues

3. **Network Errors**
   - Automatic retry with exponential backoff
   - Check network connectivity
   - Verify API endpoints are reachable

4. **Rate Limiting**
   - Reduce worker_count in queue
   - Add delays between publishes
   - Use scheduled publishing to spread load

## Examples

See `examples/publishing_example.py` for comprehensive examples including:
- Account setup
- Single platform publishing
- Multi-platform publishing
- Video validation
- Scheduled publishing
- Batch operations
- Queue management

## Future Enhancements

- [ ] Cost tracking per platform
- [ ] Analytics integration (views, engagement)
- [ ] Content performance prediction
- [ ] Automated optimal posting times
- [ ] A/B testing for titles/descriptions
- [ ] Multi-language support
- [ ] Video transcoding/optimization
- [ ] Automated thumbnail generation
- [ ] Cross-platform hashtag optimization
- [ ] Audience analytics
