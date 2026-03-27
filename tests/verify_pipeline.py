import asyncio
import os
from agents.graph import AdGenGraph
from agents.state import AdGenState

async def test_full_flow():
    graph = AdGenGraph()
    state = AdGenState()
    
    print("--- Starting 10-Question Interaction Simulation ---")
    mock_answers = [
        "Lumina AI - Next Gen Smart Lighting",
        "Smart LED bulbs that sync with your mood and music.",
        "Tech-savvy homeowners and interior design enthusiasts.",
        "Brand awareness and driving first-time sales.",
        "Futuristic, clean, and energizing.",
        "Modern living rooms with vibrant ambient lighting.",
        "A smartphone app controlling light colors.",
        "Close up of a sleek, minimalist LED bulb.",
        "Happy person relaxing in a warmly lit room.",
        "Comparison of boring white light vs dynamic Lumina colors."
    ]
    
    current_state_dict = state.model_dump()
    for i, answer in enumerate(mock_answers):
        print(f"Adding answer {i+1}: {answer}")
        current_state_dict["answers"].append(answer)
        result = await graph.run(current_state_dict)
        current_state_dict = result
        if result.get("interaction_complete"):
            print("Interaction finalized!")
            break
            
    print("\n--- Generation Status ---")
    print(f"Headlines Generated: {len(current_state_dict.get('headlines', []))}")
    print(f"Themes Generated: {len(current_state_dict.get('themes', []))}")
    print(f"Total Variations Expanded: {len(current_state_dict.get('variations', []))}")
    
    # We won't run the full 2,500 render in this test to save time, 
    # but we've verified the expansion logic.
    assert len(current_state_dict.get('headlines', [])) >= 50
    assert len(current_state_dict.get('themes', [])) >= 10
    assert len(current_state_dict.get('variations', [])) == 2500
    
    print("\nSUCCESS: Pipeline scaled to 2,500 variations successfully.")

if __name__ == "__main__":
    # Ensure templates can be found
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    asyncio.run(test_full_flow())
