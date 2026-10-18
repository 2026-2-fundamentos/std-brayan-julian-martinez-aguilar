import csv
import gzip
from collections import defaultdict
from pathlib import Path


def pregunta_12():
    """
    Para cada letra de la primera columna (`letter`), sume todos los valores
    numéricos de los pares `clave:valor` de la quinta columna (`metrics`).
    Retorne un diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"A": 177, "B": 187, "C": 114, ...}
    """

    data_path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    metric_sums = defaultdict(int)

    with gzip.open(data_path, mode="rt", encoding="utf-8", newline="") as data_file:
        rows = csv.reader(data_file, delimiter="\t")
        for row in rows:
            letter = row[0]
            for metric in row[4].split(","):
                _, raw_value = metric.split(":")
                metric_sums[letter] += int(raw_value)

    return dict(sorted(metric_sums.items()))
