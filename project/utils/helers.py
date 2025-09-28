import csv
import logging
import pandas as pd 


logger = logging.getLogger(__name__)


def get_input_values(input_df:pd.DataFrame):
    filtered_df = input_df[input_df['Run'] == 1]
    return filtered_df

def generate_csv(data, filename):
    if not data:
        raise ValueError("Data is empty. There is nothing to write to the CSV file.")

    headers = data[0].keys()

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=headers)

        writer.writeheader()

        writer.writerows(data)

    print(f"Data successfully written to {filename}",flush=True)
    logger.info(f"Data successfully written to {filename}")