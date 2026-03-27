import asyncio
from agents.llm_factory import get_llm
from langchain_core.messages import HumanMessage

async def test():
    variants = ["gemini-1.5-flash", "models/gemini-1.5-flash", "gemini-1.5-pro", "gemini-1.5-flash-latest"]
    for v in variants:
        try:
            llm = get_llm()
            llm.model = v # Force the variant
            msg = HumanMessage(content="Say Hello")
            print(f"--- Testing Variant: {v} ---")
            resp = await llm.ainvoke([msg])
            print(f"Response: {resp.content}")
            return # Success!
        except Exception as e:
            print(f"LLM Error for {v}: {e}")
            if "NOT_FOUND" not in str(e) and "404" not in str(e):
                break # If it's not a model naming error, stop

if __name__ == "__main__":
    asyncio.run(test())
