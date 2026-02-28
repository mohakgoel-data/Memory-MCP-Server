from google import genai
from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))