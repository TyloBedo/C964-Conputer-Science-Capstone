import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot as plt
import matplotlib.ticker as mtick


def scatter_locations(df) -> str:

    plt.scatter(df['x'], df['y'])

    plt.scatter(0, 0, color='red')
    plt.text(-1, 1, "Dispatch Location")

    plt.title("Job Distribution Plot")
    plt.grid(True)
    plt.xlabel("Miles")
    plt.ylabel("Miles")

    return get_plot_image()


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

    return get_plot_image()


def labor_percentage(df):

    fig, ax = plt.subplots()
    bars = ax.bar(df['team'], df['travel_percent'])
    ax.yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0))
    ax.bar_label(bars, labels=[f'{x.get_height():.02%}' for x in bars])

    plt.axhline(y=.1, color='r', linestyle='--')
    plt.ylim(0, .15)

    plt.title("Estimated Labor Percentage Per Team")
    plt.xlabel("Team")
    plt.ylabel("Labor Percentage")


    return get_plot_image()




def get_plot_image():

    # Save the figure to a buffer
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)

    base64_str:str = base64.b64encode(buf.read()).decode('utf-8')
    data_uri:str = f"data:image/png;base64,{base64_str}"
    plt.clf()

    return data_uri
