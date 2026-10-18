import json
import re
from pathlib import Path

import pandas as pd

# Columnas requeridas según el enunciado del ejercicio

REQUIRED_COLUMNS = [
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
]

# Normalización de nombres de columnas

def normalize_column_name(column_name):
    normalized = str(column_name).replace("\ufeff", "").strip().lower()
    normalized = re.sub(r"\s+", "_", normalized)
    return normalized

# Validación de valores faltantes

def is_missing_value(value):
    if pd.isna(value):
        return True
    if isinstance(value, str):
        return value.strip() == "" or value.strip().upper() == "N/A"
    return False

# Validación de emails

def is_valid_email(value):
    if pd.isna(value):
        return True

    if not isinstance(value, str):
        value = str(value)

    return bool(re.fullmatch(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", value.strip()))

# Reporte de calidad de datos

def main():
    """
    Antes de limpiar o analizar un conjunto de datos, un analista debe
    documentar qué problemas tiene. En este laboratorio usted no va a limpiar
    `data/ventas.csv.gz`: va a construir un reporte de calidad que deje evidencia
    de sus problemas, tal como están en el archivo.

    Lea `data/ventas.csv.gz` sin modificar sus valores. Para trabajar con los
    encabezados, normalícelos: páselos a minúsculas, elimine los espacios al
    inicio y al final (y cualquier marca BOM) y reemplace los espacios
    internos por `_`. Las columnas requeridas son `supplier_id`, `supplier`,
    `country`, `city`, `purchase_date`, `amount`, `discount`, `weight`,
    `units`, `unit_price` y `contact_email`.

    Escriba el reporte en `submission/data_quality_report.json` con estas
    claves:

    - `row_count`: cantidad de filas de datos.
    - `column_count`: cantidad de columnas.
    - `missing_required_columns`: lista ordenada de columnas requeridas que no
      están en el archivo.
    - `unexpected_columns`: lista ordenada de columnas del archivo que no son
      requeridas.
    - `duplicate_row_count`: cantidad de filas idénticas a una fila anterior.
    - `duplicate_supplier_id_row_count`: cantidad de filas cuyo `supplier_id`
      aparece más de una vez (cuente todas esas filas, no solo las
      repetidas).
    - `missing_value_count_by_column`: diccionario con la cantidad de valores
      faltantes de cada columna. Considere faltantes las celdas vacías y las
      que contienen `N/A`.
    - `invalid_email_count`: cantidad de valores de `contact_email` que no
      tienen la forma `usuario@dominio.extension`.
    - `invalid_unit_count`: cantidad de valores numéricos de `units` que no son
      enteros positivos. Los valores faltantes no se cuentan aquí.
    - `country_values`: lista ordenada de los valores distintos de `country`,
      escritos exactamente como aparecen en el archivo.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "row_count": 103,
          "column_count": 11,
          "missing_required_columns": [],
          ...
          "country_values": [" Colombia ", "CO", ...]
        }
    """
    # Cargar archivo CSV y normalizar nombres de columnas 

    activity_dir = Path(__file__).resolve().parents[1]
    csv_path = activity_dir / "data" / "ventas.csv.gz"

    df = pd.read_csv(csv_path, compression="gzip")
    df.columns = [normalize_column_name(column) for column in df.columns]

    # Validar columnas requeridas

    missing_required_columns = sorted(
        [column for column in REQUIRED_COLUMNS if column not in df.columns]
    )
    unexpected_columns = sorted(
        [column for column in df.columns if column not in REQUIRED_COLUMNS]
    )

    # Detectar duplicados

    duplicate_row_count = int(df.duplicated().sum())
    duplicate_supplier_id_row_count = int(
        df["supplier_id"].duplicated(keep=False).sum()
    ) if "supplier_id" in df.columns else 0

    # Contar valores faltantes por columna

    missing_value_count_by_column = {
        column: int(df[column].apply(is_missing_value).sum())
        for column in df.columns
    }

    # Validar emails y unidades

    invalid_email_count = 0
    if "contact_email" in df.columns:
        invalid_email_count = int(
            df["contact_email"].apply(lambda value: not is_valid_email(value)).sum()
        )

    invalid_unit_count = 0
    if "units" in df.columns:
        numeric_units = pd.to_numeric(df["units"], errors="coerce")
        valid_units = numeric_units.notna() & numeric_units.apply(
            lambda value: float(value).is_integer() and value > 0
        )
        invalid_unit_count = int((~valid_units & numeric_units.notna()).sum())

    # Obtener valores distintos de país
    
    country_values = []
    if "country" in df.columns:
        country_values = sorted(df["country"].dropna().unique().tolist())

    # Construir reporte final

    report = {
        "row_count": int(len(df)),
        "column_count": int(len(df.columns)),
        "missing_required_columns": missing_required_columns,
        "unexpected_columns": unexpected_columns,
        "duplicate_row_count": duplicate_row_count,
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": country_values,
    }

    # Guardar archivo JSON de salida

    output_dir = activity_dir / "submission"
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "data_quality_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    return report

# Ejecutar

if __name__ == "__main__":
    main()