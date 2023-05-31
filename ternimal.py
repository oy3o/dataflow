import oy3opy.input as input
from oy3opy.utils.string import string_width_fits
from .core import View, Flow, Callable

class App(View):
    def __init__(self, flow:Flow, window, y = 0, x = 0, height = None, width = None, offset = 0, fullscroll = True, bottomscroll = True, afterRender:Callable=None):
        self.flow = flow

        ymax, xmax = window.getmaxyx()
        self.height = ymax if not height else height
        self.width = xmax if not width else width
        self.view = window.derwin(self.height, self.width, y, x)
        self.view.keypad(True) 

        super().__init__(flow, self.height, offset)

        self.__screen_curs_min_y, self.__screen_curs_min_x = self.view.getbegyx()
        self.fullscroll = fullscroll
        self.bottomscroll = bottomscroll
        self.__stop = False
        if self.fullscroll:
            self.subscribe('full', lambda view: view.autoscroll())
        
        self.afterRender = afterRender

    def listen(self):
        input.onmouse(input.SCROLL_DOWN, self.handle_mouse)
        input.onmouse(input.SCROLL_UP, self.handle_mouse)
        self.subscribe('update', self.render)
        self.__stop = False
    def stop(self):
        input.offmouse(input.SCROLL_DOWN, self.handle_mouse)
        input.offmouse(input.SCROLL_UP, self.handle_mouse)
        self.unsubscribe('update', self.render)
        self.__stop = True
    def render(self, *args):
        if self.__stop:
            return
        if self.bottomscroll:
            try:
                self.scroll = ((len(self) == self.height) and (self.offset + len(self) == len(self.flow)))
            except:
                raise ValueError(f'{self.__len__()},{self.flow.__len__()}')

        for i, item in enumerate(self.window()):
            self.view.addstr(i, 0, string_width_fits(str(item), self.width - 1))
            self.view.clrtoeol()
        self.view.refresh()
        self.afterRender()

    def close(self):
        self.view.erase()
        self.view.refresh()

    def handle_mouse(self, y, x, type):
        if self.__stop:
            return
        if (self.__screen_curs_min_y <= y) and (y < self.__screen_curs_min_y+self.height) and (self.__screen_curs_min_x <= x) and (x < self.__screen_curs_min_x+self.width):
            if type == input.SCROLL_DOWN:
                self.curs_down()
                self.render()
            elif type == input.SCROLL_UP:
                self.curs_up()
                self.render()

    def __enter__(self):
        self.listen()
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()
        self.close()
