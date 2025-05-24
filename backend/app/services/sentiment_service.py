from typing import Dict, Any, Optional, List
import asyncio
from textblob import TextBlob
import nltk
from collections import Counter
import re

# Download required NLTK data (run once during initialization)
try:
    nltk.download('punkt', quiet=True)
    nltk.download('brown', quiet=True)
    nltk.download('wordnet', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except:
    pass

class SentimentAnalysisService:
    """Service for analyzing sentiment and emotions in journal entries"""
    
    def __init__(self):
        # Emotion keywords for basic emotion detection
        self.emotion_keywords = {
            "joy": ["happy", "joy", "joyful", "elated", "cheerful", "delighted", "pleased", "glad", "content", "satisfied"],
            "sadness": ["sad", "unhappy", "depressed", "melancholy", "sorrowful", "gloomy", "miserable", "down", "blue"],
            "anger": ["angry", "mad", "furious", "irritated", "annoyed", "frustrated", "enraged", "livid", "upset"],
            "fear": ["afraid", "scared", "fearful", "anxious", "nervous", "worried", "terrified", "panicked", "uneasy"],
            "surprise": ["surprised", "amazed", "astonished", "shocked", "stunned", "startled", "bewildered"],
            "disgust": ["disgusted", "revolted", "repulsed", "sickened", "nauseated", "appalled"],
            "love": ["love", "loving", "affectionate", "caring", "fond", "devoted", "adoring", "cherish"],
            "trust": ["trust", "confident", "secure", "faith", "reliable", "dependable", "assured"],
            "anticipation": ["excited", "eager", "looking forward", "anticipating", "hopeful", "expecting"]
        }
        
        # Intensity modifiers
        self.intensifiers = ["very", "extremely", "incredibly", "really", "so", "quite", "absolutely", "totally"]
        self.diminishers = ["slightly", "somewhat", "a bit", "a little", "rather", "fairly", "kind of", "sort of"]
    
    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using TextBlob and custom analysis.
        
        Returns:
            Dictionary containing sentiment analysis results
        """
        try:
            # Create TextBlob object
            blob = TextBlob(text)
            
            # Get polarity and subjectivity
            polarity = blob.sentiment.polarity  # -1 to 1
            subjectivity = blob.sentiment.subjectivity  # 0 to 1
            
            # Determine sentiment category
            if polarity > 0.1:
                sentiment = "positive"
            elif polarity < -0.1:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            # Calculate confidence based on polarity strength and subjectivity
            confidence = min(abs(polarity) * (1 - subjectivity * 0.5), 1.0)
            
            # Detect emotions
            emotions = await self.detect_emotions(text)
            
            # Analyze sentence-level sentiment
            sentence_sentiments = []
            for sentence in blob.sentences:
                sentence_sentiments.append({
                    "text": str(sentence),
                    "polarity": sentence.sentiment.polarity,
                    "sentiment": "positive" if sentence.sentiment.polarity > 0.1 else "negative" if sentence.sentiment.polarity < -0.1 else "neutral"
                })
            
            return {
                "polarity": round(polarity, 3),
                "subjectivity": round(subjectivity, 3),
                "sentiment": sentiment,
                "confidence": round(confidence, 3),
                "emotions": emotions,
                "sentence_sentiments": sentence_sentiments[:5],  # Limit to 5 sentences
                "dominant_emotion": max(emotions.items(), key=lambda x: x[1])[0] if emotions else None
            }
            
        except Exception as e:
            # Return neutral sentiment on error
            return {
                "polarity": 0.0,
                "subjectivity": 0.5,
                "sentiment": "neutral",
                "confidence": 0.0,
                "emotions": {},
                "error": str(e)
            }
    
    async def detect_emotions(self, text: str) -> Dict[str, float]:
        """
        Detect emotions in text based on keyword matching and context.
        
        Returns:
            Dictionary of emotion scores (0-1)
        """
        text_lower = text.lower()
        words = text_lower.split()
        emotion_scores = Counter()
        total_emotion_words = 0
        
        # Check for emotion keywords
        for emotion, keywords in self.emotion_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    # Check for intensifiers/diminishers before the keyword
                    keyword_index = text_lower.find(keyword)
                    preceding_text = text_lower[max(0, keyword_index-20):keyword_index]
                    
                    intensity = 1.0
                    for intensifier in self.intensifiers:
                        if intensifier in preceding_text:
                            intensity = 1.5
                            break
                    for diminisher in self.diminishers:
                        if diminisher in preceding_text:
                            intensity = 0.5
                            break
                    
                    score += intensity
                    total_emotion_words += 1
            
            if score > 0:
                emotion_scores[emotion] = score
        
        # Normalize scores
        if emotion_scores:
            max_score = max(emotion_scores.values())
            return {
                emotion: round(score / max_score, 2)
                for emotion, score in emotion_scores.items()
            }
        else:
            return {}
    
    def sentiment_to_mood(self, polarity: float, previous_mood: Optional[int] = None) -> int:
        """
        Convert sentiment polarity to mood score (1-10).
        
        Args:
            polarity: Sentiment polarity (-1 to 1)
            previous_mood: Previous mood score for smoothing
            
        Returns:
            Mood score (1-10)
        """
        # Convert polarity to 1-10 scale
        # -1 -> 1, 0 -> 5.5, 1 -> 10
        base_mood = int(round((polarity + 1) * 4.5 + 1))
        base_mood = max(1, min(10, base_mood))
        
        # If we have a previous mood, apply smoothing
        if previous_mood:
            # Don't change too drastically from previous mood
            max_change = 3
            if abs(base_mood - previous_mood) > max_change:
                if base_mood > previous_mood:
                    base_mood = previous_mood + max_change
                else:
                    base_mood = previous_mood - max_change
        
        return base_mood
    
    async def analyze_themes(self, texts: List[str]) -> Dict[str, Any]:
        """
        Analyze recurring themes across multiple journal entries.
        
        Args:
            texts: List of journal entry texts
            
        Returns:
            Dictionary of themes and their frequencies
        """
        # Combine all texts
        combined_text = " ".join(texts).lower()
        
        # Extract nouns as potential themes
        blob = TextBlob(combined_text)
        nouns = []
        
        for word, tag in blob.tags:
            if tag in ['NN', 'NNS', 'NNP', 'NNPS']:  # Noun tags
                if len(word) > 3 and word not in ['today', 'yesterday', 'tomorrow', 'time', 'day', 'week', 'month', 'year']:
                    nouns.append(word.lower())
        
        # Count noun frequencies
        theme_counts = Counter(nouns)
        
        # Get top themes
        top_themes = dict(theme_counts.most_common(10))
        
        # Categorize themes
        theme_categories = {
            "work": ["work", "job", "office", "meeting", "project", "deadline", "boss", "colleague"],
            "relationships": ["family", "friend", "partner", "love", "relationship", "mother", "father", "brother", "sister"],
            "health": ["health", "exercise", "sleep", "tired", "energy", "sick", "doctor", "medicine"],
            "emotions": ["happy", "sad", "angry", "anxious", "stressed", "excited", "worried", "calm"],
            "hobbies": ["read", "music", "movie", "game", "sport", "hobby", "fun", "play"]
        }
        
        categorized_themes = {}
        for category, keywords in theme_categories.items():
            score = sum(combined_text.count(keyword) for keyword in keywords)
            if score > 0:
                categorized_themes[category] = score
        
        return {
            "top_themes": top_themes,
            "theme_categories": categorized_themes,
            "total_entries_analyzed": len(texts)
        }
    
    async def generate_sentiment_summary(
        self,
        entries: List[Dict[str, Any]],
        period: str = "week"
    ) -> Dict[str, Any]:
        """
        Generate a sentiment summary for a period.
        
        Args:
            entries: List of journal entries with sentiment data
            period: Time period for summary
            
        Returns:
            Summary of sentiment trends
        """
        if not entries:
            return {
                "period": period,
                "summary": "No entries to analyze",
                "average_sentiment": 0.0,
                "trend": "stable"
            }
        
        # Extract sentiment scores
        sentiment_scores = [
            entry.get("sentiment_score", 0.0)
            for entry in entries
            if entry.get("sentiment_score") is not None
        ]
        
        if not sentiment_scores:
            return {
                "period": period,
                "summary": "No sentiment data available",
                "average_sentiment": 0.0,
                "trend": "stable"
            }
        
        # Calculate average
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        # Determine trend
        if len(sentiment_scores) >= 3:
            first_half = sentiment_scores[:len(sentiment_scores)//2]
            second_half = sentiment_scores[len(sentiment_scores)//2:]
            
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            
            if second_avg > first_avg * 1.1:
                trend = "improving"
            elif second_avg < first_avg * 0.9:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        # Count sentiment types
        positive_count = sum(1 for s in sentiment_scores if s > 0.1)
        negative_count = sum(1 for s in sentiment_scores if s < -0.1)
        neutral_count = len(sentiment_scores) - positive_count - negative_count
        
        return {
            "period": period,
            "total_entries": len(entries),
            "average_sentiment": round(avg_sentiment, 3),
            "trend": trend,
            "sentiment_distribution": {
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count
            },
            "summary": self._generate_summary_text(avg_sentiment, trend, period)
        }
    
    def _generate_summary_text(self, avg_sentiment: float, trend: str, period: str) -> str:
        """Generate human-readable summary text"""
        if avg_sentiment > 0.3:
            mood = "positive"
        elif avg_sentiment < -0.3:
            mood = "challenging"
        else:
            mood = "balanced"
        
        trend_text = {
            "improving": "showing improvement",
            "declining": "trending downward",
            "stable": "remaining steady",
            "insufficient_data": "needing more data to determine trends"
        }.get(trend, "stable")
        
        return f"Your overall mood this {period} has been {mood}, {trend_text}."

# Global instance
sentiment_service = SentimentAnalysisService()