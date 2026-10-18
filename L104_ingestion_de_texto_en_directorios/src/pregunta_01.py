import os
import pandas as pd

def pregunta_01():
    """
    Las frases de este laboratorio no están en una tabla, sino en miles de
    archivos de texto organizados en carpetas. Dentro de `data/` hay dos
    carpetas, `train/` y `test/`, y cada una contiene las carpetas
    `negative/`, `neutral/` y `positive/`. Cada archivo `.txt` contiene una
    frase, y la carpeta donde se encuentra indica su sentimiento.

    Su tarea es construir un dataset para cada división y guardarlo en:

    - `submission/train_dataset.csv`
    - `submission/test_dataset.csv`

    Cada archivo debe tener dos columnas: `phrase`, con el texto de la frase,
    y `target`, con el nombre de la carpeta de sentimiento (`negative`,
    `neutral` o `positive`). Recorra las carpetas y los archivos en orden
    alfabético, de modo que el resultado sea siempre el mismo. No guarde el
    índice de Pandas en el CSV.

    Ejemplo del formato de cada archivo:

        phrase,target
        "The real estate company posted a net loss ...",negative
        ...
        "Cardona slowed her vehicle , turned around ...",neutral
        ...
    """
    # Definir las rutas de los directorios de entrenamiento y prueba
    train_dir = 'data/train'
    test_dir = 'data/test'

    # Crear listas para almacenar las frases y los objetivos
    train_phrases = []
    train_targets = []
    test_phrases = []
    test_targets = []

    # Función para procesar un directorio y llenar las listas correspondientes
    def process_directory(base_dir, phrases_list, targets_list):
        for sentiment in sorted(os.listdir(base_dir)):
            sentiment_dir = os.path.join(base_dir, sentiment)
            if os.path.isdir(sentiment_dir):
                for filename in sorted(os.listdir(sentiment_dir)):
                    if filename.endswith('.txt'):
                        file_path = os.path.join(sentiment_dir, filename)
                        with open(file_path, 'r', encoding='utf-8') as file:
                            phrase = file.read().strip()
                            phrases_list.append(phrase)
                            targets_list.append(sentiment)

    # Procesar los directorios de entrenamiento y prueba
    process_directory(train_dir, train_phrases, train_targets)
    process_directory(test_dir, test_phrases, test_targets)

    # Crear DataFrames de Pandas
    train_df = pd.DataFrame({'phrase': train_phrases, 'target': train_targets})
    test_df = pd.DataFrame({'phrase': test_phrases, 'target': test_targets})

    # Guardar los DataFrames en archivos CSV sin índice
    os.makedirs('submission', exist_ok=True)
    train_df.to_csv('submission/train_dataset.csv', index=False)
    test_df.to_csv('submission/test_dataset.csv', index=False)