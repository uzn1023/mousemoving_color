##!/usr/bin/env python
import csv
import os

import cv2
import matplotlib.pyplot as plt
import numpy as np
import PySimpleGUI as sg
import tqdm


def proc(movie, outdir, param,fps):
    cap = cv2.VideoCapture(movie)

    divider = 1
    f = open(os.path.join(outdir,"moving.csv"),"w")
    writer_csv = csv.writer(f,lineterminator="\n")
    writer_csv.writerow(["time[s]","amount of movement[px]"])
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    frame_rate = 30
    size = ((int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
    fmt = cv2.VideoWriter_fourcc('m', 'p', '4', 'v') 
    writer = cv2.VideoWriter(os.path.join(outdir,"masked.mp4"), fmt, frame_rate, size) 

    def img_proc(img, param):
        mc_low, mc_high, X, Y, W, H, shape = param[0], param[1],param[2],param[3],param[4],param[5],param[6] 
        h,w = img.shape[:2]
        # Mask for mouse (black region)
        lower = np.array(mc_low, dtype=np.uint8)
        upper = np.array(mc_high, dtype=np.uint8)
        mask_mouse = cv2.inRange(img, lower, upper)
        # Mask for cable (white region) 
        lower = np.array(230, dtype=np.uint8)
        upper = np.array(255, dtype=np.uint8)
        mask_cable = cv2.inRange(img, lower, upper)
        # Mask for inCage region
        mask_cage = np.zeros((h,w),dtype=np.uint8)
        if shape == "cir":
            center = (X,Y)
            axes = (W,H)
            box = (center, axes, 0)
            cv2.ellipse(mask_cage,box=box, color=255,thickness=-1)
        else:
            pt1 = (int(X-W/2), int(Y-H/2))
            pt2 = (int(X+W/2), int(Y+H/2))
            cv2.rectangle(mask_cage, pt1=pt1, pt2=pt2, color=255, thickness=-1)

        mask_mouse[mask_cage == 0] = 0  # Exclude out of cage
        # Morphorogy precessing
        mask_mouse = cv2.morphologyEx(mask_mouse,cv2.MORPH_OPEN, np.ones((2,2),np.uint8))
        mask_mouse = cv2.morphologyEx(mask_mouse,cv2.MORPH_CLOSE, np.ones((2,2),np.uint8))
        mask_mouse = cv2.dilate(mask_mouse,np.ones((5,5),np.uint8),iterations = 1)  # 胴体と体の分離、ケーブルによるマウス領域の分離を防ぐ

        # Selecting most biggest region (should be mouse region)
        nlabels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask_mouse, 4)
        if nlabels > 1:
            max_idx = np.argmax(stats[1:,:], axis=0)[4] + 1
            mask_mouse[labels == max_idx, ] = 255
            mask_mouse[labels != max_idx, ] = 0
        mask_mouse = cv2.erode(mask_mouse,np.ones((5,5),np.uint8),iterations = 1)   # Recovering from dilate
        return mask_mouse, mask_cable, mask_cage

    sg.theme('Black')
    BAR_MAX = frame_count
    layout = [[sg.Text('Loading video ...')],
          [sg.ProgressBar(BAR_MAX, orientation='h', size=(50,20), key='-PROG-')],]
    window = sg.Window('Progres', layout)
    for i in tqdm.tqdm(range(frame_count)):
        ret, frame = cap.read()
        mask_mouse,mask_cable, mask_cage = img_proc(frame,param)
        out_frame = np.ones((int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 3),np.uint8)*255
        out_frame[mask_mouse > 0] = (255,0,0)
        out_frame[mask_cable > 0] = (0,255,0)
        out_frame[mask_cage == 0] = (125,125,125)
        if (i > 0) and (i % divider == 0):
            # Taking difference of mouse region
            img_xor = cv2.bitwise_xor(mask_mouse,mask_mouse_old)
            img_xor[(mask_cable != 0) | (mask_cable_old != 0)] = 0  # ケーブルがマウスの上を動いたことがマウスの動きと判定されるのを防ぐ

            out_frame[img_xor > 0] = (0,0,255)
            cnt = cv2.countNonZero(img_xor) # Calculate amount of movement
            writer.write(out_frame)
            writer_csv.writerow([str(i/fps),cnt])



        if i % divider == 0:
            mask_mouse_old = mask_mouse
            mask_cable_old = mask_cable

        window.read(timeout=0)
        window['-PROG-'].update(i+1)
    writer.release()
    cap.release()
    cv2.destroyAllWindows()
    f.close()
    window.close()
    return os.path.join(outdir,"moving.csv")

if __name__=='__main__':
    movie = r"..\data\video\general.mp4"
    outdir = r"..\result\20220310"
    proc(movie,outdir)
