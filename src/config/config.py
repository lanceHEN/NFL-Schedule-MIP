"""Contains data classes useful for configuring league information,
as well as solver settings."""

from dataclasses import dataclass, field
from typing import Dict, Iterable, Tuple

@dataclass
class LeagueConfig:
    """Stores league setting information. The NFL league structure may change,
    so this allows for necessary adaptions."""
    
    # Week info
    num_weeks: int = 18 # including bye
    weeks: Iterable[int] = field(init=False)
    
    # Time slot info
    time_slots: Iterable[str] = field(default_factory=lambda: {'Thursday Night'
                                                               'Sunday Morning',
                                                               'Sunday Afternoon',
                                                               'Sunday Night',
                                                               'Monday Night'})
    primetime_slots: Iterable[str] = field(default_factory=lambda: {'Thursday Night'
                                                               'Sunday Night',
                                                               'Monday Night'})
    max_primetime_slots: int = 6
    
    # Bye info
    min_bye: int = 5
    max_bye: int = 14
    
    # Conference info
    conferences: Iterable[str] = field(default_factory=lambda: {'NFC', 'AFC'})
    conference_divisions: Dict[str, Iterable[str]] = field(default_factory=lambda: {
        'NFC': {'NFC North', 'NFC East', 'NFC South', 'NFC West'},
        'AFC': {'AFC North', 'AFC East', 'AFC South', 'AFC West'}})
    
    # Region info
    region_divisions: Dict[str, Iterable[str]] = field(default_factory=lambda: {
        "North": {"NFC North", "AFC North"},
        "South": {"NFC South", "AFC South"},
        "East": {"NFC East", "AFC East"},
        "West": {"NFC West", "AFC West"},
    })
    region_matchups: Iterable[Tuple[str, str]] = field(default_factory=lambda: {
        ("North, South"),
        ("East", "West")
    })
    
    # Division Info
    division_conferences = field(init=False)
    other_div_other_conf_matchups: Dict[str, str] = field(init=False) # Team -> Conf
    other_div_same_conf_matchups: Dict[str, str] = field(init=False) # Team -> Conf
    division_teams: Dict[str, Iterable[str]] = field(default_factory=lambda: {
    "NFC North": {"Packers", "Lions", "Vikings", "Bears"},
    "NFC East": {"Giants", "Cowboys", "Eagles", "Commanders"},
    "NFC South": {"Panthers", "Saints", "Falcons", "Buccaneers"},
    "NFC West": {"Seahawks", "49ers", "Rams", "Cardinals"},
    "AFC North": {"Bengals", "Browns", "Ravens", "Steelers"},
    "AFC East": {"Patriots", "Bills", "Dolphins", "Jets"},
    "AFC South": {"Texans", "Titans", "Jaguars", "Colts"},
    "AFC West": {"Chiefs", "Chargers", "Broncos", "Raiders"}
    })
    
    # Team info
    all_teams: Iterable[str] = field(init=False)
    team_divisions: Dict[str, str] = field(init=False)
    team_conferences: Dict[str, str] = field(init=False)
    team_elos: Dict[str, float] = field(default_factory=lambda: {
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
    })
    sb_winner: str = "Eagles"
    
    def __post_init__(self):
        """Additional utilities automatically created from given parameters."""
        self.weeks = range(1, self.num_weeks + 1)
        self.division_conferences = {div: conf for conf in self.conferences for div in self.conference_divisions[conf]}
        self.all_teams = set(t for v in self.division_teams.values() for t in v)
        self.team_divisions = {team: div for div in self.division_teams for team in self.division_teams[div]}
        self.team_conferences = {team: conf for conf in self.conference_divisions for div in self.conference_divisions[conf] for team in self.division_teams[div]}
        
        self.other_div_other_conf_matchups = {}
        self.other_div_same_conf_matchups = {}
        for r1, r2 in self.region_matchups:
            for d1 in self.region_divisions[r1]:
                for d2 in self.region_divisions[r2]:
                    if self.division_conferences[d1] == self.division_conferences[d2]: # same conference
                        map_to_add = self.other_div_same_conf_matchups
                    else:
                        map_to_add = self.other_div_other_conf_matchups
                        
                    for t1 in d1:
                        map_to_add[t1] = d2
                    
                    for t2 in d2:
                        map_to_add[t2] = d1
                        