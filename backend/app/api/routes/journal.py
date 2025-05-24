from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional, Dict, Any
from datetime import date, datetime
from ...models.database import JournalEntryCreate, JournalEntryResponse
from ...utils.feature_flags import is_journaling_enabled
import json

# Import appropriate services based on configuration
if is_journaling_enabled():
    from ...services.auth_service import get_current_active_user
    from ...utils.supabase_client import supabase_client
else:
    # Use mock services
    from ..routes.auth import get_current_active_user
    from ...services.mock_data_service import mock_journal_service
    supabase_client = None

router = APIRouter(prefix="/api/journal", tags=["journal"])

@router.post("/entries", response_model=JournalEntryResponse)
async def create_journal_entry(
    entry: JournalEntryCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Create a new journal entry"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            # Calculate word count
            word_count = len(entry.content.split())
            
            # Prepare entry data
            entry_data = {
                "user_id": current_user["id"],
                "title": entry.title,
                "content": entry.content,
                "mood_score": entry.mood_score,
                "energy_level": entry.energy_level,
                "word_count": word_count,
                "entry_date": date.today().isoformat()
            }
            
            # Insert entry
            response = supabase.table("journal_entries").insert(entry_data).execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to create journal entry"
                )
        else:
            # Use mock service
            result = await mock_journal_service.create_entry(
                current_user.get("id", "test-user-id"),
                entry.dict()
            )
            return result
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/entries", response_model=List[JournalEntryResponse])
async def get_journal_entries(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    mood_min: Optional[int] = Query(None, ge=1, le=10),
    mood_max: Optional[int] = Query(None, ge=1, le=10)
):
    """Get journal entries for current user with filtering options"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            # Build query
            query = supabase.table("journal_entries")\
                .select("*")\
                .eq("user_id", current_user["id"])\
                .order("entry_date", desc=True)\
                .order("created_at", desc=True)
            
            # Apply filters
            if start_date:
                query = query.gte("entry_date", start_date.isoformat())
            if end_date:
                query = query.lte("entry_date", end_date.isoformat())
            if mood_min:
                query = query.gte("mood_score", mood_min)
            if mood_max:
                query = query.lte("mood_score", mood_max)
            
            # Apply pagination
            query = query.range(offset, offset + limit - 1)
            
            response = query.execute()
            
            # Parse tags from JSON strings
            for entry in response.data:
                if entry.get("tags") and isinstance(entry["tags"], str):
                    try:
                        entry["tags"] = json.loads(entry["tags"])
                    except:
                        entry["tags"] = []
            
            return response.data
        else:
            # Use mock service
            filters = {
                "limit": limit,
                "offset": offset,
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None
            }
            
            entries = await mock_journal_service.get_entries(
                current_user.get("id", "test-user-id"),
                filters
            )
            
            # Filter by mood if specified
            if mood_min or mood_max:
                entries = [
                    e for e in entries
                    if (not mood_min or e.get("mood_score", 0) >= mood_min) and
                       (not mood_max or e.get("mood_score", 10) <= mood_max)
                ]
            
            return entries
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/entries/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Get a specific journal entry"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            response = supabase.table("journal_entries")\
                .select("*")\
                .eq("id", entry_id)\
                .eq("user_id", current_user["id"])\
                .single()\
                .execute()
            
            if response.data:
                # Parse tags from JSON string
                if response.data.get("tags") and isinstance(response.data["tags"], str):
                    try:
                        response.data["tags"] = json.loads(response.data["tags"])
                    except:
                        response.data["tags"] = []
                return response.data
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Journal entry not found"
                )
        else:
            # Use mock service
            entry = await mock_journal_service.get_entry(
                current_user.get("id", "test-user-id"),
                entry_id
            )
            if entry:
                return entry
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Journal entry not found"
                )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.put("/entries/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry: JournalEntryCreate,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Update a journal entry"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            # Verify ownership
            existing = supabase.table("journal_entries")\
                .select("id")\
                .eq("id", entry_id)\
                .eq("user_id", current_user["id"])\
                .single()\
                .execute()
            
            if not existing.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Journal entry not found"
                )
            
            # Calculate word count
            word_count = len(entry.content.split())
            
            # Update entry
            update_data = {
                "title": entry.title,
                "content": entry.content,
                "mood_score": entry.mood_score,
                "energy_level": entry.energy_level,
                "word_count": word_count,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            response = supabase.table("journal_entries")\
                .update(update_data)\
                .eq("id", entry_id)\
                .execute()
            
            if response.data:
                return response.data[0]
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update journal entry"
                )
        else:
            # Use mock service
            updated_entry = await mock_journal_service.update_entry(
                current_user.get("id", "test-user-id"),
                entry_id,
                entry.dict()
            )
            if updated_entry:
                return updated_entry
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Journal entry not found"
                )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.delete("/entries/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    current_user: Dict[str, Any] = Depends(get_current_active_user)
):
    """Delete a journal entry"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            # Delete entry (RLS will ensure ownership)
            response = supabase.table("journal_entries")\
                .delete()\
                .eq("id", entry_id)\
                .eq("user_id", current_user["id"])\
                .execute()
            
            if response.data:
                return {"message": "Journal entry deleted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Journal entry not found"
                )
        else:
            # Use mock service
            deleted = await mock_journal_service.delete_entry(
                current_user.get("id", "test-user-id"),
                entry_id
            )
            if deleted:
                return {"message": "Journal entry deleted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Journal entry not found"
                )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/entries/search/tags")
