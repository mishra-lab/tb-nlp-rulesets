import sys
from pathlib import Path
sys.path.append(str(Path('./CHARTextract/RegexNLP-py/')))
from __main_simple__ import run_variable

# Fix stdout redirection due to CHARTextract
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

import json
import pandas as pd

def save_results(df, location, version=1):
    """
    Try to save results at location; if file exists, append incremental
    integer to location file name until we can save

    df:         Pandas dataframe containing results
    location:   pathlib object to output file location
    """

    try:
        df.to_csv(str(location))
    except PermissionError as err:
        stem = location.stem
        new_location = location.parent / (stem + str(version) + '.csv') 

        save_results(df, new_location, version + 1)


def main(args):
    with open(Path(args.settings)) as f:
    	project_settings = json.load(f)
        
    rules_folder = Path(*project_settings['Rules Folder'])
    rules = list(rules_folder.glob('*'))

    # run all rules in Rules Folder
    for rule in rules:
        rule_name = rule.stem
        # flag to determine whether to run rules in simple mode
        # i.e. rules that have .json files other than rule_properties or rule_settings
        mode = len(
            list(filter(lambda x: x.stem not in ('rule_properties', 'rule_settings'), rule.glob('*.json')))
            ) > 0
        mode_str = 'simple' if mode else 'advanced'
        print(f"Running rule {rule_name} using {mode_str} mode")
        run_variable(rule_name, args.settings, mode=mode_str)

    # gather predictions into a single CSV
    df_predictions = pd.DataFrame()
    generated_data = Path('./generated_data/')
    reports = list(generated_data.glob('**/error_report.json'))

    for report in reports:
        with open(report) as f:
            report_json = json.load(f)

        predictions = {}
        for pid, case in report_json["patient_cases"].items():
            predictions[pid] = case["pred"]

        df_predictions = pd.concat([df_predictions, pd.Series(predictions, name=report.parts[1])], axis=1)

    # save to output folder
    df_predictions.index.name = 'Patient ID'
    output_path = Path(args.output)
    save_results(df_predictions, output_path)
    print(df_predictions.head())

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--settings', help='Path to project settings file', default='./project_settings.json')
    parser.add_argument('--output', help='Path to output file', default='./predictions.csv')

    args = parser.parse_args()
    main(args)