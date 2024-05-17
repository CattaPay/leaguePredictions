# Scrape LEC data

library(tidyverse)
library(stringr)
library(rvest)


# function to pull game data (for players and teams)
# can only grab BO1
getGameData = function(player_data, team_data, game_link, game_date) {

  game_page = paste0("https://gol.gg", game_link, "page-fullstats/")
  
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
  team_page = paste0("https://gol.gg", game_link, "page-game/")
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
  
  plates = team_html %>%
    html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[4]/div/table/tr/td/div/div/div/div") %>%
    html_text()
  
  blue_win = team_html %>%
    html_element(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[1]/div[1]/div") %>%
    html_text() %>% str_trim() %>% str_sub(-4,-1) %>% str_trim()
  
  red_win = team_html %>%
    html_element(xpath = "/html/body/div/main/div[2]/div/div[3]/div/div/div/div[1]/div/div/div[2]/div[2]/div[1]/div") %>%
    html_text() %>% str_trim() %>% str_sub(-4,-1) %>% str_trim()
  
  bruh = "hat"
  
  # make team table
  team_stats = tibble(Date = game_date,
                      Team = c(blue_team, red_team),
                      Win = c(blue_win, red_win),
                      Kills = c(blue_team_stats[1], red_team_stats[1]),
                      Towers = c(blue_team_stats[2], red_team_stats[2]),
                      Drakes = c(blue_team_stats[3], red_team_stats[3]),
                      Barons = c(blue_team_stats[4], red_team_stats[4]),
                      Gold = c(blue_team_stats[5], red_team_stats[5]),
                      Grubs = plates[5:6],
                      Plates = plates[8:9],
                      Top_Plates = plates[11:12],
                      Mid_Plates = plates[14:15],
                      Bot_Plates = plates[17:18],
                      Game_Time = game_time)
  
  
  # finish player data
  game_table = game_table %>% add_column(Team = c(rep(blue_team, 5), rep(red_team, 5)), .before = "Player") %>%
    add_column(Date = game_date, .before = "Team")
  
  # add to full tables
  # player_data <<- bind_rows(player_data, game_table)
  # team_data <<- bind_rows(team_data, team_stats)
  
  return(list(game_table, team_stats))
}

# # LEC Winter 2024
# print("LEC Winter 2024")
# lec_link = "https://gol.gg/tournament/tournament-matchlist/LEC%20Winter%20Season%202024/"
# html = lec_link %>% read_html()
# # getting links to game pages
# all_links = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[1]/a") %>%
#   html_attr("href") %>% str_replace("..", "") %>% str_replace("page-game/", "")
# 
# # getting date of each game
# all_dates = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[7]") %>%
#   html_text()
# 
# # initializing tables
# player_data = tibble()
# team_data = tibble()
# for (i in 1:length(all_links)) {
#   game_link = all_links[i]
#   game_date = all_dates[i]
#   game_datas = getGameData(player_dat, team_dat, game_link, game_date)
#   
#   player_dat = bind_rows(player_dat, game_datas[[1]])
#   team_dat = bind_rows(team_dat, game_datas[[2]])
#   print(i)
# }
# write_csv(player_data, "LECWinter2024_player.csv")
# write_csv(team_data, "LECWinter2024_team.csv")
# 
# # LEC Summer 2023
# print("LEC Summer 2023")
# lec_link = "https://gol.gg/tournament/tournament-matchlist/LEC%20Summer%202023/"
# html = lec_link %>% read_html()
# 
# # getting links to game pages
# all_links = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[1]/a") %>%
#   html_attr("href") %>% str_replace("..", "") %>% str_replace("page-game/", "")
# 
# # getting date of each game
# all_dates = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[7]") %>%
#   html_text()
# 
# # initializing tables
# player_data = tibble()
# team_data = tibble()
# for (i in 1:length(all_links)) {
#   game_link = all_links[i]
#   game_date = all_dates[i]
#   game_datas = getGameData(player_dat, team_dat, game_link, game_date)
#   
#   player_dat = bind_rows(player_dat, game_datas[[1]])
#   team_dat = bind_rows(team_dat, game_datas[[2]])
#   print(i)
# }
# write_csv(player_data, "LECSummer2023_player.csv")
# write_csv(team_data, "LECSummer2023_team.csv")

# LEC Spring 2023
print("LEC Spring 2023")
lec_link = "https://gol.gg/tournament/tournament-matchlist/LEC%20Spring%20Season%202023/"
html = lec_link %>% read_html()

# getting links to game pages
all_links = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[1]/a") %>%
  html_attr("href") %>% str_replace("..", "") %>% str_replace("page-game/", "")

# getting date of each game
all_dates = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[7]") %>%
  html_text()

# initializing tables
player_data = tibble()
team_data = tibble()
for (i in 1:length(all_links)) {
  game_link = all_links[1]
  game_date = all_dates[1]
  game_datas = getGameData(player_dat, team_dat, game_link, game_date)
  
  player_dat = bind_rows(player_dat, game_datas[[1]])
  team_dat = bind_rows(team_dat, game_datas[[2]])
  print(i)
}
write_csv(player_data, "LECSpring2023_player.csv")
write_csv(team_data, "LECSpring2023_team.csv")

# LEC Winter 2023
print("LEC Winter 2023")
lec_link = "https://gol.gg/tournament/tournament-matchlist/LEC%20Winter%202023/"
html = lec_link %>% read_html()

# getting links to game pages
all_links = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[1]/a") %>%
  html_attr("href") %>% str_replace("..", "") %>% str_replace("page-game/", "")

# getting date of each game
all_dates = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[7]") %>%
  html_text()

# initializing tables
player_data = tibble()
team_data = tibble()
for (i in 1:length(all_links)) {
  game_link = all_links[i]
  game_date = all_dates[i]
  game_datas = getGameData(player_dat, team_dat, game_link, game_date)
  
  player_dat = bind_rows(player_dat, game_datas[[1]])
  team_dat = bind_rows(team_dat, game_datas[[2]])
  print(i)
}
write_csv(player_data, "LECWinter2023_player.csv")
write_csv(team_data, "LECWinter2023_team.csv")

## LEC Summer 2022 ##
print("LEC Summer 2022")
lec_link = "https://gol.gg/tournament/tournament-matchlist/LEC%20Summer%202022/"
html = lec_link %>% read_html()

# getting links to game pages
all_links = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[1]/a") %>%
  html_attr("href") %>% str_replace("..", "") %>% str_replace("page-game/", "")

# getting date of each game
all_dates = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[7]") %>%
  html_text()

# initializing tables
player_data = tibble()
team_data = tibble()
for (i in 1:length(all_links)) {
  game_link = all_links[i]
  game_date = all_dates[i]
  game_datas = getGameData(player_dat, team_dat, game_link, game_date)
  
  player_dat = bind_rows(player_dat, game_datas[[1]])
  team_dat = bind_rows(team_dat, game_datas[[2]])
  print(i)
}
write_csv(player_data, "LECSummer2022_player.csv")
write_csv(team_data, "LECSummer2022_team.csv")

# LEC Spring 2022
print("LEC Spring 2022")
lec_link = "https://gol.gg/tournament/tournament-matchlist/LEC%20Spring%202022/"
html = lec_link %>% read_html()

# getting links to game pages
all_links = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[1]/a") %>%
  html_attr("href") %>% str_replace("..", "") %>% str_replace("page-game/", "")

# getting date of each game
all_dates = html %>%  html_elements(xpath = "/html/body/div/main/div[2]/div/div[3]/div/section/div/div/table/tbody/tr/td[7]") %>%
  html_text()

# initializing tables
player_data = tibble()
team_data = tibble()
for (i in 1:length(all_links)) {
  game_link = all_links[i]
  game_date = all_dates[i]
  game_datas = getGameData(player_dat, team_dat, game_link, game_date)
  
  player_dat = bind_rows(player_dat, game_datas[[1]])
  team_dat = bind_rows(team_dat, game_datas[[2]])
  print(i)
}
write_csv(player_data, "LECSpring2022_player.csv")
write_csv(team_data, "LECSpring2022_team.csv")
