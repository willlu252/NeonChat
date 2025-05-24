from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import date, datetime, timedelta
from ...models.database import DailyMetricsCreate, DailyMetricsResponse
from ...utils.feature_flags import is_metrics_enabled

# Import appropriate services based on configuration
if is_metrics_enabled():
    from ...services.auth_service import get_current_active_user
    from ...utils.supabase_client import supabase_client
else:
    # Use mock services
    from ..routes.auth import get_current_active_user
    from ...services.mock_data_service import mock_metrics_service
    supabase_client = None

router = APIRouter(prefix="/api/metrics", tags=["metrics"])

def calculate_wellbeing_score(metrics: Dict[str, Any]) -> float:
    """Calculate overall wellbeing score based on various metrics"""
    # Weight factors for different metrics
    weights = {
        "sleep_hours": 0.15,
        "water_intake": 0.05,
        "exercise_minutes": 0.10,
        "stress_level": 0.15,  # Inverted
        "anxiety_level": 0.10,  # Inverted
        "happiness_level": 0.15,
        "meditation_minutes": 0.05,
        "social_interaction_quality": 0.10,
        "work_satisfaction": 0.10,
        "productivity_score": 0.05
    }
    
    score = 0.0
    total_weight = 0.0
    
    # Normalize and calculate weighted scores
    if metrics.get("sleep_hours") is not None:
        # Optimal sleep is 7-9 hours
        sleep_score = min(metrics["sleep_hours"] / 8.0, 1.0) * 10
        score += sleep_score * weights["sleep_hours"]
        total_weight += weights["sleep_hours"]
    
    if metrics.get("water_intake") is not None:
        # Optimal water is 8 glasses
        water_score = min(metrics["water_intake"] / 8.0, 1.0) * 10
        score += water_score * weights["water_intake"]
        total_weight += weights["water_intake"]
    
    if metrics.get("exercise_minutes") is not None:
        # Optimal exercise is 30+ minutes
        exercise_score = min(metrics["exercise_minutes"] / 30.0, 1.0) * 10
        score += exercise_score * weights["exercise_minutes"]
        total_weight += weights["exercise_minutes"]
    
    if metrics.get("meditation_minutes") is not None:
        # Optimal meditation is 20+ minutes
        meditation_score = min(metrics["meditation_minutes"] / 20.0, 1.0) * 10
        score += meditation_score * weights["meditation_minutes"]
        total_weight += weights["meditation_minutes"]
    
    # Direct 1-10 scores
    for metric in ["happiness_level", "social_interaction_quality", 
                   "work_satisfaction", "productivity_score"]:
        if metrics.get(metric) is not None:
            score += metrics[metric] * weights[metric]
            total_weight += weights[metric]
    
    # Inverted scores (lower is better)
    for metric in ["stress_level", "anxiety_level"]:
        if metrics.get(metric) is not None:
            inverted_score = 11 - metrics[metric]  # Convert to positive scale
            score += inverted_score * weights[metric]
            total_weight += weights[metric]
    
    # Calculate final score
    if total_weight > 0:
        final_score = (score / total_weight)
        return round(final_score, 2)
    else:
        return 0.0

