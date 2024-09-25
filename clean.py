#Data from StatsBomb Open Data found at https://github.com/statsbomb/open-data

import pandas as pd
import numpy as np
import os
from collections import defaultdict as dd

    
def square(location):
    x = location[0]
    y = location[1]
    #I chose not to divide the pitch into equal boxes, but instead take into account the different areas of the pitch.
    #The biggest reason for this was the 18 yard boxes. I wanted to make those their own boxes, as the mentality changes when a player
    #crosses into the penalty area.
    if x <= 18:
        if y <= 18:
            return 1
        elif y <= 40:
            return 2
        elif y <= 62:
            return 3
        else:
            return 4
    elif x <= 60:
        if y <= 40:
            return 5
        else:
            return 6
    elif x <= 102:
        if y <= 40:
            return 7
        else:
            return 8
    else:
        if y <= 18:
            return 9
        elif y <= 40:
            return 10
        elif y <= 62:
            return 11
        else:
            return 12

#Dividing the passing angle into 4 directions
def direction(p):
    if type(p) == dict:
        angle = p['angle']
        if angle <= -3*np.pi/4:
            return 4
        elif angle <= -np.pi/4:
            return 3
        elif angle <= np.pi/4:
            return 1
        elif angle <= 3*np.pi/4:
            return 2
        else:
            return 4
    else:
        return 0

#Dividing the pass height into 2 categories
def alt(key):
    if type(key) == dict:
        if key['height'] == {'id': 1, 'name': 'Ground Pass'}:
            return 1
        if key['height'] == {'id': 2, 'name': 'Low Pass'}:
            #still interceptable at its peak most of the time, so I grouped these passes with ground passes
            return 1
        if key['height'] == {'id': 3, 'name': 'High Pass'}:
            return 2
    else:
        return 0

def pressure(press):
    #Storing if a pass was made under pressure
    #Note - I decided to not include this in the pass types as if a pass is under pressure, every option will be under pressure, which
    #means that this factor does not have a signficant affect on which pass is a better choice, though I decided to keep the data
    # for any possible future use
    if type(press) == float:
        if press == 1.0:
            return 1
        else:
            return 0
    else:
        return 2

def receipt(x):
    #finding if the pass was received under pressure and storing that for later use
    if x['type'] == {'id': 42, 'name': 'Ball Receipt*'}:
        if 'under_pressure' in x:
            if pd.isna(x['under_pressure']):
                store[x['id']] = [x['index'], 0]
            else:
                store[x['id']] = [x['index'], x['under_pressure']]
        else:
            store[x['id']] = [x['index'], 0]
    pass

def related_pressure(x):
    #Using the stored pressure data from the above function, finds the related ball receipt for each event and stores if it was under pressure
    idx = x['index']
    if x['type'] == {'id': 30, 'name': 'Pass'}:
        if type(x['related_events']) == list:
            found = False
            for event in x['related_events']:
                if event in store:
                    if (store[event][0] > idx) and (store[event][0] <= idx + 2):
                        found = True
                        return store[event][1]
            if found == False:
                return 0
        else:
            return 0
    else:
        return 2

def shots(event):
    #Saving the xg for each possession's first shot if there was a shot for later use
    if event['type'] == {'id': 16, 'name': 'Shot'}:
        key = (event['possession'], event['possession_team']['id'], event['index'])
        if key not in shot.keys():
            #only counting the first shot of a possession, as the rebound after that is too far removed from a pass
            shot[key] = event['shot']['statsbomb_xg']
    pass

def success(p):
    #Storing if a pass was successful
    if type(p) == dict:
        if 'outcome' not in p:
            return 1
        else:
            return 0

def xg(event):
    #Finding the xg of each pass, and tracking only the events that we need for later use
    if type(event['pass']) == dict:
        if 'outcome' in event['pass']:
            #Does not inlcude injury clearances or offsides passes, since injury clearances should not be counted against a player,
            #and offside passes are not a good indicator of a player's passing ability without more information,
            #since sometimes they are a poor decision by the passer, and sometimes they are caused by poor timing by the receiver
            if event['pass']['outcome'] != {'id': 74, 'name': 'Injury Clearance'} and event['pass']['outcome'] != {'id': 76, 'name': 'Pass Offside'}:
                no_drop.append(event['id'])
                exists = False
                for key, val in shot.items():
                    #Finding the shot from the the next possession from a missed pass (and ensuring the opposing team has possession)
                    if (key[0] == event['possession'] + 1) and (key[1] != event['possession_team']['id']):
                        exists = True
                        return -val
                if exists == False:
                    return 0
            else:
                return None
        else:
            no_drop.append(event['id'])
            exists = False
            for key, val in shot.items():
                #Finding the shot from the current possession and ensuring it happened after the pass
                if (key[0] == event['possession']) and (key[2] > event['index']):
                    exists = True
                    return val
            if exists == False:
                return 0
    else:
        return None

def build(event):
    a = str(event['square'])
    b = str(event['direction'])
    c = str(event['alt'])
    d = str(event['related_pressure'])
    return a + b + c + d

