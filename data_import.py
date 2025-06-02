from pathlib import Path
from typing import Callable
from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt
import math

class RoutingData:

    # O(n)
    def __init__(self, teams:int, emps:int, data:Path|str):

        if type(data) == str:
            self.df = pd.read_csv(StringIO(data))
        else:
            self.df = pd.read_csv(data)

        self._normalize_coordinates()

        self._generate_distance_matrix()

        self.teams:int = teams # vehicles,

        # demands is budget minutes per jobs.
        self.demands:list[int] = self.df['budget'].tolist()  #[20 for _ in range(len(self.distance_matrix))]

        total_demands:int = self.df['budget'].sum()

        # interestingly, demands * 1.1 gives better results sometimes
        # 300 is max cleaning minutes per person
        # 1.25 is a modifer because OT is okay.
        max_demand:float = 300 * 1.25

        if total_demands / emps > max_demand:
            # need some more testing on this. Doesn't catch all errors.
            raise CapacityError("Not enough employees!")


        # we need to figure out how to distribute 2 3 or 4 person teams
        # ideally we will also test different distributions...
        # for now lets just distribute out the employees we have..
        self.team_sizes = [emps // teams] * teams
        for i in range(emps % teams ):
            self.team_sizes[i] += 1

        self.capacities:list[int] = \
            [int(capacity * max_demand) for capacity in self.team_sizes]


    # O(n)
    def _normalize_coordinates(self):
        # normalize coordinates so home location is centered 0.0, 0.0
        home_longitude:float = self.df.loc[0, 'longitude']
        home_latitude:float = self.df.loc[0, 'latitude']

        # 1 degree of latitude = ~69.17 miles. Varies insignificantly based on distance from the equator.
        # 1 degree of Longitude = cosine(latitude in radians) * length of 1 degree of latitude at the equator.
        latitude_miles:float = 69.17
        longitude_miles:float = math.cos(math.radians(home_latitude)) * latitude_miles

        # convert coordinates to x, y as miles.
        self.df['x'] = ((self.df['longitude'] - home_longitude) * longitude_miles)
        self.df['y'] = ((self.df['latitude'] - home_latitude) * latitude_miles)



    # O(n^2) we do exit the loop early, but it is still not logarithmic.
    def _generate_distance_matrix(self):

        n:int = len(self.df)
        self.distance_matrix:list[list[float]] = [[0 for _ in range(n)] for _ in range(n)]

        for l1 in range(n):
            for l2 in range(n):
                # Early exit condition; matrix is mirrored so we do not need to continue past l2 == l1
                if l2 >= l1:
                    break

                distance:float = self._manhattan_distance(l1, l2)
                # Our routing algorthm only accepts int values.
                # Multiply distance by 100 to maintain precision.
                self.distance_matrix[l1][l2] = int(distance * 100)
                self.distance_matrix[l2][l1] = int(distance * 100)



    #O(n)
    def _manhattan_distance(self, l1:int, l2:int) -> float:
        """ Returns the Manhattan distance between two points. """
        x1 = self.df.iloc[l1].loc['x']
        y1 = self.df.iloc[l1].loc['y']
        x2 = self.df.iloc[l2].loc['x']
        y2 = self.df.iloc[l2].loc['y']
        return abs(x1 - x2) + abs(y1 - y2)


    #O(n)
    def plot_locations(self):
        plt.scatter(self.df['x'], self.df['y'])
        plt.show()

    @property
    def dm(self):
        return self.distance_matrix


class CapacityError(Exception):
    pass

if __name__ == "__main__":


    data_path: Path = Path(__file__).resolve().parent / "data/test_data1.csv"

    _teams = 8
    _emp = 26

    rd = RoutingData(_teams, _emp, data_path)

    #print(rd.distance_matrix)
    #  0 ->  20 ->  17 ->  9 -> 0
    print(rd.dm[0][20] / 100)
    print(rd.dm[20][17] / 100)
    print(rd.dm[17][9] / 100)
    print(rd.dm[9][0] / 100)

    #print(rd.demands)
    #print(rd.capacities)
    #rd.plot_locations()

    #print (rd.df.loc[0, ['latitude', 'longitude']])
