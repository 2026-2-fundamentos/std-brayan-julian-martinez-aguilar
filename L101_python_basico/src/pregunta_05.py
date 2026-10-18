import csv
import gzip
from pathlib import Path


def pregunta_05():
    """
    Para cada letra de la primera columna (`letter`), encuentre el valor
    máximo y el valor mínimo de la segunda columna (`value`). Retorne una lista
    de tuplas `(letra, máximo, mínimo)` ordenada alfabéticamente por la letra.

    Ejemplo del formato de la respuesta:

        [("A", 9, 2), ("B", 9, 1), ...]
    """

    data_path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    value_ranges = {}

    with gzip.open(data_path, mode="rt", encoding="utf-8", newline="") as data_file:
        rows = csv.reader(data_file, delimiter="\t")
        for row in rows:
            letter = row[0]
            value = int(row[1])
            if letter not in value_ranges:
                value_ranges[letter] = [value, value]
            else:
                value_ranges[letter][0] = max(value_ranges[letter][0], value)
                value_ranges[letter][1] = min(value_ranges[letter][1], value)

    return [
        (letter, maximum, minimum)
        for letter, (maximum, minimum) in sorted(value_ranges.items())
    ]