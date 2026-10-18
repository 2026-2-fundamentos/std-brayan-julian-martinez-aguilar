import csv
import gzip
from pathlib import Path


def pregunta_06():
    """
    La quinta columna (`metrics`) contiene pares `clave:valor` separados por
    comas. Para cada clave, encuentre el valor mínimo y el valor máximo que
    aparecen en todo el archivo. Retorne una lista de tuplas
    `(clave, mínimo, máximo)` ordenada alfabéticamente por la clave.

    Observe que el orden es mínimo y luego máximo, al contrario de la
    pregunta 5.

    Ejemplo del formato de la respuesta:

        [("aaa", 1, 9), ("bbb", 1, 9), ...]
    """

    data_path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    metric_ranges = {}

    with gzip.open(data_path, mode="rt", encoding="utf-8", newline="") as data_file:
        rows = csv.reader(data_file, delimiter="\t")
        for row in rows:
            for metric in row[4].split(","):
                key, raw_value = metric.split(":")
                value = int(raw_value)
                if key not in metric_ranges:
                    metric_ranges[key] = [value, value]
                else:
                    metric_ranges[key][0] = min(metric_ranges[key][0], value)
                    metric_ranges[key][1] = max(metric_ranges[key][1], value)

    return [
        (key, minimum, maximum)
        for key, (minimum, maximum) in sorted(metric_ranges.items())
    ]