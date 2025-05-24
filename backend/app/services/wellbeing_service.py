from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta, date
import statistics

class WellbeingCalculatorService:
    """Service for calculating and analyzing wellbeing scores"""
    
    def __init__(self):
        # WHO-5 inspired wellbeing dimensions
        self.wellbeing_dimensions = {
            "physical": {
                "metrics": ["sleep_hours", "exercise_minutes", "water_intake", "steps"],
                "weight": 0.25
            },
            "mental": {
                "metrics": ["stress_level", "anxiety_level", "meditation_minutes"],
                "weight": 0.25
            },
            "emotional": {
                "metrics": ["happiness_level", "mood_score", "gratitude_count"],
                "weight": 0.25
            },
            "social": {
                "metrics": ["social_interaction_quality", "work_satisfaction", "productivity_score"],
                "weight": 0.25
            }
        }
        
        # Optimal values for normalization
        self.optimal_values = {
            "sleep_hours": 8.0,
            "exercise_minutes": 45.0,
            "water_intake": 8.0,
            "steps": 10000.0,
            "meditation_minutes": 20.0,
            "gratitude_count": 3.0
        }
        
        # Metrics that should be inverted (lower is better)
        self.inverted_metrics = ["stress_level", "anxiety_level"]
    
    async def calculate_wellbeing(self, metrics: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate overall wellbeing score and component scores.
        
        Args:
            metrics: Dictionary of daily metrics
            
        Returns:
            Dictionary with wellbeing_score and component scores
        """
        component_scores = {}
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Calculate scores for each dimension
        for dimension, config in self.wellbeing_dimensions.items():
            dimension_score = self._calculate_dimension_score(metrics, config["metrics"])
            if dimension_score is not None:
                component_scores[dimension] = dimension_score
                total_weighted_score += dimension_score * config["weight"]
                total_weight += config["weight"]
        
        # Calculate overall wellbeing score
        if total_weight > 0:
            wellbeing_score = total_weighted_score / total_weight
        else:
            wellbeing_score = 5.0  # Default neutral score
        
        # Add insights based on scores
        insights = self._generate_insights(component_scores, metrics)
        
        return {
            "wellbeing_score": round(wellbeing_score, 2),
            "components": component_scores,
            "insights": insights,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def _calculate_dimension_score(self, metrics: Dict[str, Any], dimension_metrics: List[str]) -> Optional[float]:
        """
        Calculate score for a specific wellbeing dimension.
        
        Returns:
            Score from 0-10 or None if no data
        """
        scores = []
        
        for metric in dimension_metrics:
            if metric in metrics and metrics[metric] is not None:
                value = metrics[metric]
                
                # Normalize the value
                if metric in self.optimal_values:
                    # For metrics with optimal values, score based on proximity to optimal
                    optimal = self.optimal_values[metric]
                    score = min(value / optimal, 1.0) * 10.0
                elif metric in self.inverted_metrics:
                    # For inverted metrics, lower values are better
                    score = max(0, 11 - value)  # Convert 1-10 to 10-1
                else:
                    # For direct 1-10 scale metrics
                    score = float(value)
                
                scores.append(score)
        
        if scores:
            return round(sum(scores) / len(scores), 2)
        else:
            return None
    
    def _generate_insights(self, component_scores: Dict[str, float], metrics: Dict[str, Any]) -> List[str]:
        """Generate insights based on wellbeing scores and metrics"""
        insights = []
        
        # Check for low component scores
        for dimension, score in component_scores.items():
            if score < 4.0:
                insights.append(f"Your {dimension} wellbeing needs attention (score: {score}/10)")
            elif score > 8.0:
                insights.append(f"Excellent {dimension} wellbeing! (score: {score}/10)")
        
        # Specific metric insights
        if metrics.get("sleep_hours", 0) < 6:
            insights.append("Consider improving your sleep duration for better recovery")
        elif metrics.get("sleep_hours", 0) > 9:
            insights.append("You're getting plenty of sleep - ensure it's quality rest")
        
        if metrics.get("exercise_minutes", 0) < 20:
            insights.append("Try to increase physical activity for better overall health")
        elif metrics.get("exercise_minutes", 0) > 60:
            insights.append("Great job staying active! Remember to allow for recovery")
        
        if metrics.get("stress_level", 0) > 7:
            insights.append("High stress detected - consider stress management techniques")
        
        if metrics.get("water_intake", 0) < 6:
            insights.append("Increase water intake for better hydration")
        
        # Limit insights to top 3
        return insights[:3]
    
    async def analyze_trends(
        self,
        historical_data: List[Dict[str, Any]],
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Analyze wellbeing trends over time.
        
        Args:
            historical_data: List of daily metrics with wellbeing scores
            period_days: Number of days to analyze
            
        Returns:
            Trend analysis results
        """
        if not historical_data:
            return {
                "trend": "no_data",
                "change_percentage": 0.0,
                "insights": ["Start tracking daily to see trends"]
            }
        
        # Sort by date
        sorted_data = sorted(
            historical_data,
            key=lambda x: datetime.fromisoformat(x.get("date", x.get("created_at", "")))
        )
        
        # Get recent data
        if len(sorted_data) > period_days:
            recent_data = sorted_data[-period_days:]
        else:
            recent_data = sorted_data
        
        # Calculate trend
        wellbeing_scores = [
            d.get("wellbeing_score", 5.0)
            for d in recent_data
            if d.get("wellbeing_score") is not None
        ]
        
        if len(wellbeing_scores) < 2:
            return {
                "trend": "insufficient_data",
                "change_percentage": 0.0,
                "insights": ["Need more data points to determine trends"]
            }
        
        # Simple linear regression for trend
        x_values = list(range(len(wellbeing_scores)))
        mean_x = sum(x_values) / len(x_values)
        mean_y = sum(wellbeing_scores) / len(wellbeing_scores)
        
        numerator = sum((x - mean_x) * (y - mean_y) for x, y in zip(x_values, wellbeing_scores))
        denominator = sum((x - mean_x) ** 2 for x in x_values)
        
        if denominator > 0:
            slope = numerator / denominator
        else:
            slope = 0
        
        # Determine trend
        if slope > 0.05:
            trend = "improving"
        elif slope < -0.05:
            trend = "declining"
        else:
            trend = "stable"
        
        # Calculate percentage change
        if wellbeing_scores[0] != 0:
            change_percentage = ((wellbeing_scores[-1] - wellbeing_scores[0]) / wellbeing_scores[0]) * 100
        else:
            change_percentage = 0
        
        # Generate trend insights
        trend_insights = []
        if trend == "improving":
            trend_insights.append("Your wellbeing has been improving - keep up the good work!")
        elif trend == "declining":
            trend_insights.append("Your wellbeing trend shows decline - consider what changes might help")
        else:
            trend_insights.append("Your wellbeing has been stable")
        
        # Analyze dimension trends
        dimension_trends = self._analyze_dimension_trends(recent_data)
        trend_insights.extend(dimension_trends)
        
        return {
            "trend": trend,
            "change_percentage": round(change_percentage, 1),
            "average_score": round(mean_y, 2),
            "insights": trend_insights[:3],
            "data_points": len(wellbeing_scores)
        }
    
    def _analyze_dimension_trends(self, data: List[Dict[str, Any]]) -> List[str]:
        """Analyze trends for individual wellbeing dimensions"""
        insights = []
        
        # Group scores by dimension
        dimension_scores = {dim: [] for dim in self.wellbeing_dimensions.keys()}
        
        for entry in data:
            components = entry.get("components", {})
            for dim, score in components.items():
                if dim in dimension_scores and score is not None:
                    dimension_scores[dim].append(score)
        
        # Find dimensions with significant changes
        for dimension, scores in dimension_scores.items():
            if len(scores) >= 3:
                early_avg = sum(scores[:len(scores)//2]) / len(scores[:len(scores)//2])
                late_avg = sum(scores[len(scores)//2:]) / len(scores[len(scores)//2:])
                
                if late_avg > early_avg * 1.2:
                    insights.append(f"Great improvement in {dimension} wellbeing!")
                elif late_avg < early_avg * 0.8:
                    insights.append(f"Your {dimension} wellbeing needs attention")
        
        return insights
    
    async def get_recommendations(
        self,
        current_metrics: Dict[str, Any],
        wellbeing_score: float
    ) -> List[Dict[str, str]]:
        """
        Generate personalized recommendations based on current metrics.
        
        Returns:
            List of recommendations with priority and action items
        """
        recommendations = []
        
        # Sleep recommendations
        sleep_hours = current_metrics.get("sleep_hours", 0)
        if sleep_hours < 6:
            recommendations.append({
                "priority": "high",
                "category": "sleep",
                "recommendation": "Aim for 7-9 hours of sleep",
                "action": "Set a consistent bedtime and create a relaxing bedtime routine"
            })
        
        # Exercise recommendations
        exercise_mins = current_metrics.get("exercise_minutes", 0)
        if exercise_mins < 20:
            recommendations.append({
                "priority": "high",
                "category": "physical",
                "recommendation": "Increase daily physical activity",
                "action": "Start with a 20-minute walk or light exercise"
            })
        
        # Stress management
        stress_level = current_metrics.get("stress_level", 0)
        if stress_level > 7:
            recommendations.append({
                "priority": "high",
                "category": "mental",
                "recommendation": "Implement stress reduction techniques",
                "action": "Try 10 minutes of meditation or deep breathing exercises"
            })
        
        # Hydration
        water_intake = current_metrics.get("water_intake", 0)
        if water_intake < 6:
            recommendations.append({
                "priority": "medium",
                "category": "physical",
                "recommendation": "Increase water intake",
                "action": "Keep a water bottle nearby and set hourly reminders"
            })
        
        # Social connection
        social_quality = current_metrics.get("social_interaction_quality", 0)
        if social_quality < 5:
            recommendations.append({
                "priority": "medium",
                "category": "social",
                "recommendation": "Improve social connections",
                "action": "Reach out to a friend or join a social activity"
            })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        # Return top 3 recommendations
        return recommendations[:3]
    
    def calculate_weekly_summary(self, daily_scores: List[float]) -> Dict[str, Any]:
        """
        Calculate weekly wellbeing summary.
        
        Args:
            daily_scores: List of daily wellbeing scores
            
        Returns:
            Weekly summary statistics
        """
        if not daily_scores:
            return {
                "average": 0.0,
                "min": 0.0,
                "max": 0.0,
                "trend": "no_data",
                "consistency": 0.0
            }
        
        avg_score = sum(daily_scores) / len(daily_scores)
        min_score = min(daily_scores)
        max_score = max(daily_scores)
        
        # Calculate consistency (lower std dev = more consistent)
        if len(daily_scores) > 1:
            std_dev = statistics.stdev(daily_scores)
            consistency = max(0, 100 - (std_dev * 20))  # Convert to percentage
        else:
            consistency = 100.0
        
        # Determine weekly trend
        if len(daily_scores) >= 3:
            first_half_avg = sum(daily_scores[:len(daily_scores)//2]) / len(daily_scores[:len(daily_scores)//2])
            second_half_avg = sum(daily_scores[len(daily_scores)//2:]) / len(daily_scores[len(daily_scores)//2:])
            
            if second_half_avg > first_half_avg * 1.05:
                trend = "improving"
            elif second_half_avg < first_half_avg * 0.95:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"
        
        return {
            "average": round(avg_score, 2),
            "min": round(min_score, 2),
            "max": round(max_score, 2),
            "trend": trend,
            "consistency": round(consistency, 1),
            "days_tracked": len(daily_scores)
        }

# Global instance
wellbeing_service = WellbeingCalculatorService()