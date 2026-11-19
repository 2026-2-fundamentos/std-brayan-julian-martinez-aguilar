from pathlib import Path

import pandas as pd

def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Una cadena de suministros de oficina vende mucho, pero la gerencia
    sospecha que parte de esas ventas no deja utilidad. El archivo
    `data/superstore_orders.csv.gz` tiene una fila por línea de pedido, con
    el número de pedido (`Order ID`), las ventas (`Sales`), la utilidad
    (`Profit`), el descuento aplicado (`Discount`, como proporción), el
    segmento del cliente (`Customer Segment`) y la categoría del producto
    (`Product Category`). Una utilidad negativa significa que la línea se
    vendió con pérdida.

    Use estas definiciones:

    - Margen (`profit_margin`): utilidad sobre ventas.
    - Línea con pérdida: una línea cuya utilidad es negativa.
    - `loss_line_rate`: la proporción de líneas con pérdida.
    - `lost_profit`: la suma de las pérdidas de las líneas con pérdida,
      escrita como número positivo.
    - Rango de descuento (`discount_band`): `0%` si no hubo descuento,
      `1%-5%` si fue mayor que 0 y hasta 5 %, `6%-10%` si fue mayor que 5 % y
      hasta 10 %, y `más de 10%` en otro caso.

    Genere tres archivos en `submission/`, sin el índice de Pandas y con las
    columnas en el orden indicado:

    1. `profitability_summary.csv`, con una sola fila: `lines` (cantidad de
       líneas), `orders` (pedidos distintos), `sales`, `profit`,
       `profit_margin`, `loss_lines` (cantidad de líneas con pérdida),
       `loss_line_rate` y `lost_profit`.

    2. `discount_summary.csv`, con una fila por rango de descuento, en el
       orden en que se definieron arriba: `discount_band`, `lines`, `sales`,
       `profit`, `profit_margin`, `loss_line_rate` y `lost_profit`.

    3. `priority_segments.csv`, con los cinco segmentos segmento–categoría
       que más utilidad pierden: `Customer Segment`, `Product Category`,
       `lines`, `sales`, `profit`, `profit_margin` y `lost_profit`. Considere
       solamente segmentos con al menos 100 líneas y ordénelos por
       `lost_profit` de mayor a menor.

    La función también debe retornar las tres tablas, en el mismo orden.

    Ejemplo del formato de `discount_summary.csv`:

        discount_band,lines,sales,profit,profit_margin,loss_line_rate,...
        0%,166,170539.05,29472.3789,0.1728,0.488,...
        ...
    """
    activity_dir = Path(__file__).resolve().parents[1]
    data_path = activity_dir / "data" / "superstore_orders.csv.gz"
    orders = pd.read_csv(
        data_path,
        sep=";",
        decimal=",",
        encoding="utf-8-sig",
    )

    orders["is_loss"] = orders["Profit"] < 0

    line_count = len(orders)
    total_sales = orders["Sales"].sum()
    total_profit = orders["Profit"].sum()
    loss_lines = int(orders["is_loss"].sum())

    profitability_summary = pd.DataFrame(
        [
            {
                "lines": line_count,
                "orders": orders["Order ID"].nunique(),
                "sales": total_sales,
                "profit": total_profit,
                "profit_margin": total_profit / total_sales,
                "loss_lines": loss_lines,
                "loss_line_rate": loss_lines / line_count,
                "lost_profit": (-orders.loc[orders["is_loss"], "Profit"]).sum(),
            }
        ]
    )

    def discount_band(discount: float) -> str:
        if discount == 0:
            return "0%"
        if discount <= 0.05:
            return "1%-5%"
        if discount <= 0.10:
            return "6%-10%"
        return "más de 10%"

    band_order = ["0%", "1%-5%", "6%-10%", "más de 10%"]
    orders["discount_band"] = orders["Discount"].map(discount_band)

    discount_rows = []
    for band in band_order:
        subset = orders.loc[orders["discount_band"] == band]
        sales = subset["Sales"].sum()
        profit = subset["Profit"].sum()
        lines = len(subset)
        loss_lines = int(subset["is_loss"].sum())
        discount_rows.append(
            {
                "discount_band": band,
                "lines": lines,
                "sales": sales,
                "profit": profit,
                "profit_margin": profit / sales,
                "loss_line_rate": loss_lines / lines,
                "lost_profit": (-subset.loc[subset["is_loss"], "Profit"]).sum(),
            }
        )
    discount_summary = pd.DataFrame(discount_rows)

    grouped_segments = (
        orders.groupby(["Customer Segment", "Product Category"], sort=False)
        .agg(
            lines=("Order ID", "size"),
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
        )
        .reset_index()
    )
    grouped_segments = grouped_segments.loc[grouped_segments["lines"] >= 100].copy()

    lost_profit = (
        orders.loc[orders["is_loss"]]
        .assign(lost_profit=-orders.loc[orders["is_loss"], "Profit"])
        .groupby(["Customer Segment", "Product Category"], sort=False)["lost_profit"]
        .sum()
        .rename("lost_profit")
    )
    priority_segments = grouped_segments.join(lost_profit, on=["Customer Segment", "Product Category"])
    priority_segments["lost_profit"] = priority_segments["lost_profit"].fillna(0)
    priority_segments["profit_margin"] = (
        priority_segments["profit"] / priority_segments["sales"]
    )
    priority_segments = (
        priority_segments
        .sort_values("lost_profit", ascending=False, kind="stable")
        .head(5)
        .loc[
            :,
            [
                "Customer Segment",
                "Product Category",
                "lines",
                "sales",
                "profit",
                "profit_margin",
                "lost_profit",
            ],
        ]
        .reset_index(drop=True)
    )

    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)
    profitability_summary.to_csv(
        submission_dir / "profitability_summary.csv", index=False
    )
    discount_summary.to_csv(submission_dir / "discount_summary.csv", index=False)
    priority_segments.to_csv(submission_dir / "priority_segments.csv", index=False)

    return profitability_summary, discount_summary, priority_segments
