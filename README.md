# README

## File Processor

This Python script processes a CSV file. It validates the data, identifies records with errors, and saves these records to a separate CSV file.

### Requirements

- Python 3.6 or higher
- pandas library

### Setup

Before running the script, you need to set up a virtual environment and install the necessary dependencies:

1. Create a virtual environment:

```bash
python3 -m venv venv
```

2. Activate the virtual environment:

On Unix or MacOS, run:

```bash
source venv/bin/activate
```

On Windows, run:

```bash
.\venv\Scripts\activate
```

3. Install the requirements from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### How to Run

1. Clone the repository to your local machine.
2. Navigate to the directory containing the script `file_processor.py`.
3. Run the script using Python and provide the path to the directory containing the JSON configuration file as a command-line argument. If no path is provided, the script will process the file `data_config.json` in the current directory.

```bash
python file_processor.py --route /path/to/your/directory
```

Replace `/path/to/your/directory` with the path to the directory containing your JSON configuration file.

### Output

The script will create a new CSV file in the same directory as the input file. This file will contain the records from the input file that failed the validation checks. The name of the output file will be the same as the input file, but with `_rejected_records.csv` appended to the end.

For example, if the input file is `03_EPG_EVENTOS.csv`, the output file will be `03_EPG_EVENTOS_rejected_records.csv`.

### Error Handling

The script will print an error message and stop execution if:

- The input file does not exist.
- The input file cannot be read.
- The input file does not contain all the expected columns.

### Validation Checks

The script performs the following validation checks on the data:

- Checks if the values in certain fields are unique.
- Checks if the values in certain fields are strings.
- Checks if the values in certain fields are integers.
- Checks if the values in certain fields are None.
- Checks if the values in a date field have a specific format.
- Checks if the values in a field are present in a provided list of country codes.

The script calculates the error percentage for each field and prints the result to the console.

### JSON Configuration File

The script requires a JSON configuration file to specify the validation rules for each field. In the `data_valid` object of the JSON configuration file, each key represents a field in the CSV file, and the value is another object that specifies the validation rules for that field. Here are the possible keys and their meanings:

- `"none"`: If set to `true`, the script checks that the field does not contain any None values.
- `"unique"`: If set to `true`, the script checks that all values in the field are unique.
- `"type"`: Specifies the expected data type of the field. The possible values are:
  - `"int"`: The script checks that all values in the field are integers.
  - `"string"`: The script checks that all values in the field are strings.
  - `"date"`: The script checks that all values in the field are dates in a specific format.
  - `"country_code"`: The script checks that all values in the field are present in a provided list of country codes.

Here is a simple example of the structure of the JSON configuration file:

```json
{
  "route_file": "name.csv",
  "delimiter": ",",
  "data_valid": {
    "ID": {
      "none": true,
      "unique": true,
      "type": "int"
    },
    "NOMBRE": {
      "none": true,
      "type": "string"
    },
    "FECHA": {
      "none": true,
      "type": "date"
    },
    "PAIS": {
      "none": true,
      "type": "country_code"
    }
  }
}
```

In this example, `route_file` specifies the name of the CSV file to process, `delimiter` specifies the delimiter used in the CSV file, and the `data_valid` object specifies the validation rules for each field. For example, the `ID` field should not contain any None values (`"none": true`), should contain unique values (`"unique": true`), and should contain integer values (`"type": "int"`). The `NOMBRE` field should not contain any None values and should contain string values. The `FECHA` field should not contain any None values and should contain date values. The `PAIS` field should not contain any None values and should contain values present in a provided list of country codes.