"""
Complete Publishing System Example
===================================

Demonstrates:
1. Setting up publishing manager with multiple accounts
2. Publishing to single platform
3. Multi-platform publishing
4. Scheduled publishing with queue
5. Batch publishing
6. Video validation
7. Queue management

Prerequisites:
- Video files to publish
- API credentials for upload-post.com
- YouTube OAuth credentials (for YouTube)
"""

import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from features.publishing.manager import PublishingManager
from features.publishing.queue import PublishingQueue, QueuedPublishConfig
from features.publishing.platforms.base import PublishConfig


async def example_1_setup_accounts():
    """Example 1: Set up publishing manager with accounts."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Setting up Accounts")
    print("="*60)

    manager = PublishingManager()

    # Add TikTok account
    manager.add_account(
        account_id="my_tiktok_account",
        platform="tiktok",
        credentials={
            "api_key": "your_upload_post_api_key",
            "user": "your_upload_post_user"
        }
    )

    # Add Instagram account
    manager.add_account(
        account_id="my_instagram_account",
        platform="instagram",
        credentials={
            "api_key": "your_upload_post_api_key",
            "user": "your_upload_post_user"
        }
    )

    # Add Facebook account
    manager.add_account(
        account_id="my_facebook_account",
        platform="facebook",
        credentials={
            "api_key": "your_upload_post_api_key",
            "user": "your_upload_post_user",
            "page_id": "your_facebook_page_id"
        }
    )

    # Add LinkedIn account
    manager.add_account(
        account_id="my_linkedin_account",
        platform="linkedin",
        credentials={
            "api_key": "your_upload_post_api_key",
            "user": "your_upload_post_user"
        }
    )

    # Add YouTube account
    manager.add_account(
        account_id="my_youtube_account",
        platform="youtube",
        credentials={
            "client_secrets_file": "/path/to/client_secrets.json",
            "channel_name": "MyChannel",
            "channel_id": "UC1234567890",
            "oauth_storage_dir": "/path/to/oauth/storage"
        }
    )

    # List all accounts
    accounts = manager.list_all_accounts()
    print(f"\nConfigured {len(accounts)} accounts:")
    for account in accounts:
        print(f"  - {account['account_id']}: {', '.join(account['platforms'])}")

    return manager


async def example_2_single_platform(manager: PublishingManager):
    """Example 2: Publish to single platform."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Single Platform Publishing")
    print("="*60)

    config = PublishConfig(
        title="My Awesome Video",
        description="Check out this amazing content! #viral #trending",
        tags=["viral", "trending", "awesome"],
        platform_specific={
            "tiktok": {
                "privacy": "public",
                "allow_comments": True,
                "allow_duet": True,
                "allow_stitch": True
            }
        }
    )

    print("\nPublishing to TikTok...")
    result = await manager.publish_to_platform(
        account_id="my_tiktok_account",
        platform="tiktok",
        video_path="/path/to/video.mp4",
        config=config
    )

    print(f"  Success: {result.success}")
    print(f"  Status: {result.status}")
    print(f"  Video ID: {result.video_id}")
    print(f"  URL: {result.url}")
    if not result.success:
        print(f"  Error: {result.error}")


async def example_3_multi_platform(manager: PublishingManager):
    """Example 3: Publish to multiple platforms simultaneously."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Multi-Platform Publishing")
    print("="*60)

    config = PublishConfig(
        title="Cross-Platform Content",
        description="This video is perfect for all platforms! 🚀",
        tags=["crossplatform", "socialmedia", "content"],
        thumbnail_path="/path/to/thumbnail.jpg",
        platform_specific={
            "tiktok": {
                "privacy": "public",
                "allow_comments": True
            },
            "instagram": {
                "post_type": "reels",
                "location": "New York, NY"
            },
            "facebook": {
                "privacy": "public"
            },
            "linkedin": {
                "visibility": "public"
            }
        }
    )

    platforms = ["tiktok", "instagram", "facebook", "linkedin"]
    print(f"\nPublishing to {len(platforms)} platforms: {', '.join(platforms)}")

    results = await manager.publish_multi_platform(
        account_id="my_tiktok_account",  # Using same account ID (in practice, might be different per platform)
        platforms=platforms,
        video_path="/path/to/video.mp4",
        config=config
    )

    print("\nResults:")
    for platform, result in results.items():
        print(f"\n  {platform.upper()}:")
        print(f"    Success: {result.success}")
        print(f"    Status: {result.status}")
        if result.success:
            print(f"    Video ID: {result.video_id}")
            print(f"    URL: {result.url}")
        else:
            print(f"    Error: {result.error}")

    successes = sum(1 for r in results.values() if r.success)
    print(f"\n  Overall: {successes}/{len(platforms)} platforms succeeded")


async def example_4_video_validation(manager: PublishingManager):
    """Example 4: Validate video before publishing."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Video Validation")
    print("="*60)

    video_path = "/path/to/video.mp4"
    platforms = ["tiktok", "instagram", "youtube"]

    print(f"\nValidating video for {len(platforms)} platforms...")
    results = manager.validate_video_for_platforms(video_path, platforms)

    for platform, validation in results.items():
        print(f"\n  {platform.upper()}:")
        print(f"    Valid: {validation['valid']}")

        if validation['errors']:
            print(f"    Errors:")
            for error in validation['errors']:
                print(f"      ❌ {error}")

        if validation['warnings']:
            print(f"    Warnings:")
            for warning in validation['warnings']:
                print(f"      ⚠️  {warning}")

        if 'video_info' in validation:
            info = validation['video_info']
            print(f"    Info:")
            for key, value in info.items():
                print(f"      {key}: {value}")


