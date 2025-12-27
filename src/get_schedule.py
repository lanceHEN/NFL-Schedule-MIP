# Define the LP problem
import pulp as pl
import pickle as pkl
from constants import *
import pandas as pd

########### Problem formulation
prob = pl.LpProblem('NFL_Scheduling', pl.LpMinimize)

########### Variables

# Binary Variable for Every Possible Matchup, in any Week, and any Time Slot
x = pl.LpVariable.dicts("x", (TEAMS, TEAMS, WEEKS, TIME_SLOTS), 0, 1, pl.LpBinary) # (home, away, week)

# Bye Week Variable Definition - Binary for a given week
b = pl.LpVariable.dicts("b", (TEAMS, WEEKS), 0, 1, pl.LpBinary)

############ Constraints

# No team plays itself
prob += pl.lpSum(x[team][team][w][s] for team in TEAMS for w in WEEKS for s in TIME_SLOTS) == 0

# Play home and away within conference
for team in TEAMS:
    for conf_team in CONFERENCE_MAP[team] - {team}:
        # They host the conference team
        prob += pl.lpSum(x[team][conf_team][w][s] for w in WEEKS for s in TIME_SLOTS) == 1
        
        # They play the conference team away
        prob += pl.lpSum(x[conf_team][team][w][s] for w in WEEKS for s in TIME_SLOTS) == 1
        
# Play teams from a different conference and division
for team in TEAMS:
    for other_conf_team in INTER_CONFERENCE_OTHER_DIV_MAP[team]:
        # They play the conference team either home or away ocne
        prob += pl.lpSum(x[team][other_conf_team][w][s] + x[other_conf_team][team][w][s] for w in WEEKS for s in TIME_SLOTS) == 1
        
## 2 at home, 2 on the road
for team in TEAMS:
    # 2 home
    prob += pl.lpSum(x[team][other_conf_team][w][s] for other_conf_team in INTER_CONFERENCE_OTHER_DIV_MAP[team] for w in WEEKS for s in TIME_SLOTS) == 2
    
    # 2 away
    prob += pl.lpSum(x[other_conf_team][team][w][s] for other_conf_team in INTER_CONFERENCE_OTHER_DIV_MAP[team] for w in WEEKS for s in TIME_SLOTS) == 2

# Play teams from another conference in the same division
for team in TEAMS:
    for other_conf_team in INTER_CONFERENCE_SAME_DIV_MAP[team]:
        # They play the conference team either home or away ocne
        prob += pl.lpSum(x[team][other_conf_team][w][s] + x[other_conf_team][team][w][s] for w in WEEKS for s in TIME_SLOTS) == 1
        
## 2 at home, 2 on the road
for team in TEAMS:
    # 2 home
    prob += pl.lpSum(x[team][other_conf_team][w][s] for other_conf_team in INTER_CONFERENCE_SAME_DIV_MAP[team] for w in WEEKS for s in TIME_SLOTS) == 2

    # 2 away
    prob += pl.lpSum(x[other_conf_team][team][w][s] for other_conf_team in INTER_CONFERENCE_SAME_DIV_MAP[team] for w in WEEKS for s in TIME_SLOTS) == 2


# 2 Games against teams from either remaining conference within the division
for team in TEAMS:
    for other_conf_team in DIV_MAP[team] - CONFERENCE_MAP[team] - INTER_CONFERENCE_SAME_DIV_MAP[team]:
        # They play the conference team either home or away ocne
        prob += pl.lpSum(x[team][other_conf_team][w][s] + x[other_conf_team][team][w][s] for w in WEEKS for s in TIME_SLOTS) <= 1
        
# exactly 1 home, 1 away
for team in TEAMS:
    # 1 home
    prob += pl.lpSum(x[team][other_conf_team][w][s] for other_conf_team in DIV_MAP[team] - CONFERENCE_MAP[team] - INTER_CONFERENCE_SAME_DIV_MAP[team] for w in WEEKS for s in TIME_SLOTS) == 1
    
    # 1 away
    prob += pl.lpSum(x[other_conf_team][team][w][s] for other_conf_team in DIV_MAP[team] - CONFERENCE_MAP[team] - INTER_CONFERENCE_SAME_DIV_MAP[team] for w in WEEKS for s in TIME_SLOTS) == 1

# 1 more game against a team from another division and conference
for team in TEAMS:
    prob += pl.lpSum(x[team][other_team][w][s] + x[other_team][team][w][s] for other_team in TEAMS - DIV_MAP[team] - INTER_CONFERENCE_OTHER_DIV_MAP[team] for w in WEEKS for s in TIME_SLOTS) == 1
    
# No repeated matchups
for team in TEAMS:
    for other_team in TEAMS - {team}:
        for week in range(1, NUM_WEEKS):
            prob += pl.lpSum(x[team][other_team][week][s] for s in TIME_SLOTS) + pl.lpSum(x[team][other_team][week + 1][s] for s in TIME_SLOTS) <= 1
            prob += pl.lpSum(x[team][other_team][week][s] for s in TIME_SLOTS) + pl.lpSum(x[other_team][team][week + 1][s] for s in TIME_SLOTS) <= 1
            prob += pl.lpSum(x[other_team][team][week][s] for s in TIME_SLOTS) + pl.lpSum(x[team][other_team][week + 1][s] for s in TIME_SLOTS) <= 1
            prob += pl.lpSum(x[other_team][team][week][s] for s in TIME_SLOTS) + pl.lpSum(x[other_team][team][week + 1][s] for s in TIME_SLOTS) <= 1
            
