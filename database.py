import analysis as an
import RiotAPI as api
import matplotlib.pyplot as plt

class DataBase():
    def __init__(self, refresh=False):
        # Note these methods are used to query and store the real-time data from the last 5000 instances of challenger-level TFT matches.
        # Since the Riot API limits request rates, it is more efficient to store data to use locally and only refresh the data from time
        # to time when you wish to have analysis that reflects the real-time meta.
        # In certain cases, when the game updates to a new set, all ranked history is reset and we must wait for the top players to
        # re-enter the challenger tier before their match data can be requested again. The game updated to the newest set, set 10 on Nov. 21.
        # It will take a few weeks for the top 250 challenger players to be saturated once again. In the meantime, the local data I've stored
        # reflects the matured meta of set 9.5 near the tail end of its 3-month period. Translation jsons for set 10 would also need to be updated.
        #if refresh:
            #api.storePUUIDs()
            #api.storeMatches()

        comp_data, champ_comp_data, champ_item_data, graph_data, full_comp_data, trait_dict, augment_dict, champion_dict, item_dict = an.initializeData()
        self._comp_data = comp_data
        self._champ_comp_data = champ_comp_data
        self._champ_item_data = champ_item_data
        self._graph_data = graph_data
        self._full_comp_data = full_comp_data
        self._trait_dict = trait_dict
        self._augment_dict = augment_dict
        self._champion_dict = champion_dict
        self._item_dict = item_dict
    
    def getObjective1(self, top=10):
        most_played, highest_placing, _ = an.fetchCompsData(self._full_comp_data, top)

        _, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        most_played_plt = ax1.table(cellText=[[most_played.index[i], most_played.values[i]] for i in range(top)],
                                colLabels=['Composition', 'Top-4s'],
                                loc='center')
        most_played_plt.auto_set_font_size(False)
        most_played_plt.set_fontsize(10)
        most_played_plt.scale(1.5, 1.5)
        ax1.axis('off')
        ax1.set_title('Most Played Comps')

        highest_placing_plt = ax2.table(cellText=[[highest_placing.index[i], highest_placing.values[i]] for i in range(top)],
                                colLabels=['Composition', 'Avg. Placement'],
                                loc='center')
        highest_placing_plt.auto_set_font_size(False)
        highest_placing_plt.set_fontsize(10)
        highest_placing_plt.scale(1.5, 1.5)
        ax2.axis('off')
        ax2.set_title('Highest Avg. Placing Comps')

        plt.subplots_adjust(wspace=1)
        return plt
    
    def getObjective2(self, unit, top=10):
        mpc, hpc = an.fetchChampsData(self._champ_comp_data, unit, top)
        mpi, hpi = an.fetchChampsData(self._champ_item_data, unit, top)

        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))

        most_played_plt = ax1.table(cellText=[[mpc.index[i], mpc.values[i]] for i in range(top)],
                                    colLabels=['Composition', 'Top-4s'],
                                    loc='center')
        most_played_plt.auto_set_font_size(False)
        most_played_plt.set_fontsize(10)
        most_played_plt.scale(1.5, 1.5)
        ax1.axis('off')
        ax1.set_title('Most Played Comps', pad=20)

        highest_placing_plt = ax2.table(cellText=[[hpc.index[i], hpc.values[i]] for i in range(top)],
                                        colLabels=['Composition', 'Avg. Placement'],
                                        loc='center')
        highest_placing_plt.auto_set_font_size(False)
        highest_placing_plt.set_fontsize(10)
        highest_placing_plt.scale(1.5, 1.5)
        ax2.axis('off')
        ax2.set_title('Highest Avg. Placing Comps', pad=20)

        most_played_plt_i = ax3.table(cellText=[[mpi.index[i], mpi.values[i]] for i in range(top)],
                                        colLabels=['Composition', 'Top-4s'],
                                        loc='center')
        most_played_plt_i.auto_set_font_size(False)
        most_played_plt_i.set_fontsize(10)
        most_played_plt_i.scale(1.5, 1.5)
        ax3.axis('off')
        ax3.set_title('Most Played Items', pad=20)

        highest_placing_plt_i = ax4.table(cellText=[[hpi.index[i], hpi.values[i]] for i in range(top)],
                                            colLabels=['Composition', 'Avg. Placement'],
                                            loc='center')
        highest_placing_plt_i.auto_set_font_size(False)
        highest_placing_plt_i.set_fontsize(10)
        highest_placing_plt_i.scale(1.5, 1.5)
        ax4.axis('off')
        ax4.set_title('Highest Avg. Placing Items', pad=20)

        plt.subplots_adjust(wspace=1, hspace=0.5)
        return plt
    
    def getObjective3(self, comp, search=10):
        _, _, groupby_modifier = an.fetchCompsData(self._full_comp_data, search)
        if comp not in groupby_modifier:
            return None
        
        _, ax = plt.subplots(figsize=(10, 6))
        most_played_plt = ax.table(cellText=[[groupby_modifier[comp].index[i], groupby_modifier[comp].values[i]] for i in range(5)],
                                colLabels=['Augment', 'Top-4s'],
                                loc='center')
        most_played_plt.auto_set_font_size(False)
        most_played_plt.set_fontsize(10)
        most_played_plt.scale(0.7, 1.5)
        ax.axis('off')
        ax.set_title('Most Played Augments')

        return plt
    
    def getObjective4(self, top=10):
        most_played, _, _ = an.fetchCompsData(self._full_comp_data, top)
        plot = an.performanceGraph(self._graph_data, most_played)
        return plot
    
    def getObjective5(self, augments, units, items, search=10):
        suggestions = an.suggestTeam(augments, units, items, self._champ_comp_data, self._champ_item_data, self._full_comp_data, search)
        
        _, ax = plt.subplots(figsize=(15, 6))
        most_played_plt = ax.table(cellText=[suggestions[i] for i in range(len(units))],
                                colLabels=['Unit', 'Composition', 'Avg. Placement', 'Best Augment', 'Augment Rank', '# of Top-5 Items'],
                                loc='center')
        most_played_plt.auto_set_font_size(False)
        most_played_plt.set_fontsize(10)
        most_played_plt.scale(1.2, 1.5)
        ax.axis('off')
        ax.set_title('Suggestions')

        return plt
    
    def getItemDict(self):
        return list(set(self._item_dict.values()))
    
    def getAugmentDict(self):
        return list(set(self._augment_dict.values()))
    
    def getChampionDict(self):
        return list(set(self._champion_dict.values()))