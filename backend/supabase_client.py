import os 

from dotenv import load_dotenv
from supabase import create_client
from supabase.lib.client_options import SyncClientOptions

load_dotenv()


def get_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY")

    if not url or not key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be configured."
        )

    return create_client(
        url,
        key, 
        options = SyncClientOptions(
            persist_session = False,
            auto_refresh_token = False
        )
    )