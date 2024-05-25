
import pandas as pd
import numpy as np

# WINDOW_SIZE = 8
WINDOW_SIZE = 7 # size of scrolling window (measured in games, should fix so it's matches)
MIN_DATA = 5 # lower bound for number of matches played in window size
PLAYER_COLS = ["Player", "Role", "Kills", "Deaths", "Assists", "CS", "CSM", "GPM", "VSPM", "DPM", "KAPM", "GD15", "CSD15", "XPD15"]

bigbox = [[] for _ in range(5)]
for col in PLAYER_COLS[2:]:
    bigbox[0].append("TOP_" + col)
    bigbox[1].append("JNG_" + col)
    bigbox[2].append("MID_" + col)
    bigbox[3].append("BOT_" + col)
    bigbox[4].append("SUP_" + col)

wide_colnames = []
for chunk in bigbox:
    wide_colnames += chunk

def getGameTimeS(game_time):
        if isinstance(game_time, float):
            return 0
        s = game_time.split(":")
        return int(s[0]) * 60 + int(s[1])

# removes the k from gold
def getGoldAsFloat(gold):
    if type(gold) == float:
        return gold
    return float(gold[:-1])


def getTeamSummaries(team_data, match_number):
    good = True
    match_data = team_data[team_data["Match_Number"] == match_number]
    teams = list(match_data["Team"])
    team_summaries = pd.DataFrame()
    for team in teams:
        previous_team_data = team_data[(team_data["Match_Number"] < match_number) & (team_data["Team"] == team)]
        #print(previous_team_data)
        # looking at last n matches instead of games
        prev_matches = previous_team_data["Match_Number"].unique()
        if len(prev_matches) < WINDOW_SIZE:
            first_match = 0
        else:
            first_match = prev_matches[WINDOW_SIZE-1]
        

        previous_team_data = previous_team_data[previous_team_data["Match_Number"] >= first_match].drop(labels = ["Tournament", "Date", "Game_Number"], axis = 1)

        # print(previous_team_data)
        if len(prev_matches) < MIN_DATA:
            good = False
        # team_summary = previous_team_data.groupby("Team").aggregate(np.mean).drop("Match_Number", axis = 1)
        team_summary = previous_team_data.groupby("Team").aggregate(np.mean).drop("Match_Number", axis = 1)
        # print(team_summary)
        team_summaries = pd.concat([team_summaries, team_summary])

    if team_summaries.shape[0] == 0:
        return None
    if good:
        return team_summaries.reset_index()
    return None
     
def getPlayerSummary(player, player_data, match_number):
    player_summary = player_data[(player_data["Match_Number"] < match_number) & (player_data["Player"] == player["Player"]) & (player_data["Role"] == player["Role"])]
    prev_matches = player_summary["Match_Number"].unique()
    if len(prev_matches) < WINDOW_SIZE:
        first_match = 0
    else:
        first_match = prev_matches[WINDOW_SIZE-1]
    player_summary = player_summary[player_summary["Match_Number"] >= first_match]
    # print(player_summary)

    if len(prev_matches) < MIN_DATA:
        return pd.DataFrame(data = [player["Player"], player["Role"]] + [np.nan] * 12,
                            index = PLAYER_COLS).T
    else:
        return player_summary.drop(labels = ["Tournament", "Date", "Match_Number", "Game_Number", "Team"], axis = 1).groupby(["Player", "Role"]).aggregate(np.mean).reset_index()


