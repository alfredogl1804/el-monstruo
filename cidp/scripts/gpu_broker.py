#!/usr/bin/env python3.11
"""
gpu_broker.py — Broker de Infraestructura GPU.

Gestiona la renta dinámica de GPUs en Vast.ai, RunPod y otros proveedores.
Selección por política configurable: precio, disponibilidad, reputación.

IMPORTANTE: Los precios de referencia son ORIENTATIVOS.
SIEMPRE consulta precios en tiempo real antes de provisionar.
"""

import asyncio
import json
import os
import sys
import yaml
from pathlib import Path

try:
    import aiohttp
except ImportError:
    aiohttp = None

SKILL_DIR = Path(__file__).parent.parent


def load_gpu_policy():
    """Load GPU broker policy from config."""
    path = SKILL_DIR / "config" / "gpu_policy.yaml"
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


class VastAIAdapter:
    """Adapter for Vast.ai GPU marketplace."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("VASTAI_API_KEY", "")
        self.api_base = "https://console.vast.ai/api/v0"

    async def search_offers(self, gpu_type: str = "RTX_4090", min_vram_gb: int = 24,
                            max_price_hr: float = 10.0) -> list:
        """Search for available GPU offers."""
        if not self.api_key:
            return [{"error": "VASTAI_API_KEY not set", "provider": "vastai"}]

        if not aiohttp:
            return [{"error": "aiohttp not installed", "provider": "vastai"}]

        # Vast.ai search query
        query = {
            "verified": {"eq": True},
            "external": {"eq": False},
            "rentable": {"eq": True},
            "gpu_ram": {"gte": min_vram_gb * 1024},  # MB
            "dph_total": {"lte": max_price_hr},
        }

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                params = {"q": json.dumps(query), "order": "dph_total", "limit": 10}
                async with session.get(
                    f"{self.api_base}/bundles",
                    headers=headers,
                    params=params,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        offers = data.get("offers", [])
                        return [
                            {
                                "provider": "vastai",
                                "id": o.get("id"),
                                "gpu_name": o.get("gpu_name", "unknown"),
                                "gpu_ram_gb": o.get("gpu_ram", 0) / 1024,
                                "num_gpus": o.get("num_gpus", 1),
                                "price_per_hour": o.get("dph_total", 0),
                                "reliability": o.get("reliability2", 0),
                                "dlperf": o.get("dlperf", 0),
                                "inet_up": o.get("inet_up", 0),
                                "inet_down": o.get("inet_down", 0),
                            }
                            for o in offers[:10]
                        ]
                    else:
                        return [{"error": f"API returned {resp.status}", "provider": "vastai"}]
        except Exception as e:
            return [{"error": str(e), "provider": "vastai"}]

    async def provision(self, offer_id: int, image: str = "pytorch/pytorch:latest",
                        disk_gb: int = 50) -> dict:
        """Provision a GPU instance."""
        if not self.api_key or not aiohttp:
            return {"status": "failed", "error": "Missing API key or aiohttp"}

        payload = {
            "client_id": "cidp",
            "image": image,
            "disk": disk_gb,
            "label": "cidp-training",
        }

        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                async with session.put(
                    f"{self.api_base}/asks/{offer_id}/",
                    headers=headers,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status in (200, 201):
                        data = await resp.json()
                        return {
                            "status": "provisioned",
                            "provider": "vastai",
                            "instance_id": data.get("new_contract"),
                            "details": data,
                        }
                    else:
                        text = await resp.text()
                        return {"status": "failed", "error": f"API {resp.status}: {text[:200]}"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}

    async def teardown(self, instance_id: int) -> dict:
        """Teardown a GPU instance."""
        if not self.api_key or not aiohttp:
            return {"status": "failed", "error": "Missing API key or aiohttp"}

        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                async with session.delete(
                    f"{self.api_base}/instances/{instance_id}/",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    return {"status": "torn_down" if resp.status == 200 else "failed"}
        except Exception as e:
            return {"status": "failed", "error": str(e)}


class RunPodAdapter:
    """Adapter for RunPod GPU cloud."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get("RUNPOD_API_KEY", "")
        self.api_base = "https://api.runpod.io/v2"

    async def search_offers(self, gpu_type: str = "NVIDIA A100",
                            max_price_hr: float = 10.0) -> list:
        """Search for available GPU offers on RunPod."""
        if not self.api_key:
            return [{"error": "RUNPOD_API_KEY not set", "provider": "runpod"}]

        # RunPod uses GraphQL
        query = """
        query {
            gpuTypes {
                id
                displayName
                memoryInGb
                secureCloud
                communityCloud
                lowestPrice {
                    minimumBidPrice
                    uninterruptablePrice
                }
            }
        }
        """

        try:
            if not aiohttp:
                return [{"error": "aiohttp not installed", "provider": "runpod"}]

            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                async with session.post(
                    "https://api.runpod.io/graphql",
                    headers=headers,
                    json={"query": query},
                    timeout=aiohttp.ClientTimeout(total=30),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        gpu_types = data.get("data", {}).get("gpuTypes", [])
                        offers = []
                        for g in gpu_types:
                            price = g.get("lowestPrice", {})
                            if price and price.get("uninterruptablePrice", 999) <= max_price_hr:
                                offers.append({
                                    "provider": "runpod",
                                    "id": g["id"],
                                    "gpu_name": g.get("displayName", "unknown"),
                                    "gpu_ram_gb": g.get("memoryInGb", 0),
                                    "price_per_hour": price.get("uninterruptablePrice", 0),
                                    "spot_price": price.get("minimumBidPrice", 0),
                                })
                        return sorted(offers, key=lambda x: x["price_per_hour"])[:10]
                    else:
                        return [{"error": f"API returned {resp.status}", "provider": "runpod"}]
        except Exception as e:
            return [{"error": str(e), "provider": "runpod"}]


async def provision_gpu(workload: dict, budget_usd: float) -> dict:
    """
    Provision a GPU based on workload requirements and budget.

    Args:
        workload: Dict with min_vram_gb, preferred_gpu, duration_estimate, etc.
        budget_usd: Maximum budget in USD.

    Returns:
        Dict with provisioning result.
    """
    policy = load_gpu_policy()
    min_vram = workload.get("min_vram_gb", 24)
    max_hourly = policy.get("selection_policy", {}).get("cost_guardrails", {}).get("max_hourly_usd", 10.0)
    max_hourly = min(max_hourly, budget_usd)

    results = {"offers": [], "selected": None, "status": "searching"}

    # Search Vast.ai first (priority 1)
    vastai = VastAIAdapter()
    vastai_offers = await vastai.search_offers(min_vram_gb=min_vram, max_price_hr=max_hourly)
    results["offers"].extend(vastai_offers)

    # Search RunPod (priority 2)
    runpod = RunPodAdapter()
    runpod_offers = await runpod.search_offers(max_price_hr=max_hourly)
    results["offers"].extend(runpod_offers)

    # Filter out errors
    valid_offers = [o for o in results["offers"] if "error" not in o]

    if not valid_offers:
        results["status"] = "no_offers"
        results["error"] = "No GPU offers found within budget"
        return results

    # Score and select best offer
    weights = policy.get("selection_policy", {}).get("weights", {})
    best_offer = None
    best_score = -1

    for offer in valid_offers:
        score = 0
        # Price score (lower is better)
        price = offer.get("price_per_hour", 999)
        score += weights.get("price", 0.4) * (1 - min(price / max_hourly, 1))
        # Reliability score
        reliability = offer.get("reliability", 0.5)
        score += weights.get("reliability", 0.2) * reliability
        # VRAM score
        vram = offer.get("gpu_ram_gb", 0)
        score += weights.get("availability", 0.25) * min(vram / max(min_vram, 1), 1)

        if score > best_score:
            best_score = score
            best_offer = offer

    results["selected"] = best_offer
    results["selection_score"] = best_score
    results["status"] = "selected"

    return results
