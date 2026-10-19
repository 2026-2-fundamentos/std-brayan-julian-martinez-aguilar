import unicodedata
from pathlib import Path

import pandas as pd

def pregunta_01():
    """
    El archivo `data/solicitudes_de_credito.csv.gz` contiene las solicitudes de
    un programa de crédito, pero llegó sucio: tiene una columna de índice que
    no pertenece a los datos, registros duplicados, registros incompletos y
    valores que representan lo mismo escritos de formas distintas en los
    campos de texto, las fechas, el estrato y el monto.

    Su tarea es limpiarlo y guardar el resultado en
    `submission/solicitudes_de_credito.csv`, usando punto y coma (`;`) como
    separador y sin el índice de Pandas.

    El archivo limpio debe cumplir lo siguiente:

    - Contiene solamente las nueve columnas `sexo`, `tipo_de_emprendimiento`,
      `idea_negocio`, `barrio`, `estrato`, `comuna_ciudadano`,
      `fecha_de_beneficio`, `monto_del_credito` y `línea_credito`, en ese
      orden.
    - Los campos de texto están en minúsculas y sus palabras separadas por
      espacios.
    - `estrato` y `monto_del_credito` son números enteros, sin símbolos ni
      separadores de miles.
    - Todas las fechas de `fecha_de_beneficio` usan un mismo formato, por
      ejemplo `AAAA-MM-DD`.
    - No hay registros incompletos. La única excepción es
      `comuna_ciudadano`: sus valores faltantes son parte de los datos
      originales y deben conservarse.
    - No hay registros duplicados.

    Ejemplo del formato del archivo:

        sexo;tipo_de_emprendimiento;idea_negocio;barrio;estrato;...
        femenino;comercio;almacen de ropa en;los cerros el vergel;2;...
        ...
    """
    activity_dir = Path(__file__).resolve().parents[1]
    df = pd.read_csv(
        activity_dir / "data" / "solicitudes_de_credito.csv.gz",
        sep=";",
        compression="gzip",
        index_col=0,
    )

    # Convertir todos los campos de texto a minúsculas y reemplazar guiones bajos por espacios

    text_columns = ["sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", "línea_credito"]
    for col in text_columns:
        df[col] = (
            df[col]
            .str.lower()
            .str.replace(r"[_-]+", " ", regex=True)
            .str.strip()
            .str.normalize("NFKD")
            .str.encode("ascii", errors="ignore")
            .str.decode("ascii")
        )

    # Convertir estrato y monto_del_credito a enteros

    df["estrato"] = pd.to_numeric(df["estrato"], errors="coerce").astype("Int64")
    df["monto_del_credito"] = pd.to_numeric(
        df["monto_del_credito"]
        .astype("string")
        .str.replace(r"[$,\s]", "", regex=True)
        .str.replace(r"\.0+$", "", regex=True),
        errors="coerce",
    ).astype("Int64")

    # Normalizar las fechas a un formato uniforme (AAAA-MM-DD)

    df["fecha_de_beneficio"] = pd.to_datetime(
        df["fecha_de_beneficio"], format="mixed", dayfirst=True, errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    # Eliminar registros incompletos, excepto para comuna_ciudadano

    df = df.dropna(subset=[col for col in df.columns if col != "comuna_ciudadano"])
    df = df.drop_duplicates()

    # Reordenar las columnas según lo especificado

    column_order = ["sexo", "tipo_de_emprendimiento", "idea_negocio", "barrio", 
                    "estrato", "comuna_ciudadano", "fecha_de_beneficio", 
                    "monto_del_credito", "línea_credito"]
    df = df[column_order]

    # Guardar el DataFrame limpio en un archivo CSV con punto y coma como separador y sin índice

    output_path = activity_dir / "submission" / "solicitudes_de_credito.csv"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, sep=";", index=False)