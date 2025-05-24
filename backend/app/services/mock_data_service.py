"""Mock data service for testing without database"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
import uuid
import random

# Mock data storage
MOCK_JOURNAL_ENTRIES = {}
MOCK_DAILY_METRICS = {}

class MockJournalService:
    """Mock journal service for UI testing"""
    
    def __init__(self):
        # Create some sample entries
        self._create_sample_data()
    
    def _create_sample_data(self):
        """Create sample journal entries for testing"""
        test_user_id = "test-user-id"
        
        # Create 5 sample entries
        for i in range(5):
            entry_id = str(uuid.uuid4())
            entry_date = date.today() - timedelta(days=i)
            
            entry = {
                "id": entry_id,
                "user_id": test_user_id,
                "title": f"Day {i+1} Reflections" if i % 2 == 0 else None,
                "content": self._get_sample_content(i),
                "mood_score": random.randint(4, 9),
                "energy_level": random.randint(3, 8),
                "sentiment_score": random.uniform(-0.2, 0.8),
                "tags": self._get_sample_tags(i),
                "ai_observations": "This entry shows positive emotional growth and self-awareness.",
                "entry_date": entry_date.isoformat(),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
                "word_count": random.randint(50, 300)
            }
            
            MOCK_JOURNAL_ENTRIES[entry_id] = entry
    
    def _get_sample_content(self, index: int) -> str:
        contents = [
            "Today was a productive day. I managed to complete most of my tasks and felt quite accomplished. The morning meditation really helped set a positive tone.",
            "Feeling a bit overwhelmed with work lately. Need to find better ways to manage stress and maintain work-life balance. Maybe I should start exercising more regularly.",
            "Had a great conversation with a friend today. It reminded me how important social connections are for mental wellbeing. Grateful for the people in my life.",
            "Tried a new recipe today and it turned out amazing! Small victories like these make me happy. Also started reading a new book on mindfulness.",
            "Reflecting on my goals for the month. I've made good progress on some, but others need more attention. Time to refocus and prioritize."
        ]
        return contents[index % len(contents)]
    
    def _get_sample_tags(self, index: int) -> List[str]:
        all_tags = ["productivity", "stress", "gratitude", "relationships", "goals", "mindfulness", "exercise", "work", "self-care"]
        return random.sample(all_tags, random.randint(2, 4))
    
    async def create_entry(self, user_id: str, entry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new journal entry"""
        entry_id = str(uuid.uuid4())
        
        entry = {
            "id": entry_id,
            "user_id": user_id,
            "title": entry_data.get("title"),
            "content": entry_data.get("content", ""),
            "mood_score": entry_data.get("mood_score"),
            "energy_level": entry_data.get("energy_level"),
            "sentiment_score": random.uniform(-0.5, 0.8),
            "tags": ["reflection", "daily"],
            "ai_observations": None,
            "entry_date": date.today().isoformat(),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "word_count": len(entry_data.get("content", "").split())
        }
        
        MOCK_JOURNAL_ENTRIES[entry_id] = entry
        return entry
    
    async def get_entries(self, user_id: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get journal entries with filters"""
        entries = [e for e in MOCK_JOURNAL_ENTRIES.values() if e.get("user_id") == user_id or user_id == "test-user-id"]
        
        # Apply filters
        if filters.get("start_date"):
            entries = [e for e in entries if e["entry_date"] >= filters["start_date"]]
        if filters.get("end_date"):
            entries = [e for e in entries if e["entry_date"] <= filters["end_date"]]
        
        # Sort by date
        entries.sort(key=lambda x: x["entry_date"], reverse=True)
        
        # Apply pagination
        offset = filters.get("offset", 0)
        limit = filters.get("limit", 10)
        
        return entries[offset:offset + limit]
    
    async def get_entry(self, user_id: str, entry_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific journal entry"""
        entry = MOCK_JOURNAL_ENTRIES.get(entry_id)
        if entry and (entry.get("user_id") == user_id or user_id == "test-user-id"):
            return entry
        return None
    
    async def update_entry(self, user_id: str, entry_id: str, entry_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a journal entry"""
        entry = MOCK_JOURNAL_ENTRIES.get(entry_id)
        if entry and (entry.get("user_id") == user_id or user_id == "test-user-id"):
            entry.update({
                "title": entry_data.get("title", entry["title"]),
                "content": entry_data.get("content", entry["content"]),
                "mood_score": entry_data.get("mood_score", entry["mood_score"]),
                "energy_level": entry_data.get("energy_level", entry["energy_level"]),
                "updated_at": datetime.utcnow().isoformat(),
                "word_count": len(entry_data.get("content", entry["content"]).split())
            })
            return entry
        return None
    
    async def delete_entry(self, user_id: str, entry_id: str) -> bool:
        """Delete a journal entry"""
        entry = MOCK_JOURNAL_ENTRIES.get(entry_id)
        if entry and (entry.get("user_id") == user_id or user_id == "test-user-id"):
            del MOCK_JOURNAL_ENTRIES[entry_id]
            return True
        return False

class MockMetricsService:
    """Mock metrics service for UI testing"""
    
    def __init__(self):
        # Create some sample metrics
        self._create_sample_data()
    
    def _create_sample_data(self):
        """Create sample daily metrics for testing"""
        test_user_id = "test-user-id"
        
        # Create metrics for last 30 days
        for i in range(30):
            metric_date = date.today() - timedelta(days=i)
            metric_id = f"{test_user_id}_{metric_date.isoformat()}"
            
            metric = {
                "id": str(uuid.uuid4()),
                "user_id": test_user_id,
                "date": metric_date.isoformat(),
                "sleep_hours": random.uniform(5, 9),
                "water_intake": random.randint(4, 10),
                "exercise_minutes": random.randint(0, 60),
                "steps": random.randint(2000, 15000),
                "stress_level": random.randint(2, 8),
                "anxiety_level": random.randint(1, 7),
                "happiness_level": random.randint(4, 9),
                "meditation_minutes": random.randint(0, 30),
                "social_interaction_quality": random.randint(3, 9),
                "prayer_minutes": random.randint(0, 20),
                "gratitude_count": random.randint(0, 5),
                "work_satisfaction": random.randint(4, 8),
                "productivity_score": random.randint(3, 9),
                "wellbeing_score": random.uniform(4.5, 8.5),
                "created_at": datetime.utcnow().isoformat()
            }
            
            MOCK_DAILY_METRICS[metric_id] = metric
    
    async def save_metrics(self, user_id: str, metrics_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save or update daily metrics"""
        metric_date = metrics_data.get("date", date.today().isoformat())
        metric_id = f"{user_id}_{metric_date}"
        
        # Calculate wellbeing score
        wellbeing_score = self._calculate_wellbeing(metrics_data)
        
        metric = MOCK_DAILY_METRICS.get(metric_id, {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "date": metric_date,
            "created_at": datetime.utcnow().isoformat()
        })
        
        metric.update({
            **metrics_data,
            "wellbeing_score": wellbeing_score
        })
        
        MOCK_DAILY_METRICS[metric_id] = metric
        return metric
    
    def _calculate_wellbeing(self, metrics: Dict[str, Any]) -> float:
        """Simple wellbeing calculation"""
        score = 5.0
        
        if metrics.get("sleep_hours", 0) >= 7:
            score += 1
        if metrics.get("exercise_minutes", 0) >= 30:
            score += 1
        if metrics.get("stress_level", 10) <= 5:
            score += 1
        if metrics.get("happiness_level", 0) >= 7:
            score += 1
        if metrics.get("water_intake", 0) >= 8:
            score += 0.5
        
        return min(10.0, round(score, 1))
    
    async def get_metrics(self, user_id: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get daily metrics with filters"""
        metrics = []
        
        for key, metric in MOCK_DAILY_METRICS.items():
            if metric.get("user_id") == user_id or user_id == "test-user-id":
                metrics.append(metric)
        
        # Apply filters
        if filters.get("start_date"):
            metrics = [m for m in metrics if m["date"] >= filters["start_date"]]
        if filters.get("end_date"):
            metrics = [m for m in metrics if m["date"] <= filters["end_date"]]
        
        # Sort by date
        metrics.sort(key=lambda x: x["date"], reverse=True)
        
        # Apply pagination
        offset = filters.get("offset", 0)
        limit = filters.get("limit", 30)
        
        return metrics[offset:offset + limit]
    
    async def get_metrics_by_date(self, user_id: str, metric_date: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific date"""
        metric_id = f"{user_id}_{metric_date}"
        metric = MOCK_DAILY_METRICS.get(metric_id)
        
        # Also check test user metrics
        if not metric and user_id != "test-user-id":
            test_metric_id = f"test-user-id_{metric_date}"
            metric = MOCK_DAILY_METRICS.get(test_metric_id)
        
        return metric

# Global instances
mock_journal_service = MockJournalService()
mock_metrics_service = MockMetricsService()