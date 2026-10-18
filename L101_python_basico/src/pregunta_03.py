import csv
import gzip
from collections import defaultdict
from pathlib import Path


def pregunta_03():
    """
    Sume los valores de la segunda columna (`value`) para cada letra de la
    primera columna (`letter`). Retorne una lista de tuplas `(letra, suma)`
    ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 53), ("B", 36), ("C", 27), ...]
    """
    data_path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    value_sums = defaultdict(int)

    with gzip.open(data_path, mode="rt", encoding="utf-8", newline="") as data_file:
        rows = csv.reader(data_file, delimiter="\t")
        for row in rows:
            value_sums[row[0]] += int(row[1])

    return sorted(value_sums.items())