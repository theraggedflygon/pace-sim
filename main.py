import random
import pandas as pd


class simulation:
    def __init__(self, trials, groups, elo_dict):
        self.trials = trials
        self.groups = groups
        self.elo_dict = elo_dict
        self.results = {team: [0, 0, 0, 0] for group in groups for team in group}

    def sim(self, log=False):
        for i in range(self.trials):
            t = trial(self.groups, self.elo_dict, self.results)
            t.sim_tournament()
            if log and i % 100 == 0:
                print(i)
        for key, data in self.results.items():
            self.results[key] = [d / self.trials for d in data]


class trial:
    def __init__(self, groups, elo_dict, results):
        self.prelim_groups = groups
        self.elo_dict = elo_dict
        self.prelim_results = dict()
        self.results = results

    def sim_tournament(self):
        prelim_results = []
        for group in self.prelim_groups:
            prelim_results.append(self.sim_group(group))

        tiers = [[] for i in range(6)]
        for group in prelim_results:
            teams = list(group.keys())
            for i in range(6):
                tiers[i].append(teams[i])

        playoff_groups = [[] for _ in range(12)]
        for i in range(3):
            for j in range(2):
                random.shuffle(tiers[i * 2 + j])
                for k in range(4):
                    playoff_groups[i * 4 + k] += tiers[i * 2 + j][k * 3:k * 3 + 3]
        # counts teams making tier 1
        for pg in playoff_groups[:4]:
            for team in pg:
                self.results[team][0] += 1
        playoff_results = []
        for group in playoff_groups:
            playoff_results.append(self.sim_group(group))

        super_groups = [[] for i in range(9)]
        for i in range(3):
            for j in range(4):
                pool = list(playoff_results[i * 4 + j])
                for k in range(3):
                    super_groups[i * 3 + k] += pool[k * 2: k * 2 + 2]

        for team in super_groups[0]:
            self.results[team][1] += 1

        super_results = []
        for sg in super_groups:
            super_results.append(self.sim_group(sg))

        final_results = [list(group.keys()) for group in super_results]

        self.results[final_results[0][0]][2] += 1
        ctr = 1
        for bracket in final_results:
            for team in bracket:
                self.results[team][3] += ctr
                ctr += 1

    def sim_group(self, group):
        group_results = {team: 0 for team in group}
        random.shuffle(group)
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                win, lose = self.sim_game([group[i], group[j]])
                group_results[win] += 1
        return {team: wins for team, wins in sorted(group_results.items(), key=lambda item: item[1])}

    def sim_game(self, teams):
        prob = random.random()
        expect = 1 / (1 + (10 ** ((self.elo_dict[teams[0]] - self.elo_dict[teams[1]]) / 25)))
        if prob < expect:
            return teams[0], teams[1]
        else:
            return teams[1], teams[0]


if __name__ == "__main__":
    elos = dict()
    with open("data/groger.csv", 'r') as file:
        data = file.read().split("\n")
    for row in data:
        team_name, value = row.split(",")
        elos[team_name] = float(value)
    with open("data/groups.txt", 'r') as file:
        groups = [row.split(",") for row in file.read().split("\n")]

    tournament = simulation(100000, groups, elos)
    tournament.sim(log=True)
    df = pd.DataFrame.from_dict(tournament.results, orient='index', columns=["Tier 1", 'Top Bracket', "Champion",
                                                                             "Avg Finish"])
    df.to_csv("results/pace2022.csv")
