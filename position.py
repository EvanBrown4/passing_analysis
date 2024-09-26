#Data from StatsBomb Open Data found at https://github.com/statsbomb/open-data

import pandas as pd
import os
from collections import defaultdict as dd
from scipy import stats

general = pd.read_json(r'general_stats.json')
train = pd.read_json(r'passing_data.json')

# Getting the set of players who have played in each positions (players can be in multiple sets)
gset = set([])
cbset = set([])
obset = set([])
dmset = set([])
cmset = set([])
amset = set([])
wset = set([])
fset = set([])

def player(event):
    if event['pos'] == 1:
        gset.add(event['player'])
    elif event['pos'] == 2:
        cbset.add(event['player'])
    elif event['pos'] == 3:
        obset.add(event['player'])
    elif event['pos'] == 4:
        dmset.add(event['player'])
    elif event['pos'] == 5:
        cmset.add(event['player'])
    elif event['pos'] == 6:
        wset.add(event['player'])
    elif event['pos'] == 7:
        amset.add(event['player'])
    elif event['pos'] == 8:
        fset.add(event['player'])
    else:
        pass

train.apply(player, axis = 1)

# Adding each player to their position's list and to a list of all players to set up dataframes
gdx = []
cbx = []
obx = []
dmx = []
cmx = []
amx = []
wx = []
fx = []
all = []

for player in gset:
    gdx.append((player, 0, 0))
    if player not in all:
        all.append((player, 0, 0))
for player in cbset:
    cbx.append((player, 0, 0))
    if player not in all:
        all.append((player, 0, 0))
for player in obset:
    obx.append((player, 0, 0))
    if player not in all:
        all.append((player, 0, 0))
for player in dmset:
    dmx.append((player, 0, 0))
    if player not in all:
        all.append((player, 0, 0))
for player in cmset:
    cmx.append((player, 0, 0))
    if player not in all:
        all.append((player, 0, 0))
for player in amset:
    amx.append((player, 0, 0))
    if player not in all:
        all.append((player, 0, 0))
for player in wset:
    wx.append((player, 0, 0))
    if player not in all:
        all.append((player, 0, 0))
for player in fset:
    fx.append((player, 0, 0))
    if player not in all:
        all.append((player, 0, 0))

# Building the positional dataframes, using the lists built above for the rows
df_g = pd.DataFrame(gdx, columns = ['name', 'successes', 'total_attempts'])
df_cb = pd.DataFrame(cbx, columns = ['name', 'successes', 'total_attempts'])
df_ob = pd.DataFrame(obx, columns = ['name', 'successes', 'total_attempts'])
df_dm = pd.DataFrame(dmx, columns = ['name', 'successes', 'total_attempts'])
df_cm = pd.DataFrame(cmx, columns = ['name', 'successes', 'total_attempts'])
df_am = pd.DataFrame(amx, columns = ['name', 'successes', 'total_attempts'])
df_w = pd.DataFrame(wx, columns = ['name', 'successes', 'total_attempts'])
df_f = pd.DataFrame(fx, columns = ['name', 'successes', 'total_attempts'])

g = dd(dict)
cb = dd(dict)
ob = dd(dict)
dm = dd(dict)
cm = dd(dict)
am = dd(dict)
w = dd(dict)
f = dd(dict)

# Sort each player's xg by each type of pass.
# Store in a dictionary.
def gen_sort(df, event, pos):
    name = event['player']
    index = df.loc[df['name'] == name].index[0]
    id = event['val']
    # Adding each player's passing events to their stats in their position's dataframe
    complete = df.at[index, 'successes']
    all = df.at[index, 'total_attempts']
    df.at[index, 'successes'] = complete + event['success']
    df.at[index, 'total_attempts'] = all + 1
    # Storing each player's stats, separated by each type of pass, in a dictionary to help find each player's xg
    if id in pos[name]:
        pos[name][id] = (pos[name][id][0] + event['success'], pos[name][id][1] + 1)
    else:
        pos[name][id] = (event['success'], 1)

# Find each player's xg
def xg(name, pos):
    if name in pos:
        count = 0
        xg = 0
        for id in pos[name]:
            # Collecting the xg data for each type of pass
            gen_index = general.loc[general['id'] == id].index[0]
            xga = general.at[gen_index, 'xga']
            xgf = general.at[gen_index, 'xgf']
            # Finding the success rate of each type of pass for each individual player
            complete = pos[name][id][0]/pos[name][id][1]
            missed = 1 - complete
            count += 1
            # Weighting the player's xg based off of their success rate for each type of pass (acting as a risk assessment for each pass
            # since a higher success rate leads to a higher xg)
            # Since the data from the general dataframe was the xg per pass for each type of pass, all we need to do is weight the xgf
            # and xga and put them together to find each player's xg per pass for each type of pass.
            # We then add the xgs for all passses made by each player and average them to find each player's average xg across all passes
            # The reason we do this is because if a player is generally more successful with one type of pass, it is a better decision for
            # them to make that pass than someone who is less successful with that type of pass.
            xg += (xgf * complete) - (xga * missed)
        # Count will always be higher than 0 since pass types (id) are only added into pos[name] when an event is that pass type
        return (xg/count)
    else:
        pass

