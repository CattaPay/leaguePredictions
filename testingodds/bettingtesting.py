
import pandas as pd
import numpy as np
import xgboost as xgb

betting_data = pd.read_csv("testingodds/lckodds_spring2024.csv")

# print(betting_data)

# prediction_data = pd.read_csv("testingodds/lck_2023_5-5.csv").set_index("Match_Number", drop = True)
# prediction_data = pd.read_csv("testSplits/lck_spring_2024.csv").set_index("Match_Number", drop = True)
prediction_data = pd.read_csv("testSplits/lck_summer_test.csv").set_index("Match_Number", drop = True)


# print(prediction_data)

bst = xgb.Booster()
# bst.load_model("models/full_5-5.json")
bst.load_model("models/7_5nominortwoyears.json")

blue_cols = []
red_cols = []
for col in prediction_data.columns:
    blue_cols.append("B_" + col)
    red_cols.append("R_" + col)

all_predictions = pd.DataFrame()
match_numbers = [99]
for ind in np.unique(match_numbers):
    match_data = prediction_data.loc[ind]
    bluevsred = pd.DataFrame(pd.concat([match_data.iloc[0].reset_index(drop = True), match_data.iloc[1].reset_index(drop = True)], axis = 0)).T
    redvsblue = pd.DataFrame(pd.concat([match_data.iloc[1].reset_index(drop = True), match_data.iloc[0].reset_index(drop = True)], axis = 0)).T

    match_stack = pd.concat([bluevsred, redvsblue])
    match_stack.columns = blue_cols + red_cols
    
    # remove meaningless columns
    match_stack = match_stack.drop(["B_Side", "R_Side", "B_Winner", "R_Winner"], axis = 1)

    # set up for prediction
    match_test = match_stack.drop(["B_Tournament", "R_Tournament", "B_Team", "R_Team"], axis = 1).reset_index(drop = True).apply(pd.to_numeric, errors='ignore')
    # match_test = match_test.drop(["R_Top_Plates", "R_Mid_Plates", "R_Bot_Plates", "R_Plates", "B_Top_Plates", "B_Mid_Plates", "B_Bot_Plates", "B_Plates"], axis = 1)

    # print(match_test)
    dtest = xgb.DMatrix(data = match_test)
    scores = bst.predict(dtest)

    match_predictions = pd.DataFrame(data = [[match_data.iloc[0]["Tournament"], ind, match_data.iloc[0]["Team"], match_data.iloc[1]["Team"], scores[0], scores[1]]],
                                     columns = ["Tournament", "Match_Number", "Team1", "Team2", "Team1Blue", "Team2Blue"])
    all_predictions = pd.concat([all_predictions, match_predictions])

print(all_predictions)

# mathy way to predict series odds
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
    
def getEarnings(result, blue_odds, red_odds, correct, to_bet):
    if to_bet == 0:
        return 0
    if correct and to_bet == 1:
        if result == 1:
            return blue_odds - 1
        return red_odds - 1
    if not correct and to_bet == 1:
        return -1
    if correct and to_bet == -1:
        return -1
    if result == 1:
        return blue_odds - 1
    return red_odds - 1

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
    
# print(all_predictions)
betting_predictions = pd.merge(all_predictions, betting_data).drop(["Blue", "Red"], axis = 1)
betting_predictions["Best_Of"] = betting_predictions.apply(lambda row: max(row.Blue_Score, row.Red_Score) * 2 - 1, axis = 1)

# super simple... will make better later
# being made better
betting_predictions["Series_Prediction"] = betting_predictions.apply(lambda row: seriesOdds(row.Team1Blue, row.Team2Blue, row.Best_Of), axis = 1)
betting_predictions["Series_Result"] = betting_predictions.apply(lambda row: int(row.Blue_Score > row.Red_Score), axis = 1)

# print(betting_predictions.sort_values(by = "Series_Prediction" , ascending = False).dropna())


# boolean
threshold = 0.2
minodds = 1.2
betting_predictions["To_Bet"] = betting_predictions.apply(lambda row: abs(row.Series_Prediction - 0.5) > threshold and min(row.Blue_Odds, row.Red_Odds) > minodds, axis = 1)
# betting_predictions["To_Bet"] = 1
# if To_Bet == -1, it means bet on the team you think will lose
# betting_predictions["To_Bet"] = betting_predictions.apply(lambda row: betByOdds(row.Series_Prediction, row.Blue_Odds, row.Red_Odds, threshold = 0), axis = 1)


betting_predictions["Series_Correct"] = betting_predictions.apply(lambda row: abs(row.Series_Prediction - row.Series_Result) < 0.5, axis = 1)
betting_predictions["Earnings"] = betting_predictions.apply(lambda row: getEarnings(row.Series_Result, row.Blue_Odds, row.Red_Odds, row.Series_Correct, row.To_Bet), axis = 1)
betting_predictions["Bet_Wins"] = betting_predictions.apply(lambda row: row.To_Bet * row.Series_Correct, axis = 1)
betting_predictions["Bet_Losses"] = betting_predictions.apply(lambda row: row.To_Bet * (1-row.Series_Correct), axis = 1)


def getSummary(predictions):
    summary = predictions[["Tournament", "Series_Correct", "Earnings", "To_Bet", "Bet_Wins", "Bet_Losses"]].groupby("Tournament").sum()
    summary = pd.concat([summary, predictions[["Tournament", "Series_Correct", "Earnings"]].groupby("Tournament").mean()], axis = 1)
    summary = pd.concat([predictions[["Tournament", "Series_Correct"]].groupby("Tournament").count(), summary], axis = 1)
    summary.columns = ["NSeries", "Correct", "Total_Earnings", "Bets", "Bets_Won", "Bets_Lost", "Prediction_Rate", "Earnings_per_Game"]
    summary["Earnings_per_Bet"] = summary.apply(lambda row: row.Total_Earnings / row.Bets if row.Bets > 0 else 0, axis = 1)
    return summary
    # print(summary)


# print(betting_predictions.sort_values(by = "Earnings", ascending = False))
summary = getSummary(betting_predictions)


print(summary)

#print(all_predictions)
# summary.to_csv("modelresults/0.15_1.1final")


# print(betting_predictions[betting_predictions["To_Bet"] != 0][["Team1", "Team2", "Blue_Odds", "Red_Odds", "To_Bet", "Series_Prediction", "Earnings"]])