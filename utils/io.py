import pandas as pd
import json
import tkinter as tk


def readvalues(file_name: str) -> None:
    df = pd.read_csv(file_name, sep="\t")
    time = df.columns[0]
    value = df.columns[1]
    return df[time].to_numpy(dtype=float), df[value].to_numpy(dtype=float)


def savetojson(data: dict, filename=None) -> str:
    if filename is None:
        outfile = tk.filedialog.asksaveasfile(
            initialfile="circuit.json", defaultextension=".json", filetypes=[("All Files", "*.*"), ("JSON", "*.json")]
        )
    else:
        outfile = open(filename, "w")
    if outfile is None:
        return
    json_str = json.dumps(data, indent=4)
    outfile.write(json_str)
    return outfile.name


def loadfromjson(filename=None) -> tuple[dict, str]:
    if filename is None:
        infile = tk.filedialog.askopenfile(filetypes=[("All Files", "*.*"), ("JSON", "*.json")])
    else:
        infile = open(filename, "r")
    if infile is None:
        return None, None
    data = json.load(infile)
    return data, infile.name