def position(pos):
    #Dividing the positions into 8 general areas
    if type(pos) == dict:
        id = pos['id']
        if id == 1:
            #Goalkeeper
            return 1
        elif id == 2:
            #Outside Back
            return 3
        elif id <= 5:
            #Center Back
            return 2
        elif id == 6:
            #Outside Back
            return 3
        elif id <= 8:
            #Winger
            return 6
        elif id <= 11:
            #Defensive Midfielder
            return 4
        elif id == 12:
            #Winger
            return 6
        elif id <= 15:
            #Center Midfielder
            return 5
        elif id <= 17:
            #Winger
            return 6
        elif id <= 20:
            #Attacking Midfielder
            return 7
        elif id == 21:
            #Winger
            return 6
        else:
            #Forward
            return 8
    else:
        return 0

def player_change(player):
    #Cleaning the player column
    if type(player) == dict:
        return player['name']
    else:
        return None

def body(action):
    #Cleaning the body part section of passes and storing separately
    #Helps enable me to remove the passing data to safe space after I have stored all the information I need separately
    if type(action) == dict:
        if 'body_part' in action:
            return action['body_part']['name']
        else:
            'Unknown'
    else:
        return None

os.remove(r'passing_data.json')
for file in os.listdir(r'clean_files'):
    os.remove(r'clean_files\\' + file)

#cleaning each file before merging them all
for file in os.listdir(r'statsbomb\data\events'):
    data = pd.read_json(r'statsbomb\data\\events\\' + file)

    #Remove uncessecary columns
    drop_list = []
    not_needed = ['carry', 'duel', 'ball_recovery', 'block', 'substitution', 'foul_committed', 'foul_won', 'injury_stoppage', 'bad_behaviour',
                  'clearance', 'half_start', 'half_end', 'player_off', 'miscontrol', '50_50', 'counter_press', 'play_pattern', 'timestamp',
                  'ball_receipt', 'period', 'dribble', 'minute', 'second', 'duration']
    for col in not_needed:
        if col in data.columns:
            drop_list.append(col)
    data2 = data.drop(drop_list, axis = 1)

    #Remove duplicates
    no_dup = data2.drop_duplicates(subset = 'id', keep = 'first')

    #Remove rows with missing values
    empty_columns = ['id', 'index', 'type', 'possession', 'possession_team', 'location']
    no_empty = no_dup.dropna(axis=0, subset = empty_columns)

    #Convert data types to floats and integers
    next = no_empty.apply(pd.to_numeric, errors='ignore')

    #Scaling down the data types to save memory
    cols = next.select_dtypes(include=['float64']).columns.to_list()
    downcast = next.astype({col:'float32' for col in cols})

    cols2 = next.select_dtypes(include=['int64']).columns.to_list()
    final = downcast.astype({col:'int8' for col in cols2})
    final['index'] = final.index
    df = final.reset_index()

    #function dictionaries stored here to ensure they are reset for each file
    store = dd()
    shot = dd()
    no_drop = []

    #Sorts passes into 12 general locations, 4 general angles, and 2 general heights
    #Finds the pressure on the receiver and stores that for each pass as well 
    df['square'] = df['location'].apply(square)
    df['direction'] = df['pass'].apply(direction)
    df['alt'] = df['pass'].apply(alt)
    df['pressure'] = df['under_pressure'].apply(pressure)
    df.apply(receipt, axis = 1)
    df['related_pressure'] = df.apply(related_pressure, axis=1)
    df.apply(shots, axis = 1)

    #Stores whether a pass was successful (drops events that are injury clearances or offsides in the next apply function)
    df['success'] = df['pass'].apply(success)
    
    #Stores the xg value of the possession following the pass
    df['xg'] = df.apply(xg, axis = 1)

    #Sorts the passes into 8 general positions and cleans up the player column
    df['pos'] = df['position'].apply(position)
    df['player'] = df['player'].apply(player_change)

    #Stores the body part used for each pass for individual analysis so the rest of the passing data can be removed
    df['body_part'] = df['pass'].apply(body)

    #Drops columns uneeded after the apply functions
    df = df.loc[df['id'].isin(no_drop)]
    df = df.drop(['type', 'possession', 'team', 'position', 'possession_team', 'tactics', 'location', 'pass', 'shot', 'goalkeeper', 'counterpress',
                  'interception', 'related_events', 'under_pressure'], axis = 1)

    df['val'] = df.apply(build, axis = 1)
    df = df.drop(['square', 'direction', 'alt', 'pressure', 'related_pressure'], axis = 1)

    #Save the cleaned data
    df.to_json(r'clean_files\\' + file[:-5] + r"_clean.json")

#Ensuring no duplicate files are merged
no_dup_files = set([])
for file in os.listdir(r'clean_files'):
    no_dup_files.add(r'clean_files\\' + file)
files = list(no_dup_files)

#Merging all the files into one
def merge(files):
    #Used recursion to avoid as much repeat reading of rows in the data frames, and it is still the same number of merges
    #as if files were merged in a line (1 and 2, then the result of that and 3, etc.)

    #base cases
    if len(files) == 2:
        file_i = pd.read_json(files[0])
        file_j = pd.read_json(files[1])
        return pd.concat([file_i, file_j], ignore_index=True)
    elif len(files) == 1:
        return pd.read_json(files[0])
    elif len(files) == 0:
        return None
    #recursive case
    else:
        merged1 = merge(files[:int(len(files)/2)])
        merged2 = merge(files[int(len(files)/2):])
        return pd.concat([merged1, merged2], ignore_index=True)

merged = merge(files)

merged.to_json(r'passing_data.json')