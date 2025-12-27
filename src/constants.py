# Define important NFL constants

# Weeks
NUM_WEEKS = 18 # including bye
WEEKS = range(1,NUM_WEEKS+1)

# Time slots
TIME_SLOTS = ['Thursday Night', 'Sunday Morning', 'Sunday Afternoon', 'Sunday Night', 'Monday Night']
PRIMETIME_SLOTS = list(set(TIME_SLOTS) - {'Sunday Morning', 'Sunday Afternoon'})

# Bye constraints
MIN_BYE = 5
MAX_BYE = 12

# Teams - Conferences and Divisions
NFC_NORTH = {'Packers', 'Lions', 'Vikings', 'Bears'}
NFC_EAST = {'Giants', 'Cowboys', 'Eagles', 'Commanders'}
NFC_SOUTH = {'Panthers', 'Saints', 'Falcons', 'Buccaneers'}
NFC_WEST = {'Seahawks', '49ers', 'Rams', 'Cardinals'}

AFC_NORTH = {'Bengals', 'Browns', 'Ravens', 'Steelers'}
AFC_EAST = {'Patriots', 'Bills', 'Dolphins', 'Jets'}
AFC_SOUTH = {'Texans', 'Titans', 'Jaguars', 'Colts'}
AFC_WEST = {'Chiefs', 'Chargers', 'Broncos', 'Raiders'}

NFC_CONFS = [NFC_NORTH, NFC_EAST, NFC_SOUTH, NFC_WEST]

AFC_CONFS = [AFC_NORTH, AFC_EAST, AFC_SOUTH, AFC_WEST]

CONFERENCES = NFC_CONFS + AFC_CONFS

NFC_TEAMS = NFC_NORTH | NFC_EAST | NFC_SOUTH | NFC_WEST
AFC_TEAMS = AFC_NORTH | AFC_EAST | AFC_SOUTH | AFC_WEST
TEAMS = NFC_TEAMS | AFC_TEAMS
TEAMS_LIST = list(TEAMS)
#TEAMS_TO_LIST_IDX = {t: i for i, t in enumerate(TEAMS_LIST)}

# Map team to division - NFC or AFC
DIV_MAP = {team: NFC_TEAMS for team in NFC_TEAMS}
DIV_MAP.update({team: AFC_TEAMS for team in AFC_TEAMS})

# Mapping of conferences
CONFERENCE_MAP = dict()
for conf in CONFERENCES:
    for team in conf:
        CONFERENCE_MAP[team] = conf

# Initial ratings - Useful for making balanced schedules in the problem, and for starting season simulation
RATINGS_MAP = {
 'Eagles': 1629,
 'Ravens': 1678,
 'Bills': 1632,
 'Chiefs': 1587,
 'Lions': 1592,
 'Packers': 1594,
 'Commanders': 1563,
 'Vikings': 1531,
 'Broncos': 1537,
 'Rams': 1539,
 'Bengals': 1536,
 'Buccaneers': 1525,
 'Texans': 1496,
 'Seahawks': 1489,
 'Chargers': 1545,
 'Steelers': 1515,
 'Dolphins': 1454,
 '49ers': 1480,
 'Cowboys': 1486,
 'Cardinals': 1524,
 'Colts': 1479,
 'Jets': 1439,
 'Falcons': 1480,
 'Bears': 1480,
 'Saints': 1346,
 'Jaguars': 1466,
 'Raiders': 1460,
 'Patriots': 1416,
 'Browns': 1346,
 'Panthers': 1353,
 'Giants': 1374,
 'Titans': 1375
}

# Mapping of inter-conference matchups - different divisions
INTER_CONFERENCE_OTHER_DIV_MAP = dict()

INTER_CONFERENCE_OTHER_DIV_MATCHUPS = [(NFC_NORTH, AFC_NORTH), (NFC_EAST, AFC_EAST), (NFC_SOUTH, AFC_SOUTH), (NFC_WEST, AFC_WEST)]

for conf_matchup in INTER_CONFERENCE_OTHER_DIV_MATCHUPS:
    conf_teams = conf_matchup[0]
    opponent_conf_teams = conf_matchup[1]
    # conf teams play opponent conf teams
    for conf_team in conf_teams:
        INTER_CONFERENCE_OTHER_DIV_MAP[conf_team] = opponent_conf_teams
        
    # and opponent conf teams play conf teams
    for opponent_conf_team in opponent_conf_teams:
        INTER_CONFERENCE_OTHER_DIV_MAP[opponent_conf_team] = conf_teams
    
# Mapping of inter-conference matchups - same divisions
INTER_CONFERENCE_SAME_DIV_MAP = dict()

INTER_CONFERENCE_SAME_DIV_MATCHUPS = [(NFC_NORTH, NFC_SOUTH), (NFC_EAST, NFC_WEST), (AFC_NORTH, AFC_SOUTH), (AFC_EAST, AFC_WEST)]

for conf_matchup in INTER_CONFERENCE_SAME_DIV_MATCHUPS:
    conf_teams = conf_matchup[0]
    opponent_conf_teams = conf_matchup[1]
    # conf teams play opponent conf teams
    for conf_team in conf_teams:
        INTER_CONFERENCE_SAME_DIV_MAP[conf_team] = opponent_conf_teams
        
    # and opponent conf teams play conf teams
    for opponent_conf_team in opponent_conf_teams:
        INTER_CONFERENCE_SAME_DIV_MAP[opponent_conf_team] = conf_teams
        
        