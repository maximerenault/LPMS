import pandas as pd


def readvalues(file_name):
    df = pd.read_csv(file_name, sep="\t")
    time = df.columns[0]
    value = df.columns[1]
    return df[time].to_numpy(dtype=float), df[value].to_numpy(dtype=float)
