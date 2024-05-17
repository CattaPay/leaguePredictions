
import pandas as pd

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

def naiveTestSet(input_player, input_team, output_player, output_team, training_path):
    training_data = pd.DataFrame()

    for game_id in range(output_team.shape[0] // 2):
        game_teams = output_team.loc[output_team["Game_Ids"] == game_id, ["Team"]]
        game_teams = pd.merge(game_teams, input_team, on = ["Team"], how = "left")

        
        game_players = output_player.loc[output_player["Game_Ids"] == game_id, ["Player", "Role"]]
        game_players = pd.merge(game_players, input_player, on = ["Player", "Role"], how = "left")

        # remove player names and roles + similar
        # game_teams = game_teams.drop(axis = 1, labels = "Team")
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
        # full_vector = full_vector.drop(axis = 1, labels = "R_Win")

        # add data to training set
        training_data = pd.concat([training_data, full_vector], axis = 0)

    training_data.to_csv(training_path, index = False)
    return training_data


def splitTestSet(input_player, input_team, output_player, output_team, training_path):
    training_data = pd.DataFrame()
    for game_id in range(output_team.shape[0] // 2):
        game_teams = output_team.loc[output_team["Game_Ids"] == game_id, ["Team"]]
        game_teams = pd.merge(game_teams, input_team, on = ["Team"], how = "left")

        game_players = output_player.loc[output_player["Game_Ids"] == game_id, ["Player", "Role"]]
        game_players = pd.merge(game_players, input_player, on = ["Player", "Role"], how = "left").reset_index(drop = True)

        game_players = game_players.drop(axis = 1, labels = ["Player", "Role"])

        player_table = pd.DataFrame()
        for i in range(5):
            player_table = pd.concat([player_table, (game_players.loc[[i,i+5]]).reset_index(drop = True)], axis = 1)
        
        # game_teams = game_teams.drop(axis = 1, labels = ["Team"])

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


# create test dataset for LEC 2024 Spring
player_table, team_table = getInputData("LEC/Winter2024", gamesThreshold = 4)

# team rosters

# print(player_table)
# print(team_table)

roles = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]
fnatic = pd.DataFrame({"Team": ["Fnatic"] * 5, 
                       "Role": roles,
                       "Player": ["Oscarinin", "Razork", "Humanoid", "Noah", "Jun"]})

g2 = pd.DataFrame({"Team": ["G2 Esports"] * 5, 
                       "Role": roles,
                       "Player": ["Brokenblade", "Yike", "Caps", "Hans sama", "Mikyx"]})

giantx = pd.DataFrame({"Team": ["GIANTX"] * 5, 
                       "Role": roles,
                       "Player": ["Odoamne", "Peach", "Jackies", "Patrik", "Ignar"]})

kc = pd.DataFrame({"Team": ["Karmine Corp"] * 5, 
                       "Role": roles,
                       "Player": ["Cabochard", "Bo", "Saken", "Upset", "Targamas"]})

mad = pd.DataFrame({"Team": ["MAD Lions KOI"] * 5, 
                       "Role": roles,
                       "Player": ["Myrwn", "Elyoya", "Fresskowy", "Supa", "Alvaro"]})

rogue = pd.DataFrame({"Team": ["Rogue"] * 5, 
                       "Role": roles,
                       "Player": ["Finn", "Markoon", "Larssen", "Comp", "Zoelys"]})

sk = pd.DataFrame({"Team": ["SK Gaming"] * 5, 
                       "Role": roles,
                       "Player": ["Irrelevant", "Isma", "Nisqy", "Exakick", "Doss"]})

bds = pd.DataFrame({"Team": ["Team BDS"] * 5, 
                       "Role": roles,
                       "Player": ["Adam", "Sheo", "nuc", "Ice", "Labrov"]})

heretics = pd.DataFrame({"Team": ["Team Heretics"] * 5, 
                       "Role": roles,
                       "Player": ["Wunder", "Jankos", "Zwyroo", "Flakked", "Trymbi"]})

vitality = pd.DataFrame({"Team": ["Team Vitality"] * 5, 
                       "Role": roles,
                       "Player": ["Photon", "Daglas", "Vetheo", "Carzzy", "Hylissang"]})


roster = pd.concat([fnatic, g2, giantx, kc, mad, rogue, sk, bds, heretics, vitality]).reset_index()

# blue side, red side

player_dat, team_dat = getInputData("LEC/Winter2024", gamesThreshold = 4)
matchups = [("Team Vitality", "Team Heretics"),
            ("Fnatic", "Rogue"),
            ("Team BDS", "G2 Esports"),
            ("Karmine Corp", "GIANTX"),
            ("MAD Lions KOI", "SK Gaming"),
            ("Team Vitality", "Team BDS"),
            ("Team Heretics", "Rogue"),
            ("Fnatic", "Karmine Corp"),
            ("GIANTX", "SK Gaming"),
            ("MAD Lions KOI", "G2 Esports"),
            ("Rogue", "Team BDS"),
            ("SK Gaming", "Team Vitality"),
            ("GIANTX", "MAD Lions KOI"),
            ("Team Heretics", "Fnatic"),
            ("G2 Esports", "Karmine Corp"),
            ("SK Gaming", "Team BDS"),
            ("GIANTX", "Fnatic"),
            ("G2 Esports", "Team Heretics"),
            ("MAD Lions KOI", "Team Vitality"),
            ("Karmine Corp", "Rogue"),
            ("GIANTX", "Team BDS"),
            ("Rogue", "Team Vitality"),
            ("MAD Lions KOI", "Karmine Corp"),
            ("Team Heretics", "SK Gaming"),
            ("Fnatic", "G2 Esports"),
            ("Team BDS", "Team Heretics"),
            ("Team Vitality", "Fnatic"),
            ("G2 Esports", "GIANTX"),
            ("Rogue", "MAD Lions KOI"),
            ("SK Gaming", "Karmine Corp")]

game_id = 0
team_games = pd.DataFrame()
player_games = pd.DataFrame()

# print(team_dat)

for pairing in matchups:
    # print(pairing)
    blue_team = pairing[0]
    red_team = pairing[1]
    teams = pd.DataFrame({"Team": [blue_team, red_team]})
    players = pd.concat([roster.loc[roster["Team"] == blue_team], roster.loc[roster["Team"] == red_team]])

    teams["Game_Ids"] = [game_id] * 2
    players["Game_Ids"] = [game_id] * 10

    game_id += 1
    team_games = pd.concat([team_games, teams])
    player_games = pd.concat([player_games, players])

team_games = team_games.reset_index(drop = True)
player_games = player_games.reset_index(drop = True).drop(axis = 1, labels = "index")


boi = naiveTestSet(player_dat, team_dat, player_games, team_games, "MLData/LEC_2023_Spring_Test.csv")
boi = splitTestSet(player_dat, team_dat, player_games, team_games, "MLDataSplit/LEC_2023_Spring_Test.csv")
