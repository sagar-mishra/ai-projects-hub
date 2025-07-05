import sys
sys.path.insert(0, r"E:\projects\effective_date_parser")

import os
import json
import config
import pandas as pd
import numpy as np
from dateutil.parser import parse


def load_files():
    """
    function to load test file, probability file and file dataframe
    """
    with open(config.test_result_json_file, 'r') as f:
        data = json.load(f)
    with open(config.test_probab_json_file, 'r') as f:
        data_prob = json.load(f)

    file_df = pd.read_csv(config.file_id_csv)

    return data, data_prob, file_df

def get_prob(probs, id_):
    for prob in probs:
        if prob.get('id') == id_:
            return prob.get('probability')


def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False


def post_process(data, data_prob, file_df):
    final_results = []
    for d in data:
        answer = d['answer']
        id_ = d['id']

        probs = get_prob(data_prob, id_)

        selective_answers, selective_prob = [], []

        for index, ans in enumerate(answer):
            try :
                if is_date(ans):
                    selective_answers.append(ans)
                    selective_prob.append(probs[index])
            except:
                pass
        
        f_date = ''
        if len(selective_prob) > 0:
            max_idx = np.argmax(selective_prob)

            predicted_answer = selective_answers[max_idx]
            parsed_date = parse(predicted_answer)
            f_date = parsed_date.strftime('%d/%m/%Y')

        final_results.append([file_df[file_df.id == id_]['file_name'].values[0], f_date])   

    
    return final_results


def persist_predictions(final_results):
    """
    function to persist predictions into dataframe
    final_results : list of lists(file_name, date)
    """
    output_dir = os.path.join(config.root_dir, "output")

    if not os.path.exists(output_dir):
        os.mkdir(output_dir)

    pd.DataFrame(final_results, columns=[['file','value']]).to_csv(os.path.join(output_dir,"model_prediction.csv"), index= False)

if __name__ == "__main__":

    data, data_prob, file_df = load_files()
    final_prediction_list = post_process(data, data_prob, file_df)
    persist_predictions(final_prediction_list)    
