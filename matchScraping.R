# more advanced scraping
# should be able to grab Bo1, Bo3, and Bo5
# includes sort of metadata with the stats
  # ie. Tournament, Match no., Game no., Date

library(tidyverse)
library(rvest)

# game_link: https.../game/stats/xxxxx/page-game/ (from summary page)
getGameData = function(game_link, tournament, match_date, match_num, game_num, plates = TRUE) {
  game_page = gsub("page-game", "page-fullstats", game_link)
  game_html = game_page %>% read_html()
  player_stats = game_html %>% html_element(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/table") %>%
    html_table()
  
  stat_ids = c(1,2,4,5,6,8,11,13,20,29,31,38,39,40)
  stat_names = c("Player", "Role", "Kills", "Deaths", "Assists", "CS",
                 "CSM", "GPM", "VSPM", "DPM", "KAPM", "GD15", "CSD15", "XPD15")
  
  # Player (1), Role (2), Kills (4), Deaths (5), Assists (6), CS (8),
  # CSM (11), GPM (13), VSPM (20), DPM (29), KAPM (31), 
  # GD15 (38), CSD15 (39), XPD15 (40)
  
  game_table = player_stats[stat_ids,c(-1)]
  game_table = tibble(data.frame(t(game_table)))
  colnames(game_table) <- stat_names
  
  # get team data
  team_page = game_link
  team_html = team_page %>% read_html()
  game_time = team_html %>% 
    html_element(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[1]/div[2]/h1") %>%
    html_text()
  
  blue_team = team_html %>% 
    html_element(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[1]/div[1]/div/a") %>%
    html_text()
  
  blue_team_stats = team_html %>%
    html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[1]/div[2]/div/span") %>%
    html_text() %>% str_trim()
  
  red_team = team_html %>% 
    html_element(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[2]/div[1]/div/a") %>%
    html_text()
  
  red_team_stats = team_html %>%
    html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[2]/div[2]/div/span") %>%
    html_text() %>% str_trim()
  
  if (plates) {
    platedata = team_html %>%
      html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[4]/div/table/tr/td/div/div/div/div") %>%
      html_text()
  }
  
  blue_win = team_html %>%
    html_element(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[1]/div[1]/div") %>%
    html_text() %>% str_trim() %>% str_sub(-4,-1) %>% str_trim()
  
  red_win = team_html %>%
    html_element(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[2]/div[1]/div") %>%
    html_text() %>% str_trim() %>% str_sub(-4,-1) %>% str_trim()
  
  bruh = "hat"
  
  # make team table
  if (plates){
    team_stats = tibble(Tournament = tournament,
                        Date = match_date,
                        Match_Number = match_num,
                        Game_Number = game_num,
                        Team = c(blue_team, red_team),
                        Win = c(blue_win, red_win),
                        Kills = c(blue_team_stats[1], red_team_stats[1]),
                        Towers = c(blue_team_stats[2], red_team_stats[2]),
                        Drakes = c(blue_team_stats[3], red_team_stats[3]),
                        Barons = c(blue_team_stats[4], red_team_stats[4]),
                        Gold = c(blue_team_stats[5], red_team_stats[5]),
                        Grubs = platedata[5:6],
                        Plates = platedata[8:9],
                        Top_Plates = platedata[11:12],
                        Mid_Plates = platedata[14:15],
                        Bot_Plates = platedata[17:18],
                        Game_Time = game_time)
  }
  else{
    team_stats = tibble(Tournament = tournament,
                        Date = match_date,
                        Match_Number = match_num,
                        Game_Number = game_num,
                        Team = c(blue_team, red_team),
                        Win = c(blue_win, red_win),
                        Kills = c(blue_team_stats[1], red_team_stats[1]),
                        Towers = c(blue_team_stats[2], red_team_stats[2]),
                        Drakes = c(blue_team_stats[3], red_team_stats[3]),
                        Barons = c(blue_team_stats[4], red_team_stats[4]),
                        Gold = c(blue_team_stats[5], red_team_stats[5]),
                        Game_Time = game_time)
  }
  
  
  # finish player data
  game_table = game_table %>% add_column(Team = c(rep(blue_team, 5), rep(red_team, 5)), .before = "Player") %>%
    add_column(Tournament = tournament, Date = match_date, 
               Match_Number = match_num, Game_Number = game_num, .before = "Team")
  
  # add to full tables
  # player_data <<- bind_rows(player_data, game_table)
  # team_data <<- bind_rows(team_data, team_stats)
  
  return(list(game_table, team_stats))
}

# match_link: https.../game/stats/xxxxx/page-summary/ (from match summary page)
getGameLinks = function(match_link) {
  match_html = match_link %>% read_html()
  game_links = match_html %>% 
    html_elements(xpath = "/html/body/div/main/div[2]/div/div[2]/div/nav[1]/div/ul/li/a") %>% 
    html_attr("href") %>%
    str_replace("..", "")
  game_links = game_links[2:(length(game_links)-1)]
  game_links = paste0("https://gol.gg", game_links)
  return(game_links)
}

getMatchData = function(match_link, tournament, match_date, match_num, plates = TRUE) {
  # initializing tables
  player_data = tibble()
  team_data = tibble()
  
  # get game links
  game_links = getGameLinks(match_link)
  for (i in 1:length(game_links)) {
    game_dat = getGameData(game_links[i], tournament, match_date, match_num, i, plates)
    player_data = bind_rows(player_data, game_dat[[1]])
    team_data = bind_rows(team_data, game_dat[[2]])
  }
  
  return(list(player_data, team_data))
  
}

# https://gol.gg/tournament/tournament-stats/LCS%20Spring%202024/
getTournamentData = function(tournament_link, doWrite = F, plates = TRUE){
  tournament_matches = gsub("tournament-stats", "tournament-matchlist", tournament_link)
  
  html = tournament_matches %>% read_html()
  # getting links to game pages
  all_links = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[1]/a") %>%
    html_attr("href") %>% str_replace("..", "")# %>% str_replace("page-game/", "")
  
  all_links = paste0("https://gol.gg", all_links)
  # getting date of each game
  all_dates = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[7]") %>%
    html_text()
  
  # getting tournament name
  tournament = html %>% 
    html_elements(xpath = "/html/body/div/main/div[2]/div/h1[1]") %>%
    html_text() %>% str_trim()
    
  # initializing tables
  player_data = tibble()
  team_data = tibble()
  
  for (i in 1:length(all_links)){
    match_link = all_links[i]
    match_date = all_dates[i]
    # print(match_link)
    game_dat = getMatchData(match_link, tournament, match_date, length(all_links)-i+1, plates)
    
    player_data = bind_rows(player_data, game_dat[[1]])
    team_data = bind_rows(team_data, game_dat[[2]])
    
    print(paste0(tournament, ": Match ", i, " out of ", length(all_links)))
  }
  
  if (doWrite) {
    tournament_name = gsub(" ", "_", tournament)
    directory_path = paste0("tournaments/", tournament_name)
    dir.create(directory_path, showWarning = F)
    write_csv(player_data, paste0("tournaments/", tournament_name, "/player.csv"))
    write_csv(team_data, paste0("tournaments/", tournament_name, "/team.csv"))
  }
  
  return(list(player_data, team_data))
}

# works on tournament that is incomplete
getHalfTournamentData = function(tournament_link, doWrite = F, plates = TRUE){
  tournament_matches = gsub("tournament-stats", "tournament-matchlist", tournament_link)
  
  html = tournament_matches %>% read_html()
  # getting links to game pages
  all_links = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[1]/a") %>%
    html_attr("href") %>% str_replace("..", "")# %>% str_replace("page-game/", "")
  
  all_links = paste0("https://gol.gg", all_links)
  # getting date of each game
  all_dates = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[7]") %>%
    html_text()
  
  # getting tournament name
  tournament = html %>% 
    html_elements(xpath = "/html/body/div/main/div[2]/div/h1[1]") %>%
    html_text() %>% str_trim()
  
  # initializing tables
  player_data = tibble()
  team_data = tibble()
  
  for (i in 1:length(all_links)){
    match_link = all_links[i]
    match_date = all_dates[i]
    print(match_link)
    tryCatch(
      {game_dat = getMatchData(match_link, tournament, match_date, length(all_links)-i+1, plates)
      }, error = function(msg){
        game_dat <<- list(tibble(), tibble())
        print("Ur shit broke: ")
      }
    )
    # print(game_dat)
    player_data = bind_rows(player_data, game_dat[[1]])
    team_data = bind_rows(team_data, game_dat[[2]])
    
    print(paste0(tournament, ": Match ", i, " out of ", length(all_links)))
  }
  
  if (doWrite) {
    tournament_name = gsub(" ", "_", tournament)
    directory_path = paste0("tournaments/", tournament_name)
    dir.create(directory_path, showWarning = F)
    write_csv(player_data, paste0("tournaments/", tournament_name, "/player.csv"))
    write_csv(team_data, paste0("tournaments/", tournament_name, "/team.csv"))
  }
  
  return(list(player_data, team_data))
}


# replaced getTournamentData with getHalfTournamentData
# hopefully won't break
getAllTournaments = function(tournaments_path){
  tournament_links = read_file(tournaments_path) %>%
    read_html() %>%
    html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/table/tbody/tr/td[2]/a") %>%
    html_attr("href")
  
  for (tournament_link in tournament_links){
    getHalfTournamentData(tournament_link, doWrite = T, plates)
  }
}

getSeason = function(tournaments_path, season_name, plates = TRUE) {
  tournament_links = read_file(tournaments_path) %>%
    read_html() %>%
    html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/table/tbody/tr/td[2]/a") %>%
    html_attr("href")

  # initializing tables
  player_data = tibble()
  team_data = tibble()
  
  count = 0
  for (tournament_link in tournament_links){
    game_dat = getTournamentData(tournament_link, doWrite = F, plates)
    new_games = max(game_dat[[2]]$Match_Number)
    if (count > 0){
      team_data = mutate(team_data, Match_Number = Match_Number + new_games)
      player_data = mutate(player_data, Match_Number = Match_Number + new_games)
    }
    count = count + 1
    player_data = bind_rows(player_data, game_dat[[1]])
    team_data = bind_rows(team_data, game_dat[[2]])
    # print(team_data)
  }
  if (plates) {
    dir.create(paste0("seasons/", season_name), showWarning = F)
    write_csv(player_data, paste0("seasons/", season_name, "/player.csv"))
    write_csv(team_data, paste0("seasons/", season_name, "/team.csv"))
  } else {
    dir.create(paste0("seasons_noplates/", season_name), showWarning = F)
    write_csv(player_data, paste0("seasons_noplates/", season_name, "/player.csv"))
    write_csv(team_data, paste0("seasons_noplates/", season_name, "/team.csv"))
  }
  
  
  return(list(player_data, team_data))
  
}

safeGetSeason = function(tournaments_path, season_name, plates = TRUE) {
  tryCatch(
    {getSeason(tournaments_path, season_name, plates)
      
    }, error = function(msg){
      print("Skipped game")
      print(season_name)
    }
  )
}

# 
# tournament_path = "tournamentpages/lck2023.html"
# getAllTournaments(tournament_path)
# 
# getSeason("tournamentpages/lck2023.html", "lck_2023")
# getSeason("tournamentpages/lpl2023.html", "lpl_2023")
# getSeason("tournamentpages/lcs2023.html", "lcs_2023")
# getSeason("tournamentpages/lec2023.html", "lec_2023")
# getSeason("tournamentpages/nacl2023.html", "nacl_2023")
# getSeason("tournamentpages/lckcl2023.html", "lckcl_2023")

# safeGetSeason("tournamentpages/lck2022.html", "lck_2022")
# safeGetSeason("tournamentpages/lcs2022.html", "lcs_2022")
# safeGetSeason("tournamentpages/lec2022.html", "lec_2022")
# safeGetSeason("tournamentpages/nacl2022.html", "nacl_2022")
# safeGetSeason("tournamentpages/lckcl2022.html", "lckcl_2022")
# safeGetSeason("tournamentpages/vcs2023.html", "vcs_2023")
# safeGetSeason("tournamentpages/vcs2022.html", "vcs_2022")
# safeGetSeason("tournamentpages/pcs2023.html", "pcs_2023")
# safeGetSeason("tournamentpages/pcs2022.html", "pcs_2022")
# safeGetSeason("tournamentpages/ljl2023.html", "ljl_2023")
# safeGetSeason("tournamentpages/ljl2022.html", "ljl_2022")


# safeGetSeason("tournamentpages/lcs2021.html", "lcs_2021", plates = FALSE)
# safeGetSeason("tournamentpages/lcs2020.html", "lcs_2020", plates = FALSE)
# safeGetSeason("tournamentpages/lcs2019.html", "lcs_2019", plates = FALSE)
# 
# safeGetSeason("tournamentpages/lec2021.html", "lec_2021", plates = FALSE)
# safeGetSeason("tournamentpages/lec2020.html", "lec_2020", plates = FALSE)
# safeGetSeason("tournamentpages/lec2019.html", "lec_2019", plates = FALSE)
# 
# safeGetSeason("tournamentpages/lck2021.html", "lck_2021", plates = FALSE)
# safeGetSeason("tournamentpages/lck2020.html", "lck_2020", plates = FALSE)

# safeGetSeason("tournamentpages/lck2019.html", "lck_2019", plates = FALSE)
# 
# safeGetSeason("tournamentpages/ljl2021.html", "ljl_2021", plates = FALSE)
# safeGetSeason("tournamentpages/ljl2020.html", "ljl_2020", plates = FALSE)
# safeGetSeason("tournamentpages/ljl2019.html", "ljl_2019", plates = FALSE)
# 
# safeGetSeason("tournamentpages/nacl2021.html", "nacl_2021", plates = FALSE)
# safeGetSeason("tournamentpages/nacl2020.html", "nacl_2020", plates = FALSE)
# safeGetSeason("tournamentpages/nacl2019.html", "nacl_2019", plates = FALSE)
# 
# safeGetSeason("tournamentpages/pcs2021.html", "pcs_2021", plates = FALSE)
# safeGetSeason("tournamentpages/pcs2020.html", "pcs_2020", plates = FALSE)
# 
# safeGetSeason("tournamentpages/vcs2021.html", "vcs_2021", plates = FALSE)
# safeGetSeason("tournamentpages/vcs2020.html", "vcs_2020", plates = FALSE)
# safeGetSeason("tournamentpages/vcs2019.html", "vcs_2019", plates = FALSE)
# 
# safeGetSeason("tournamentpages/lckcl2021.html", "lckcl_2021", plates = FALSE)
# safeGetSeason("tournamentpages/lckcl2020.html", "lckcl_2020", plates = FALSE)

# lck2024dat = getTournamentData("https://gol.gg/tournament/tournament-stats/LCK%20Spring%202024/", doWrite = T, plates = TRUE)

safeGetSeason("tournamentpages/lck_2024_05_24.html", "lck_2024_05_24", plates = TRUE)
