import os
from typing import Dict, Any, List, Optional
from fastmcp import FastMCP
from datetime import datetime, date, timedelta
import asyncio
from ..utils.supabase_client import supabase_client
from ..models.database import JournalEntryCreate

# Initialize MCP server
mcp = FastMCP("Journaling MCP Server")
mcp.description = "MCP server for journaling tools including mood analysis, wellbeing calculation, and tag generation"

# Global services (will be initialized with app)
sentiment_service = None
wellbeing_service = None

def set_services(sentiment_svc, wellbeing_svc):
    """Set global service instances"""
    global sentiment_service, wellbeing_service
    sentiment_service = sentiment_svc
    wellbeing_service = wellbeing_svc

@mcp.tool()
async def analyze_mood(text: str, previous_mood: Optional[int] = None) -> Dict[str, Any]:
    """
    Analyze mood from journal entry text.
    
    Args:
        text: The journal entry text to analyze
        previous_mood: Previous mood score for context (1-10)
    
    Returns:
        Dictionary with mood_score, sentiment, and confidence
    """
    if not sentiment_service:
        return {
            "mood_score": 5,
            "sentiment": "neutral",
            "confidence": 0.0,
            "error": "Sentiment service not initialized"
        }
    
    try:
        # Analyze sentiment
        sentiment_result = await sentiment_service.analyze_sentiment(text)
        
        # Convert sentiment to mood score
        mood_score = sentiment_service.sentiment_to_mood(
            sentiment_result["polarity"],
            previous_mood
        )
        
        return {
            "mood_score": mood_score,
            "sentiment": sentiment_result["sentiment"],
            "polarity": sentiment_result["polarity"],
            "confidence": sentiment_result["confidence"],
            "emotions": sentiment_result.get("emotions", {})
        }
    except Exception as e:
        return {
            "mood_score": previous_mood or 5,
            "sentiment": "neutral",
            "confidence": 0.0,
            "error": str(e)
        }

