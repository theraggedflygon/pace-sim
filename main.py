import random


class simulation:
    def __init__(self, trials, groups, elo_dict):
        self.trials = trials
        self.groups = groups
        self.elo_dict = elo_dict

    def sim(self):
        for i in range(self.trials):
            t = trial(self.groups, self.elo_dict)
            t.sim_tournament()


class trial:
    def __init__(self, groups, elo_dict):
        self.prelim_groups = groups
        self.elo_dict = elo_dict
        self.prelim_results = dict()

    def sim_tournament(self):
        prelim_results = []
        for group in self.prelim_groups:
            prelim_results.append(self.sim_group(group))


    def sim_group(self, group):
        group_results = {team: 0 for team in group}
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                win, lose = self.sim_game(group[i], group[j])
                group_results[win] += 1
        

    def sim_game(self, teams):
        prob = random.random()
        expect = 1 / (1 + (10 ** ((self.elo_dict[teams[0]] - self.elo_dict[teams[1]]) / 100)))
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

    tournament = simulation(1, groups, elos)
    tournament.sim()
