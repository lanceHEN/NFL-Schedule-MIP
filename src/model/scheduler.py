"""For code to solve the NFL scheduling problem."""

import math

import pulp as pl
import pandas as pd

from config import LeagueConfig

class NFLScheduler:
    """This class will solve a mixed-integer program to find a feasible schedule
    (i.e. respects all real-life NFL schedule rules) that also is as balanced as
    possible, by minimizing the maximum deviation from the league-average strength
    of schedule.
    """
    
    def __init__(self, league_config: LeagueConfig = LeagueConfig):
        """
        Initializes an NFLScheduler with the given league settings.
        This will also build the LP problem into the attribute 'problem'.
        """
        self.self.league_config = league_config
        self._gen_problem()

    def _gen_problem(self) -> None:
        """Creates a Pulp LP Problem, fixing constraints matching the given league config.
        
        EFFECT: Stores the problem in the field self.problem. Stores the informative variables
        x and b, where x[home][away][week] is 1 if home plays away in the given week and 0
        otherwise, and b[team][week] is 1 if team has a bye week in the given week and 0
        otherwise.
        """
        
        ########### Problem formulation
        prob = pl.LpProblem('NFL_Scheduling', pl.LpMinimize)

        ########### Variables

        # Binary Variable for Every Possible Matchup, in any Week, and any Time Slot
        x = pl.LpVariable.dicts("x", (self.league_config.teams, self.league_config.teams, self.league_config.weeks,
                                      self.league_config.time_slots), 0, 1, pl.LpBinary) # (home, away, week)

        # Bye Week Variable Definition - Binary for a given week
        b = pl.LpVariable.dicts("b", (self.league_config.teams, self.league_config.weeks), 0, 1, pl.LpBinary)

        ############ Constraints

        # No team plays itself
        prob += pl.lpSum(x[team][team][w][s] for team in self.league_config.teams for w in self.league_config.weeks
                         for s in self.league_config.time_slots) == 0

        # Play home and away within division
        for team in self.league_config.teams:
            for conf_team in set(self.league_config.team_divisions[team]) - {team}:
                # They host the conference team
                prob += pl.lpSum(x[team][conf_team][w][s] for w in self.league_config.weeks for s in self.league_config.time_slots) == 1
        
                # They play the conference team away
                prob += pl.lpSum(x[conf_team][team][w][s] for w in self.league_config.weeks for s in self.league_config.time_slots) == 1
        
        # Play teams from a different conference and division
        for team in self.league_config.teams:
            for other_conf_team in self.league_config.other_div_other_conf_matchups[team]:
                # They play the conference team either home or away ocne
                prob += pl.lpSum(x[team][other_conf_team][w][s] + x[other_conf_team][team][w][s] 
                                 for w in self.league_config.weeks for s in self.league_config.time_slots) == 1
        
        ## 2 at home, 2 on the road
        for team in self.league_config.teams:
            # 2 home
            prob += pl.lpSum(x[team][other_conf_team][w][s] for other_conf_team in self.league_config.other_div_other_conf_matchups[team]
                             for w in self.league_config.weeks for s in self.league_config.time_slots) == 2
    
            # 2 away
            prob += pl.lpSum(x[other_conf_team][team][w][s] for other_conf_team in self.league_config.other_div_other_conf_matchups[team]
                             for w in self.league_config.weeks for s in self.league_config.time_slots) == 2

        # Play teams from another conference in the same division
        for team in self.league_config.teams:
            for other_conf_team in self.league_config.other_div_same_conf_matchups[team]:
                # They play the conference team either home or away ocne
                prob += pl.lpSum(x[team][other_conf_team][w][s] + x[other_conf_team][team][w][s] for w in self.league_config.weeks
                                 for s in self.league_config.time_slots) == 1
        
        ## 2 at home, 2 on the road
        for team in self.league_config.teams:
            # 2 home
            prob += pl.lpSum(x[team][other_conf_team][w][s] for other_conf_team in self.league_config.other_div_same_conf_matchups[team]
                             for w in self.league_config.weeks for s in self.league_config.time_slots) == 2

            # 2 away
            prob += pl.lpSum(x[other_conf_team][team][w][s] for other_conf_team in self.league_config.other_div_same_conf_matchups[team]
                             for w in self.league_config.weeks for s in self.league_config.time_slots) == 2


