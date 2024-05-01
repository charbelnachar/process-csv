import argparse
import json
import os
from functools import reduce
from typing import Any
from typing import Dict

import pandas as pd

problems: Dict[str, Any] = {}

none: str = "none"
unique: str = "unique"
type: str = "type"
int_type: str = "int"
string_type: str = "string"
date_type: str = "date"
country_code_type: str = "country_code"


class ColumnNotFoundError(Exception):
    pass


def extract_data(file: str, delimiter: str) -> pd.DataFrame:
    """
    Extracts data from a CSV file and sets custom indices.

    Parameters:
    file (str): The path to the CSV file.
    delimiter (str): The delimiter used in the CSV file.

    Returns:
    DataFrame: The DataFrame containing the extracted data.

    Raises:
    FileNotFoundError: If the file does not exist.
    pd.errors.ParserError: If there is an error reading the file.
    """
    try:
        df = pd.read_csv(file, delimiter=delimiter)
        df.index = df.index + 2
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file} was not found.")
    except pd.errors.ParserError:
        raise pd.errors.ParserError(f"There was an error reading the file {file}.")


def extract_json_config(file: str) -> dict:
    """
    Extracts data from a JSON file.

    Parameters:
    file (str): The path to the JSON file.

    Returns:
    dict: The dictionary containing the extracted data.

    Raises:
    FileNotFoundError: If the file does not exist.
    json.JSONDecodeError: If there is an error decoding the JSON.
    """
    try:
        with open(file, 'r') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file} was not found.")
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError("There was an error decoding the JSON in the file.", e.doc, e.pos)


def set_percentage_error(field: str, error: str) -> None:
    """
    Sets the percentage error for a field in the problem's dictionary.

    Parameters:
    field (str): The field name.
    error (str): The error message.
    """
    problems[field] = error


def validate_unique_fields(df: pd.DataFrame, field: str) -> pd.DataFrame:
    """
    Validates the uniqueness of values in a field.

    Parameters:
    df (DataFrame): The DataFrame to validate.
    field (str): The field name to validate.

    Returns:
    DataFrame: A DataFrame containing information about repeated values.
    """

    # Get a boolean mask of duplicated values
    duplicates_mask = df[field].duplicated(keep=False)
    percentage: float = 0

    if duplicates_mask.any():
        # Create a DataFrame with indices of duplicated values
        duplicated_indices = df[duplicates_mask].reset_index()

        # Group by value and get a list of indices for each repeated value
        grouped_indices = duplicated_indices.groupby(field)['index'].apply(list)

        # Create a new DataFrame with necessary columns
        new_df = grouped_indices.reset_index()
        new_df.columns = ["Repeat_" + field, 'repeated_indexes']
        new_df['index'] = new_df['repeated_indexes'].apply(lambda x: x.pop(0))

        # Rearrange columns in specified order
        new_df = new_df[['index', "Repeat_" + field, 'repeated_indexes']]

        percentage = round(duplicates_mask.mean() * 100, 4)
    else:
        new_df = pd.DataFrame(columns=['index', "Repeat_" + field, 'repeated_indexes'])

    set_percentage_error(field, f"Error_rate: {percentage}%")
    return new_df


def validate_string_fields(df: pd.DataFrame, field: str) -> pd.DataFrame:
    """
    Validates if the values in a field are not strings.

    Parameters:
    df (DataFrame): The DataFrame to validate.
    field (str): The field name to validate.

    Returns:
    DataFrame: A DataFrame containing information about non-string values.
    """
    percentage: float = 0
    non_string_mask = df[field].apply(lambda x: not isinstance(x, str) and not pd.isnull(x))

    if non_string_mask.any():

        # none_indices = non_string_mask[non_string_mask].index

        # Create a new DataFrame
        new_df = pd.DataFrame({
            'index': df.index[non_string_mask],
            f'NULL_{field}_STRING': True
        })

        new_df.set_index('index')

        percentage = round(non_string_mask.mean() * 100, 4)
        set_percentage_error(field, f"Error_rate: {percentage}%")
    else:
        return pd.DataFrame(columns=["index", f'NULL_{field}_STRING'])

    return new_df


