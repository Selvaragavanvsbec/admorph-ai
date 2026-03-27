from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from .state import AdGenState
from .interactive_agent import BriefCollector
from .theme_agent import ThemeAgent
from .copy_agent import CopyGenerator
from .image_agent import ImageAgent
from engines.variant_engine import VariantGenerator
from services.renderer import Renderer

class AdGenGraph:
    def __init__(self):
        self.workflow = StateGraph(AdGenState)
        
        # Initialize nodes
        self.brief_collector = BriefCollector()
        self.theme_agent = ThemeAgent()
        self.copy_generator = CopyGenerator()
        self.image_agent = ImageAgent()
        self.variant_generator = VariantGenerator()
        self.renderer = Renderer()
        
        # Build the graph
        self._build_graph()

    def _build_graph(self):
        # Nodes
        self.workflow.add_node("collect_brief", self.brief_collector.run)
        self.workflow.add_node("process_images", self.image_agent.run)
        self.workflow.add_node("generate_themes", self.theme_agent.run)
        self.workflow.add_node("generate_copy", self.copy_generator.run)
        self.workflow.add_node("expand_variants", self.variant_generator.run)
        self.workflow.add_node("render_ads", self._render_node)
        
        # Logic Flow
        self.workflow.set_entry_point("collect_brief")
        
        # Conditional edge for the question loop
        self.workflow.add_conditional_edges(
            "collect_brief",
            self._should_continue_interaction,
            {
                "continue": END, # LangGraph handles external interaction via END
                "proceed": "process_images"
            }
        )
        
        self.workflow.add_edge("process_images", "generate_themes")
        self.workflow.add_edge("generate_themes", "generate_copy")
        self.workflow.add_edge("generate_copy", "expand_variants")
        self.workflow.add_edge("expand_variants", "render_ads")
        self.workflow.add_edge("render_ads", END)
        
        self.app = self.workflow.compile()

    def _should_continue_interaction(self, state: AdGenState):
        if state.interaction_complete:
            return "proceed"
        return "continue"

    async def _render_node(self, state: AdGenState) -> dict:
        """Batch rendering node."""
        # For testing, limit to 10 to avoid huge timeouts and crashing the computer
        # For production, we render all 2,500
        render_results = await self.renderer.render_batch(state.variations[:10])
        return {"rendering_complete": True}

    async def run(self, inputs: dict):
        return await self.app.ainvoke(inputs)
