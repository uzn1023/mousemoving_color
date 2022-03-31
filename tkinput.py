##!/usr/bin/env python

import tkinter as tk
from tkinter import ttk


def main():
    win = tk.Tk()
    win.title('Input parameter')
    win.geometry("300x200")

    var = tk.IntVar(win)
    var.set(500)

    label1 = ttk.Label(win, text='Threshold')
    label1.grid(row=1,column=1)
    label1.grid_configure(padx=10, pady=15)

    sp1 = tk.Spinbox(win,textvariable=var,from_=0,to=100000,increment=100)
    sp1.grid(row=1,column=2)
    sp1.grid_configure(padx=10, pady=15)

    label2 = ttk.Label(win, text='Bout')
    label2.grid(row=2,column=1)
    label2.grid_configure(padx=10, pady=15)

    var2 = tk.DoubleVar()
    var2.set(0.25)
    ary=[0, 0.25, 0.5, 1, 2]
    sp2 = tk.Spinbox(win,textvariable=var2,value=ary,state='readonly')
    sp2.grid(row=2,column=2)
    sp2.grid_configure(padx=10, pady=15)

    frame = ttk.Frame(win)
    frame.grid(row=3,column=2)
    frame.grid_configure(padx=10, pady=15)
    button = tk.Button(frame, text="Calculate",command=lambda:print(var2.get()))
    button.grid()

    win.mainloop()

    print(var.get())
    print(var2.get())

if __name__ == '__main__':
    main()
