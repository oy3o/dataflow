# dataflow

dataflow processing data flow and views, which can subscribe to data change events, as well as view update window.
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