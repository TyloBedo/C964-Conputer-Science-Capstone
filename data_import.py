from pathlib import Path
import pandas as pd


def load_data(data_path:Path|str|None = None) -> pd.DataFrame:

    if not data_path:
        data_path: Path = Path(__file__).resolve().parent / "data/data.csv"

    df = pd.read_csv(data_path)

    # normalize coordinates so home location is centered 0.0, 0.0
    lat_offset:float = df.loc[df['location'] == 'home', 'lat'].iloc[0]
    lon_offset:float = df.loc[df['location'] == 'home', 'lon'].iloc[0]
    df['lat'] = df['lat'] - lat_offset
    df['lon'] = df['lon'] - lon_offset

    return df



if __name__ == "__main__":
    _df = load_data()
    print(_df)