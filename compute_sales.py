import json
import sys
import time
from typing import Any


def load_json(path: str) -> Any:
    """Load a JSON file and return its parsed content, or None on error."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ERROR: No se encontró el archivo: {path}")
    except json.JSONDecodeError as exc:
        print(f"ERROR: JSON inválido en {path}: {exc}")
    except Exception as exc:
        print(f"ERROR: No se pudo leer {path}: {exc}")
    return None


def build_price_map(catalog: Any) -> dict[str, float]:
    """
    Build mapping: product_title -> price
    Expects catalog to be a list of dicts with keys: 'title', 'price'.
    """
    prices: dict[str, float] = {}

    if not isinstance(catalog, list):
        print("ERROR: El catálogo debe ser una lista de productos (JSON array).")
        return prices

    for item in catalog:
        if not isinstance(item, dict):
            print(f"AVISO: Entrada inválida en catálogo (no es objeto): {item}")
            continue

        title = item.get("title")
        price = item.get("price")

        if not isinstance(title, str) or title.strip() == "":
            print(f"AVISO: Producto sin 'title' válido en catálogo: {item}")
            continue

        try:
            price_value = float(price)
        except (TypeError, ValueError):
            print(f"AVISO: Precio inválido para '{title}': {price}")
            continue

        prices[title] = price_value

    return prices


def compute_total_sales(prices: dict[str, float], sales: Any) -> tuple[float, int]:
    """
    Compute total sales cost.
    Expects sales to be a list of dicts with keys: 'Product', 'Quantity'.
    Returns (total, error_count).
    """
    total = 0.0
    errors = 0

    if not isinstance(sales, list):
        print("ERROR: El registro de ventas debe ser una lista (JSON array).")
        return total, 1

    for record in sales:
        if not isinstance(record, dict):
            print(f"AVISO: Venta inválida (no es objeto): {record}")
            errors += 1
            continue

        product = record.get("Product")
        quantity = record.get("Quantity")

        if not isinstance(product, str) or product.strip() == "":
            print(f"AVISO: Venta sin 'Product' válido: {record}")
            errors += 1
            continue

        try:
            qty = int(quantity)
        except (TypeError, ValueError):
            print(f"AVISO: Cantidad inválida para '{product}': {quantity}")
            errors += 1
            continue

        if qty < 0:
            print(f"AVISO: Cantidad negativa para '{product}': {qty}")
            errors += 1
            continue

        if product not in prices:
            print(f"AVISO: Producto no existe en catálogo: '{product}'")
            errors += 1
            continue

        total += prices[product] * qty

    return total, errors


def format_results(total: float, errors: int, elapsed: float) -> str:
    return (
        "=== Sales Results ===\n"
        f"Total Sales: ${total:.2f}\n"
        f"Errors/Warnings: {errors}\n"
        f"Execution Time: {elapsed:.6f} seconds\n"
    )


def write_results(text: str, filename: str = "SalesResults.txt") -> None:
    with open(filename, "w", encoding="utf-8") as f:
        f.write(text)


def main() -> int:
    if len(sys.argv) != 3:
        print("Uso: python compute_sales.py priceCatalogue.json salesRecord.json")
        return 1

    catalog_path = sys.argv[1]
    sales_path = sys.argv[2]

    start = time.perf_counter()

    catalog = load_json(catalog_path)
    sales = load_json(sales_path)

    if catalog is None or sales is None:
        print("ERROR: No se pudo cargar uno o ambos archivos de entrada.")
        return 1

    prices = build_price_map(catalog)
    total, errors = compute_total_sales(prices, sales)

    elapsed = time.perf_counter() - start
    output = format_results(total, errors, elapsed)

    print(output)
    write_results(output)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