# No more than 6 primetime slots per team
for team in TEAMS:
    prob += pl.lpSum(x[team][other_team][w][s] + x[other_team][team][w][s] for w in WEEKS for other_team in TEAMS for s in PRIMETIME_SLOTS) <= 6

# Number of Games per Time Slot
# Per week, 1 TNF, 1 SNF, 1 MNF, 4 Afternoon, rest early
for week in WEEKS:
    # TNF
    prob += pl.lpSum(x[home][away][week]['Thursday Night'] for home in TEAMS for away in TEAMS) == 1
    
    # Sunday Afternoon
    prob += pl.lpSum(x[home][away][week]['Sunday Afternoon'] for home in TEAMS for away in TEAMS) == 4
    
    # SNF
    prob += pl.lpSum(x[home][away][week]['Sunday Night'] for home in TEAMS for away in TEAMS) == 1
    
    # MNF
    prob += pl.lpSum(x[home][away][week]['Monday Night'] for home in TEAMS for away in TEAMS) == 1
    
# SB Winner Must Play first TNF Game home
prob += pl.lpSum(x['Eagles'][away][1]['Thursday Night'] for away in TEAMS) == 1

# 1 Bye per team
for team in TEAMS:
    prob += pl.lpSum(b[team][w] for w in WEEKS) == 1
    
# Bye week falls in valid range
for team in TEAMS:
    prob += pl.lpSum(b[team][w] for w in range(1, MIN_BYE)) == 0
    prob += pl.lpSum(b[team][w] for w in range(MAX_BYE + 1, NUM_WEEKS + 1)) == 0
    
# Same number of teams per bye week

# Bye weeks evenly distributed for each week, i.e. for each eligible bye week, there are len(teams) / (max_bye - min_bye + 1) teams on bye
teams_per_bye = len(TEAMS) / (MAX_BYE - MIN_BYE + 1)

for bye in range(MIN_BYE, MAX_BYE + 1):
    prob += pl.lpSum(b[team][bye] for team in TEAMS) == teams_per_bye

# Team must be either on bye, home, or away
for team in TEAMS:
    for week in WEEKS:
        prob += pl.lpSum(x[team][other_team][week][s] + x[other_team][team][week][s] for other_team in TEAMS for s in TIME_SLOTS) + b[team][week] == 1

############# Objective Function

# Balance team schedules - minimized maximum difference in total opponent rankings from mean
d = pl.LpVariable("d") # the max difference in total oppponent rankings

# Abstract away SOS calculation into variables
s = pl.LpVariable.dicts("s", (TEAMS))

s_hat = pl.LpVariable("s_hat")

# Calculate team SOS's once
for team in TEAMS:
    prob += s[team] == pl.lpSum(RATINGS_MAP[o]*x[team][o][w][s] + RATINGS_MAP[o]*x[o][team][w][s] for o in TEAMS for w in WEEKS for s in TIME_SLOTS)
    
# Calculare mean SOS once
prob += s_hat == (1/len(TEAMS))*pl.lpSum(s[t] for t in TEAMS)

# d >= s_i - s_hat, i.e. it's the max difference
for team in TEAMS:
    prob += d >= s[team] - s_hat
    prob += d >= -(s[team] - s_hat)

prob += d

######### Solve with Gurobi - up to 10 mins
status = prob.solve(pl.GUROBI(
    msg=True,
    Threads=0,
    MIPFocus=1,
    Heuristics=0.3,
    Cuts=-1,
    Symmetry=2,
    Presolve=2,
    Method=-1,
    MIPGap=0.02, timeLimit=600))

print("Status:", pl.LpStatus[status])
print("Objective value:", pl.value(prob.objective))

# Get schedule for each team - output pandas dataframe with each week as a column and each team as a row.
week_to_matchup = {wk:["BYE"]*len(TEAMS) for wk in WEEKS} # Pre-fill with byes; replace with the matchups

for week in WEEKS:
    for i, team in enumerate(TEAMS_LIST):
        if b[team][week].value() == 1: # Bye?
            continue # already filled with bye
        else:
            # Otherwise, they must be playing a game
            for other_team in TEAMS:
                found=False # To break multiple fors once found
                for slot in TIME_SLOTS:   
                    if x[team][other_team][week][slot].value() == 1:
                        week_to_matchup[week][i] = f"vs {other_team}"
                        found=True
                        break
                
                    if x[other_team][team][week][slot].value() == 1:
                        week_to_matchup[week][i] = f"@ {other_team}"
                        found=True
                        break
                    
                if found:
                    break

# Ensure can display entire table
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
schedule_df = pd.DataFrame(week_to_matchup)
schedule_df.insert(0, "Team", TEAMS_LIST)
schedule_df.set_index("Team")
print(schedule_df)