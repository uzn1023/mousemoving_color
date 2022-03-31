##!/usr/bin/env python
import cv2
import numpy as np
import PySimpleGUI as sg
import copy


def setparam(movie):
    mc_up = 20
    X, Y, W, H = 500, 500, 900, 900
    vidFile = cv2.VideoCapture(movie)
    # GUI preparation
    sg.theme('Black')
    txt_H = sg.Text('Mouse color range',size=(15,1),font=("",15,"bold"))
    txt_Hmin = sg.Text('H min',size=(5,1))
    sld_Hmin = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Hmin-', default_value = 0)
    txt_Hmax = sg.Text('H max',size=(5,1))
    sld_Hmax = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Hmax-', default_value = 255)
    txt_Smin = sg.Text('S min',size=(5,1))
    sld_Smin = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Smin-', default_value = 0)
    txt_Smax = sg.Text('S max',size=(5,1))
    sld_Smax = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Smax-', default_value = 255)
    txt_Vmin = sg.Text('V min',size=(5,1))
    sld_Vmin = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Vmin-', default_value = 0)
    txt_Vmax = sg.Text('V max',size=(5,1))
    sld_Vmax = sg.Slider(range=(0, 255),size=(20, 10), orientation='h', key='-Vmax-', default_value = 30)

    txt_mc = sg.Text('Mask setting',size=(15,1),font=("",15,"bold"))
    txt_mcx = sg.Text('pos X',size=(15,1))
    sld_mcx = sg.Slider(range=(0, 1300),size=(20, 10), default_value=X, orientation='h', key='x')
    txt_mcy = sg.Text('pos Y',size=(15,1))
    sld_mcy = sg.Slider(range=(0, 1000),size=(20, 10), default_value=Y, orientation='h', key='y')
    txt_mw = sg.Text('Mask width',size=(15,1))
    sld_mw = sg.Slider(range=(0, 2000),size=(20, 10), default_value=W, orientation='h', key='w')
    txt_mh = sg.Text('Mask height',size=(15,1))
    sld_mh = sg.Slider(range=(0, 2000),size=(20, 10), default_value=H, orientation='h', key='h')
    txt_ms = sg.Text('Mask shape',size=(15,1))
    rad_cir = sg.Radio("Circle", size=(10, 1), group_id = "shape", key="cir")
    rad_rec = sg.Radio("Rectangle", size=(10, 1), group_id = "shape", key="rec", default=True)

    column = [txt_H],\
             [txt_Hmin, sld_Hmin, txt_Hmax, sld_Hmax],\
             [txt_Smin, sld_Smin, txt_Smax, sld_Smax],\
             [txt_Vmin, sld_Vmin, txt_Vmax, sld_Vmax],\
             [txt_mc],\
             [txt_mcx, sld_mcx, txt_mcy,sld_mcy],\
             [txt_mw, sld_mw, txt_mh, sld_mh],\
             [txt_ms, rad_cir, rad_rec]

    layout = [[sg.Column(column)], [sg.Image(filename='', key='frame'), sg.Image(filename='', key='image')],[sg.Button('Done', size=(10, 1), font='Helvetica 14')]]
    window = sg.Window('SelectParameter', layout, no_titlebar=False, location=(0, 0), resizable=True)
    while(1):
        event, values = window.read(timeout=0)
        mouse_low = [values["-Hmin-"],values["-Smin-"],values["-Vmin-"]]
        mouse_high = [values["-Hmax-"],values["-Smax-"],values["-Vmax-"]]
        X, Y, W, H = int(values['x']), int(values['y']), int(values["w"]), int(values["h"])
        ret, frame = vidFile.read()
        if not ret:
            vidFile.set(cv2.CAP_PROP_POS_FRAMES, 1)
            continue
        h,w = frame.shape[:2]
        lower = np.array(mouse_low, dtype=np.uint8)
        upper = np.array(mouse_high, dtype=np.uint8)
        img = cv2.inRange(frame, lower, upper)

        mask_cage = np.zeros((h,w),dtype=np.uint8)
        if values["cir"] == True:
            center = (X,Y)
            axes = (W,H)
            box = (center, axes, 0)
            cv2.ellipse(mask_cage,box=box, color=255,thickness=-1)
            shape = "cir"
        else:
            pt1 = (int(X-W/2), int(Y-H/2))
            pt2 = (int(X+W/2), int(Y+H/2))
            cv2.rectangle(mask_cage, pt1=pt1, pt2=pt2, color=255, thickness=-1)
            shape = "rec"
        img[mask_cage == 0] = 127
        frame[mask_cage == 0] = (127, 127, 127)
        frm_o = copy.copy(frame)
        frm_o = cv2.resize(frm_o, dsize=None, fx=0.5, fy=0.5)
        framebytes = cv2.imencode('.png', frm_o)[1].tobytes()
        img_o = copy.copy(img)
        img_o = cv2.resize(img_o, dsize=None, fx=0.5, fy=0.5)
        imgbytes = cv2.imencode('.png', img_o)[1].tobytes()
        window['frame'].update(data=framebytes)
        window['image'].update(data=imgbytes)
        # 最小値が最大値を超えないようにする
        if values["-Hmin-"] > values["-Hmax-"]:
            window["-Hmax-"].update(values["-Hmin-"])
        if values["-Smin-"] > values["-Smax-"]:
            window["-Smax-"].update(values["-Smin-"])
        if values["-Vmin-"] > values["-Vmax-"]:
            window["-Vmax-"].update(values["-Vmin-"])
        # Done > 次の画面に遷移        
        if event in ('Done', None):
            window.close()
            break
        param = [mouse_low, mouse_high, X, Y, W, H, shape]
    return param
if __name__ == '__main__':
    setparam(r"E:\SSG_Share_1\Uezono\data\video\general_long.mp4")




