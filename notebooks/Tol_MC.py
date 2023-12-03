# Monte Carlo Simulation for Tolerance Stack Up Analysis
import numpy as np
import pandas as pd
from io import StringIO

def get_dfX(path_x):
    try:
        df_X = pd.read_csv(path_x)
        df_X['max'] = df_X['nominal'] + df_X['upper_tol']
        df_X['min'] = df_X['nominal'] + df_X['lower_tol']
        df_X['mean'] = (df_X['max'] + df_X['min']) / 2
        df_X['std'] = (df_X['max'] - df_X['min']) / 2 / df_X['sigma_level']
        return df_X
    except:
        print("Cannot get the parameters for X")
        return None

def mc_tol(df_X, transf, N_SIM):
    df = pd.DataFrame()
    for i in range(df_X.shape[0]):
        df[df_X['name'][i]] = np.random.normal(df_X['mean'][i], df_X['std'][i], N_SIM)
    df = df.eval(transf)
    return df