
import pandas as pd
import numpy as np

# converts data rollingwindow data into matches to allow for betting odds data entry

match_data = pd.read_csv("testSplits/lck_spring_2024.csv")

match_data = match_data.set_index(["Match_Number"], drop = True)

all_matches = pd.DataFrame()

for ind in np.unique(match_data.index):
    series_data = match_data.loc[ind].reset_index()[["Tournament", "Match_Number", "Team", "Side", "Winner"]]
    tournament = series_data.iloc[0]["Tournament"]
    match_number = series_data.iloc[0]["Match_Number"]
    blueteam = series_data.iloc[0]["Team"]
    redteam = series_data.iloc[1]["Team"]
    bluescore = int(series_data[series_data["Team"] == blueteam]["Winner"].sum())
    redscore = int(series_data[series_data["Team"] == redteam]["Winner"].sum())
    # print(series_data)

    match = pd.DataFrame(data = [[tournament, match_number, blueteam, redteam, bluescore, redscore]],
                         columns = ["Tournament", "Match_Number", "Blue", "Red", "Blue_Score", "Red_Score"])    

    all_matches = pd.concat([all_matches, match])
    # gamedat = match_data.loc[ind].head(2).reset_index()[["Tournament", "Match_Number", "Team", "Side", "Winner"]]

all_matches.sort_values(by = "Match_Number", ascending = False).to_csv("testingodds/bettingsetup.csv", index = False)