@mcp.tool()
async def calculate_wellbeing(metrics: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculate well-being score from daily metrics.
    
    Args:
        metrics: Dictionary of daily metrics (sleep_hours, stress_level, etc.)
    
    Returns:
        Dictionary with wellbeing_score and component scores
    """
    if not wellbeing_service:
        return {
            "wellbeing_score": 5.0,
            "components": {},
            "error": "Wellbeing service not initialized"
        }
    
    try:
        # Calculate wellbeing
        result = await wellbeing_service.calculate_wellbeing(metrics)
        return result
    except Exception as e:
        return {
            "wellbeing_score": 5.0,
            "components": {},
            "error": str(e)
        }

@mcp.tool()
async def generate_tags(text: str, max_tags: int = 5) -> List[str]:
    """
    Generate relevant tags for a journal entry.
    
    Args:
        text: The journal entry text
        max_tags: Maximum number of tags to generate
    
    Returns:
        List of generated tags
    """
    try:
        # Simple tag generation based on key topics
        # In production, this would use NLP for better extraction
        import re
        from collections import Counter
        
        # Remove common words
        stop_words = set([
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'about', 'as', 'is', 'was', 'are', 'were',
            'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'them', 'their',
            'my', 'your', 'his', 'her', 'its', 'our', 'me', 'him', 'us'
        ])
        
        # Extract words
        words = re.findall(r'\b[a-z]+\b', text.lower())
        words = [w for w in words if w not in stop_words and len(w) > 3]
        
        # Count word frequency
        word_freq = Counter(words)
        
        # Get most common words as tags
        tags = [word for word, _ in word_freq.most_common(max_tags)]
        
        # Add some contextual tags based on content
        if any(word in text.lower() for word in ['happy', 'joy', 'excited', 'great']):
            tags.append('positive')
        if any(word in text.lower() for word in ['sad', 'depressed', 'anxious', 'worried']):
            tags.append('challenging')
        if any(word in text.lower() for word in ['work', 'job', 'office', 'meeting']):
            tags.append('work')
        if any(word in text.lower() for word in ['family', 'friend', 'relationship']):
            tags.append('relationships')
        if any(word in text.lower() for word in ['exercise', 'gym', 'run', 'workout']):
            tags.append('fitness')
        
        # Return unique tags up to max_tags
        unique_tags = list(dict.fromkeys(tags))[:max_tags]
        return unique_tags
        
    except Exception as e:
        return ["general"]

@mcp.tool()
async def detect_patterns(user_id: str, days: int = 30) -> Dict[str, Any]:
    """
    Detect patterns in user's journal entries and metrics.
    
    Args:
        user_id: User ID to analyze
        days: Number of days to analyze
    
    Returns:
        Dictionary with detected patterns and insights
    """
    try:
        supabase = supabase_client.get_client()
        
        # Calculate date range
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Get journal entries
        entries_response = supabase.table("journal_entries")\
            .select("mood_score, energy_level, tags, entry_date, created_at")\
            .eq("user_id", user_id)\
            .gte("entry_date", start_date.isoformat())\
            .lte("entry_date", end_date.isoformat())\
            .execute()
        
        # Get daily metrics
        metrics_response = supabase.table("daily_metrics")\
            .select("wellbeing_score, sleep_hours, stress_level, date")\
            .eq("user_id", user_id)\
            .gte("date", start_date.isoformat())\
            .lte("date", end_date.isoformat())\
            .execute()
        
        patterns = {
            "mood_trends": [],
            "energy_patterns": [],
            "wellbeing_insights": [],
            "correlations": []
        }
        
        if entries_response.data:
            # Analyze mood trends
            moods = [e["mood_score"] for e in entries_response.data if e.get("mood_score")]
            if moods:
                avg_mood = sum(moods) / len(moods)
                mood_trend = "stable"
                if len(moods) > 7:
                    recent_avg = sum(moods[-7:]) / 7
                    older_avg = sum(moods[:-7]) / len(moods[:-7])
                    if recent_avg > older_avg * 1.1:
                        mood_trend = "improving"
                    elif recent_avg < older_avg * 0.9:
                        mood_trend = "declining"
                
                patterns["mood_trends"].append({
                    "average_mood": round(avg_mood, 1),
                    "trend": mood_trend,
                    "data_points": len(moods)
                })
        
        if metrics_response.data:
            # Analyze wellbeing patterns
            wellbeing_scores = [m["wellbeing_score"] for m in metrics_response.data if m.get("wellbeing_score")]
            sleep_hours = [m["sleep_hours"] for m in metrics_response.data if m.get("sleep_hours")]
            stress_levels = [m["stress_level"] for m in metrics_response.data if m.get("stress_level")]
            
            if wellbeing_scores and sleep_hours:
                # Check correlation between sleep and wellbeing
                if len(wellbeing_scores) == len(sleep_hours):
                    # Simple correlation check
                    good_sleep_wellbeing = []
                    poor_sleep_wellbeing = []
                    
                    for i, sleep in enumerate(sleep_hours):
                        if sleep >= 7:
                            good_sleep_wellbeing.append(wellbeing_scores[i])
                        else:
                            poor_sleep_wellbeing.append(wellbeing_scores[i])
                    
                    if good_sleep_wellbeing and poor_sleep_wellbeing:
                        good_avg = sum(good_sleep_wellbeing) / len(good_sleep_wellbeing)
                        poor_avg = sum(poor_sleep_wellbeing) / len(poor_sleep_wellbeing)
                        
                        if good_avg > poor_avg * 1.2:
                            patterns["correlations"].append({
                                "type": "sleep_wellbeing",
                                "insight": "Better sleep correlates with higher wellbeing scores",
                                "strength": "strong"
                            })
        
        return patterns
        
    except Exception as e:
        return {
            "error": str(e),
            "patterns": {}
        }

@mcp.tool()
async def suggest_prompts(mood: int, recent_topics: List[str] = None) -> List[str]:
    """
    Suggest journal prompts based on mood and recent topics.
    
    Args:
        mood: Current mood score (1-10)
        recent_topics: List of recent journal topics/tags
    
    Returns:
        List of suggested journal prompts
    """
    prompts = []
    
    # Mood-based prompts
    if mood <= 3:
        prompts.extend([
            "What's one small thing that could make today a bit better?",
            "Describe a time when you overcame a similar challenge.",
            "What would you tell a friend going through this?",
            "List three things you're grateful for, no matter how small."
        ])
    elif mood <= 5:
        prompts.extend([
            "What's taking up most of your mental energy right now?",
            "Describe your ideal day - what would it look like?",
            "What's one thing you'd like to change about your current situation?",
            "When did you last feel truly content? What was different?"
        ])
    elif mood <= 7:
        prompts.extend([
            "What's going well in your life right now?",
            "What goal are you working towards?",
            "Describe a recent moment that made you smile.",
            "What are you looking forward to?"
        ])
    else:
        prompts.extend([
            "What's contributing to your positive mood today?",
            "How can you share this positive energy with others?",
            "What achievement are you most proud of recently?",
            "Describe this feeling in detail - capture it for future reference."
        ])
    
    # Topic-based prompts
    if recent_topics:
        if "work" in recent_topics:
            prompts.append("How do you want your career to evolve in the next year?")
        if "relationships" in recent_topics:
            prompts.append("What qualities do you value most in your relationships?")
        if "fitness" in recent_topics:
            prompts.append("How does physical activity affect your mental state?")
        if "challenging" in recent_topics:
            prompts.append("What coping strategies have worked best for you?")
    
    # General reflection prompts
    prompts.extend([
        "What did you learn about yourself today?",
        "If today had a color, what would it be and why?",
        "What would your future self thank you for doing today?"
    ])
    
    # Return 5 random prompts from the list
    import random
    return random.sample(prompts, min(5, len(prompts)))

@mcp.tool()
async def generate_ai_insights(
    entry_text: str,
    mood_score: int,
    metrics: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate AI therapist insights based on journal entry and metrics.
    
    Args:
        entry_text: The journal entry text
        mood_score: Current mood score
        metrics: Optional daily metrics
    
    Returns:
        AI-generated insights and observations
    """
    try:
        insights = []
        
        # Analyze entry length and engagement
        word_count = len(entry_text.split())
        if word_count < 50:
            insights.append("Your entry today is quite brief. Sometimes exploring thoughts in more detail can provide clarity.")
        elif word_count > 500:
            insights.append("You've shared a lot today. This level of reflection shows deep engagement with your thoughts.")
        
        # Mood-based insights
        if mood_score <= 3:
            insights.append("I notice you're experiencing some challenges. Remember that difficult emotions are temporary and valid.")
        elif mood_score >= 8:
            insights.append("Your positive mood is wonderful to see. Consider what specific factors contributed to this feeling.")
        
        # Check for emotional words
        emotional_words = {
            "positive": ["happy", "joy", "excited", "grateful", "proud", "confident"],
            "negative": ["sad", "angry", "frustrated", "anxious", "worried", "stressed"],
            "neutral": ["tired", "busy", "routine", "normal", "okay"]
        }
        
        text_lower = entry_text.lower()
        detected_emotions = []
        
        for emotion_type, words in emotional_words.items():
            for word in words:
                if word in text_lower:
                    detected_emotions.append((emotion_type, word))
        
        if detected_emotions:
            primary_emotion = detected_emotions[0][0]
            if primary_emotion == "negative":
                insights.append("I notice you're working through some difficult emotions. This awareness is the first step toward processing them.")
            elif primary_emotion == "positive":
                insights.append("The positive emotions you're expressing are valuable. Consider what actions or thoughts led to these feelings.")
        
        # Metrics-based insights
        if metrics:
            if metrics.get("sleep_hours", 0) < 6:
                insights.append("Your sleep has been limited. This might be affecting your mood and energy levels.")
            if metrics.get("stress_level", 0) > 7:
                insights.append("High stress levels can impact many areas of life. What stress-reduction techniques work best for you?")
            if metrics.get("exercise_minutes", 0) > 30:
                insights.append("Great job staying active! Physical activity is strongly linked to improved mood.")
        
        # Combine insights
        if insights:
            return " ".join(insights[:3])  # Limit to 3 insights
        else:
            return "Thank you for sharing your thoughts today. Regular journaling helps build self-awareness and emotional resilience."
            
    except Exception as e:
        return "Your reflection today is valuable. Keep exploring your thoughts and feelings through journaling."

# Create FastAPI app for MCP
def get_mcp_app():
    """Get the MCP FastAPI app"""
    return mcp.get_app(transport="streamable-http")

# Export MCP instance
__all__ = ["mcp", "get_mcp_app", "set_services"]