import pandas as pd
import os
from collections import defaultdict as dd
from scipy import stats

raw_df = pd.read_json(r'passing_data.json')

# Building a dataframe for each type of pass
idx = []
for a in range(1,13):
    for b in range(1,5):
        for c in range(1,3):
            for d in range(0, 2):
                new_id = str(a) + str(b) + str(c) + str(d)
                idx.append((int(new_id), 0, 0, dict({'count': 0, 'avg': 0, 'total': 0}), dict({'count': 0, 'avg': 0, 'total': 0})))

df = pd.DataFrame(idx, columns = ['id', 'successes', 'total_attempts', 'xga', 'xgf'])

# Finding the data of each individual type of pass
# For each event, finding the type of pass (event['val']), finding the index of that type of pass in the dataframe,
# and then adding the data from the event to the dataframe
def attempts(event):
    id = event['val']
    index = df.loc[df['id'] == id].index[0]
    successes = df.at[index, 'successes']
    total = df.at[index, 'total_attempts']
    xga = df.at[index, 'xga']
    xgf = df.at[index, 'xgf']
    # Update a holder variable for the expected goals against and for depending on if the xg is positive (for) or negative (against)
    if event['xg'] < 0:
        goal_a = event['xg'] * -1
        goal_f = 0
    elif event['xg'] > 0:
        goal_a = 0
        goal_f = event['xg']
    else:
        goal_a = 0
        goal_f = 0
    # Updates the dataframe with the new data
    df.at[index, 'successes'] = successes + event['success']
    df.at[index, 'total_attempts'] = total + 1

    # Tracking the count and total xgs to make for easy and efficient averaging
    total_a = xga['total'] + goal_a
    count_a = xga['count'] + 1
    avg_a = total_a / count_a
    df.at[index, 'xga'] = {'count': count_a, 'avg': avg_a, 'total': total_a}

    total_f = xgf['total'] + goal_f
    count_f = xgf['count'] + 1
    avg_f = total_f / count_f
    df.at[index, 'xgf'] = {'count': count_f, 'avg': avg_f, 'total': total_f}
    
# Once all events are run through above, everything is already calculated, so we can remove any unnessecary data
def change_tot(goal):
    return goal['total']
def change_xg(goal):
    return goal['avg']

# These two functions are not needed for the individual data, as these things are calculated individually and positionally,
# but they are still usesful to compare different types of passes to each other, so I decided to include them for any possible need
# later, whether it is to use for another dataframe, to use for a different type of analysis, or to help players with their decision making

# Finding the expected goals for each event by weighting the xga and xgf based on the completion rate then subtracting them
# Return the expected goals.
def expected(event):
    if event['total_attempts'] == 0:
        complete = 0
        missed = 0
    else:
        complete = event['successes']/event['total_attempts']
        missed = 1 - complete
    i_xgf = event['xgf']*complete
    i_xga = event['xga']*missed

    xgf = i_xgf
    xga = i_xga
    return xgf - xga

# Use of percentile instead of other statistical measures explained in paper
def percentile(expected):
    return stats.percentileofscore(df['expected'], expected)

# Add general stats.
raw_df.apply(attempts, axis = 1)
df['xga'] = df['xga'].apply(change_xg)
df['xgf'] = df['xgf'].apply(change_xg)
df['expected'] = df.apply(expected, axis = 1)
df['percentile'] = df['expected'].apply(percentile)

os.remove(r'general_stats.json')
df.to_json(r'general_stats.json')