from pathlib import Path
from io import StringIO
import pandas as pd
import matplotlib.pyplot as plt
import math

class RoutingData:

    # O(n)
    def __init__(self, data:Path|str):

        if type(data) == str:
            self.df = pd.read_csv(StringIO(data))
        else:
            self.df = pd.read_csv(data)

        self._normalize_coordinates()

        self._generate_distance_matrix()




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