# Sorting each event into its position, and calling gen_sort based on the position.
def pos_sort(event):
    if event['pos'] == 1:
        gen_sort(df_g, event, g)
    elif event['pos'] == 2:
        gen_sort(df_cb, event, cb)
    elif event['pos'] == 3:
        gen_sort(df_ob, event ,ob)
    elif event['pos'] == 4:
        gen_sort(df_dm, event, dm)
    elif event['pos'] == 5:
        gen_sort(df_cm, event, cm)
    elif event['pos'] == 6:
        gen_sort(df_w, event, w)
    elif event['pos'] == 7:
        gen_sort(df_am, event, am)
    elif event['pos'] == 8:
        gen_sort(df_f, event, f)
    else:
        pass

# Use of percentile instead of other statistical measures explained in paper
def percentile(expected, df):
    return stats.percentileofscore(df['xg'], expected)

# Finding the player's pass completion rate
def rate(player):
    if player['total_attempts'] == 0:
        return 0
    else:
        return player['successes']/player['total_attempts']
    
def pass_rate_percentile(rate, df):
    return stats.percentileofscore(df['Pass Rate'], rate)

# Building out each position's dataframe using all the above functions
train.apply(pos_sort, axis = 1)
df_g['xg'] = df_g['name'].apply(xg, args = (g,))
df_g['percentile'] = df_g['xg'].apply(percentile, args = (df_g,))
df_g['Pass Rate'] = df_g.apply(rate, axis = 1)
df_g['Pass Rate Percentile'] = df_g['Pass Rate'].apply(pass_rate_percentile, args = (df_g,))
df_g = df_g[df_g['total_attempts'] >= 30]
df_g = df_g.sort_values(by = ['percentile'], axis = 0, ascending = False)

df_cb['xg'] = df_cb['name'].apply(xg, args = (cb,))
df_cb['percentile'] = df_cb['xg'].apply(percentile, args = (df_cb,))
df_cb['Pass Rate'] = df_cb.apply(rate, axis = 1)
df_cb['Pass Rate Percentile'] = df_cb['Pass Rate'].apply(pass_rate_percentile, args = (df_cb,))
df_cb = df_cb[df_cb['total_attempts'] >= 30]
df_cb = df_cb.sort_values(by = ['percentile'], axis = 0, ascending = False)

df_ob['xg'] = df_ob['name'].apply(xg, args = (ob,))
df_ob['percentile'] = df_ob['xg'].apply(percentile, args = (df_ob,))
df_ob['Pass Rate'] = df_ob.apply(rate, axis = 1)
df_ob['Pass Rate Percentile'] = df_ob['Pass Rate'].apply(pass_rate_percentile, args = (df_ob,))
df_ob = df_ob[df_ob['total_attempts'] >= 30]
df_ob = df_ob.sort_values(by = ['percentile'], axis = 0, ascending = False)

df_dm['xg'] = df_dm['name'].apply(xg, args = (dm,))
df_dm['percentile'] = df_dm['xg'].apply(percentile, args = (df_dm,))
df_dm['Pass Rate'] = df_dm.apply(rate, axis = 1)
df_dm['Pass Rate Percentile'] = df_dm['Pass Rate'].apply(pass_rate_percentile, args = (df_dm,))
df_dm = df_dm[df_dm['total_attempts'] >= 30]
df_dm = df_dm.sort_values(by = ['percentile'], axis = 0, ascending = False)

df_cm['xg'] = df_cm['name'].apply(xg, args = (cm,))
df_cm['percentile'] = df_cm['xg'].apply(percentile, args = (df_cm,))
df_cm['Pass Rate'] = df_cm.apply(rate, axis = 1)
df_cm['Pass Rate Percentile'] = df_cm['Pass Rate'].apply(pass_rate_percentile, args = (df_cm,))
df_cm = df_cm[df_cm['total_attempts'] >= 30]
df_cm = df_cm.sort_values(by = ['percentile'], axis = 0, ascending = False)

df_am['xg'] = df_am['name'].apply(xg, args = (am,))
df_am['percentile'] = df_am['xg'].apply(percentile, args = (df_am,))
df_am['Pass Rate'] = df_am.apply(rate, axis = 1)
df_am['Pass Rate Percentile'] = df_am['Pass Rate'].apply(pass_rate_percentile, args = (df_am,))
df_am = df_am[df_am['total_attempts'] >= 30]
df_am = df_am.sort_values(by = ['percentile'], axis = 0, ascending = False)

