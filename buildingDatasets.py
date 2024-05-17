
# building game prediction dataset
# a few options... could look at previous n games
# or could look at team/player performance in previous split

# starting with previous split

import pandas as pd
import numpy as np

# gets the player and team data for the split used as input (usually spring or winter)
# only includes players that have reached the gamesThreshold
def getInputData(folderPath, gamesThreshold = 0):
    player_path = folderPath + "/player.csv"
    team_path = folderPath + "/team.csv"
    
    springPlayerData = pd.read_csv(player_path)

    avgs = springPlayerData.drop(axis = 1, labels = ["Date", "Team"]).groupby(["Player", "Role"]).mean()
    ngames = springPlayerData.drop(axis = 1, labels = ["Date", "Team"]).groupby(["Player", "Role"]).size().to_frame("Games")
    player_dat = avgs.join(ngames).reset_index()
    player_dat = player_dat.loc[player_dat["Games"] >= gamesThreshold]
    # print(dat)

    # converts game times to integer seconds
    def getGameTimeS(game_time):
        s = game_time.split(":")
        return int(s[0]) * 60 + int(s[1])

    # removes the k from gold
    def getGoldAsFloat(gold):
        return float(gold[:-1])

    springTeamData = pd.read_csv(team_path).drop(axis = 1, labels = "Grubs")

    conv_game_times = []
    for time in springTeamData["Game_Time"]:
        conv_game_times.append(getGameTimeS(time))

    gold_as_int = []
    for gold in springTeamData["Gold"]:
        gold_as_int.append(getGoldAsFloat(gold))

    springTeamData["Game_Time_s"] = pd.Series(conv_game_times)
    springTeamData["Gold_Num"] = pd.Series(gold_as_int)
    springTeamData = springTeamData.drop(axis = 1, labels = ["Game_Time", "Gold"])

    springTeamData["WinNum"] = springTeamData["Win"].transform(lambda x: int(x == "WIN"))

    team_dat = springTeamData.drop(axis = 1, labels = ["Date", "Win"]).groupby("Team").mean().reset_index()
    return player_dat, team_dat

# grabs and processes output data (usually summer or spring)
def getOutputData(folderPath):
# getting games to predict
    player_path = folderPath + "/player.csv"
    team_path = folderPath + "/team.csv"
    summerTeamData = pd.read_csv(team_path)
    summerPlayerData = pd.read_csv(player_path)

    # add gameids to each game
    games = summerTeamData.shape[0] // 2
    game_ids = []
    for i in range(games):
        game_ids.append(games - i - 1)
        game_ids.append(games - i - 1)

    summerTeamData["Game_Ids"] = game_ids

    game_ids = []
    for i in range(games):
        for j in range(10):
            game_ids.append(games - i - 1)

    summerPlayerData["Game_Ids"] = game_ids

    return summerPlayerData, summerTeamData

# a few options here:
# could predict each team's prob of winning independently, then combine them somehow
# or could use some mixture of stats between the teams (will run into problems with NaNs)
# can also use full data for each game (but potentially double the predictors)

