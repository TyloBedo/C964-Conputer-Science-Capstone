import base64
from io import BytesIO

import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt


def scatter_locations(df) -> str:
    plt.scatter(df['x'], df['y'])

    plt.scatter(0, 0, color='red')
    plt.text(-1, 1, "Dispatch Location")

    plt.title("Job Distribution Plot")
    plt.grid(True)
    plt.xlabel("Miles")
    plt.ylabel("Miles")

    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    base64_str:str = base64.b64encode(buf.read()).decode('utf-8')
    data_uri:str = f"data:image/png;base64,{base64_str}"
    plt.clf()

    return data_uri


def plot_route(df, df2) -> str:

    for i in range(len(df)):
        route = df['route'].iloc[i]
        _x = []
        _y = []
        for location in route:
            _x.append(df2['x'].iloc[location])
            _y.append(df2['y'].iloc[location])
        plt.plot(_x, _y, label=f"Team {df['team'].iloc[i] + 1}", marker='o', linestyle='-')


    plt.title("Team Distribution Plot")
    plt.grid(True)
    plt.xlabel("Miles")
    plt.ylabel("Miles")
    plt.legend()

    # Save the figure to a buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    base64_str:str = base64.b64encode(buf.read()).decode('utf-8')
    data_uri:str = f"data:image/png;base64,{base64_str}"
    plt.clf()

    return data_uri