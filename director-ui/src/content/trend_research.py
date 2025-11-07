"""
Trend Research with Perplexity AI

Real-time web search for trending topics, hashtags, and content styles
to optimize social media content for virality.
"""

import httpx
from typing import List, Literal, Optional
from pydantic import BaseModel
from datetime import datetime


class TrendInsight(BaseModel):
    """A single trending topic or insight."""
    title: str
    description: str
    hashtags: List[str]
    content_style: str
    platform: str
    relevance_score: Optional[float] = None


class TrendResearchResult(BaseModel):
    """Results from trend research query."""
    topic: str
    platform: str
    trends: List[TrendInsight]
    search_date: datetime
    raw_response: str
    tokens_used: int


class TrendResearcher:
    """
    Research trending topics and content styles using Perplexity AI.

    Uses Perplexity's real-time web search to find current viral trends,
    hashtags, and content styles that are performing well on social platforms.
    """

    def __init__(self, api_key: str, model: str = "sonar"):
        """
        Initialize TrendResearcher.

        Args:
            api_key: Perplexity API key
            model: Model to use (sonar, sonar-pro, etc.)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )

    async def research_trends(
        self,
        topic: str,
        platform: Literal["tiktok", "youtube", "instagram", "twitter", "linkedin"] = "tiktok",
        num_trends: int = 3
    ) -> TrendResearchResult:
        """
        Research current viral trends related to a topic.

        Args:
            topic: The topic to research (e.g., "fitness", "productivity")
            platform: Target social media platform
            num_trends: Number of trends to return (1-10)

        Returns:
            TrendResearchResult with trending insights

        Example:
            >>> researcher = TrendResearcher(api_key="...")
            >>> result = await researcher.research_trends("cold showers", "tiktok", 3)
            >>> for trend in result.trends:
            ...     print(trend.title, trend.hashtags)
        """
        # Build platform-specific prompt
        prompt = self._build_prompt(topic, platform, num_trends)

        # Query Perplexity
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are a social media trend analyst with real-time web access. Provide current, actionable insights about viral trends."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.2,
            "max_tokens": 1000
        }

        response = await self.client.post(self.base_url, json=payload)
        response.raise_for_status()
        result = response.json()

        # Extract response
        content = result["choices"][0]["message"]["content"]
        tokens_used = result["usage"]["total_tokens"]

        # Parse trends from response
        trends = self._parse_trends(content, platform)

        return TrendResearchResult(
            topic=topic,
            platform=platform,
            trends=trends,
            search_date=datetime.now(),
            raw_response=content,
            tokens_used=tokens_used
        )

    def _build_prompt(
        self,
        topic: str,
        platform: str,
        num_trends: int
    ) -> str:
        """Build platform-specific trend research prompt."""

        platform_specifics = {
            "tiktok": "Focus on viral sounds, trending effects, and short-form content styles. Include hashtag suggestions.",
            "youtube": "Focus on trending video formats, thumbnails styles, and title patterns. Include keyword suggestions.",
            "instagram": "Focus on Reels trends, aesthetic styles, and caption patterns. Include hashtag suggestions.",
            "twitter": "Focus on trending topics, conversation starters, and thread formats.",
            "linkedin": "Focus on professional content trends, thought leadership topics, and engagement patterns."
        }

        return f"""Find the top {num_trends} current viral trends related to: {topic}

Platform: {platform}
{platform_specifics.get(platform, "Focus on trending topics and content styles.")}

For each trend, provide:
1. Clear title/name of the trend
2. Brief description (2-3 sentences)
3. Relevant hashtags (3-5 per trend)
4. Content style/format (e.g., "POV storytelling", "before/after comparison")
5. Why it's working right now

