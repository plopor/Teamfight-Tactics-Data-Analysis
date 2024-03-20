import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# This function takes in the translated data along with the raw match data and processes it into categorized dataframe objects.
# A composition represents the team of units that the player builds and is a combination of different levels of different traits.
# Any unit has a variety of traits that contributes to the overall level of that trait in the composition.

# These dataframe objects collates all the matches and are as follows:

# The composition data which indexes by a specific trait combination and for each such "comp" lists all the augments which were played with
# the comp along with the frequencies of the placements 1-8.

# The champion-composition data which indexes by a specific unit and lists all the "comps" that play this unit along with both the 
# frequency this unit appears in this comp as well as the average placement.

# The champion-item data which indexes by a specific unit and lists all the items that this unit is equipped with along with both the
# frequency each item is equipped on the unit as well as the average placement for this combination.

# Finally, the graph data stores the total damage that each composition did to other players for each round.
def queryData(df, trait_dict, augment_dict, champion_dict, item_dict):
    comp_data = dict()
    champ_item_data = dict()
    champ_comp_data = dict()
    graph_data = dict()

    # The first inner function is responsible for collating and storing the data related to compositions, this includes comp_data and graph_data
    # given a single row of the raw data, which represents a single game instance, it adds the relevant information to the two dictionaries.
    def getCompData(row):
        trait_list = []
        single_traits = []
        
        # This takes all the traits that the player had active at the time and stores them. In particular, certain units have "unique" traits
        # that only pertain to the unit and so is stored separately since it won't contribute to the composition naming scheme
        for trait in row['traits']:
            name = trait['name']
            if trait['style'] > 1:
                if trait['tier_total'] > 1:
                    trait_list.append((trait['style'], name))
                else:
                    single_traits.append(name)
        trait_list = sorted(trait_list, key=lambda x: (x[0], x[1]), reverse=True)
        single_traits = sorted(single_traits)

        # This section formats the names of the composition based on the 2 highest-level non-unique active traits
        comp_name = []
        for trait in trait_list[:2]:
            comp_name.append(f"{trait_dict[trait[1]]} {trait[0]}")
        if len(comp_name) == 0:
            comp_name = ' '.join(single_traits)
        else:
            comp_name = ' '.join(comp_name)
        if comp_name == '':
            comp_name = 'Built Different'
        modifier = ""
        if len(row['augments']) > 0:
            aug_name = row['augments'][0]
            if aug_name[-2:] == 'HR':
                aug_name = aug_name[:-2]
            modifier = augment_dict[aug_name]

        # This section generates the data used by the graph and stores the damage dealt to opponents in a list for the last round the player played.
        if comp_name in graph_data:
            if row['last_round'] in graph_data[comp_name]:
                graph_data[comp_name][row['last_round']].append(row['total_damage_to_players'])
            else:
                graph_data[comp_name][row['last_round']] = [row['total_damage_to_players']]
        else:
            round_num = dict()
            round_num[row['last_round']] = [row['total_damage_to_players']]
            graph_data[comp_name] = round_num
        
        # This section stores the augment or "modifier" that the player chose for this match. Augments provide different buffs and effects to teh
        # player's team.
        if comp_name in comp_data:
            if modifier not in comp_data[comp_name]:
                placement = {key: 0 for key in range(1, 9)}
                comp_data[comp_name][modifier] = placement
                comp_data[comp_name][modifier][row['placement']] = 1
            else:
                comp_data[comp_name][modifier][row['placement']] += 1
        else:
            modifiers = dict()
            placement = {key: 0 for key in range(1, 9)}
            comp_data[comp_name] = modifiers
            comp_data[comp_name][modifier] = placement
            comp_data[comp_name][modifier][row['placement']] += 1
        return comp_name
    
    # The second inner function is responsible for collating and storing all the data that is prevalent to the units. This includes champ_item and
    # champ_comp data. Given a game instance and the composition name that was played during this game, adds the relevant data to the dictionaries.
    def getChampData(row, comp_name):
        score = row['placement']

        # This loops over all the units that the player fielded as a part of the composition
        for unit in row['units']:
            id = champion_dict[unit['character_id']]

            # This stores the number of times that the unit was played in the given composition along with the average placement.
            if id in champ_comp_data:
                if comp_name in champ_comp_data[id]:
                    champ_comp_data[id][comp_name][0] += 1
                    champ_comp_data[id][comp_name][1] += score
                else:
                    champ_comp_data[id][comp_name] = [1, score]
            else:
                champ_comp_data[id] = dict()
                champ_comp_data[id][comp_name] = [1, score]

            # This loops over all the items that were equipped on the unit and adds to the relevant data (frequency and avg. placement).
            if id in champ_item_data:
                for item in unit['itemNames']:
                    item = item_dict[item]
                    if item in champ_item_data[id]:
                        champ_item_data[id][item][0] += 1
                        champ_item_data[id][item][1] += score
                    else:
                        champ_item_data[id][item] = [1, score]
            else:
                champ_item_data[id] = dict()
                for item in unit['itemNames']:
                    champ_item_data[id][item_dict[item]] = [1, score]

    # This is the main loop that parses each of the matches, calling the above inner functions to populate the dictionaries
    for index, row in df.iterrows():
        comp_name = getCompData(row)
        getChampData(row, comp_name)
    
    return comp_data, champ_comp_data, champ_item_data, graph_data


