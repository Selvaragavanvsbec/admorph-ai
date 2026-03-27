import time
import sys

def time_import(name):
    print(f"B_Importing {name}...", flush=True)
    start = time.time()
    try:
        __import__(name)
    except Exception as e:
        print(f"E_FAIL! {name}: {e}", flush=True)
        return
    print(f"A_DONE ({time.time() - start:.2f}s)", flush=True)

time_import("config")
time_import("agents.state")
time_import("agents.interactive_agent")
time_import("agents.theme_agent")
time_import("agents.copy_agent")
time_import("agents.image_agent")
time_import("engines.variant_engine")
time_import("services.renderer")
time_import("agents.graph")
print("All imports finished.", flush=True)