# gonna start with full data, probably try assessing independently after
def naiveTrainingSet(input_player, input_team, output_player, output_team, training_path):
    training_data = pd.DataFrame()

    for game_id in range(output_team.shape[0] // 2):
        game_teams = output_team.loc[output_team["Game_Ids"] == game_id, ["Team", "Win"]]
        game_teams = pd.merge(game_teams, input_team, on = ["Team"], how = "left")

        
        game_players = output_player.loc[output_player["Game_Ids"] == game_id, ["Player", "Role"]]
        game_players = pd.merge(game_players, input_player, on = ["Player", "Role"], how = "left")

        # remove player names and roles + similar
        game_teams = game_teams.drop(axis = 1, labels = "Team")
        game_players = game_players.drop(axis = 1, labels = ["Player", "Role"])

        teams_vector = pd.concat([game_teams.loc[game_teams.index[0]], game_teams.loc[game_teams.index[1]]])

        players_vector = pd.DataFrame()
        for i in game_players.index:
            players_vector = pd.concat([players_vector, game_players.loc[i]])
        
        # giving blue and red side distinct names
        team_colnames = []
        blue_colnames = []
        red_colnames = []
        for col in game_teams.columns:
            blue_colnames.append("B_" + col)
            red_colnames.append("R_" + col)
        team_colnames = blue_colnames + red_colnames
        
        bigbox = [[] for _ in range(10)]

        for col in game_players.columns:
            bigbox[0].append("B_TOP_" + col)
            bigbox[1].append("B_JNG_" + col)
            bigbox[2].append("B_MID_" + col)
            bigbox[3].append("B_BOT_" + col)
            bigbox[4].append("B_SUP_" + col)
            bigbox[5].append("R_TOP_" + col)
            bigbox[6].append("R_JNG_" + col)
            bigbox[7].append("R_MID_" + col)
            bigbox[8].append("R_BOT_" + col)
            bigbox[9].append("R_SUP_" + col)

        player_colnames = []
        for chunk in bigbox:
            player_colnames += chunk


        # set names to unique ones for team and role
        teams_vector.index = team_colnames
        players_vector.index = player_colnames
        # print(teams_vector)

        full_vector = pd.concat([teams_vector, players_vector]).transpose()

        # remove Red team wins indicator
        full_vector = full_vector.drop(axis = 1, labels = "R_Win")

        # add data to training set
        training_data = pd.concat([training_data, full_vector], axis = 0)

    training_data.to_csv(training_path, index = False)
    return training_data

# predicts each team's probability independently, splitting data by team
def splitTrainingSet(input_player, input_team, output_player, output_team, training_path):
    #
    training_data = pd.DataFrame()
    for game_id in range(output_team.shape[0] // 2):

        game_teams = output_team.loc[output_team["Game_Ids"] == game_id, ["Team", "Win"]]
        game_teams = pd.merge(game_teams, input_team, on = ["Team"], how = "left")

        game_players = output_player.loc[output_player["Game_Ids"] == game_id, ["Player", "Role"]]
        game_players = pd.merge(game_players, input_player, on = ["Player", "Role"], how = "left").reset_index(drop = True)

        game_players = game_players.drop(axis = 1, labels = ["Player", "Role"])

        player_table = pd.DataFrame()
        for i in range(5):
            player_table = pd.concat([player_table, (game_players.loc[[i,i+5]]).reset_index(drop = True)], axis = 1)
        
        game_teams = game_teams.drop(axis = 1, labels = ["Team"])

        bigbox = [[] for _ in range(5)]
        for col in game_players.columns:
            bigbox[0].append("TOP_" + col)
            bigbox[1].append("JNG_" + col)
            bigbox[2].append("MID_" + col)
            bigbox[3].append("BOT_" + col)
            bigbox[4].append("SUP_" + col)
        
        player_colnames = []
        for chunk in bigbox:
            player_colnames += chunk

        player_table.columns = player_colnames
        all_game_data = pd.concat([game_teams, player_table], axis = 1)
        training_data = pd.concat([training_data, all_game_data], axis = 0)

    training_data.to_csv(training_path, index = False)
    return training_data

# gets LCS 2022 training data
player_table, team_table = getInputData("LCS/Spring2022", gamesThreshold = 4)
summerPlayer, summerTeam = getOutputData("LCS/Summer2022")
splitTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLDataSplit/LCS_2022.csv")
# naiveTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLData/LCS_2022.csv")
print("Done")

# gets LCS 2023 training data
player_table, team_table = getInputData("LCS/Spring2023", gamesThreshold = 4)

# replacing CLG with NRG
team_table = team_table.replace({"CLG": "NRG"})
summerPlayer, summerTeam = getOutputData("LCS/Summer2023")
splitTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLDataSplit/LCS_2023.csv")
# naiveTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLData/LCS_2023.csv")
print("Done")

# gets LEC 2022 training data
player_table, team_table = getInputData("LEC/Spring2022", gamesThreshold = 4)
summerPlayer, summerTeam = getOutputData("LEC/Summer2022")
splitTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLDataSplit/LEC_2022.csv")
# naiveTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLData/LEC_2022.csv")
print("Done")

# gets LEC 2023 training data
player_table, team_table = getInputData("LEC/Winter2023", gamesThreshold = 4)
summerPlayer, summerTeam = getOutputData("LEC/Spring2023")
splitTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLDataSplit/LEC_2023_Spring.csv")
# naiveTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLData/LEC_2023_Spring.csv")
print("Done")

player_table, team_table = getInputData("LEC/Spring2023", gamesThreshold = 4)
summerPlayer, summerTeam = getOutputData("LEC/Summer2023")
splitTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLDataSplit/LEC_2023_Summer.csv")
# naiveTrainingSet(player_table, team_table, summerPlayer, summerTeam, "MLData/LEC_2023_Summer.csv")
print("Done")