# The following functions all aggregate the generated specifically categorized dataframes created by queryData above in a specific way
# that is required by one of the objectives of the project


# This function is called by the endpoint for objective 1. This returns the compositions organized by frequency played, highest avg. placing,
# and best augments (detemined by the highest avg. placement)
def fetchCompsData(comp_data, num):
    groupby_comp = comp_data.groupby(level=0).sum().T

    most_played = groupby_comp.sum().sort_values(ascending=False).head(num)

    def avg_placement(col):
        total_placement = 0
        count = 1
        for i in col:
            total_placement += count * i
            count += 1
        return total_placement / col.sum()
    
    # Having grouped the dataframe by the compositions (to evaluate over all the augments), we only consider the top "num" of them and apply 
    # the above inner function which calculates the average placement for the composition.
    highest_placing = groupby_comp[most_played.index].apply(avg_placement).sort_values(ascending=True)

    def top_modifiers(group):
        group['win_frequency'] = group.iloc[:, :4].sum(axis=1)
        return group.nlargest(5, 'win_frequency').reset_index(level=0, drop=True).iloc[:, -1]
    
    # This groups by the composition and considers the top "num" of them as well. It applies the above function to the aggregate which picks the top 5
    # augments for this composition based on the frequency of top-4 placements.
    groupby_modifier = comp_data.loc[most_played.index].groupby(level=0).apply(top_modifiers)

    return most_played, highest_placing, groupby_modifier

# This function is called by the endpoint for objective 2. Given either champ_comp or champ_item data and a unit, this returns the top "num" 
# of the most frequently played and highest placing compositions or items for this unit.
def fetchChampsData(champ_data, champ, num):
    champ_data = pd.DataFrame(champ_data)
    # This filters the compositions for all the entries for which the unit is not played in the composition
    most_played = champ_data[champ].apply(lambda x: x[0] if not isinstance(x, float) else x).nlargest(num)
    # The lambda function gets the average placement by dividing the placement total with the number of datapoints
    highest_placing = champ_data[champ].loc[most_played.index].apply(lambda x: x[1]/x[0]).nsmallest(num)

    return most_played, highest_placing