#       2 Games against teams from either remaining conference within the division
        for team in self.league_config.teams:
            for other_conf_team in set(self.league_config.team_divisions[team]) - set(self.league_config.team_conferences[team]) - set(self.league_config.other_div_same_conf_matchups[team]):
                # They play the conference team either home or away ocne
                prob += pl.lpSum(x[team][other_conf_team][w][s] + x[other_conf_team][team][w][s] for w in self.league_config.weeks
                                 for s in self.league_config.time_slots) <= 1
        
        # exactly 1 home, 1 away
        for team in self.league_config.teams:
            # 1 home
            prob += pl.lpSum(x[team][other_conf_team][w][s] for other_conf_team in set(self.league_config.team_divisions[team]) - set(self.league_config.team_conferences[team]) - set(self.league_config.other_div_same_conf_matchups[team])
                             for w in self.league_config.weeks for s in self.league_config.time_slots) == 1
    
            # 1 away
            prob += pl.lpSum(x[other_conf_team][team][w][s] for other_conf_team in set(self.league_config.team_divisions[team]) - set(self.league_config.team_conferences[team]) - set(self.league_config.other_div_same_conf_matchups[team])
                             for w in self.league_config.weeks for s in self.league_config.time_slots) == 1

        # 1 more game against a team from another division and conference
        for team in self.league_config.teams:
            prob += pl.lpSum(x[team][other_team][w][s] + x[other_team][team][w][s] for other_team in set(self.league_config.teams) - set(self.league_config.team_divisions[team]) - set(self.league_config.other_div_other_conf_matchups[team])
                             for w in self.league_config.weeks for s in self.league_config.time_slots) == 1
    
        # No repeated matchups
        for team in self.league_config.teams:
            for other_team in set(self.league_config.team) - {team}:
                for week in self.league_config.weeks:
                    prob += pl.lpSum(x[team][other_team][week][s] for s in self.league_config.time_slots) + pl.lpSum(x[team][other_team][week + 1][s] for s in self.league_config.time_slots) <= 1
                    prob += pl.lpSum(x[team][other_team][week][s] for s in self.league_config.time_slots) + pl.lpSum(x[other_team][team][week + 1][s] for s in self.league_config.time_slots) <= 1
                    prob += pl.lpSum(x[other_team][team][week][s] for s in self.league_config.time_slots) + pl.lpSum(x[team][other_team][week + 1][s] for s in self.league_config.time_slots) <= 1
                    prob += pl.lpSum(x[other_team][team][week][s] for s in self.league_config.time_slots) + pl.lpSum(x[other_team][team][week + 1][s] for s in self.league_config.time_slots) <= 1
            
        # No more than max_primetime_slots primetime slots per team
        for team in self.league_config.teams:
            prob += pl.lpSum(x[team][other_team][w][s] + x[other_team][team][w][s] for w in self.league_config.weeks for other_team in self.league_config.teams for s in self.league_config.primetime_slots) <= self.league_config.max_primetime_slots

        # Number of Games per Time Slot
        # Per week, 1 TNF, 1 SNF, 1 MNF, 4 Afternoon, rest early
        for week in self.league_config.weeks:
            # TNF
            prob += pl.lpSum(x[home][away][week]['Thursday Night'] for home in self.league_config.teams for away in self.league_config.teams) == 1
    
            # Sunday Afternoon
            prob += pl.lpSum(x[home][away][week]['Sunday Afternoon'] for home in self.league_config.teams for away in self.league_config.teams) == 4
    
            # SNF
            prob += pl.lpSum(x[home][away][week]['Sunday Night'] for home in self.league_config.teams for away in self.league_config.teams) == 1
    
            # MNF
            prob += pl.lpSum(x[home][away][week]['Monday Night'] for home in self.league_config.teams for away in self.league_config.teams) == 1
    
        # SB Winner Must Play first game home
        prob += pl.lpSum(x[self.league_config.sb_winner][away][1][self.league_config.time_slots[0]] for away in self.league_config.teams) == 1

        # byes_per_team Byes per team
        for team in self.league_config.teams:
            prob += pl.lpSum(b[team][w] for w in self.league_config.weeks) == self.league_config.byes_per_team
    
        # Bye week falls in valid range
        for team in self.league_config.teams:
            prob += pl.lpSum(b[team][w] for w in range(1, self.league_config.min_bye)) == 0
            prob += pl.lpSum(b[team][w] for w in range(self.league_config.max_bye + 1, self.league_config.num_weeks + 1)) == 0
    
        # Same number of teams per bye week

        # Bye weeks evenly distributed for each week, i.e. for each eligible bye week, if k = len(teams) / (max_bye - min_bye + 1),
        # there are between floor(k) and ceil(k) teams on bye
        k = len(self.league_config.teams) / (self.league_config.max_bye - self.league_config.min_bye + 1)

        for bye in range(self.league_config.min_bye, self.league_config.max_bye + 1):
            prob += pl.lpSum(b[team][bye] for team in self.league_config.teams) >= math.floor(k)
            prob += pl.lpSum(b[team][bye] for team in self.league_config.teams) <= math.ceil(k)

        # Team must be either on bye, home, or away
        for team in self.league_config.teams:
            for week in self.league_config.weeks:
                prob += pl.lpSum(x[team][other_team][week][s] + x[other_team][team][week][s] for other_team in self.league_config.teams for s in self.league_config.time_slots) + b[team][week] == 1

        ############# Objective Function

        # Balance team schedules - minimized maximum difference in total opponent rankings from mean
        d = pl.LpVariable("d") # the max difference in total oppponent rankings

        # Abstract away SOS calculation into variables
        s = pl.LpVariable.dicts("s", (self.league_config.teams))

        s_hat = pl.LpVariable("s_hat")

        # Calculate team SOS's once
        for team in self.league_config.teams:
            prob += s[team] == pl.lpSum(self.league_config.ratings_map[o]*x[team][o][w][s] + self.league_config.ratings_map[o]*x[o][team][w][s] for o in self.league_config.teams for w in self.league_config.weeks for s in self.league_config.time_slots)
    
        # Calculare mean SOS once
        prob += s_hat == (1/len(self.league_config.teams))*pl.lpSum(s[t] for t in self.league_config.teams)

        # d >= s_i - s_hat, i.e. it's the max difference
        for team in self.league_config.teams:
            prob += d >= s[team] - s_hat
            prob += d >= -(s[team] - s_hat)

        prob += d
        
        self.problem = prob
        self._x = x
        self._b = b
        
    def solve(self, solver) -> pd.DataFrame:
        """
        Solves the problem with the given solver, returning the produced
        schedule as a pandas dataframe with a row for each team and a column
        for each week.
        """
        self.problem.solve(solver)
               
        # Get schedule for each team - output pandas dataframe with each week as a column and each team as a row.
        week_to_matchup = {wk:["BYE"]*len(self.league_config.teams) for wk in self.league_config.weeks} # Pre-fill with byes; replace with the matchups

        for week in self.self.league_config.weeks:
            for i, team in enumerate(self.self.league_config.teams):
                if self._b[team][week].value() == 1: # Bye?
                    continue # already filled with bye
                else:
                    # Otherwise, they must be playing a game
                    for other_team in self.self.league_config.teams:
                        found=False # To break multiple fors once found
                        for slot in self.self.league_config.time_slots:   
                            if self._x[team][other_team][week][slot].value() == 1:
                                week_to_matchup[week][i] = f"{slot} vs {other_team}"
                                found=True
                                break
                
                            if self._x[other_team][team][week][slot].value() == 1:
                                week_to_matchup[week][i] = f"{slot} @ {other_team}"
                                found=True
                                break 
                            
                        if found:
                            break

        schedule_df = pd.DataFrame(week_to_matchup)
        schedule_df.insert(0, "Team", list(self.league_config.teams))
        schedule_df = schedule_df.set_index("Team")
        return schedule_df