Format each trend clearly. Be specific and actionable. Only return {num_trends} trends — no more, no less."""

    def _parse_trends(self, response: str, platform: str) -> List[TrendInsight]:
        """
        Parse trends from Perplexity response.

        This is a simple parser - can be enhanced with more sophisticated
        NLP or structured output formatting.
        """
        trends = []

        # Split by numbered items or clear separators
        sections = []
        for line in response.split('\n'):
            if line.strip() and (
                line.strip()[0].isdigit() or
                line.startswith('**') or
                line.startswith('##')
            ):
                sections.append([line])
            elif sections:
                sections[-1].append(line)

        # Parse each section
        for section in sections:
            text = '\n'.join(section)

            # Extract title (first line)
            lines = [l.strip() for l in text.split('\n') if l.strip()]
            if not lines:
                continue

            title = lines[0].lstrip('0123456789.#* ').rstrip(':')

            # Extract hashtags
            hashtags = []
            for line in lines:
                words = line.split()
                hashtags.extend([w for w in words if w.startswith('#')])

            # Description is the rest
            description = ' '.join(lines[1:3] if len(lines) > 1 else lines)

            # Try to identify content style
            content_style = "Unknown"
            style_keywords = {
                "pov": "POV storytelling",
                "before": "Before/after comparison",
                "tutorial": "Tutorial/how-to",
                "reaction": "Reaction video",
                "voiceover": "Voice-over narration",
                "transition": "Transition effects",
                "storytime": "Story-time narrative"
            }
            for keyword, style in style_keywords.items():
                if keyword in text.lower():
                    content_style = style
                    break

            trends.append(TrendInsight(
                title=title,
                description=description[:200],  # Limit description length
                hashtags=hashtags[:5],  # Max 5 hashtags per trend
                content_style=content_style,
                platform=platform
            ))

        return trends[:10]  # Max 10 trends

    async def generate_content_strategy(
        self,
        topic: str,
        platform: str,
        trends: List[TrendInsight]
    ) -> str:
        """
        Generate a content strategy based on researched trends.

        Args:
            topic: Original topic
            platform: Target platform
            trends: List of trend insights

        Returns:
            Strategic recommendations for content creation
        """
        trend_summary = "\n".join([
            f"- {t.title}: {t.description}"
            for t in trends
        ])

        prompt = f"""Based on these current {platform} trends related to {topic}:

{trend_summary}

Create a strategic content plan that:
1. Leverages these trends effectively
2. Provides specific content ideas (3-5 ideas)
3. Suggests optimal posting times/frequency
4. Recommends hashtag strategy
5. Identifies potential collaboration opportunities

Be specific and actionable."""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }

        response = await self.client.post(self.base_url, json=payload)
        response.raise_for_status()
        result = response.json()

        return result["choices"][0]["message"]["content"]

    async def optimize_hashtags(
        self,
        content_description: str,
        platform: str,
        max_hashtags: int = 10
    ) -> List[str]:
        """
        Generate optimized hashtags for content.

        Args:
            content_description: Description of the content
            platform: Target platform
            max_hashtags: Maximum number of hashtags to generate

        Returns:
            List of recommended hashtags
        """
        platform_limits = {
            "tiktok": 30,
            "instagram": 30,
            "youtube": 15,
            "twitter": 10,
            "linkedin": 30
        }

        max_allowed = min(max_hashtags, platform_limits.get(platform, 10))

        prompt = f"""Generate {max_allowed} trending, relevant hashtags for this {platform} content:

{content_description}

Requirements:
- Mix of popular and niche hashtags
- Platform-appropriate
- Currently trending
- Ranked by potential reach

Return only hashtags, one per line, starting with #."""

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 200
        }

        response = await self.client.post(self.base_url, json=payload)
        response.raise_for_status()
        result = response.json()

        content = result["choices"][0]["message"]["content"]

        # Extract hashtags
        hashtags = []
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('#'):
                # Clean up hashtag
                tag = line.split()[0].rstrip('.,;:')
                if tag and len(tag) > 1:
                    hashtags.append(tag)

        return hashtags[:max_allowed]

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
