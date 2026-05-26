import os

import yaml


def load_yaml(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_action_registry(base_path):
    registry_path = os.path.join(base_path, "autonomy_ladder", "action_registry_v0.yaml")
    return load_yaml(registry_path)


def get_allowlist(base_path):
    allowlist_path = os.path.join(base_path, "autonomy_ladder", "r1_self_evolution_allowlist.yaml")
    return load_yaml(allowlist_path)
