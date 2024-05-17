
import pandas as pd
import os

folder = "rollinginputs"

all_seasons = os.listdir(folder)
test_seasons = ["lck_2023", "lcs_2024", "lcs_2023", "lec_2023", "lec_2024", "ljl_2023", "nacl_2023", "pcs_2023", "vcs_2023", "lckcl_2023"]
non_major = ["lckcl_2022", "lckcl_2021", "ljl_2022", "ljl_2021", "ljl_2020", "ljl_2019", "nacl_2022", "nacl_2021", "nacl_2020", "nacl_2019", "pcs_2022", "pcs_2021", "pcs_2020", "vcs_2022", "vcs_2021", "vcs_2020", "vcs_2019"]
bestofone = ["lcs_2022", "lcs_2021", "lcs_2020", "lcs_2019", "lec_2022", "lec_2021", "lec_2020", "lec_2019", "lckcl_2021"]
prevtwoyears = ["lck_2020", "lck_2019", "lcs_2020", "lcs_2019", "lec_2020", "lec_2019", "ljl_2020", "ljl_2019", "nacl_2020", "nacl_2019", "vcs_2020", "pcs_2020", "vcs_2019"]
bad_regions = ["ljl_2022", "ljl_2021", "ljl_2020", "ljl_2019", "pcs_2022", "pcs_2021", "pcs_2020", "vcs_2022", "vcs_2021", "vcs_2020", "vcs_2019"]
challengers = ["lckcl_2022", "lckcl_2021", "nacl_2022", "nacl_2021", "nacl_2020", "nacl_2019"]
america = ["nacl_2022", "nacl_2021", "nacl_2020", "nacl_2019", "lcs_2022", "lcs_2021", "lcs_2020", "lcs_2019"]

bad_guessers = prevtwoyears + ["ljl_2022", "ljl_2021", "vcs_2022", "vcs_2021", "pcs_2021", "pcs_2022"]

empty = []

drop_from_test = ["ljl_2023", "nacl_2023", "pcs_2023", "vcs_2023", "lckcl_2023", "lcs_2023", "lec_2023", "lcs_2024", "lec_2024"]


training_seasons = all_seasons
for season in test_seasons:
    training_seasons.remove(season + ".csv")

for season in bad_guessers:
    # print(season)
    training_seasons.remove(season + ".csv")


training_dataset = pd.DataFrame()
for season in training_seasons:
    fpath = folder + "/" + season
    new_data = pd.read_csv(fpath)
    new_data["Season"] = season[:-4]

    training_dataset = pd.concat([training_dataset, new_data])
    print(season, training_dataset.shape)

training_dataset.to_csv("combineddata/training.csv", index = False)

test_dataset = pd.DataFrame()

for season in drop_from_test:
    test_seasons.remove(season)

for season in test_seasons:
    fpath = folder + "/" + season + ".csv"
    new_data = pd.read_csv(fpath)
    new_data["Season"] = season
    test_dataset = pd.concat([test_dataset, new_data])
    print(season, test_dataset.shape)

test_dataset.to_csv("combineddata/test.csv", index = False)

