from pathlib import Path

import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def build_cohort_analysis() -> pd.DataFrame:
    """
    Una tienda quiere saber si sus clientes vuelven a comprar después de su
    primera compra. Para responder, agrupe a los clientes en cohortes según
    el mes de su primera compra y mida, mes a mes, qué proporción de cada
    cohorte vuelve a comprar. Use `data/sales.csv.gz`, que tiene una fila por
    orden con su cliente (`CustomerID`) y su fecha (`OrderDate`).

    Use estas definiciones:

    - `cohort_month`: el mes de la primera compra del cliente, escrito como
      `AAAA-MM`.
    - `period_index`: los meses transcurridos desde `cohort_month`; es 0 en el
      mes de la primera compra, 1 en el mes siguiente, y así sucesivamente.
    - `active_customers`: la cantidad de clientes distintos de la cohorte que
      compraron en ese período.
    - `cohort_size`: la cantidad de clientes de la cohorte, es decir, sus
      clientes activos en el período 0.
    - `retention_rate`: `active_customers` sobre `cohort_size`.

    Genere dos archivos en `submission/`:

    1. `cohort_retention.csv`, sin el índice de Pandas, con las columnas
       `cohort_month`, `period_index`, `active_customers`, `cohort_size` y
       `retention_rate`, y una fila por cada combinación cohorte–período
       observada, ordenadas por cohorte y período.

    2. `cohort_retention_heatmap.png`, un mapa de calor de `retention_rate`
       con una fila por cohorte (eje vertical) y una columna por período
       (eje horizontal). Muestre los valores como porcentajes. Los períodos
       que todavía no se pueden observar para una cohorte no significan
       retención cero: déjelos vacíos en el mapa.

    La función también debe retornar la tabla de retención.

    Ejemplo del formato de `cohort_retention.csv`:

        cohort_month,period_index,active_customers,cohort_size,retention_rate
        2022-01,0,100,100,1.0
        2022-01,1,26,100,0.26
        ...
    """
    activity_dir = Path(__file__).resolve().parents[1]
    data_path = activity_dir / "data" / "sales.csv.gz"
    sales = pd.read_csv(data_path)

    sales["order_month"] = pd.to_datetime(sales["OrderDate"]).dt.to_period("M")
    first_purchase = (
        sales.groupby("CustomerID", as_index=False)["order_month"].min()
        .rename(columns={"order_month": "cohort_month"})
    )
    sales = sales.merge(first_purchase, on="CustomerID", how="left")

    sales["period_index"] = (
        sales["order_month"].dt.year - sales["cohort_month"].dt.year
    ) * 12 + (
        sales["order_month"].dt.month - sales["cohort_month"].dt.month
    )

    cohort_size = (
        first_purchase.groupby("cohort_month", as_index=False)["CustomerID"]
        .nunique()
        .rename(columns={"CustomerID": "cohort_size"})
    )

    retention = (
        sales.groupby(["cohort_month", "period_index"], as_index=False)[
            "CustomerID"
        ]
        .nunique()
        .rename(columns={"CustomerID": "active_customers"})
    )
    retention = retention.merge(cohort_size, on="cohort_month", how="left")
    retention["retention_rate"] = (
        retention["active_customers"] / retention["cohort_size"]
    )

    retention["cohort_month"] = retention["cohort_month"].astype(str)
    retention = retention[
        [
            "cohort_month",
            "period_index",
            "active_customers",
            "cohort_size",
            "retention_rate",
        ]
    ].sort_values(["cohort_month", "period_index"])
    retention["period_index"] = retention["period_index"].astype("int64")
    retention["active_customers"] = retention["active_customers"].astype("int64")
    retention["cohort_size"] = retention["cohort_size"].astype("int64")

    submission_dir = activity_dir / "submission"
    submission_dir.mkdir(parents=True, exist_ok=True)
    retention.to_csv(
        submission_dir / "cohort_retention.csv", index=False
    )

    heatmap = retention.pivot(
        index="cohort_month",
        columns="period_index",
        values="retention_rate",
    ).sort_index()
    masked = np.ma.masked_invalid(heatmap.to_numpy())

    figure, axis = plt.subplots(
        figsize=(max(8, heatmap.shape[1] * 0.8), max(4, heatmap.shape[0] * 0.45))
    )
    image = axis.imshow(
        masked,
        aspect="auto",
        cmap="Blues",
        vmin=0,
        vmax=1,
    )

    axis.set_xticks(range(heatmap.shape[1]))
    axis.set_xticklabels([str(column) for column in heatmap.columns])
    axis.set_yticks(range(heatmap.shape[0]))
    axis.set_yticklabels(heatmap.index)
    axis.set_xlabel("Period index")
    axis.set_ylabel("Cohort month")
    figure.colorbar(image, ax=axis, label="Retention")

    for row in range(heatmap.shape[0]):
        for column in range(heatmap.shape[1]):
            value = heatmap.iloc[row, column]
            if pd.notna(value):
                axis.text(
                    column,
                    row,
                    f"{value:.1%}",
                    ha="center",
                    va="center",
                    color="white" if value > 0.55 else "black",
                    fontsize=8,
                )

    figure.tight_layout()
    figure.savefig(
        submission_dir / "cohort_retention_heatmap.png",
        dpi=150,
        bbox_inches="tight",
    )
    plt.close(figure)

    return retention