def validate_int_fields(df: pd.DataFrame, field: str) -> pd.DataFrame:
    """
    Validates if the values in a field are integers.

    Parameters:
    df (DataFrame): The DataFrame to validate.
    field (str): The field name to validate.

    Returns:
    DataFrame: A DataFrame containing information about non-integer values.
    """
    percentage: float = 0
    non_null_int_mask = df[field].apply(lambda x: not (isinstance(x, int) or isinstance(x, float)) and not pd.isnull(x))

    if non_null_int_mask.any():

        # none_indices = non_string_mask[non_string_mask].index.tolist()

        # Create a new DataFrame

        new_df = pd.DataFrame({
            'index': df.index[non_null_int_mask],
            f'NULL_{field}_INT': True
        })

        new_df.set_index('index')

        percentage = round(non_null_int_mask.mean() * 100, 4)
        set_percentage_error(field, f"Error_rate: {percentage}%")
    else:
        return pd.DataFrame(columns=["index", f'NULL_{field}_INT'])

    return new_df


def validate_none_fields(df: pd.DataFrame, field: str) -> pd.DataFrame:
    """
    Validates if the values in a field are None.

    Parameters:
    df (DataFrame): The DataFrame to validate.
    field (str): The field name to validate.

    Returns:
    DataFrame: A DataFrame containing information about None values.
    """
    percentage: float = 0
    none_mask = df[field].isnull()

    if none_mask.any():

        new_df = pd.DataFrame({
            'index': df.index[none_mask],
            f'NONE_{field}_VALUE': True
        })

        new_df = new_df.set_index('index')

        percentage = round(none_mask.mean() * 100, 4)
    else:
        new_df = pd.DataFrame(columns=["index", f'NONE_{field}_VALUE'])

    set_percentage_error(field, f"Error_rate: {percentage}%")

    return new_df


def validate_date_format(df: pd.DataFrame, field: str) -> pd.DataFrame:
    """
    Validates if the values in a date field have a specific format.

    Parameters:
    df (DataFrame): The DataFrame to validate.
    field (str): The field name to validate.

    Returns:
    DataFrame: A DataFrame containing information about invalid date formats.
    """
    formato_deseado: str = '%Y-%m-%d %H:%M:%S'
    percentage: float = 0

    invalid_format_mask = pd.to_datetime(df[field], format=formato_deseado, errors='coerce').isna()

    if invalid_format_mask.any():
        # invalid_indices = invalid_format_mask[invalid_format_mask].index

        # Create a new DataFrame
        new_df = pd.DataFrame({
            'index': df.index[invalid_format_mask],
            f'INVALID_{field}_FORMAT': True
        })

        new_df = new_df.set_index('index')

    else:
        return pd.DataFrame(columns=["index", f'INVALID_{field}_FORMAT'])

    return new_df


def validate_country_codes(df: pd.DataFrame, field: str) -> pd.DataFrame:
    """
    Validates if the values in a field are present in the provided list of country codes.

    Parameters:
    df (DataFrame): The DataFrame to validate.
    field (str): The field name to validate.


    Returns:
    DataFrame: A DataFrame containing information about non-matching values.
    """
    country_list = ["AR", "BR", "CL", "CO", "CR", "CU", "DO", "EC", "SV", "GT", "HT", "HN", "JM", "MX", "NI", "PA",
                    "PY", "PE", "PR", "UY", "VE"]

    non_matching_values = df.loc[~df[field].isin(country_list) & df[field].notnull()]

    if not non_matching_values.empty:
        new_df = pd.DataFrame({
            'index': df.index[non_matching_values],
            f'NOT_IN_{field}_LIST': True
        })

        percentage = len(non_matching_values) / len(df) * 100
        set_percentage_error(field, f"Error_rate: {percentage}%")

        return new_df
    else:
        return pd.DataFrame(columns=["index", f'NOT_IN_{field}_LIST'])


def calculate_percentage_error(original: pd.DataFrame, merge: pd.DataFrame) -> str:
    """
    Calculates the percentage error between two DataFrames.

    Parameters:
    original (DataFrame): The original DataFrame.
    merge (DataFrame): The merged DataFrame.

    Returns:
    str: The percentage error as a string.
    """
    len_ori = len(original)
    len_merge = len(merge)
    if len_ori == len_merge:
        return "0%"
    elif len_ori == 0:
        return "0%"
    else:
        return f'{round(((len_ori - len_merge) / len_ori) * 100, 4)}%'


