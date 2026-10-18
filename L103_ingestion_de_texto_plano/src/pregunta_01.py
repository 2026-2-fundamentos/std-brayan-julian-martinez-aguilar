import re

import pandas as pd


def pregunta_01():
    """
    El archivo `data/clusters_report.txt` es un reporte de clústeres de
    palabras clave pensado para ser leído por una persona, no por un programa:
    los encabezados ocupan varias líneas, las columnas están alineadas con
    espacios y la lista de palabras clave de un clúster continúa en las líneas
    siguientes.

    Su tarea es convertir ese reporte en un DataFrame de Pandas con una fila
    por clúster y las columnas:

    - `cluster`: número del clúster, como entero.
    - `cantidad_de_palabras_clave`: como entero.
    - `porcentaje_de_palabras_clave`: como número decimal; por ejemplo, el
      texto `15,9 %` debe quedar como `15.9`.
    - `principales_palabras_clave`: todas las palabras clave del clúster en un
      solo texto, separadas por una coma y un único espacio.

    Retorne el DataFrame.

    Ejemplo del formato de la respuesta (se omite la última columna):

           cluster  cantidad_de_palabras_clave  porcentaje_de_palabras_clave
        0        1                         105                          15.9
        1        2                         102                          15.4
        ...
    """
    with open("data/clusters_report.txt", "r", encoding="utf-8") as file:
        lines = file.readlines()

    records = []
    current = None

    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("-"):
            continue

        header_match = re.match(r"^\s*(\d+)\s+(\d+)\s+(\d+,\d+)\s*%\s*(.*)$", line)
        if header_match:
            if current is not None:
                records.append(current)

            cluster = int(header_match.group(1))
            cantidad = int(header_match.group(2))
            porcentaje = float(header_match.group(3).replace(",", "."))
            texto_keywords = header_match.group(4).strip()

            current = {
                "cluster": cluster,
                "cantidad_de_palabras_clave": cantidad,
                "porcentaje_de_palabras_clave": porcentaje,
                "principales_palabras_clave": [texto_keywords] if texto_keywords else [],
            }
            continue

        if current is not None:
            current["principales_palabras_clave"].append(stripped)

    if current is not None:
        records.append(current)

    df = pd.DataFrame(records)
    if df.empty:
        return df

    df["principales_palabras_clave"] = (
        df["principales_palabras_clave"]
        .apply(lambda palabras: " ".join(palabras))
        .apply(lambda text: re.sub(r"\s+", " ", text).strip())
        .apply(lambda text: re.sub(r"\s*,\s*", ", ", text))
        .apply(lambda text: text.rstrip("."))
    )

    return df[[
        "cluster",
        "cantidad_de_palabras_clave",
        "porcentaje_de_palabras_clave",
        "principales_palabras_clave",
    ]]