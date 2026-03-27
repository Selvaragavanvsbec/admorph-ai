from agents.copy_agent import CopyAgent
from agents.layout_agent import LayoutAgent
from agents.strategy_agent import StrategyAgent
from agents.variant_engine import VariantEngine
from agents.visual_agent import VisualAgent
from scoring.heuristic_scoring import HeuristicScoringEngine
from services.optimization import BanditOptimizer, BrandGuard, PerformancePredictor
from services.template_renderer import TemplateRenderer


class Orchestrator:
    def __init__(self) -> None:
        self.strategy_agent = StrategyAgent()
        self.copy_agent = CopyAgent()
        self.variant_engine = VariantEngine()
        self.scoring_engine = HeuristicScoringEngine()
        self.layout_agent = LayoutAgent()
        self.visual_agent = VisualAgent()
        self.renderer = TemplateRenderer()
        self.predictor = PerformancePredictor()
        self.bandit = BanditOptimizer()
        self.brand_guard = BrandGuard()

    def run(self, brief: dict) -> dict:
        strategy = self.strategy_agent.run(brief)
        copy = self.copy_agent.run(brief, strategy)

        variants = self.variant_engine.run(copy["headlines"], copy["ctas"], max_variants=50)
        variants = self.scoring_engine.run(variants, tone=brief["tone"])
        variants = self.layout_agent.run(variants, platform=brief["platform"])
        variants = self.visual_agent.run(variants, brand_colors=brief["brand_colors"])

        approved = [v for v in variants if self.brand_guard.validate(v)]
        rendered = self.renderer.render(approved, platform=brief["platform"])

        for variant in rendered:
            variant["predicted_ctr"] = self.predictor.predict_ctr(variant)

        return {
            "strategy": strategy,
            "best_variant": self.bandit.suggest_next(rendered),
            "variants": rendered,
        }