def validate_field_dic(df: pd.DataFrame, field: str, validations: dict) -> list:
    """
    Validates a DataFrame field based on rules in a dictionary.

    Parameters:
    df (pandas.DataFrame): DataFrame to validate.
    field (str): Field to validate.
    validations (dict): Validation rules.

    Returns:
    list: List of DataFrames with validation results.

    Raises:
    ColumnNotFoundError: If the DataFrame does not have the expected columns.

    """
    list_df = []
    try:
        if none in validations and validations[none]:
            list_df.append(validate_none_fields(df, field))
        if unique in validations and validations[unique]:
            list_df.append(validate_unique_fields(df, field))
        if type in validations:
            if validations[type] == int_type:
                list_df.append(validate_int_fields(df, field))
            if validations[type] == string_type:
                list_df.append(validate_string_fields(df, field))
            if validations[type] == date_type:
                list_df.append(validate_date_format(df, field))
            if validations[type] == country_code_type:
                list_df.append(validate_country_codes(df, field))
    except KeyError:
        raise ColumnNotFoundError(f"The DataFrame does not have the expected column: {field}")
    return list_df


def validate_fields_from_json(df: pd.DataFrame, data_config: dict) -> pd.DataFrame:
    """
    Validates the fields of a DataFrame based on the rules specified in a JSON configuration.

    Parameters:
    df (pandas.DataFrame): The DataFrame to validate.
    data_config (dict): The JSON configuration containing the validation rules.
                        The keys are the field names and the values are dictionaries specifying the validations for
                        each field.

    Returns:
    pandas.DataFrame: A DataFrame containing the validation results. Each row corresponds to a validation error,
                      and the columns correspond to the fields of the original DataFrame.
    """
    list_df = []
    # Iterate over each field in the dictionary and perform the corresponding validations
    for field, validations in data_config["data_valid"].items():
        list_df.extend(validate_field_dic(df, field, validations))

    if list_df:
        merged_df = reduce(lambda left, right: pd.merge(left, right, on=['index'], how='outer'), list_df)
    else:
        merged_df = pd.DataFrame()

    merged_df.columns = merged_df.columns.str.upper()
    return merged_df


def verify_columns(df, expected_columns):
    """
    Verifies that the columns of a DataFrame include a list of expected columns.

    Parameters:
    df (pandas.DataFrame): The DataFrame to check.
    expected_columns (list of str): The list of expected column names.

    Raises:
    ValueError: If the DataFrame does not have the expected columns.
    """
    actual_columns = set(df.columns.tolist())
    if not set(expected_columns).issubset(actual_columns):
        missing_columns = set(expected_columns) - actual_columns
        raise ValueError(
            f"The DataFrame does not have all the expected columns. Missing columns: {missing_columns}")


def save_rejected_data(data: pd.DataFrame, rejected_file: str) -> None:
    """
    Saves rejected data to a CSV file.

    Parameters:
    data (DataFrame): The rejected data.
    rejected_file (str): The path to the CSV file to save the rejected data.
    """
    data.to_csv(rejected_file, index=False)


def main():
    try:
        file_json = '/data_config.json'
        parser = argparse.ArgumentParser(description="Proce sa la ruta.")

        parser.add_argument("--route", type=str, default=os.getcwd() + file_json, help="La ruta a los archivos.")

        args = parser.parse_args()
        route_json_conf = args.route

        print(f'Extracting configuration from {route_json_conf}...')
        dic = extract_json_config(route_json_conf)
        file = dic.get("route_file")

        delimiter = dic.get("delimiter")
        rejected_file = file.replace('.csv', '') + "_rejected_records.csv"

        print(f'Extracting data from {file}...')
        df = extract_data(file, delimiter)

        print("Validating fields...")

        data_out = validate_fields_from_json(df, dic)

        print(f'percentage of life of the file {calculate_percentage_error(df, data_out)}')
        print(f"Saving rejected records to '{rejected_file}':")
        save_rejected_data(data_out, rejected_file)

        print("Process completed.")

    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
    except pd.errors.ParserError as e:
        print(f"ParserError: {e}")
    except ValueError as e:
        print(f"ValueError: {e}")
    except FileNotFoundError as e:
        print(f"FileNotFoundError: {e}")
    except ColumnNotFoundError as e:
        print(e)
    except KeyError as e:
        print(f"KeyError: {e}")


if __name__ == "__main__":
    main()
