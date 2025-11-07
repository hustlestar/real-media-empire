"""
Tests for Perplexity trend research.

All tests use mocks - no real API calls.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.content.trend_research import (
    TrendResearcher,
    TrendInsight,
    TrendResearchResult
)


@pytest.fixture
def trend_researcher():
    """Create TrendResearcher instance."""
    return TrendResearcher(api_key="test_key", model="sonar")


class TestTrendResearcherInit:
    """Test TrendResearcher initialization."""

    def test_initialization(self):
        """Test creating trend researcher."""
        researcher = TrendResearcher(api_key="test_api_key")
        assert researcher.api_key == "test_api_key"
        assert researcher.model == "sonar"
        assert researcher.base_url == "https://api.perplexity.ai/chat/completions"

    def test_initialization_custom_model(self):
        """Test creating with custom model."""
        researcher = TrendResearcher(api_key="key", model="sonar-pro")
        assert researcher.model == "sonar-pro"


class TestTrendResearch:
    """Test trend research functionality."""

    @pytest.mark.asyncio
    async def test_research_trends_success(self, trend_researcher):
        """Test successful trend research."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": """1. **Cold Plunge Challenge**
Description: TikTokers are documenting their reactions to cold showers/plunges
Hashtags: #ColdPlunge #ColdShower #WimHof #MorningRoutine #Biohacking

2. **75 Hard Transformation**
Description: 75-day challenge including cold showers as part of routine
Hashtags: #75Hard #Transformation #DisciplineEqualsFreedom"""
                }
            }],
            "usage": {
                "total_tokens": 150
            }
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_response
        trend_researcher.client = mock_client

        # Test research
        result = await trend_researcher.research_trends(
            topic="cold showers",
            platform="tiktok",
            num_trends=2
        )

        # Verify result
        assert isinstance(result, TrendResearchResult)
        assert result.topic == "cold showers"
        assert result.platform == "tiktok"
        assert len(result.trends) > 0
        assert result.tokens_used == 150

        # Verify API call
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert "model" in call_args[1]["json"]
        assert "messages" in call_args[1]["json"]

    @pytest.mark.asyncio
    async def test_research_different_platforms(self, trend_researcher):
        """Test research for different platforms."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": "1. Test trend\n#test"}
            }],
            "usage": {"total_tokens": 50}
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_response
        trend_researcher.client = mock_client

        platforms = ["tiktok", "youtube", "instagram", "twitter", "linkedin"]

        for platform in platforms:
            result = await trend_researcher.research_trends(
                topic="fitness",
                platform=platform,
                num_trends=1
            )
            assert result.platform == platform


class TestHashtagOptimization:
    """Test hashtag optimization."""

    @pytest.mark.asyncio
    async def test_optimize_hashtags_success(self, trend_researcher):
        """Test successful hashtag optimization."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": """#MorningRoutine
#ProductivityTips
#TimeManagement
#SuccessHabits
#RiseAndGrind"""
                }
            }],
            "usage": {"total_tokens": 50}
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_response
        trend_researcher.client = mock_client

        # Test optimization
        hashtags = await trend_researcher.optimize_hashtags(
            content_description="Morning routine video for productivity",
            platform="tiktok",
            max_hashtags=10
        )

        # Verify result
        assert isinstance(hashtags, list)
        assert len(hashtags) <= 10
        assert all(tag.startswith('#') for tag in hashtags)
        assert "#MorningRoutine" in hashtags

    @pytest.mark.asyncio
    async def test_optimize_hashtags_platform_limits(self, trend_researcher):
        """Test hashtag optimization respects platform limits."""
        mock_client = AsyncMock()

        # Generate 50 hashtags
        hashtags_content = "\n".join([f"#Tag{i}" for i in range(50)])

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {"content": hashtags_content}
            }],
            "usage": {"total_tokens": 100}
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_response
        trend_researcher.client = mock_client

        # TikTok: max 30
        hashtags = await trend_researcher.optimize_hashtags(
            content_description="Test content",
            platform="tiktok",
            max_hashtags=40  # Request 40 but should get max 30
        )
        assert len(hashtags) <= 30

        # Twitter: max 10
        hashtags = await trend_researcher.optimize_hashtags(
            content_description="Test content",
            platform="twitter",
            max_hashtags=20  # Request 20 but should get max 10
        )
        assert len(hashtags) <= 10