df_w['xg'] = df_w['name'].apply(xg, args = (w,))
df_w['percentile'] = df_w['xg'].apply(percentile, args = (df_w,))
df_w['Pass Rate'] = df_w.apply(rate, axis = 1)
df_w['Pass Rate Percentile'] = df_w['Pass Rate'].apply(pass_rate_percentile, args = (df_w,))
df_w = df_w[df_w['total_attempts'] >= 30]
df_w = df_w.sort_values(by = ['percentile'], axis = 0, ascending = False)

df_f['xg'] = df_f['name'].apply(xg, args = (f,))
df_f['percentile'] = df_f['xg'].apply(percentile, args = (df_f,))
df_f['Pass Rate'] = df_f.apply(rate, axis = 1)
df_f['Pass Rate Percentile'] = df_f['Pass Rate'].apply(pass_rate_percentile, args = (df_f,))
df_f = df_f[df_f['total_attempts'] >= 30]
df_f = df_f.sort_values(by = ['percentile'], axis = 0, ascending = False)

# Finding the general pass completion rate for each player, not just when they are playing in a specific position
def pass_rate(name):
    gidx = df_g.loc[df_g['name'] == name].index
    if gidx.empty:
        gsuccess = 0
        gtotal = 0
    else:
        gsuccess = df_g.at[gidx[0], 'successes']
        gtotal = df_g.at[gidx[0], 'total_attempts']
    cbidx = df_cb.loc[df_cb['name'] == name].index
    if cbidx.empty:
        cbsuccess = 0
        cbtotal = 0
    else:
        cbsuccess = df_cb.at[cbidx[0], 'successes']
        cbtotal = df_cb.at[cbidx[0], 'total_attempts']
    obidx = df_ob.loc[df_ob['name'] == name].index
    if obidx.empty:
        obsuccess = 0
        obtotal = 0
    else:
        obsuccess = df_ob.at[obidx[0], 'successes']
        obtotal = df_ob.at[obidx[0], 'total_attempts']
    dmidx = df_dm.loc[df_dm['name'] == name].index
    if dmidx.empty:
        dmsuccess = 0
        dmtotal = 0
    else:
        dmsuccess = df_dm.at[dmidx[0], 'successes']
        dmtotal = df_dm.at[dmidx[0], 'total_attempts']
    cmidx = df_cm.loc[df_cm['name'] == name].index
    if cmidx.empty:
        cmsuccess = 0
        cmtotal = 0
    else:
        cmsuccess = df_cm.at[cmidx[0], 'successes']
        cmtotal = df_cm.at[cmidx[0], 'total_attempts']
    amidx = df_am.loc[df_am['name'] == name].index
    if amidx.empty:
        amsuccess = 0
        amtotal = 0
    else:
        amsuccess = df_am.at[amidx[0], 'successes']
        amtotal = df_am.at[amidx[0], 'total_attempts']
    widx = df_w.loc[df_w['name'] == name].index
    if widx.empty:
        wsuccess = 0
        wtotal = 0
    else:
        wsuccess = df_w.at[widx[0], 'successes']
        wtotal = df_w.at[widx[0], 'total_attempts']
    fidx = df_f.loc[df_f['name'] == name].index
    if fidx.empty:
        fsuccess = 0
        ftotal = 0
    else:
        fsuccess = df_f.at[fidx[0], 'successes']
        ftotal = df_f.at[fidx[0], 'total_attempts']
    successes = gsuccess + cbsuccess + obsuccess + dmsuccess + cmsuccess + amsuccess + wsuccess + fsuccess
    attempts = gtotal + cbtotal + obtotal + dmtotal + cmtotal + amtotal + wtotal + ftotal
    if attempts == 0:
        return 0
    else:
        return successes/attempts

def percentile_pass(rate, df):
    return stats.percentileofscore(df['Pass Rate'], rate)

# Finding each player's pass completion rate and percentile compared to all players in the data, not just their position
total_percentiles = pd.DataFrame(all, columns = ['name', 'rate', 'percentile'])
all_players = pd.DataFrame(all, columns = ['name', 'rate', 'percentile'])
all_players = all_players.drop(['rate', 'percentile'], axis = 1)
all_players['Pass Rate'] = total_percentiles['name'].apply(pass_rate)
all_players['Percentile'] = all_players['Pass Rate'].apply(percentile_pass, args = (all_players,))

# Saving all relevant dataframes to json files
os.remove(r'positions\\all_players.json')
all_players.to_json(r'positions\\all_players.json')

os.remove(r'positions\\g.json')
os.remove(r'positions\\cb.json')
os.remove(r'positions\\ob.json')
os.remove(r'positions\\dm.json')
os.remove(r'positions\\cm.json')
os.remove(r'positions\\am.json')
os.remove(r'positions\\w.json')
os.remove(r'positions\\f.json')

df_g.to_json(r'positions\\g.json')
df_cb.to_json(r'positions\\cb.json')
df_ob.to_json(r'positions\\ob.json')
df_dm.to_json(r'positions\\dm.json')
df_cm.to_json(r'positions\\cm.json')
df_am.to_json(r'positions\\am.json')
df_w.to_json(r'positions\\w.json')
df_f.to_json(r'positions\\f.json')