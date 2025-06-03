from router import Router
import pandas as pd
from routing_data import RoutingData
from pathlib import Path



class RouteAnalyzer:


    def __init__(self, teams:int, emp:int, data_path:Path|str):
        self.teams = teams
        self.emp = emp

        self.rd = RoutingData(self.teams, self.emp, data_path)

        self.route = Router(self.rd)

        self.route.solve()

        self.routes = self.route.routes

        self.df = pd.DataFrame.from_records(self.routes)
        self.df['people_distance'] = self.df['distance'] * self.df['team_size']
        self.df['travel_minutes'] = self.df['people_distance'] * 2
      #  self.df.loc['Total'] = self.df.sum()

        self.df['travel_percent'] = self.df['travel_minutes'] / (self.df['budget_minutes'] * 4)


        self.df['route_string'] = self.df['route'].apply(self.get_route_string)


        #print(self.df)

    def get_route_string(self, route):
        route_string: str = ""
        for location in route:
            name = self.rd.df.loc[location, 'location']
            route_string += f"{name} -> "
        return route_string[:-4]



if __name__ == "__main__":


    data_path: Path = Path(__file__).resolve().parent / "data/test_data3.csv"

    ra = RouteAnalyzer(8, 26, data_path)
