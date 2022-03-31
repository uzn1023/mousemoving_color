##!/usr/bin/env python
import csv

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import gridspec


def proc(csv_in,Threshold,bout,fig):
    df = pd.read_csv(csv_in,names=("time","move"),skiprows=1)
    frag_freeze = 0
    freeze_start = 0
    df["bin"] = 0   # Freeze/Move判定値代入用
    i_start = 0
    df_freeze = pd.DataFrame(index=[],columns=["start","end","long"])
    for i in range(len(df.time)):
        if df.iat[i,1] < Threshold:
            if frag_freeze == 0:
                freeze_start = df.iat[i,0]
            frag_freeze = 1
        else:
            if frag_freeze == 1:
                freeze_end = df.iat[i,0]
                if freeze_end - freeze_start > bout:
                    rec = pd.Series([freeze_start, freeze_end, freeze_end-freeze_start], index = df_freeze.columns)
                    df_freeze = df_freeze.append(rec, ignore_index = True)
                    for j in range(i_start, i+1, 1):
                        df.iat[j,2] = 1
                else:
                    for j in range(i_start, i+1, 1):
                        df.iat[j,2] = 0
            else:
                df.iat[i,2] = 0
            frag_freeze = 0
            i_start = i + 1

    if frag_freeze == 1:
        freeze_end = df.iat[i,0]
        if freeze_end - freeze_start > bout:
            rec = pd.Series([freeze_start, freeze_end, freeze_end-freeze_start], index = df_freeze.columns)
            df_freeze = df_freeze.append(rec, ignore_index = True)
            for j in range(i_start, i+1, 1):
                df.iat[j,2] = 1
        else:
            for j in range(i_start, i+1, 1):
                df.iat[j,2] = 0

        rec = pd.Series([freeze_start, freeze_end, freeze_end-freeze_start], index = df_freeze.columns)
        df_freeze = df_freeze.append(rec, ignore_index = True)

    spec = gridspec.GridSpec(ncols = 1, nrows = 2, height_ratios=[3, 1])
    ax1 = fig.add_subplot(spec[0])
    ax1.hlines(Threshold, df.iat[0,0], df.iat[i,0], linestyle = "dashed", linewidth = 0.5, color = "red")
    ax1.plot(df.time,df.move, linewidth = 0.5, color = "blue")
    ax1.set_ylabel("Count of moving [px]")
    ax1.set_title("Threshold=" + str(Threshold) + ", Bout=" + str(bout))

    ax2 = fig.add_subplot(spec[1],sharex = ax1)

    for j in range(len(df_freeze.start)):
        ax2.axvspan(df_freeze.iat[j,0], df_freeze.iat[j,1], color="black")
    ax2.set_xlabel("Time [s]")
    return fig, df_freeze, df

