import csv
import gzip
from pathlib import Path


def pregunta_10():
    """
    Para cada registro del archivo, en el mismo orden en que aparecen,
    retorne una tupla con la letra de la primera columna (`letter`), la
    cantidad de elementos de la cuarta columna (`codes`) y la cantidad de
    pares de la quinta columna (`metrics`). El resultado es una lista con una
    tupla por registro.

    Ejemplo del formato de la respuesta:

        [("E", 3, 5), ("A", 3, 4), ("B", 4, 4), ...]
    """

    data_path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    result = []

    with gzip.open(data_path, mode="rt", encoding="utf-8", newline="") as data_file:
        rows = csv.reader(data_file, delimiter="\t")
        for row in rows:
            codes_count = len(row[3].split(","))
            metrics_count = len(row[4].split(","))
            result.append((row[0], codes_count, metrics_count))

    return result