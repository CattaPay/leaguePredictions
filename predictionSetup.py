def line_prepender(filename, lines):
    with open(filename, 'r+') as f:
        header = f.readline()
        content = f.read()
        f.seek(0, 0)
        f.write(header.rstrip('\r\n') + '\n' + lines + '\n' + content)

games = [["T1", "KT Rolster"],
         ["Hanwha Life eSports", "Nongshim RedForce"],\
         ["OK BRION", "FearX"],
         ["Kwangdong Freecs", "Dplus KIA"]]

roles = ["TOP", "JUNGLE", "MID", "ADC", "SUPPORT"]

rosters = {"Hanwha Life eSports": ["Doran", "Peanut", "Zeka", "Viper", "Delight"],
           "Dplus KIA": ["kingen", "Lucid", "ShowMaker", "Aiming", "Kellin"],
           "Nongshim RedForce": ["DnDn", "Sylvie", "Callme", "Jiwoo", "GuGer"],
           "FearX": ["Clear", "Raptor", "Clozer", "Hena", "Execute"],
           "Kwangdong Freecs": ["DuDu", "Cuzz", "Bulldog", "Leaper", "Andil"],
           "KT Rolster": ["PerfecT", "Pyosik", "Bdd", "Deft", "BeryL"],
           "OK BRION": ["Morgan", "Youngjae", "Karis", "Envyy", "Pollu"],
           "DRX": ["Rascal", "Sponge", "kyeahoo", "Teddy", "Pleata"],
           "Gen.G eSports": ["Kiin", "Canyon", "Chovy", "Peyz", "Lehends"],
           "T1": ["Zeus", "Oner", "Faker", "Gumayusi", "Keria"]}

players = []
for i in games:
    game_players = rosters[i[0]] + rosters[i[1]]
    players.append(game_players)




# Tournament,Date,Match_Number,Game_Number,Team,Player,Role,Kills,Deaths,Assists,CS,CSM,GPM,VSPM,DPM,KAPM,GD15,CSD15,XPD15
# Tournament,Date,Match_Number,Game_Number,Team,Win,Kills,Towers,Drakes,Barons,Gold,Grubs,Plates,Top_Plates,Mid_Plates,Bot_Plates,Game_Time
start_game = 125
for i in range(len(games)):
    game = start_game + i
    lines = ""
    lines += "New,0," + str(game) + ",1," + games[i][0] + ",LOSS,0,0,0,0,0k,0,0,0,0,0,"
    lines += "\n"
    lines += "New,0," + str(game) + ",1," + games[i][1] + ",LOSS,0,0,0,0,0k,0,0,0,0,0,"
    line_prepender("seasons/lck_summer_test/team.csv", lines)

    lines = ""
    for j in range(10):
        lines += ",," + str(game) + ",1,," + players[i][j] + "," + roles[j % 5] + ",,,,,,,,,,,,"
        lines += "\n"

    lines = lines.rstrip("\n")    
    
    line_prepender("seasons/lck_summer_test/player.csv", lines)



