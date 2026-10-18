import csv
import gzip
from collections import defaultdict
from pathlib import Path


def pregunta_11():
    """
    La cuarta columna (`codes`) contiene letras minúsculas separadas por
    comas. Para cada una de esas letras, sume los valores de la segunda
    columna (`value`) de los registros en los que aparece. Retorne un
    diccionario `{letra: suma}` con las letras en orden alfabético.

    Ejemplo del formato de la respuesta:

        {"a": 122, "b": 49, "c": 91, ...}
    """

    data_path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    value_sums = defaultdict(int)

    with gzip.open(data_path, mode="rt", encoding="utf-8", newline="") as data_file:
        rows = csv.reader(data_file, delimiter="\t")
        for row in rows:
            value = int(row[1])
            for code in row[3].split(","):
                value_sums[code] += value

    return dict(sorted(value_sums.items()))