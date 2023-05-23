from oy3opy import *

events = ['empty', 'full', 'append', 'remove', 'change', 'update', 'expired']

@subscribe(events)
class Flow:
    def __init__(self, data = [], max = None, expire = None, roll = True):
        self.data = data[:max]
        self.max = max
        self.expire = expire
        self.roll = roll

    def append(self, item):
        if len(self.data) == self.max:
            if self.roll:
                self.remove(0)
                self.data.append(item)
            else:
                self.trigger('full')
        else:
            self.data.append(item)
        self.trigger('append', len(self)-1, item)
        self.trigger('update', self)

    def remove(self, index):
        item = self.data[index]
        del self.data[index]
        self.trigger('remove', index, item)
        self.trigger('update', self)
        if len(self) == 0:
            self.trigger('empty')
        return item

    def last(self, n):
        return self.data[-n:]

    def change(self, index, newItem):
        oldItem = self.data[index]
        self.data[index] = newItem
        self.trigger('change', oldItem, newItem)
        self.trigger('update', self)
        return oldItem

    def pick(self, index):
        return self.data[index]

    def clear(self):
        while len(self):
            self.remove(0)

    def update(self):
        change = False
        for i, item in enumerate(self.data):
            if self.expire(item):
                self.remove(i)
                self.trigger('expired', item)
                change = True

        if change:
            self.trigger('update', self)

    def __len__(self):
        return len(self.data)


@subscribe(['update','full'])
class View:
    def __init__(self, flow, height, offset=0, overflow=False, scroll=False):
        self.flow = flow
        self.data = flow.data
        self.height = height
        self.offset = offset
        self.overflow = overflow 
        self.scroll = scroll 
        self.mark = 0 # self.offset = max(0,  > 0)
        self.flow.subscribe('update', lambda *_: self.update()) 
        self.flow.subscribe('append', lambda *_: self.markto(1))
        self.flow.subscribe('remove', lambda *_: self.markto(-1)) 

    def markto(self, s):
        self.mark = s

    def curs_up(self, n=1):
        if self.overflow or self.offset > 0:
            self.offset -= n
            return True 
        else:
            return False 

    def curs_down(self, n=1):
        if self.overflow or (self.offset + self.height < len(self.data)):
            self.offset += n
            return True 
        else:
            return False 
    def curs_to(self, pos):
        if self.overflow or (0 <= pos <= len(self.data) - self.height):
            self.offset = pos
            return True 
        else:
            return False

    def window(self):
        return self.data[self.offset:self.offset + self.height]

    def update(self):
        if self.scroll:
            self.offset += self.mark
        self.mark = 0
        self.trigger('update', self)
        if len(self) == self.height:
            self.trigger('full', self)
    
    def __len__(self):
        return len(self.data) - self.offset