async def example_5_scheduled_publishing():
    """Example 5: Scheduled publishing with queue."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Scheduled Publishing")
    print("="*60)

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from features.publishing.queue import Base

    # Set up database (in-memory for example)
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    # Create manager and queue
    manager = PublishingManager()
    manager.add_account(
        account_id="scheduled_account",
        platform="tiktok",
        credentials={"api_key": "...", "user": "..."}
    )

    queue = PublishingQueue(db, manager, worker_count=2)

    # Schedule video for 1 hour from now
    scheduled_time = datetime.utcnow() + timedelta(hours=1)

    config = PublishConfig(
        title="Scheduled Content",
        description="This was scheduled in advance!",
        tags=["scheduled", "automation"]
    )

    queued_config = QueuedPublishConfig(
        account_id="scheduled_account",
        platforms=["tiktok", "instagram"],
        video_path="/path/to/video.mp4",
        config=config,
        scheduled_time=scheduled_time,
        priority=8,  # High priority
        max_retries=3,
        webhook_url="https://myapp.com/webhook/publish-complete"
    )

    job = queue.add_job("job_123", queued_config)

    print(f"\nJob scheduled:")
    print(f"  Job ID: {job.id}")
    print(f"  Status: {job.status}")
    print(f"  Scheduled: {job.scheduled_time}")
    print(f"  Priority: {job.priority}")
    print(f"  Max Retries: {job.max_retries}")

    # Start queue workers
    print("\nStarting queue workers...")
    await queue.start()

    # In production, queue would run continuously
    # For example, let it process for a bit
    await asyncio.sleep(2)

    # Check job status
    job = queue.get_job("job_123")
    print(f"\nJob status after 2s: {job.status}")

    # Stop queue
    await queue.stop()


async def example_6_batch_publishing():
    """Example 6: Batch publish multiple videos."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Batch Publishing")
    print("="*60)

    manager = PublishingManager()

    # Prepare batch of videos
    batch = []

    for i in range(3):
        config = PublishConfig(
            title=f"Batch Video {i+1}",
            description=f"Video {i+1} from batch publishing",
            tags=[f"batch{i+1}", "automation"]
        )

        batch.append({
            "account_id": "my_tiktok_account",
            "platforms": ["tiktok", "instagram"],
            "video_path": f"/path/to/video_{i+1}.mp4",
            "config": config
        })

    print(f"\nPublishing {len(batch)} videos in batch...")
    results = await manager.publish_batch(batch)

    for i, result_map in enumerate(results, 1):
        print(f"\n  Video {i}:")
        for platform, result in result_map.items():
            status_icon = "✅" if result.success else "❌"
            print(f"    {status_icon} {platform}: {result.status}")


async def example_7_queue_management():
    """Example 7: Queue management and monitoring."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Queue Management")
    print("="*60)

    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from features.publishing.queue import Base, QueueStatus

    # Set up database
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()

    manager = PublishingManager()
    queue = PublishingQueue(db, manager)

    # Add multiple jobs
    for i in range(5):
        config = PublishConfig(
            title=f"Queue Test {i+1}",
            description="Testing queue management"
        )

        queued_config = QueuedPublishConfig(
            account_id="test_account",
            platforms=["tiktok"],
            video_path=f"/path/to/video_{i+1}.mp4",
            config=config,
            priority=i + 1  # Varying priorities
        )

        queue.add_job(f"job_{i+1}", queued_config)

    # Get queue stats
    stats = queue.get_queue_stats()
    print("\nQueue Statistics:")
    for status, count in stats.items():
        print(f"  {status}: {count}")

    # List pending jobs
    pending = queue.get_pending_jobs(limit=3)
    print(f"\nNext {len(pending)} jobs to process:")
    for job in pending:
        print(f"  - {job.id}: {job.title} (priority: {job.priority})")

    # Cancel a job
    if pending:
        job_to_cancel = pending[0].id
        success = queue.cancel_job(job_to_cancel)
        print(f"\nCancelled job {job_to_cancel}: {success}")

    # List jobs by status
    all_jobs = queue.list_jobs(status=QueueStatus.PENDING, limit=10)
    print(f"\nPending jobs: {len(all_jobs)}")


async def main():
    """Run all examples."""
    print("\n" + "="*80)
    print("PUBLISHING SYSTEM EXAMPLES")
    print("="*80)
    print("\nNote: These examples use placeholder paths and credentials.")
    print("Replace with your actual values before running.")

    # Example 1: Setup
    manager = await example_1_setup_accounts()

    # Example 2: Single platform
    # await example_2_single_platform(manager)

    # Example 3: Multi-platform
    # await example_3_multi_platform(manager)

    # Example 4: Validation
    # await example_4_video_validation(manager)

    # Example 5: Scheduled publishing
    # await example_5_scheduled_publishing()

    # Example 6: Batch publishing
    # await example_6_batch_publishing()

    # Example 7: Queue management
    # await example_7_queue_management()

    print("\n" + "="*80)
    print("Examples complete!")
    print("="*80)


if __name__ == "__main__":
    # Run with: python examples/publishing_example.py
    asyncio.run(main())
