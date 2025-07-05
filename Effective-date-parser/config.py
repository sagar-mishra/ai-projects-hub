import os

root_dir = r"E:\data\effective_date_parser\train"
contracts_dir = os.path.join(root_dir,"full_contract_txt")
train_file = os.path.join(root_dir,"train.csv")
pred_file = os.path.join(root_dir,"prediction.csv")
processed_train_file = os.path.join(root_dir,"processed_train.json")
processed_eval_file = os.path.join(root_dir,"processed_eval.json")
processed_pred_file = os.path.join(root_dir, "processed_test.json")
file_id_csv = os.path.join(root_dir,"file_id.csv")
test_result_json_file = os.path.join(root_dir,"test_results.json")
test_probab_json_file = os.path.join(root_dir,"test_prob.json")
final_prediction_csv = os.path.join(root_dir, "final_prediction.csv")
model_type="bert"
model_name= "bert-base-cased"
output_dir_path = os.path.join(root_dir,model_type)
best_model_dir_path = os.path.join(output_dir_path,"best_model")