@router.post("/daily", response_model=DailyMetricsResponse)
async def create_or_update_daily_metrics(
    metrics: DailyMetricsCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create or update daily metrics for current user"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            # Use today's date if not provided
            metric_date = metrics.date or date.today()
            
            # Calculate wellbeing score
            metrics_dict = metrics.dict(exclude_none=True)
            wellbeing_score = calculate_wellbeing_score(metrics_dict)
            
            # Prepare metrics data
            metrics_data = {
                "user_id": current_user["id"],
                "date": metric_date.isoformat(),
                "wellbeing_score": wellbeing_score,
                **{k: v for k, v in metrics_dict.items() if k != "date"}
            }
            
            # Check if metrics already exist for this date
            existing = supabase.table("daily_metrics")\
                .select("id")\
                .eq("user_id", current_user["id"])\
                .eq("date", metric_date.isoformat())\
                .execute()
            
            if existing.data:
                # Update existing metrics
                response = supabase.table("daily_metrics")\
                    .update(metrics_data)\
                    .eq("id", existing.data[0]["id"])\
                    .execute()
            else:
                # Create new metrics
                response = supabase.table("daily_metrics")\
                    .insert(metrics_data)\
                    .execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to save daily metrics"
                )
        else:
            # Use mock service
            metrics_dict = metrics.dict(exclude_none=True)
            metrics_dict["date"] = (metrics.date or date.today()).isoformat()
            
            result = await mock_metrics_service.save_metrics(
                current_user.get("id", "test-user-id"),
                metrics_dict
            )
            return result
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/daily", response_model=List[DailyMetricsResponse])
async def get_daily_metrics(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(default=30, ge=1, le=365),
    offset: int = Query(default=0, ge=0)
):
    """Get daily metrics for current user"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            # Build query
            query = supabase.table("daily_metrics")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .order("date", desc=True)
            
            # Apply filters
            if start_date:
                query = query.gte("date", start_date.isoformat())
            if end_date:
                query = query.lte("date", end_date.isoformat())
            
            # Apply pagination
            query = query.range(offset, offset + limit - 1)
            
            response = query.execute()
            
            return response.data
        else:
            # Use mock service
            filters = {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "limit": limit,
                "offset": offset
            }
            
            metrics = await mock_metrics_service.get_metrics(
                current_user.get("id", "test-user-id"),
                filters
            )
            return metrics
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/daily/{metric_date}", response_model=DailyMetricsResponse)
async def get_daily_metrics_by_date(
    metric_date: date,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get daily metrics for a specific date"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            response = supabase.table("daily_metrics")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .eq("date", metric_date.isoformat())\
                .single()\
                .execute()
            
            if response.data:
                return response.data
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Metrics not found for this date"
                )
        else:
            # Use mock service
            metric = await mock_metrics_service.get_metrics_by_date(
                current_user.get("id", "test-user-id"),
                metric_date.isoformat()
            )
            if metric:
                return metric
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Metrics not found for this date"
                )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/daily/{metric_date}")
async def delete_daily_metrics(
    metric_date: date,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete daily metrics for a specific date"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            response = supabase.table("daily_metrics")\
                .delete()\
                .eq("user_id", current_user["id"])\
                .eq("date", metric_date.isoformat())\
                .execute()
            
            if response.data:
                return {"message": "Daily metrics deleted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Metrics not found for this date"
                )
        else:
            # Mock service doesn't have delete method, just return success
            return {"message": "Daily metrics deleted successfully"}
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/trends/weekly")
async def get_weekly_trends(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    weeks: int = Query(default=4, ge=1, le=52)
):
    """Get weekly trends for metrics"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
        else:
            # Use mock service for trends
            end_date = date.today()
            start_date = end_date - timedelta(weeks=weeks)
            
            filters = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": 1000,
                "offset": 0
            }
            
            response_data = await mock_metrics_service.get_metrics(
                current_user.get("id", "test-user-id"),
                filters
            )
        
        # For supabase
        if supabase_client:
            # Calculate date range
            end_date = date.today()
            start_date = end_date - timedelta(weeks=weeks)
            
            # Get all metrics in range
            response = supabase.table("daily_metrics")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .gte("date", start_date.isoformat())\
                .lte("date", end_date.isoformat())\
                .order("date")\
                .execute()
            
            if not response.data:
                return {"weeks": [], "averages": {}}
            
            metrics_data = response.data
        else:
            # response_data already set from mock service above
            if not response_data:
                return {"weeks": [], "averages": {}}
            metrics_data = response_data
        
        # Group by week
        weekly_data = {}
        for metric in metrics_data:
            metric_date = datetime.fromisoformat(metric["date"]).date()
            week_start = metric_date - timedelta(days=metric_date.weekday())
            week_key = week_start.isoformat()
            
            if week_key not in weekly_data:
                weekly_data[week_key] = []
            weekly_data[week_key].append(metric)
        
        # Calculate weekly averages
        weekly_trends = []
        for week_start, metrics in sorted(weekly_data.items()):
            week_avg = {
                "week_start": week_start,
                "metrics_count": len(metrics),
                "avg_wellbeing": 0,
                "avg_sleep": 0,
                "avg_stress": 0,
                "avg_happiness": 0,
                "avg_exercise": 0
            }
            
            # Calculate averages
            wellbeing_scores = [m["wellbeing_score"] for m in metrics if m.get("wellbeing_score")]
            sleep_hours = [m["sleep_hours"] for m in metrics if m.get("sleep_hours")]
            stress_levels = [m["stress_level"] for m in metrics if m.get("stress_level")]
            happiness_levels = [m["happiness_level"] for m in metrics if m.get("happiness_level")]
            exercise_minutes = [m["exercise_minutes"] for m in metrics if m.get("exercise_minutes")]
            
            if wellbeing_scores:
                week_avg["avg_wellbeing"] = round(sum(wellbeing_scores) / len(wellbeing_scores), 2)
            if sleep_hours:
                week_avg["avg_sleep"] = round(sum(sleep_hours) / len(sleep_hours), 1)
            if stress_levels:
                week_avg["avg_stress"] = round(sum(stress_levels) / len(stress_levels), 1)
            if happiness_levels:
                week_avg["avg_happiness"] = round(sum(happiness_levels) / len(happiness_levels), 1)
            if exercise_minutes:
                week_avg["avg_exercise"] = round(sum(exercise_minutes) / len(exercise_minutes), 0)
            
            weekly_trends.append(week_avg)
        
        # Calculate overall averages
        overall_averages = {
            "wellbeing": 0,
            "sleep": 0,
            "stress": 0,
            "happiness": 0,
            "exercise": 0
        }
        
        if weekly_trends:
            avg_wellbeing = [w["avg_wellbeing"] for w in weekly_trends if w["avg_wellbeing"] > 0]
            avg_sleep = [w["avg_sleep"] for w in weekly_trends if w["avg_sleep"] > 0]
            avg_stress = [w["avg_stress"] for w in weekly_trends if w["avg_stress"] > 0]
            avg_happiness = [w["avg_happiness"] for w in weekly_trends if w["avg_happiness"] > 0]
            avg_exercise = [w["avg_exercise"] for w in weekly_trends if w["avg_exercise"] > 0]
            
            if avg_wellbeing:
                overall_averages["wellbeing"] = round(sum(avg_wellbeing) / len(avg_wellbeing), 2)
            if avg_sleep:
                overall_averages["sleep"] = round(sum(avg_sleep) / len(avg_sleep), 1)
            if avg_stress:
                overall_averages["stress"] = round(sum(avg_stress) / len(avg_stress), 1)
            if avg_happiness:
                overall_averages["happiness"] = round(sum(avg_happiness) / len(avg_happiness), 1)
            if avg_exercise:
                overall_averages["exercise"] = round(sum(avg_exercise) / len(avg_exercise), 0)
        
        return {
            "weeks": weekly_trends,
            "overall_averages": overall_averages
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/insights")
async def get_metrics_insights(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    days: int = Query(default=30, ge=7, le=90)
):
    """Get insights and recommendations based on recent metrics"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
        else:
            # Use mock service for insights
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            filters = {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "limit": 1000,
                "offset": 0
            }
            
            response_data = await mock_metrics_service.get_metrics(
                current_user.get("id", "test-user-id"),
                filters
            )
        
        # For supabase
        if supabase_client:
            # Get recent metrics
            end_date = date.today()
            start_date = end_date - timedelta(days=days)
            
            response = supabase.table("daily_metrics")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .gte("date", start_date.isoformat())\
                .lte("date", end_date.isoformat())\
                .execute()
            
            if not response.data:
                return {
                    "insights": ["Start tracking your daily metrics to get personalized insights!"],
                    "recommendations": ["Begin with basic metrics like sleep hours and mood levels."]
                }
            
            metrics_data = response.data
        else:
            # response_data already set from mock service above
            if not response_data:
                return {
                    "insights": ["Start tracking your daily metrics to get personalized insights!"],
                    "recommendations": ["Begin with basic metrics like sleep hours and mood levels."]
                }
            metrics_data = response_data
        
        # Analyze metrics
        insights = []
        recommendations = []
        
        # Sleep analysis
        sleep_data = [m["sleep_hours"] for m in metrics_data if m.get("sleep_hours")]
        if sleep_data:
            avg_sleep = sum(sleep_data) / len(sleep_data)
            if avg_sleep < 6:
                insights.append(f"Your average sleep ({avg_sleep:.1f} hours) is below recommended levels.")
                recommendations.append("Try to get 7-9 hours of sleep per night for optimal health.")
            elif avg_sleep > 9:
                insights.append(f"You're sleeping more than average ({avg_sleep:.1f} hours).")
                recommendations.append("Consider if excessive sleep might indicate other health concerns.")
        
        # Stress analysis
        stress_data = [m["stress_level"] for m in metrics_data if m.get("stress_level")]
        if stress_data:
            avg_stress = sum(stress_data) / len(stress_data)
            if avg_stress > 7:
                insights.append(f"Your stress levels are high (average: {avg_stress:.1f}/10).")
                recommendations.append("Consider stress reduction techniques like meditation or exercise.")
        
        # Exercise analysis
        exercise_data = [m["exercise_minutes"] for m in metrics_data if m.get("exercise_minutes")]
        if exercise_data:
            avg_exercise = sum(exercise_data) / len(exercise_data)
            if avg_exercise < 20:
                insights.append(f"Your daily exercise ({avg_exercise:.0f} minutes) is below recommended levels.")
                recommendations.append("Aim for at least 30 minutes of moderate exercise daily.")
        
        # Wellbeing trends
        wellbeing_data = [(m["date"], m["wellbeing_score"]) 
                          for m in metrics_data if m.get("wellbeing_score")]
        if len(wellbeing_data) > 7:
            # Compare recent week to previous
            sorted_data = sorted(wellbeing_data, key=lambda x: x[0])
            recent_scores = [score for _, score in sorted_data[-7:]]
            previous_scores = [score for _, score in sorted_data[-14:-7]]
            
            if recent_scores and previous_scores:
                recent_avg = sum(recent_scores) / len(recent_scores)
                previous_avg = sum(previous_scores) / len(previous_scores)
                
                if recent_avg > previous_avg * 1.1:
                    insights.append("Your wellbeing has improved by over 10% this week!")
                elif recent_avg < previous_avg * 0.9:
                    insights.append("Your wellbeing has declined this week.")
                    recommendations.append("Review your recent changes and focus on self-care.")
        
        return {
            "insights": insights if insights else ["Keep tracking consistently for personalized insights!"],
            "recommendations": recommendations if recommendations else ["You're doing great! Keep up the good habits."],
            "summary": {
                "days_tracked": len(metrics_data),
                "avg_wellbeing": round(sum(m["wellbeing_score"] for m in metrics_data if m.get("wellbeing_score")) / len([m for m in metrics_data if m.get("wellbeing_score")]), 2) if any(m.get("wellbeing_score") for m in metrics_data) else None
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )