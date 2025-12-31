"""This is a small script showing an examplar process of
getting an NFL schedule."""

import pulp as pl

from config import LeagueConfig
from model import NFLScheduler


def main():
    # Set up config
    
    # Maybe we want to add an additional weeks and give each team 2 byes.
    conf = LeagueConfig(min_bye=5, max_bye=16, byes_per_team=2)

    scheduler = NFLScheduler(conf)

    # Use Gurobi solver with 1 hour max time
    solver = pl.GUROBI(
        msg=True,
        Threads=0,
        MIPFocus=1,
        Heuristics=0.3,
        Cuts=-1,
        Symmetry=2,
        Presolve=2,
        Method=-1,
        MIPGap=0.02,
        timeLimit=6000,
    )

    # Get the schedule
    schedule = scheduler.solve(solver)

    print(schedule)


if __name__ == "__main__":
    main()
