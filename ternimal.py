import oy3opy.input as input
from oy3opy.utils.string import maxwidth
from .core import View

class App(View):
    def __init__(self, flow, window, y = 0, x = 0, height = None, width = None, offset = 0, fullscroll = True, bottomscroll = True):
        self.flow = flow

        ymax, xmax = window.getmaxyx()
        self.height = ymax if not height else height
        self.width = xmax if not width else width
        self.viewer = window.derwin(self.height, self.width, y, x)
        self.viewer.keypad(True) 

        super().__init__(flow, self.height, offset)

        self.fullscroll = fullscroll
        self.bottomscroll = bottomscroll
        self.__stop = False
        if self.fullscroll:
            self.subscribe('full', lambda view: view.autoscroll())

    def listen(self):
        input.onmouse(input.SCROLL_DOWN, self.mouse_down)
        input.onmouse(input.SCROLL_UP, self.mouse_up)
        self.subscribe('update', self.render)
        self.__stop = False
    def stop(self):
        input.offmouse(input.SCROLL_DOWN, self.mouse_down)
        input.offmouse(input.SCROLL_UP, self.mouse_up)
        self.unsubscribe('update', self.render)
        self.__stop = True
    def render(self, *args):
        if self.__stop:
            return
        if self.bottomscroll:
            self.scroll = ((len(self) == self.height) and (self.offset + len(self) == len(self.flow)))
        self.viewer.erase()
        for i, item in enumerate(self.window()):
            self.viewer.addstr(i, 0, maxwidth(str(item), self.width - 1))
        self.viewer.refresh()

    def close(self):
        self.viewer.erase()
        self.viewer.refresh()

    def mouse_up(self, *args):
        if self.__stop:
            return
        self.curs_up()
        self.render()

    def mouse_down(self, *args):
        if self.__stop:
            return
        self.curs_down()
        self.render()
    
    def __enter__(self):
        self.listen()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        self.close()
