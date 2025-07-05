import sys
sys.path.insert(0, r"E:\projects\effective_date_parser")

import os
import json
import pandas as pd
from pprint import pprint

import config


def create_train_data(train_df):
    """
    function to create train data according to questionanswermodel simple transformer
    """
    train_data = []

    question_id = 1
    question = "What is effective date?"
    for index, row in train_df.iterrows():
        try :
            file_name = row["file"]
            name, ext = os.path.splitext(file_name)
            txt_file = os.path.join(config.contracts_dir, name+".txt")
            possible_ans = eval(row["Start Date"])
            actual_ans = row["Start Date-Answer"]

            if len(possible_ans) > 0:
                possible_ans = possible_ans[0]
            else:
                possible_ans = ""

            data_dict = dict()
            
            with open(txt_file, encoding="utf8") as f:
                data = f.read()

                data_dict["context"] = data

                qas_dict = dict()
                qas_dict["question"] = question
                qas_dict["id"] = question_id
                question_id += 1
                
                answer_dict = dict()
                if possible_ans != '' and actual_ans != '':
                    if possible_ans in data:
                        answer_idx = data.find(possible_ans)
                        is_impossible = False
                        answer_dict = {
                            "text" : possible_ans,
                            "answer_start" : answer_idx
                        }
                    else:
                        is_impossible = True
                else:
                    is_impossible = True

                if is_impossible:
                    qas_dict["is_impossible"] = is_impossible
                    qas_dict["answers"] = []
                else:
                    qas_dict["is_impossible"] = is_impossible
                    qas_dict["answers"] = [answer_dict]

                data_dict["qas"] = [qas_dict]
            train_data.append(data_dict)
        except:
            pass

    return train_data

def create_test_data(pred_df):
    test_data = []
    question_id = 1
    question = "What is effective date?"
    file_idx = []
    for index, row in pred_df.iterrows():
        try:
            file_name = row["file"]
            file_idx.append([file_name, question_id])
            name, ext = os.path.splitext(file_name)
            txt_file = os.path.join(config.contracts_dir, name+".txt")

            data_dict = dict()
            
            with open(txt_file, encoding="utf8") as f:
                data = f.read()

                data_dict["context"] = data

                qas_dict = dict()
                qas_dict["question"] = question
                qas_dict["id"] = question_id
                question_id += 1

                data_dict["qas"] = [qas_dict]

            test_data.append(data_dict)
        except:
            pass

    return test_data, file_idx

def create_data():
    train_df = pd.read_csv(config.train_file)
    pred_df = pd.read_csv(config.pred_file)

    train_df.fillna('')
    train_size = int(train_df.shape[0]*0.9)

    temp_train_df = train_df[:train_size]
    temp_val_df = train_df[train_size:]

    train_data = create_train_data(temp_train_df)

    with open(config.processed_train_file,"w+") as f:
        json.dump(train_data,f)

    eval_data = create_train_data(temp_val_df)

    with open(config.processed_eval_file,"w+") as f:
        json.dump(eval_data,f)


    test_data, file_idx = create_test_data(pred_df)

    with open(config.processed_pred_file,"w+") as f:
        json.dump(test_data,f)

    pd.DataFrame(file_idx, columns=["file_name","id"]).to_csv(config.file_id_csv,index=False)


if __name__ == '__main__':
    create_data()


    

