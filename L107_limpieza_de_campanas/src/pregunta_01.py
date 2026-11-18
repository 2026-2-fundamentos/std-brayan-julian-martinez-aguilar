from pathlib import Path

import pandas as pd

"""
Los datos de una campaña de mercadeo bancario llegaron repartidos en diez
archivos comprimidos, `data/bank-marketing-campaing-*.csv.gz`, con
información mezclada del cliente, de la campaña y del contexto económico.
Su tarea es leerlos directamente desde los archivos comprimidos, sin
descomprimirlos a mano, y separarlos en tres tablas limpias.

Guarde cada tabla como un CSV sin comprimir en `submission/`, sin el índice
de Pandas y con las columnas en el orden indicado:

1. `client.csv`: `client_id`, `age`, `job`, `marital`, `education`,
    `credit_default` y `mortgage`.
    - En `job`, elimine los puntos y cambie los guiones por guiones bajos.
    - En `education`, cambie los puntos por guiones bajos y deje el valor
      `unknown` como faltante.
    - En `credit_default` y `mortgage`, escriba 1 si el valor es `yes` y 0
      en cualquier otro caso.

2. `campaign.csv`: `client_id`, `number_contacts`, `contact_duration`,
    `previous_campaign_contacts`, `previous_outcome`, `campaign_outcome` y
    `last_contact_date`.
    - En `previous_outcome`, escriba 1 si el valor es `success` y 0 en
      cualquier otro caso.
    - En `campaign_outcome`, escriba 1 si el valor es `yes` y 0 en
      cualquier otro caso.
    - Construya `last_contact_date` a partir de las columnas `month` y
      `day`, usando el año 2022 y el formato `AAAA-MM-DD`.

3. `economics.csv`: `client_id`, `cons_price_idx` y
    `euribor_three_months`.

La función también debe retornar las tres tablas, en el orden `client`,
`campaign` y `economics`.

Ejemplo del formato de `campaign.csv`:

    client_id,number_contacts,contact_duration,...,last_contact_date
    0,1,261,...,2022-05-13
    ...
"""
def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
  # Leer los archivos comprimidos y concatenarlos en un solo DataFrame
  dataframes = []
  for i in range(10):
      df = pd.read_csv(f'data/bank-marketing-campaing-{i}.csv.gz', compression='gzip')
      dataframes.append(df)
  data = pd.concat(dataframes, ignore_index=True)

  # Crear la tabla client
  client = data[['client_id', 'age', 'job', 'marital', 'education', 'credit_default', 'mortgage']].copy()
  client['job'] = client['job'].str.replace('.', '', regex=False).str.replace('-', '_', regex=False)
  client['education'] = client['education'].replace('unknown', pd.NA).str.replace('.', '_', regex=False)
  client['credit_default'] = (client['credit_default'] == 'yes').astype(int)
  client['mortgage'] = (client['mortgage'] == 'yes').astype(int)

  # Crear la tabla campaign
  campaign = data[['client_id', 'number_contacts', 'contact_duration', 'previous_campaign_contacts', 'previous_outcome', 'campaign_outcome', 'month', 'day']].copy()
  campaign['previous_outcome'] = (campaign['previous_outcome'] == 'success').astype(int)
  campaign['campaign_outcome'] = (campaign['campaign_outcome'] == 'yes').astype(int)
  month_numbers = {
      'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4, 'may': 5, 'jun': 6,
      'jul': 7, 'aug': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12,
  }
  date_parts = pd.DataFrame({
      'year': 2022,
      'month': campaign['month'].map(month_numbers),
      'day': campaign['day'],
  })
  campaign['last_contact_date'] = pd.to_datetime(date_parts).dt.strftime('%Y-%m-%d')
  campaign.drop(columns=['month', 'day'], inplace=True)

  # Crear la tabla economics
  economics = data[['client_id', 'cons_price_idx', 'euribor_three_months']].copy()

  # Guardar las tablas como CSV sin comprimir
  Path('submission').mkdir(parents=True, exist_ok=True)
  client.to_csv('submission/client.csv', index=False)
  campaign.to_csv('submission/campaign.csv', index=False)
  economics.to_csv('submission/economics.csv', index=False)

  return client, campaign, economics


