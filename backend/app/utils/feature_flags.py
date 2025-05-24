"""Feature flags for optional functionality"""
from .supabase_client import supabase_client

def is_supabase_configured() -> bool:
    """Check if Supabase is configured and available"""
    return supabase_client is not None and supabase_client.is_configured()

def is_journaling_enabled() -> bool:
    """Check if journaling features are enabled"""
    return is_supabase_configured()

def is_metrics_enabled() -> bool:
    """Check if metrics tracking is enabled"""
    return is_supabase_configured()

def is_auth_enabled() -> bool:
    """Check if authentication is enabled"""
    return is_supabase_configured()

# Feature status for logging
def print_feature_status():
    """Print the status of all features"""
    print("\n=== Feature Status ===")
    print(f"Authentication: {'✓ Enabled' if is_auth_enabled() else '✗ Disabled'}")
    print(f"Journaling: {'✓ Enabled' if is_journaling_enabled() else '✗ Disabled'}")
    print(f"Metrics Tracking: {'✓ Enabled' if is_metrics_enabled() else '✗ Disabled'}")
    print("=====================\n")