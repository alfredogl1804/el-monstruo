"""Tech Radar & Vanguard — El Monstruo Sprint 60 + 63.1."""
from .tech_radar import (
    TechRadar,
    DependencyUpdate,
    TechTrend,
    TechRadarError,
    get_tech_radar,
    init_tech_radar,
)
from .intelligence_engine import (
    ResearchIntelligenceEngine,
    DiscoveryItem,
    IntegrationProposal,
    get_intelligence_engine,
    init_intelligence_engine,
    INTELIGENCIA_SIN_SUPABASE,
)
from .semantic_scholar import (
    SemanticScholarClient,
    get_scholar_client,
    init_scholar_client,
    DEFAULT_TOPICS,
)
from .weekly_digest import (
    WeeklyDigestGenerator,
    get_digest_generator,
    init_digest_generator,
)

__all__ = [
    # Sprint 60
    "TechRadar",
    "DependencyUpdate",
    "TechTrend",
    "TechRadarError",
    "get_tech_radar",
    "init_tech_radar",
    # Sprint 63.1
    "ResearchIntelligenceEngine",
    "DiscoveryItem",
    "IntegrationProposal",
    "get_intelligence_engine",
    "init_intelligence_engine",
    "INTELIGENCIA_SIN_SUPABASE",
    "SemanticScholarClient",
    "get_scholar_client",
    "init_scholar_client",
    "DEFAULT_TOPICS",
    "WeeklyDigestGenerator",
    "get_digest_generator",
    "init_digest_generator",
]
