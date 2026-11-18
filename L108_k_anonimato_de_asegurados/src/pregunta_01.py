import pandas as pd
import json
from pathlib import Path

"""
    Una aseguradora quiere publicar datos de sus afiliados para que un grupo
    de investigación estudie el costo de los seguros, sin que nadie pueda
    reconocer a una persona. El archivo `data/insurance.csv.gz` tiene una fila
    por afiliado con su edad (`age`), sexo (`sex`), índice de masa corporal
    (`bmi`), número de hijos (`children`), si fuma (`smoker`), región
    (`region`) y el costo de su seguro (`charges`).

    El archivo no tiene nombres ni documentos, pero eso no basta: la edad, el
    sexo, el índice de masa corporal, el número de hijos y la región son
    cuasi-identificadores, porque combinados pueden señalar a una persona.
    `smoker` es el atributo sensible que se quiere proteger.

    En este laboratorio usted va a medir el riesgo de reidentificación y a
    decidir qué publicar. Use estas definiciones:

    - Una clase de equivalencia es un grupo de registros con los mismos
      valores en todos los cuasi-identificadores. Un conjunto de datos cumple
      k-anonimato si toda clase tiene al menos k registros. Use k = 5.
    - `age_group`: `18-29`, `30-39`, `40-49` o `50-64`.
    - `bmi_group`: `bajo peso` (menos de 18.5), `normal` (desde 18.5 y menos
      de 25), `sobrepeso` (desde 25 y menos de 30) u `obesidad` (30 o más).
    - `children_group`: `0`, `1-2` o `3+`.

    Evalúe dos esquemas de generalización:

    - `with_children`: `age_group`, `sex`, `bmi_group`, `children_group` y
      `region`.
    - `without_children`: `age_group`, `sex`, `bmi_group` y `region`; el
      número de hijos no se publica.

    En cada esquema, suprima (no publique) los registros de las clases con
    menos de 5 registros. Luego, entre las clases publicadas, identifique las
    que no tienen diversidad en el atributo sensible, es decir, aquellas en
    las que todos los afiliados fuman o ninguno fuma: en esas clases, saber
    que alguien pertenece a ellas revela si fuma.

    Escriba `submission/privacy_report.json` con estas claves:

    - `original_k`: el menor tamaño de clase usando los cuasi-identificadores
      originales, sin generalizar.
    - `original_unique_records`: cuántos registros son los únicos de su clase
      con los cuasi-identificadores originales.
    - `schemes`: un diccionario con una entrada por esquema (`with_children` y
      `without_children`), cada una con las claves `quasi_identifiers` (la
      lista de columnas del esquema), `equivalence_classes` (clases antes de
      suprimir), `k_before_suppression`, `suppressed_records`,
      `published_records`, `published_classes`,
      `classes_without_smoker_diversity` y
      `records_without_smoker_diversity`.
    - `selected_scheme`: el esquema que suprime menos registros.
    - `mean_charges_original` y `mean_charges_published`: el costo promedio
      de todos los afiliados y el de los registros publicados con el esquema
      seleccionado.
    - `smoker_rate_original` y `smoker_rate_published`: la proporción de
      fumadores en ambos casos.

    Escriba también `submission/insurance_published.csv`, sin el índice de
    Pandas, con los registros publicados del esquema seleccionado, en el
    mismo orden del archivo original, y las columnas del esquema seguidas de
    `smoker` y `charges`.

    La función también debe retornar el reporte como un diccionario.

    Ejemplo del formato del reporte:

        {
          "original_k": 1,
          "original_unique_records": 1330,
          "schemes": {
            "with_children": {
              "quasi_identifiers": ["age_group", "sex", ...],
              "equivalence_classes": 278,
              ...
            },
            ...
          },
          ...
        }
    """

def pregunta_01():
    # Leer el archivo comprimido
    data = pd.read_csv('data/insurance.csv.gz', compression='gzip')

    # Crear las columnas de grupo
    data['age_group'] = pd.cut(data['age'], bins=[18, 30, 40, 50, 65], right=False, labels=['18-29', '30-39', '40-49', '50-64'])
    data['bmi_group'] = pd.cut(data['bmi'], bins=[0, 18.5, 25, 30, float('inf')], right=False, labels=['bajo peso', 'normal', 'sobrepeso', 'obesidad'])
    data['children_group'] = pd.cut(data['children'], bins=[0, 1, 3, float('inf')], right=False, labels=['0', '1-2', '3+'])

    # Calcular original_k y original_unique_records
    original_k = data.groupby(['age', 'sex', 'bmi', 'children', 'region']).size().min()
    original_unique_records = (data.groupby(['age', 'sex', 'bmi', 'children', 'region']).size() == 1).sum()

    # Definir los esquemas
    schemes = {
        "with_children": ['age_group', 'sex', 'bmi_group', 'children_group', 'region'],
        "without_children": ['age_group', 'sex', 'bmi_group', 'region']
    }

    report = {
        "original_k": int(original_k),
        "original_unique_records": int(original_unique_records),
        "schemes": {}
    }

    for scheme_name, quasi_identifiers in schemes.items():
        # Crear clases de equivalencia
        equivalence_classes = data.groupby(quasi_identifiers, observed=True).size()
        k_before_suppression = equivalence_classes.min()
        suppressed_records = equivalence_classes[equivalence_classes < 5].sum()
        published_classes = equivalence_classes[equivalence_classes >= 5]
        published_records = published_classes.sum()

        # Identificar clases sin diversidad en smoker
        smoker_diversity = data.groupby(quasi_identifiers, observed=True)['smoker'].nunique()
        published_smoker_diversity = smoker_diversity.reindex(published_classes.index)
        classes_without_smoker_diversity = published_smoker_diversity[
            published_smoker_diversity == 1
        ]
        records_without_smoker_diversity = published_classes[
            classes_without_smoker_diversity.index
        ].sum()

        report["schemes"][scheme_name] = {
            "quasi_identifiers": quasi_identifiers,
            "equivalence_classes": int(equivalence_classes.size),
            "k_before_suppression": int(k_before_suppression),
            "suppressed_records": int(suppressed_records),
            "published_records": int(published_records),
            "published_classes": int(published_classes.size),
            "classes_without_smoker_diversity": int(classes_without_smoker_diversity.size),
            "records_without_smoker_diversity": int(records_without_smoker_diversity),
        }

    selected_scheme = min(
        report["schemes"],
        key=lambda scheme_name: report["schemes"][scheme_name]["suppressed_records"],
    )
    quasi_identifiers = schemes[selected_scheme]

    equivalence_sizes = data.groupby(
        quasi_identifiers,
        observed=True,
    ).transform("size")
    published = data[equivalence_sizes >= 5].copy()

    report["selected_scheme"] = selected_scheme
    report["mean_charges_original"] = float(data["charges"].mean())
    report["mean_charges_published"] = float(published["charges"].mean())
    report["smoker_rate_original"] = float((data["smoker"] == "yes").mean())
    report["smoker_rate_published"] = float((published["smoker"] == "yes").mean())

    published_columns = quasi_identifiers + ["smoker", "charges"]
    submission_dir = Path("submission")
    submission_dir.mkdir(parents=True, exist_ok=True)
    (submission_dir / "privacy_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    published[published_columns].to_csv(
        submission_dir / "insurance_published.csv",
        index=False,
    )

    return report
