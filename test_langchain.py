import time
print("Importing langchain-core...")
start = time.time()
from langchain_core.messages import HumanMessage
print(f"DONE in {time.time() - start:.2f}s")
