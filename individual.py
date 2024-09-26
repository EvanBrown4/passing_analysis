import pandas as pd
import os

# Track the successes of passes using different body parts
def body(event, body_df):
    body_part = event['body_part']
    if body_part == None:
        body_part = 'Other'
    index = body_df.loc[body_df['body_part'] == body_part].index[0]
    body_df.at[index, 'successful'] += event['success']
    body_df.at[index, 'attempts'] += 1

# Build the full passing decision making stats for a specific player. Save the resulting database to storage.
def player_stats(player, all):    
    df = pd.read_json('passing_data.json')
    df = df.loc[df['player'] == player]
    if len(df) == 0:
        return None
    else:
        # Checking the average position played by the player and loading in that position's data
        mode = df.mode()['pos'][0]
        if mode <= 0.5:
            return None
        elif mode == 1:
            pos = pd.read_json(r'positions\\g.json')
        elif mode <= 2.5:
            pos = pd.read_json(r'positions\\cb.json')
        elif mode <= 3.5:
            pos = pd.read_json(r'positions\\ob.json')
        elif mode <= 4.5:
            pos = pd.read_json(r'positions\\dm.json')
        elif mode <= 5.5:
            pos = pd.read_json(r'positions\\cm.json')
        elif mode <= 6.5:
            pos = pd.read_json(r'positions\\w.json')
        elif mode <= 7.5:
            pos = pd.read_json(r'positions\\am.json')
        else:
            pos = pd.read_json(r'positions\\f.json')
        
        # Getting the player's indiviudal stats compared to both their position and all players in the data
        index = pos.loc[pos['name'] == player].index[0]
        percentile = pos.at[index, 'percentile']
        xg = pos.at[index, 'xg']
        all_idx = all.loc[all['name'] == player].index[0]
        rate = all.at[all_idx, 'Pass Rate']
        rate_perc = all.at[all_idx, 'Percentile']
        pos_pass_perc = pos.at[index, 'Pass Rate Percentile']

        # Building the dataframe of the player's passing data by pass type, separated by goalkeepers and outfield players
        if mode == 1:
            body_parts = [('Right Foot', 0, 0), ('Left Foot', 0, 0), ('Head', 0, 0), ('No Touch', 0, 0), ('Other', 0, 0), ('Keeper Arm', 0, 0), ('Drop Kick', 0, 0)]
        else:
            body_parts = [('Right Foot', 0, 0), ('Left Foot', 0, 0), ('Head', 0, 0), ('No Touch', 0, 0), ('Other', 0, 0)]
        body_df = pd.DataFrame(body_parts, columns = ['body_part', 'successful', 'attempts'])
        # Filling out the dataframe just built 
        df = df.apply(body, axis = 1, args = (body_df,))

        # Calculating the completion rate for each pass type and storing it along with the total attempts of that pass type
        r_attempt = body_df.at[0, 'attempts']
        r_suc = body_df.at[0, 'successful']
        if r_attempt != 0:
            right = ((r_suc / r_attempt) * 100, r_attempt)
        else:
            right = None
        l_attempt = body_df.at[1, 'attempts']
        l_suc = body_df.at[1, 'successful']
        if l_attempt != 0:
            left = ((l_suc / l_attempt) * 100, l_attempt)
        else:
            left = None
        h_attempt = body_df.at[2, 'attempts']
        h_suc = body_df.at[2, 'successful']
        if h_attempt != 0:
            head = ((h_suc / h_attempt) * 100, h_attempt)
        else:
            head = None
        nt_attempt = body_df.at[3, 'attempts']
        nt_suc = body_df.at[3, 'successful']
        if nt_attempt != 0:
            no_touch = ((nt_suc / nt_attempt) * 100, nt_attempt)
        else:
            no_touch = None
        o_attempt = body_df.at[4, 'attempts']
        o_suc = body_df.at[4, 'successful']
        if o_attempt != 0:
            other = ((o_suc / o_attempt) * 100, o_attempt)
        else:
            other = None
        # Ensuring goalkeeper stats are only stored for goalkeepers then
        # Building the final dataframe of player's individual stats from everything found above
        if mode == 1:
            k_attempt = body_df.at[5, 'attempts']
            k_suc = body_df.at[5, 'successful']
            if k_attempt != 0:
                keeper_arm = ((k_suc / k_attempt) * 100, k_attempt)
            else:
                keeper_arm = None
            dk_attempt = body_df.at[6, 'attempts']
            dk_suc = body_df.at[6, 'successful']
            if dk_attempt != 0:
                drop_kick = ((dk_suc / dk_attempt) * 100, dk_attempt)
            else:
                drop_kick = None
            player_df = pd.DataFrame(columns = ['Completion Rate', 'Completion Rate Position Percentile', 'Completion Rate Overall Percentile', 'xg', 'percentile', 'right', 'left', 'head', 'no touch', 'keeper arm', 'drop kick', 'other'])
            player_df.loc[0] = [rate*100, pos_pass_perc * 100, rate_perc * 100, xg, percentile, right, left, head, no_touch, keeper_arm, drop_kick, other]
        else:
            player_df = pd.DataFrame(columns = ['Completion Rate', 'Completion Rate Position Percentile', 'Completion Rate Overall Percentile', 'xg', 'percentile', 'right', 'left', 'head', 'no touch', 'other'])
            player_df.loc[0] = [rate*100, pos_pass_perc, rate_perc, xg, percentile, right, left, head, no_touch, other]
        
        # Saving the dataframe as a json
        os.remove(r'individual_stats.json')
        player_df.to_json(r'individual_stats.json')

all_players = pd.read_json(r'positions\\all_players.json')

# Chose to use Krepin Diatta after looking through the positional results and
# finding a player high on the list whom wouldn't be expected to be there.
player_stats('Krépin Diatta', all_players)