def getSeasonData(folder_path, output_path, verbose = False, match_numbers = False, plates = True):
    team_data = pd.read_csv(folder_path + "/team.csv")
    nmatches = max(team_data["Match_Number"])

    # processing dataframe
    conv_game_times = []
    for time in team_data["Game_Time"]:
        conv_game_times.append(getGameTimeS(time))

    gold_as_int = []
    for gold in team_data["Gold"]:
        gold_as_int.append(getGoldAsFloat(gold))

    team_data["Game_Time"] = pd.Series(conv_game_times)
    team_data["Gold"] = pd.Series(gold_as_int)

    if plates:
        team_data = team_data.drop(labels = "Grubs", axis = 1)

    team_data = team_data.assign(Win = team_data.Win.map({"LOSS": 0, "WIN": 1}))

    
    # removing NA and displaying message
    nas = team_data[team_data.isna().any(axis = 1)]
    if nas.shape[0] > 0:
        print(f'{nas.shape[0]} rows removed')
        team_data = team_data.dropna(axis = 0)

    # ensuring barons is read as numeric
    team_data["Barons"] = pd.to_numeric(team_data["Barons"])

    player_data = pd.read_csv(folder_path + "/player.csv")
    # print(player_data)

    all_outputs = pd.DataFrame()
    for match_number in range(1, nmatches + 1):
        if verbose:
            print(match_number) if match_number % 10 == 0 else None
        match_data = team_data[team_data["Match_Number"] == match_number]
        if match_data.shape[0] == 0:
            ngames = 0
        else:
            ngames = max(match_data["Game_Number"])
        team_summaries = getTeamSummaries(team_data, match_number) 
        if team_summaries is not None:
            # print(team_summaries)
            player_match_table = pd.DataFrame()
            for game in range(1, ngames + 1):
                game_data = match_data[match_data["Game_Number"] == game]
                player_game_data = player_data[(player_data["Match_Number"] == match_number) & (player_data["Game_Number"] == game)]
                player_summaries = pd.DataFrame()
                for i in player_game_data.index:
                    player = player_game_data.loc[i]
                    player_summary = getPlayerSummary(player, player_data, match_number)
                    player_summaries = pd.concat([player_summaries, player_summary], axis = 0)

                player_summaries = player_summaries.reset_index(drop = True)
                # print(player_summaries)

                player_stats = player_summaries.drop(["Player", "Role"], axis = 1)

                player_table = pd.DataFrame()
                for i in range(5):
                    player_table = pd.concat([player_table, player_stats.loc[[i,i+5]].reset_index(drop = True)], axis = 1)
                player_table.columns = wide_colnames

                player_table["Side"] = ["Blue", "Red"]
                player_match_table = pd.concat([player_match_table, player_table])
                
            #print(team_summaries)
            game_output = pd.concat([team_summaries, player_match_table.reset_index(drop = True)], axis = 1)
            game_output["Winner"] = match_data["Win"].reset_index(drop = True)
            if match_numbers:
                game_output["Match_Number"] = match_number
                game_output["Tournament"] = match_data["Tournament"].iloc[0]

            all_outputs = pd.concat([all_outputs, game_output])
                # print(game_output)
            
    all_outputs = all_outputs[all_outputs["Team"].notna()].reset_index(drop = True)

    if plates:
        all_outputs = all_outputs.drop(labels = ["Plates", "Top_Plates", "Mid_Plates", "Bot_Plates"], axis = 1)

    all_outputs.to_csv(output_path, index = False)

    return all_outputs


    # if verbose:
    #     print(all_outputs)
#print(team_summaries)
    

# getSeasonData("seasons/lcs_2023", "rollinginputs/lcs_2023.csv", verbose = True)

import os

# foldernames = os.listdir("seasons")

# print(foldernames)
# for foldername in foldernames:
#     print(foldername)
#     inputfolder = "seasons/" + foldername
#     outputfile = "rollinginputs/" + foldername + ".csv"
#     getSeasonData(inputfolder, outputfile, match_numbers = True, verbose = True)


# foldernames = os.listdir("seasons_noplates")
# print(foldernames)
# for foldername in foldernames:
#     print(foldername)
#     inputfolder = "seasons_noplates/" + foldername
#     outputfile = "rollinginputs/" + foldername + ".csv"
#     getSeasonData(inputfolder, outputfile, verbose = True, match_numbers = True, plates = False)

getSeasonData("seasons/lck_summer_test", "testSplits/lck_summer_test.csv", verbose = True, match_numbers = True)
