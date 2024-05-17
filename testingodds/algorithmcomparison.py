
import os
import pandas as pd

# model_files = os.listdir("modelresults")
# all_models = pd.DataFrame()
# for i in range(27):
#     this_model = pd.read_csv("modelresults/" + model_files[i])[["Total_Earnings", "Bets", "Bets_Won", "Bets_Lost", "NSeries", "Correct"]].sum().to_frame().T
#     model_specs = model_files[i].split("_")

#     model_info = pd.DataFrame(data = [[model_specs[0] + model_specs[1] + model_specs[2], model_specs[3], model_specs[4]]], columns = ["Model_Name", "Threshold", "Min_Odds"])
  

#     this_model = pd.concat([model_info, this_model], axis = 1)
#     # print(this_model)
#     all_models = pd.concat([all_models, this_model], axis = 0)

# all_models["Bet_Accuracy"] = all_models.apply(lambda row: row.Bets_Won / row.Bets if row.Bets != 0 else 0, axis = 1)

# # print(all_models)
# # all_models.to_csv("testingodds/Model_Summaries.csv")

# summary = all_models.drop(["Model_Name", "Bet_Accuracy"], axis = 1).groupby(["Threshold", "Min_Odds"]).sum()
# summary["Bet_Accuracy"] = summary.apply(lambda row: row.Bets_Won / row.Bets if row.Bets != 0 else 0, axis = 1)
# print(summary)

# summary.to_csv("testingodds/Model_Summaries.csv")


model_files = os.listdir("modelresults")[0:3]
print(model_files)

all_models = pd.DataFrame()

for i in range(3):
    this_model = pd.read_csv("modelresults/" + model_files[i])[["Total_Earnings", "Bets", "Bets_Won", "Bets_Lost", "NSeries", "Correct"]].sum().to_frame().T
    model_specs = model_files[i].split("_")

    model_info = pd.DataFrame(data = [[model_specs]], columns = ["Name"])
  

    this_model = pd.concat([model_info, this_model], axis = 1)
    # print(this_model)
    all_models = pd.concat([all_models, this_model], axis = 0)

print(all_models)
all_models.to_csv("testingodds/final_summaries")