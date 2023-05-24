# dataflow

dataflow processing data flow and views, which can subscribe to data change events, as well as view update window.
## Basic API
```py
from oy3opy.dataflow import *

# create a roll update flow with max size 10
flow = Flow(max=10, expire=None, roll=True)
# create a slide window with height 5 offset 0
view = View(flow, height=5, offset=0, overflow=False, scroll=False)

def render(list): print(list)
def autoscroll(): view.scroll = True
# subscribe scroll on full view
view.subscribe("full", lambda *_: autoscroll())
# subscribe update to render view
view.subscribe("update", lambda *_: render(view.window()))

for i in range(15):
    flow.append(i)
```
## Termnial UI API
The terminal UI interface implemented based on Basic API supports mouse scrolling, full screen automatic scrolling and scrolling only at the bottom.
```py
from oy3opy.dataflow import Flow
from oy3opy.dataflow.ternimal import App
from oy3opy.utils.string import random_word
from oy3opy.input import listen, stop
import curses
import threading
import time

screen = curses.initscr()
screen.keypad(True) 
curses.noecho()
curses.cbreak()
curses.raw()
curses.curs_set(0)

running = True
def mouse_listen():
    global running
    for wc in listen(screen, move=0):
        if wc == 'q':
            stop()
            running = False

flow = Flow(expire=None, roll=True)
with App(flow, screen, height=5) as app: # (self, flow, window, y = 0, x = 0, height = None, width = None, offset = 0, fullscroll = True, bottomscroll = True):
    t = threading.Thread(target=mouse_listen)
    t.setDaemon(True)
    t.start()

    for i in range(30):
        if not running:
            break

        flow.append(f' {i}| {random_word(128)}')
        time.sleep(0.5)

curses.endwin()
```