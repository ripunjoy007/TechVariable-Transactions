import pandas as pd


# Read CSV using pandas and returing List of objects as per column name. Header columns are required
def process_uploaded_file(filepath):
    try:
        with open(filepath, 'r') as file:
            reader = pd.read_csv(file, squeeze=True)
            items = reader.to_dict(orient='records')

            if len(items) > 0:
                print(items[0].keys())
                if list(items[0].keys()) != ['Transaction Name', 'Product Name', 'Quantity', 'Unit Price',
                                             'Delivered to city']:
                    raise Exception('Columns mismatch in input CSV file')

            return items
    except Exception as e:
        raise e

