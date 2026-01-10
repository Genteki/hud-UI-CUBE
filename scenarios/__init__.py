"""UI-CUBE scenarios (deterministic benchmark only)."""
from scenarios.deterministic import register_deterministic_scenarios


def register_scenarios(env):
    register_deterministic_scenarios(env)
