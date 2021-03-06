# !/usr/bin/env python
import copy
import io
import os
import time
import tkinter as tk
import tkinter.filedialog
import tkinter.messagebox
from tkinter import ttk

import cv2
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import csvproc
import movieproc
import setparam

FONTSIZE = 'Helvetica 14'
FONTSIZE2 = 'Helvetica 10'


def runmovie(moviename, moviemask, outdir):
    vidFile = cv2.VideoCapture(moviename)
    num_frames = vidFile.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = vidFile.get(cv2.CAP_PROP_FPS)
    w = int(vidFile.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(vidFile.get(cv2.CAP_PROP_FRAME_HEIGHT))
    vidFile2 = cv2.VideoCapture(moviemask)
    num_frames2 = vidFile2.get(cv2.CAP_PROP_FRAME_COUNT)
    fps2 = vidFile2.get(cv2.CAP_PROP_FPS)

    sg.theme('Black')
    column = [sg.Text('Parameters', justification='center', size=(15, 1), text_color='#FFFFFF', font=(FONTSIZE))],\
             [sg.Text('Bout', size=(7, 1), text_color='#FFFFFF', font=(FONTSIZE2)), sg.Spin(values=('0.00', '0.25', '0.50', '1.00', '2.00'), initial_value='0.25', key='Bout', font=(FONTSIZE))],\
             [sg.Text('Threshold', size=(7, 1), text_color='#FFFFFF', font=(FONTSIZE2)), sg.Spin([x*100 for x in range(100)], 200, key='Threshold', font=(FONTSIZE))],\
             [sg.Image(filename='', key='-hist-')],\
             [sg.Text('CSV export', justification='center', size=(15, 1), text_color='#FFFFFF', font=(FONTSIZE))],\
             [sg.Text('Interval (sec)', size=(10, 1), text_color='#FFFFFF', font=(FONTSIZE2)), sg.Spin([x*10 for x in range(100)], 60, key='Interval', font=(FONTSIZE))],\
             [sg.Button('Export', size=(10, 1), font='Helvetica 12')]
    column2 = [sg.Image(filename='', key='-image-')
               ], [sg.Image(filename='', key='-image2-')]
    layout = [[sg.Column(column), sg.Image(filename='', key='-graph-'), sg.Column(column2)],
              [sg.Text('0', justification='center', size=(8, 1), text_color='#000', background_color='#FFFFFF', key='-time-', font=(FONTSIZE)), sg.Slider(range=(0, num_frames), size=(40, 10), orientation='h',
                                                                                                                                                          key='-slider-'), sg.Button('STOP/PLAY', size=(10, 1), font='Helvetica 14'), sg.Button('SAVE', size=(10, 1), font='Helvetica 14'), sg.Button('ZOOMABLE', size=(10, 1), font='Helvetica 14')],
              [sg.Button('Exit', size=(10, 1), font='Helvetica 14')]]

    window = sg.Window('MouseDitection', layout,
                       no_titlebar=False, location=(0, 0), resizable=True)

    image_elem = window['-image-']
    image2_elem = window['-image2-']
    slider_elem = window['-slider-']
    graph_elem = window['-graph-']
    playtime_elem = window['-time-']
    hist_elem = window['-hist-']

    window.read(timeout=0)
    Threshold = 200
    Bout = 0.25

    # ??????????????????
    def graph_renew():
        fig = plt.figure()
        fig.canvas.draw()
        fig, df_freeze, df = csvproc.proc(csv_out, Threshold, Bout, fig)
        item = io.BytesIO()
        fig.savefig(item, format='png')
        graph_elem.update(data=item.getvalue())
        fig.savefig(os.path.join(outdir, "pic.png"))
        return fig, df_freeze, df
    # ????????????????????????????????????????????????????????????

    def interval(df_freeze, interval):
        i = 1
        freeze_tot = 0
        freeze_tot_all = 0
        df_interval = pd.DataFrame(index=[], columns=["total of interval"])
        for j in range(len(df_freeze.start)):
            if df_freeze.iat[j, 1] < interval * i:
                freeze_tot = freeze_tot + df_freeze.iat[j, 2]
            else:
                freeze_tot = freeze_tot + (interval * i - df_freeze.iat[j, 0])
                rec = pd.Series([freeze_tot], index=df_interval.columns)
                df_interval = df_interval.append(rec, ignore_index=True)
                freeze_tot = 0
                freeze_tot = freeze_tot + (df_freeze.iat[j, 1] - interval * i)
                i = i + 1
        return df_interval
    fig, df_freeze, df = graph_renew()

    # ????????????????????????
    fig2 = plt.figure(figsize=(3.5, 2.5))
    ax_hist = fig2.add_subplot()
    move = df["move"]

    def hist_renew(Threshold):
        _, bin, patches = ax_hist.hist(move, bins=200, color="red")
        for i in range(200):
            if bin[i+1] < Threshold:
                patches[i].set_facecolor('blue')
        ax_hist.set_xlabel("Count of moving [px]")
        ax_hist.set_ylabel("Frequency")
        item = io.BytesIO()
        fig2.subplots_adjust(left=0.2, bottom=0.2)
        fig2.savefig(item, format='png')
        hist_elem.update(data=item.getvalue())
    hist_renew(Threshold)
    cur_frame = 0
    play_flag = 1
    zoom_flag = 0
    while vidFile.isOpened():
        starttime = time.time()
        # ?????????????????????
        event, values = window.read(timeout=0)

        # ???Exit??????????????????????????????
        if event in ('Exit', None):
            break

        #?????????????????????????????????????????????
        ret, frame = vidFile.read()
        ret2, frame2 = vidFile2.read()

        #??????????????????????????????????????????????????????????????????????????????
        if not (ret and ret2):  # if out of data stop looping
            vidFile.set(cv2.CAP_PROP_POS_FRAMES, 0)
            vidFile2.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        #??????????????????????????????????????????????????????????????????????????????????????????????????????
        if int(values['-slider-']) != cur_frame-1:
            cur_frame = int(values['-slider-'])
            vidFile.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)
            vidFile2.set(cv2.CAP_PROP_POS_FRAMES, cur_frame)

        if event in ('STOP/PLAY', None):
            if play_flag == 1:
                play_flag = 0
            else:
                play_flag = 1
        # ????????????????????????: ????????????????????????????????????????????????????????????
        if event in ('SAVE', None):
            root = tk.Tk()
            root.withdraw()
            root.filename = tkinter.filedialog.asksaveasfilename(
                initialdir="outdir", title="Save as", filetypes=[("img file", "*.png")])
            fig.savefig(os.path.join(outdir, root.filename))
        # ???????????????????????????????????????????????????
        if event in ('ZOOMABLE', None):
            plt.show(block=False)
        # CSV(Bout???????????????????????????)?????????????????????
        if event in ('Export'):
            try:
                filename = "freezelist_" + "bout" + \
                    str(int(float(values['Bout'])*100)) + \
                    "thr" + str(values['Threshold']) + ".csv"
                df_freeze.to_csv(os.path.join(outdir, filename))
                df_interval = interval(df_freeze, int(values['Interval']))
                filename = "interval_" + "bout" + str(int(float(values['Bout'])*100)) + "thr" + str(
                    values['Threshold']) + "intvl" + str(values['Interval']) + ".csv"
                df_interval.to_csv(os.path.join(outdir, filename))
            except ValueError:  # ???????????????????????????????????????????????????
                print("Error Interval is not number")
        # ??????????????????????????????????????????????????????
        try:
            if Threshold != int(values['Threshold']) or Bout != float(values['Bout']):
                Threshold = int(values['Threshold'])
                Bout = float(values['Bout'])
                plt.close()
                fig, _, df = graph_renew()
                hist_renew(Threshold)
        except ValueError:  # ???????????????????????????????????????????????????
            pass

        # Write time bar on the graph
        graph = cv2.imread(os.path.join(outdir, "pic.png"))
        x = int(101 + (cur_frame / vidFile.get(cv2.CAP_PROP_FRAME_COUNT)) * (553 - 101))
        graph = cv2.line(graph, (x, 58), (x, 310), (0, 255, 0), 2)
        graph = cv2.line(graph, (x, 343), (x, 427), (0, 255, 0), 2)
        imgbytes_graph = cv2.imencode('.png', graph)[1].tobytes()
        graph_elem.update(data=imgbytes_graph)

        if play_flag == 0:
            continue

        #?????????????????????????????????
        slider_elem.update(cur_frame)
        cur_time = int(cur_frame/fps)
        playtime_elem.update(str(cur_time) + " s")
        cur_frame += 1

        secs = int(cur_frame // fps)
        sec = secs % 60
        mins = secs // 60
        min = mins % 60
        hr = mins // 60

        timestump = str(hr) + ":" + str(min).zfill(2) + ":" + str(sec).zfill(2)
        if len(df) > cur_frame:
            if df.iat[cur_frame, 2] == 1:
                txt = "Freezing"
                color = (255, 0, 0)
            else:
                txt = "Moving"
                color = (0, 0, 255)

        # ????????????????????????????????????240px????????????
        frm_o = copy.copy(frame)
        rate = 240/h
        frm_o = cv2.resize(frm_o, dsize=None, fx=rate, fy=rate)
        # ????????????????????????freeze/move?????????
        cv2.putText(frm_o, timestump, org=(20, 30), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                    fontScale=0.7, color=(0, 0, 0), thickness=2, lineType=cv2.LINE_4)
        cv2.putText(frm_o, txt, org=(120, 30), fontFace=cv2.FONT_HERSHEY_SIMPLEX,
                        fontScale=0.6, color=color, thickness=2, lineType=cv2.LINE_4)
        # ??????????????????png???,?????????????????????
        imgbytes = cv2.imencode('.png', frm_o)[1].tobytes()
        # ?????????????????????
        totaltime = 1/fps
        waittime = totaltime - ( time.time() - starttime + 0.04 )
        if waittime > 0:
            time.sleep(waittime)
        # ????????????
        image_elem.update(data=imgbytes)
        # New >> old
        frm2_o = copy.copy(frame2)
        frm2_o = cv2.resize(frm2_o, dsize=None, fx=rate, fy=rate)
        imgbytes = cv2.imencode('.png', frm_o)[1].tobytes()
        imgbytes2 = cv2.imencode('.png', frm2_o)[1].tobytes()
        image2_elem.update(data=imgbytes2)


# ????????????
print("<<<MouseFreezingDetection>>>")
print("Ver. 0.4 : 2022.07.28")
print("For color videos")

programname = "MouseDitection"
root = tk.Tk()
root.withdraw()
fTyp = [("", "*.mp4 *.avi")]
tkinter.messagebox.showinfo(programname, 'Please select video file.')
movie = tkinter.filedialog.askopenfilename(filetypes=fTyp, initialdir="~")
tkinter.messagebox.showinfo(programname, 'Please select output folder.')
outdir = tkinter.filedialog.askdirectory(initialdir="~")

param = setparam.setparam(movie)

vidFile = cv2.VideoCapture(movie)
fps = vidFile.get(cv2.CAP_PROP_FPS)
# mouse ditection and calclate moving -> csv file
csv_out = movieproc.proc(movie, outdir, param,fps)
movie_mask = os.path.join(outdir, "masked.mp4")
runmovie(movie, movie_mask, outdir)
