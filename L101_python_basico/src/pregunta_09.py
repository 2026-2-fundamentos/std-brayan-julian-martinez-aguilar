import csv
import gzip
from collections import Counter
from pathlib import Path


def pregunta_09():
    """
    Cuente cuántas veces aparece cada clave en la quinta columna (`metrics`)
    de todo el archivo. Retorne un diccionario `{clave: cantidad}` con las
    claves en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"aaa": 13, "bbb": 16, "ccc": 23, ...}
    """

    data_path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    metric_counts = Counter()

    with gzip.open(data_path, mode="rt", encoding="utf-8", newline="") as data_file:
        rows = csv.reader(data_file, delimiter="\t")
        for row in rows:
            for metric in row[4].split(","):
                key, _ = metric.split(":")
                metric_counts[key] += 1

    return dict(sorted(metric_counts.items()))