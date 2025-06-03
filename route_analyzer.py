from router import Router
import pandas as pd
from routing_data import RoutingData


class RouteAnalyzer:


    def __init__(self, teams:int, emp:int, data:str):
        self.rd = RoutingData(teams, emp, data)

        route = Router(self.rd)
        route.solve()

        self.df = pd.DataFrame.from_records(route.routes)
        self.df['people_distance'] = self.df['distance'] * self.df['team_size']
        self.df['travel_minutes'] = self.df['people_distance'] * 2
        self.df['travel_percent'] = self.df['travel_minutes'] / (self.df['budget_minutes'] * 4)
        self.df['route_string'] = self.df['route'].apply(self.get_route_string)


    def get_route_string(self, route):
        route_string: str = ""
        for location in route:
            name = self.rd.df.loc[location, 'location']
            route_string += f"{name} -> "
        return route_string[:-4]



if __name__ == "__main__":

    from pathlib import Path
    data_path: Path = Path(__file__).resolve().parent / "data/test_data3.csv"

    with open(data_path, 'r') as file:
        ra = RouteAnalyzer(8, 26, file.read())

        print(ra.df)
