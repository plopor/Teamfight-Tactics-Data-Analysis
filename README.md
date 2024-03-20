The data files that are required for this project can be downloaded here: https://drive.google.com/drive/folders/1HZA7Yvi3Nx4-N0G26w4QJo72Rpic3Xz2?usp=sharing
Put the resulting 'data' folder in my project directory.

# Data analysis on League of Legends autobattler Teamfight Tactics.

# Project walkthrough video can be found here: https://www.youtube.com/watch?v=jdAMa4aEdP4

This data analysis project is meant to analyze and document evolving meta trends in Teamfight Tactics. This is done by utilizing the Riot Games API, and specific endpoints for unit and trait statistics, item data, match history data, and challenger player data.

It would have methods that:
- Returns a list of the top most played/highest-placing compositions
- Takes in a unit and displays the most common compositions/synergies it is played in along with highest-placing/popular items
- Takes in a match modifier and shows the change in performance of compositions given the modifier
- For the top comps, returns a graph visualizing performance over a span of a specified time and across patches.
- Given an input of match modifier, starting units, and items, return the closest matching composition to play this match with the highest average placing
