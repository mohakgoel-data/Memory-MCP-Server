from google import genai
from clients import client, supabase
from models import ExtractionResult
from dotenv import load_dotenv
from prompt import prompt

load_dotenv()

def get_embedding(text: str) -> list:
    result = client.models.embed_content(
        model="gemini-embedding-001",
        contents=text
    )
    return result.embeddings[0].values

def remember(user_id: str, conversation_text: str) -> int:

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt+"Conversatiuon:\n"+conversation_text,
        config=genai.types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=ExtractionResult
        )
    )


    result = ExtractionResult.model_validate_json(response.text)
    stored_count = 0
    for memory in result.memories:
        embedding = get_embedding(memory.content)
        supabase.table("memories").insert({
            "user_id": user_id,
            "content": memory.content,
            "category": memory.category.value,
            "tag": memory.tag,
            "importance": memory.importance,
            "strength": 1.0,
            "embedding": embedding
        }).execute()
        stored_count += 1

    return stored_count

def recall(user_id: str, query: str) -> list:

    query_embedding = get_embedding(query)

    results = supabase.rpc("match_memories", {
        "query_embedding": query_embedding,
        "match_threshold": 0.595,
        "match_count": 5,
        "p_user_id": user_id
    }).execute()

    for memory in results.data:
        new_strength = min(1.0, memory["strength"] + 0.1)
        supabase.table("memories").update(
            {"strength": new_strength, "last_recalled": "NOW()"}
        ).eq("id", memory["id"]).execute()

    return results.data


def forget(user_id: str, memory_id: str) -> bool:

    result = supabase.table("memories").delete()\
        .eq("id", memory_id)\
        .eq("user_id", user_id)\
        .execute()

    return len(result.data) > 0


def get_all_memories(user_id: str) -> list:

    result = supabase.table("memories")\
        .select("*")\
        .eq("user_id", user_id)\
        .order("created_at", desc=True)\
        .execute()

    return result.data