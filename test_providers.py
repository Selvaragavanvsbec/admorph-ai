import time
def test_mi(n):
    print(f"B_{n}")
    s = time.time()
    try:
        __import__(n)
        print(f"A_{n} DONE ({time.time()-s:.2f}s)")
    except Exception as e:
        print(f"F_{n}: {e}")

test_mi("langchain_openai")
test_mi("langchain_google_genai")
test_mi("langchain_anthropic")
test_mi("langchain_ollama")
print("ALL DONE")