async def search_by_tags(
    tags: List[str] = Query(...),
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0)
):
    """Search journal entries by tags"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            # Build query for tag search
            query = supabase.table("journal_entries")\
                .select("*")\
                .eq("user_id", current_user["id"])
            
            # Add tag filters (tags are stored as JSONB array)
            for tag in tags:
                query = query.contains("tags", [tag])
            
            # Apply pagination and ordering
            query = query.order("entry_date", desc=True)\
                .range(offset, offset + limit - 1)
            
            response = query.execute()
            
            # Parse tags from JSON strings
            for entry in response.data:
                if entry.get("tags") and isinstance(entry["tags"], str):
                    try:
                        entry["tags"] = json.loads(entry["tags"])
                    except:
                        entry["tags"] = []
            
            return response.data
        else:
            # Use mock service - filter by tags manually
            all_entries = await mock_journal_service.get_entries(
                current_user.get("id", "test-user-id"),
                {"limit": 100, "offset": 0}
            )
            
            # Filter by tags
            filtered = []
            for entry in all_entries:
                entry_tags = entry.get("tags", [])
                if all(tag in entry_tags for tag in tags):
                    filtered.append(entry)
            
            # Apply pagination
            return filtered[offset:offset + limit]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/entries/stats/summary")
async def get_journal_stats(
    current_user: Dict[str, Any] = Depends(get_current_active_user),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get journal statistics for current user"""
    try:
        if supabase_client:
            supabase = supabase_client.get_client()
            
            # Build base query
            query = supabase.table("journal_entries")\
                .select("mood_score, energy_level, word_count, entry_date")\
                .eq("user_id", current_user["id"])
            
            # Apply date filters
            if start_date:
                query = query.gte("entry_date", start_date.isoformat())
            if end_date:
                query = query.lte("entry_date", end_date.isoformat())
            
            response = query.execute()
            data = response.data
        else:
            # Use mock service
            filters = {
                "start_date": start_date.isoformat() if start_date else None,
                "end_date": end_date.isoformat() if end_date else None,
                "limit": 1000,  # Get all for stats
                "offset": 0
            }
            data = await mock_journal_service.get_entries(
                current_user.get("id", "test-user-id"),
                filters
            )
        
        if not data:
            return {
                "total_entries": 0,
                "total_words": 0,
                "avg_mood": None,
                "avg_energy": None,
                "entries_by_date": {}
            }
        
        # Calculate statistics
        total_entries = len(data)
        total_words = sum(entry.get("word_count", 0) for entry in data)
        
        mood_scores = [entry["mood_score"] for entry in data if entry.get("mood_score")]
        avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else None
        
        energy_levels = [entry["energy_level"] for entry in data if entry.get("energy_level")]
        avg_energy = sum(energy_levels) / len(energy_levels) if energy_levels else None
        
        # Count entries by date
        entries_by_date = {}
        for entry in data:
            date_str = entry.get("entry_date", "")
            entries_by_date[date_str] = entries_by_date.get(date_str, 0) + 1
        
        return {
            "total_entries": total_entries,
            "total_words": total_words,
            "avg_mood": round(avg_mood, 2) if avg_mood else None,
            "avg_energy": round(avg_energy, 2) if avg_energy else None,
            "entries_by_date": entries_by_date
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )