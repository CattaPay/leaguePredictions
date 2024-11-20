import pandas as pd
import numpy as np
import xgboost as xgb

# defining betting related functions
def seriesOdds(team1Blue, team2Blue, best_of):
    if best_of == 1:
        return max(team1Blue, team2Blue)
    if best_of == 3:
        a = max(team1Blue, 1-team2Blue)
        b = max(1-team1Blue, team2Blue)
        return a * (1-b) + a * a * b + a * (1-a) * (1-b)
    if best_of == 5:
        a = max(team1Blue, 1-team2Blue)
        b = max(1-team1Blue, team2Blue)
        p1 = a * (1-b) * (1-b)
        p2 = 2*a*a*b*(1-b) + a*(1-a)*(1-b)*(1-b)
        p3 = a*a*a*b*b + 4*a*a*b*(1-a)*(1-b) + a*(1-a)*(1-a)*(1-b)*(1-b)
        return p1 + p2 + p3

def betByOdds(predictions, blue_odds, red_odds, threshold = 0):
    blue_threshold = 1 / blue_odds
    red_threshold = 1 / red_odds
    if blue_threshold > 0.5:
        if predictions > blue_threshold + threshold:
            return 1
        if (1-predictions) < red_threshold - threshold:
            return -1
        return 0
    else:
        if predictions > red_threshold + threshold:
            return 1
        if (1-predictions) < blue_threshold - threshold:
            return -1
        return 0

def oddsConverter(odds):
    if odds < 0:
        return (100 - odds) / -odds
    else:
        return (100 + odds) / 100

bst = xgb.Booster()
bst.load_model("models/7_5nominortwoyears.json")

prediction_data = pd.read_csv("testSplits/lck_summer_test.csv")

blue_cols = []
red_cols = []
for col in prediction_data.columns:
    blue_cols.append("B_" + col)
    red_cols.append("R_" + col)

# sets up for prediction with each team as blue and red
print()
match_numbers = [197, 198]
all_predictions = pd.DataFrame()
for match_number in match_numbers:
    match_data = prediction_data.loc[prediction_data["Match_Number"] == match_number]
    bluevsred = pd.DataFrame(pd.concat([match_data.iloc[0].reset_index(drop = True), match_data.iloc[1].reset_index(drop = True)], axis = 0)).T
    redvsblue = pd.DataFrame(pd.concat([match_data.iloc[1].reset_index(drop = True), match_data.iloc[0].reset_index(drop = True)], axis = 0)).T
    match_stack = pd.concat([bluevsred, redvsblue])
    match_stack.columns = blue_cols + red_cols

    # remove meaningless columns
    match_stack = match_stack.drop(["B_Side", "R_Side", "B_Winner", "R_Winner"], axis = 1)

    # set up for prediction
    match_test = match_stack.drop(["B_Tournament", "R_Tournament", "B_Team", "R_Team", "R_Match_Number", "B_Match_Number"], axis = 1).reset_index(drop = True).apply(pd.to_numeric, errors='ignore')

    dpredict = xgb.DMatrix(data = match_test)
    predictions = bst.predict(dpredict)

    prediction = seriesOdds(predictions[0], predictions[1], 5)
    # print(prediction, match_data.iloc[0]["Team"], match_data.iloc[1]["Team"])
    all_predictions = pd.concat([all_predictions, pd.DataFrame([match_data.iloc[0]["Team"], match_data.iloc[1]["Team"], prediction])], axis = 1)

all_predictions = all_predictions.T.reset_index(drop = True)
all_predictions.columns = ["Blue", "Red", "Prediction"]

all_predictions.to_csv("predictions/lck_summer_2024.csv", index = False)
print(all_predictions)