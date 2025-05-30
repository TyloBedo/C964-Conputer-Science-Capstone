from pathlib import Path

import pandas
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import math


# O(n)
def load_data(data_path:Path|str|None = None) -> pd.DataFrame:
    """ Loads data from CSV file. Uses default data if none is provided."""
    if not data_path:
        data_path: Path = Path(__file__).resolve().parent / "data/data.csv"

    df = pd.read_csv(data_path)

    # normalize coordinates so home location is centered 0.0, 0.0

    lon_offset:float = df.loc[df['location'] == 'home', 'lon'].iloc[0]
    lat_offset:float = df.loc[df['location'] == 'home', 'lat'].iloc[0]

    # 1 degree of Longitude = cosine (latitude in radians) * length of degree (miles) at equator
    lat_miles:float = 69.17
    lon_miles:float = math.cos(math.radians(lat_offset)) * lat_miles

    df['x'] = (df['lon'] - lon_offset) * lon_miles
    df['y'] = (df['lat'] - lat_offset) * lat_miles

    return df


# O(n^2) we do exit the loop early but it is still not logarithmic.
def generate_distance_matrix(df:pd.DataFrame) -> pd.DataFrame:

    n:int = len(df)
    matrix:np.ndarray = np.zeros((n, n))

    for l1 in range(n):
        for l2 in range(n):
            # Early exit condition; matrix is mirrored so we do not need to continue past l2 == l1
            if l2 > l1:
                break

            distance:float = manhattan_distance(df.iloc[l1].loc['x'], df.iloc[l1].loc['y'],
                                                df.iloc[l2].loc['x'], df.iloc[l2].loc['y'])
            matrix[l1, l2] = distance
            matrix[l2, l1] = distance

    return pandas.DataFrame(matrix, index=df['location'], columns=df['location'])


#O(n)
def manhattan_distance(x1:float, y1:float, x2:float, y2:float) -> float:
    """ Returns the Manhattan distance between two points. """
    return abs(x1 - x2) + abs(y1 - y2)




def plot_locations(df:pd.DataFrame) -> None:

    plt.scatter(df['x'], df['y'])

    # for i, label in enumerate(df['location']):
    #     plt.annotate(label, (df['x'][i], df['y'][i]))

    plt.show()


if __name__ == "__main__":
    _df = load_data()

    #dm = generate_distance_matrix(_df)
    #print(dm)

    plot_locations(_df)