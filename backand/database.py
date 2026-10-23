
import os
from pathlib import Path

from dotenv import load_dotenv
from supabase import create_client, Client

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        "Configure SUPABASE_URL e SUPABASE_KEY no arquivo .env"
    )

supabase: Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)
print("URL carregada:", SUPABASE_URL)
print(
    "Tipo da chave:",
    "publishable" if SUPABASE_KEY.startswith("sb_publishable_")
    else "outro tipo"
)