#!/usr/bin/env python3
"""
Currency Converter USD → MXN
Fetches the latest exchange rate and calculates the total cost in Mexican Pesos.
Uses free exchange rate APIs (no key required).

Usage: python convert_currency.py <amount_usd> [--with-tax]

The --with-tax flag adds the 20% Mexico import tax estimate.
"""

import json
import sys
from datetime import datetime

import requests

# Free exchange rate API endpoints (tried in order)
EXCHANGE_APIS = [
    {
        "name": "ExchangeRate-API (free)",
        "url": "https://open.er-api.com/v6/latest/USD",
        "extract": lambda data: data.get("rates", {}).get("MXN"),
    },
    {
        "name": "frankfurter.app",
        "url": "https://api.frankfurter.app/latest?from=USD&to=MXN",
        "extract": lambda data: data.get("rates", {}).get("MXN"),
    },
]


def get_exchange_rate() -> dict:
    """Fetch the current USD to MXN exchange rate."""
    for api in EXCHANGE_APIS:
        try:
            response = requests.get(api["url"], timeout=10)
            response.raise_for_status()
            data = response.json()
            rate = api["extract"](data)
            if rate:
                return {
                    "rate": float(rate),
                    "source": api["name"],
                    "date": datetime.now().isoformat(),
                    "status": "success",
                }
        except Exception:
            continue

    return {
        "rate": None,
        "error": "No se pudo obtener el tipo de cambio de ninguna fuente",
        "status": "error",
    }


def calculate_total_mxn(
    product_price_usd: float,
    shipping_cost_usd: float = 0,
    import_tax_included: bool = False,
    import_tax_rate: float = 0.20,
) -> dict:
    """Calculate total cost in MXN including shipping and optional import tax."""
    fx = get_exchange_rate()
    if fx["status"] != "success":
        return fx

    rate = fx["rate"]
    subtotal_usd = product_price_usd + shipping_cost_usd
    tax_usd = 0 if import_tax_included else subtotal_usd * import_tax_rate
    total_usd = subtotal_usd + tax_usd

    return {
        "exchange_rate": rate,
        "exchange_source": fx["source"],
        "exchange_date": fx["date"],
        "product_price_usd": product_price_usd,
        "product_price_mxn": round(product_price_usd * rate, 2),
        "shipping_cost_usd": shipping_cost_usd,
        "shipping_cost_mxn": round(shipping_cost_usd * rate, 2),
        "import_tax_included": import_tax_included,
        "import_tax_usd": round(tax_usd, 2),
        "import_tax_mxn": round(tax_usd * rate, 2),
        "total_usd": round(total_usd, 2),
        "total_mxn": round(total_usd * rate, 2),
        "status": "success",
    }


def main():
    if len(sys.argv) < 2:
        print("Uso: python convert_currency.py <monto_usd> [costo_envio_usd] [--with-tax]")
        print("  --with-tax  Agrega el impuesto de importación estimado (~20%)")
        print("\nEjemplo: python convert_currency.py 25.99 3.50 --with-tax")
        sys.exit(1)

    amount = float(sys.argv[1])
    shipping = float(sys.argv[2]) if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else 0
    with_tax = "--with-tax" in sys.argv

    result = calculate_total_mxn(amount, shipping, import_tax_included=not with_tax)

    if result["status"] == "success":
        print(f"💱 Tipo de cambio: 1 USD = {result['exchange_rate']:.2f} MXN")
        print(f"   Fuente: {result['exchange_source']}")
        print(f"\n📦 Producto:  ${result['product_price_usd']:.2f} USD = ${result['product_price_mxn']:.2f} MXN")
        if shipping > 0:
            print(f"🚚 Envío:     ${result['shipping_cost_usd']:.2f} USD = ${result['shipping_cost_mxn']:.2f} MXN")
        if result["import_tax_usd"] > 0:
            print(f"🏛️  Impuesto:  ${result['import_tax_usd']:.2f} USD = ${result['import_tax_mxn']:.2f} MXN (~20%)")
        else:
            print("🏛️  Impuesto:  Incluido en el precio")
        print(f"\n💰 TOTAL:     ${result['total_usd']:.2f} USD = ${result['total_mxn']:.2f} MXN")
    else:
        print(f"Error: {result.get('error', 'desconocido')}")

    # Save to JSON
    output_path = "currency_conversion.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(f"\n--- Datos guardados en: {output_path} ---")


if __name__ == "__main__":
    main()