class TestContentStrategy:
    """Test content strategy generation."""

    @pytest.mark.asyncio
    async def test_generate_content_strategy(self, trend_researcher):
        """Test content strategy generation."""
        mock_client = AsyncMock()

        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": """Content Strategy:

1. Leverage cold plunge reactions
2. Create before/after transformations
3. Post 2-3 times per week
4. Best times: 6-9am, 7-9pm
5. Collaborate with fitness influencers"""
                }
            }],
            "usage": {"total_tokens": 200}
        }
        mock_response.raise_for_status = MagicMock()

        mock_client.post.return_value = mock_response
        trend_researcher.client = mock_client

        # Create mock trends
        trends = [
            TrendInsight(
                title="Cold Plunge Challenge",
                description="Viral cold shower content",
                hashtags=["#ColdPlunge", "#Challenge"],
                content_style="Before/after reaction",
                platform="tiktok"
            )
        ]

        # Test strategy generation
        strategy = await trend_researcher.generate_content_strategy(
            topic="cold showers",
            platform="tiktok",
            trends=trends
        )

        # Verify result
        assert isinstance(strategy, str)
        assert len(strategy) > 0


class TestPromptBuilding:
    """Test prompt building."""

    def test_build_prompt_tiktok(self, trend_researcher):
        """Test building TikTok-specific prompt."""
        prompt = trend_researcher._build_prompt("fitness", "tiktok", 3)

        assert "fitness" in prompt
        assert "tiktok" in prompt.lower()
        assert "hashtag" in prompt.lower()
        assert "3" in prompt

    def test_build_prompt_youtube(self, trend_researcher):
        """Test building YouTube-specific prompt."""
        prompt = trend_researcher._build_prompt("cooking", "youtube", 5)

        assert "cooking" in prompt
        assert "youtube" in prompt.lower()
        assert "keyword" in prompt.lower()
        assert "5" in prompt

    def test_build_prompt_linkedin(self, trend_researcher):
        """Test building LinkedIn-specific prompt."""
        prompt = trend_researcher._build_prompt("business", "linkedin", 3)

        assert "business" in prompt
        assert "linkedin" in prompt.lower()
        assert "professional" in prompt.lower()


class TestTrendParsing:
    """Test trend parsing from responses."""

    def test_parse_trends_basic(self, trend_researcher):
        """Test parsing basic trend format."""
        response = """1. **Cold Plunge Videos**
Documenting cold shower reactions
#ColdPlunge #Challenge #Viral

2. **Morning Routine**
POV morning routines with cold showers
#MorningRoutine #Productivity"""

        trends = trend_researcher._parse_trends(response, "tiktok")

        assert len(trends) == 2
        assert trends[0].title == "Cold Plunge Videos"
        assert "#ColdPlunge" in trends[0].hashtags
        assert trends[0].platform == "tiktok"

    def test_parse_trends_with_hashtags(self, trend_researcher):
        """Test extracting hashtags from trends."""
        response = """1. Fitness Challenge
#Fitness #Challenge #Motivation #Gym #Workout"""

        trends = trend_researcher._parse_trends(response, "instagram")

        assert len(trends) >= 1
        assert len(trends[0].hashtags) > 0
        assert all(tag.startswith('#') for tag in trends[0].hashtags)

    def test_parse_trends_limits_hashtags(self, trend_researcher):
        """Test that parsing limits hashtags per trend."""
        response = f"""1. Test Trend
{' '.join([f'#Tag{i}' for i in range(20)])}"""

        trends = trend_researcher._parse_trends(response, "tiktok")

        # Should limit to 5 hashtags per trend
        assert len(trends[0].hashtags) <= 5

    def test_parse_trends_empty_response(self, trend_researcher):
        """Test parsing empty response."""
        response = ""

        trends = trend_researcher._parse_trends(response, "tiktok")

        assert isinstance(trends, list)
        assert len(trends) == 0


class TestClientLifecycle:
    """Test HTTP client lifecycle."""

    @pytest.mark.asyncio
    async def test_close_client(self, trend_researcher):
        """Test closing HTTP client."""
        mock_client = AsyncMock()
        trend_researcher.client = mock_client

        await trend_researcher.close()

        mock_client.aclose.assert_called_once()
