# Soccer Passing Analysis
Analysis of xG value of different passes and player's cumulative xG based on their passes and decision making.

* Note *
This was a project created for an application. It was done under a tight time constraint, so many things were simplified.
The presentation and short paper also required by the application are included in the repo.
Also, please ensure you unzip the passing_data file to ensure the program works.
* Note *

This analysis focuses on the passing ability, both surrounding accuracy and decision making, of players. It compares players to others in similar positions, allowing an accurate evaluation of a player's passing ability. For more information on the methodology, pros and cons, and my future goals for this analysis, take a look at the 'Methodology Report' pdf.

For further analysis on a player I chose to analyze, Krépin Diatta, please take a look at the 'Player Analysis - Krépin Diatta' pdf.

To analyze a different player:
Be sure to open to folder 'source_code' on whatever IED you use to ensure the program works.
In the individual.py file, just input the player name you would like to analyze and print out the resulting DataFrame. If the function returns None, that means that either the input player is not in the dataset, or their name doesn't match the name in the dataset. Many players have their full names, while some only have first and last. Check the player's position's DataFrame in the positions folder to find their accurate name in the dataset. The function will also save the input player's data as a json file named 'individual_stats.json'.

The data used in this analysis is from StatsBomb Open Data found at https://github.com/statsbomb/open-data. A huge thanks to them for the high quality data that made this possible.

If you would like to reproduce any part of this, please credit both StatsBomb (more information on this found at the link above), and myself, Evan Brown.

For any other questions, please feel free to reach out to me at ecb10@rice.edu.
