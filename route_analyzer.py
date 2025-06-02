from router import Router
import pandas as pd
from data_import import RoutingData
from pathlib import Path
import base64
from io import BytesIO

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt



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
        self.df.loc['Total'] = self.df.sum()

        self.df['travel_percent'] = self.df['travel_minutes'] / (self.df['budget_minutes'] * 4)



        print(self.df[['travel_percent','budget_minutes','travel_minutes']])

        print(self.df)


    def plot_route(self):
        data = {'x':[0], 'y':[0], 'c':[0]}
        for i in range(len(self.df) - 1):
            route = self.df['route'].iloc[i]
            _x = []
            _y = []
            _c = []
            for location in route:

                _x.append(self.rd.df['x'].iloc[location])
                _y.append(self.rd.df['y'].iloc[location])
                _c.append(i+1)
            plt.plot(_x, _y, label=i+1, marker='o', linestyle='-')
                # data['x'].append(_x)
                # data['y'].append(_y)
                # data['c'].append(i + 1)

        #plt.scatter(data['x'], data['y'], c=data['c'], cmap="tab20")

        plt.title("Team Distribution Plot")
        plt.legend()

        # Save the figure to a buffer
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        base64_str = base64.b64encode(buf.read()).decode('utf-8')
        data_uri = f"data:image/png;base64,{base64_str}"

        #plt.show()

        return data_uri


if __name__ == "__main__":


    data_path: Path = Path(__file__).resolve().parent / "data/test_data3.csv"

    ra = RouteAnalyzer(8, 26, data_path)

    ra.plot_route()