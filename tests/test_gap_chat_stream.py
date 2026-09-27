import asyncio
import json
from api.routers.chat import handle_chat_stream, ChatPayload, Message

async def main():
    payload = ChatPayload(profile="alaa_roucadi", messages=[Message(role="user", content="/gap OnePoint_Agentic_Delivery_Manager_JD.md")])
    response = await handle_chat_stream(payload)
    print("Stream initiated for Alaa Eddine Roucadi! Chunks:")
    count = 0
    async for chunk in response.body_iterator:
        text = chunk if isinstance(chunk, str) else chunk.decode("utf-8", errors="replace")
        if text.startswith('9:{"toolCallId"'):
            parsed = json.loads(text[2:])
            print("\n=== GENERATIVE UI ARGS FOR GapAnalysisCard ===")
            print(json.dumps(parsed, indent=2))
        elif text.startswith('0:"'):
            print("\n=== TEXT DELTA ===")
            print(json.loads(text[2:]))
        count += 1
    print(f"Total chunks yielded: {count}")

if __name__ == "__main__":
    asyncio.run(main())
