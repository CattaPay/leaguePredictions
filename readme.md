# leaguePredictions #
An attempt to predict the results of professional league of legends games based on prior results. It uses a random forest model in the XGBoost package trained on a rolling average of a variety of statistics over a player/teams previous games.  

### Info
The models are fit on data pulled from gol.gg, an archive of statistics from all major and minor regions. The final model was trained to predict only LCK results, as they tended to have the least variability of all major regions.


### Files
- LECscraping.R
  - a first attempt to pull data from gol.gg
  - format of pulled data is not ideal
- cleanerScraping.R
  - a second attempt to pull data from gol.gg
  - failed to scrape best-of series
- matchScraping.R
  - the finished webscraping code
  - allows for scraping BO3 and BO5 series
  - can get data where plating info is not available
- rollingwindow.py
  - gets rolling averages of player and team statistics based on the global variables at the top of the file
- buildingDatasets.py
  - outdated code to get average statistics from previous tournaments
- combiningDatasets.py
  - selects tournaments and create training/testing files for models
- MLSplit.ipynb
  - outdated model trained on previous tournaments
- MLthings.ipynb
  - outdated model trained on previous tournaments
- rollingAlgorithmWide.ipynb
  - model trained on rolling window statistics
- testingodds
  - files to compare model results to betting odds
  - allows for evaluation of models