# This function is called by the endpoint for objective 5. Given a list of augments, units, and items, it returns a
# recommendation for each unit the best composition to play based on the augments and items provided
def suggestTeam(augments, units, items, cc, ci, fc, num):
    suggestions = []
    for unit in units:
        mpc, hpc = fetchChampsData(cc, unit, num)
        mpi, _ = fetchChampsData(ci, unit, num)

        # This retrieves the augment options which are the augments that people have played with this composition
        options = fc.loc[mpc.index[0]]
        avg_placement = round(hpc.loc[mpc.index[0]], 3)
        # This creates a new column for the total number of top-4s with the augment to sort by it
        options['total_wins'] = options.iloc[:, :4].sum(axis=1)
        options = options.sort_values(by='total_wins', ascending=False)
        augment_indices = [options.index.get_loc(x) for x in augments if x in options.index]
        augment_score = 0
        augment = f"None in the top {num}"
        # This then picks the augment from the input list that has the lowest index in this sorted series 
        # and assigns that as the augment score
        if len(augment_indices) != 0:
            augment_score = min(augment_indices) + 1
            augment = options.index[augment_score - 1]

        # This iterates the input list of items and checks the number of 
        item_score = 0
        if len(items) != 0:
            for index in mpi.head(5).index:
                if index in items:
                    item_score += 1
        
        # The resulting suggestion which contains information on the recommended composition along with
        # the suggested augment and item usability
        suggestion = [unit, mpc.index[0], avg_placement, augment, augment_score, item_score]
        suggestions.append(suggestion)

    return suggestions

# This function is called by the endpoint for objective 4. It displays a scatter graph of damage over the duration of the
# game in rounds showing the average expected damage dealt by the most played comps at each point in the game.
def performanceGraph(g, most_played):
    graph_data = pd.DataFrame(g)
    graph_data = graph_data[most_played.index]

    for col in graph_data.columns:
        x = []
        y = []
        for index, val in graph_data[col].items():
            if isinstance(val, list):
                x.append(index)
                y.append(np.mean(val))
        plt.scatter(x, y, label=col)

    plt.xlabel('round eliminated')
    plt.ylabel('damage dealt')
    plt.legend()
    plt.savefig('sample_performance_graph.png')
    return plt

# These functions parse through the translation json files downloaded from Riot detailing
# the in-game names for their representations in their data and stores them to display.
def fetchTranslations():
    trait_dict = dict()
    augment_dict = dict()
    champion_dict = dict()
    item_dict = dict()

    with open('data/tft-trait.json', 'r') as file:
        t = json.load(file)['data']
    for k, v in t.items():
        trait_dict[k] = v['name']

    with open('data/tft-augments.json', 'r') as file:
        a = json.load(file)['data']
    for k, v in a.items():
        augment_dict[k] = v['name']

    with open('data/tft-champion.json', 'r') as file:
        c = json.load(file)['data']
    for k, v in c.items():
        champion_dict[k] = v['name']

    with open('data/tft-item.json', 'r') as file:
        i = json.load(file)['data']
    for k, v in i.items():
        item_dict[v['id']] = v['name']
    
    return trait_dict, augment_dict, champion_dict, item_dict

# This function parses the raw match data retrieved from the Riot API call as well as the downloaded translation files and 
# stores them into specific categorized dataframes for better access. The match data is stored in MATCH.json
def initializeData():
    json_file_path = 'data/MATCH.json'
    json_objects = []
    with open(json_file_path, 'r') as file:
        for line in file:
            match = json.loads(line)
            json_objects += match['info']['participants']

    # Create a Pandas DataFrame
    df = pd.DataFrame(json_objects)

    # They are categorized into the translations tables for traits, augments, units, and items
    trait_dict, augment_dict, champion_dict, item_dict = fetchTranslations()

    # And using the translations, creates data tables for the project objectives to query
    c, cc, ci, g = queryData(df, trait_dict, augment_dict, champion_dict, item_dict)
    fc = pd.concat({key: pd.DataFrame(val).T for key, val in c.items()}, axis = 0)

    return c, cc, ci, g, fc, trait_dict, augment_dict, champion_dict, item_dict