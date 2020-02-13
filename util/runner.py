import sys
from pathlib import Path
sys.path.append(str(Path('./CHARTextract/RegexNLP-py/')))
from __main_simple__ import run_variable

# Fix stdout redirection due to CHARTextract
sys.stdout = sys.__stdout__
sys.stderr = sys.__stderr__

import json
import pandas as pd

def main(args):
    rules_folder = Path(args.rules)
    rules = list(rules_folder.glob('*'))

    # run all rules in Rules Folder
    for rule in rules:
        rule_name = rule.stem
        # flag to determine whether to run rules in advanced mode
        # i.e. rules that have .json files other than rule_properties or rule_settings
        mode = len(
            list(filter(lambda x: x.stem not in ('rule_properties', 'rule_settings'), rule.glob('*.json')))
            ) > 0
        mode_str = 'advanced' if mode else 'simple'
        run_variable(rule_name, './project_settings.json', mode=mode_str)

    # gather predictions into a single CSV
    df_predictions = pd.DataFrame()
    generated_data = Path('./generated_data/')
    reports = list(generated_data.glob('**/error_report.json'))

    for report in reports:
        with open(report) as f:
            report_json = json.load(f)

        predictions = {}
        for pid, case in report_json["patient_cases"].items():
            predictions[int(pid)] = case["pred"]

        df_predictions = pd.concat([df_predictions, pd.Series(predictions, name=report.parts[1])], axis=1)

    df_predictions.index.name = 'Patient ID'
    df_predictions.to_csv('./predictions.csv')
    print(df_predictions.head())

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--rules', help='Path to rules folder', required=True)

    args = parser.parse_args()
    main(args)