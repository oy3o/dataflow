from oy3opy import *

events = ['empty', 'full', 'append', 'remove', 'change', 'update', 'expired']

@subscribe(events)
class Flow(list):
    def __init__(self, data = [], max = None, expire = None, roll = True):
        super().__init__(data[:max])
        self.max = max
        self.expire = expire
        self.roll = roll

    def append(self, item):
        if len(self) == self.max:
            if self.roll:
                self.remove(0)
                super().append(item)
            else:
                self.trigger('full')
        else:
            super().append(item)
        self.trigger('append', len(self)-1, item)
        self.trigger('update', self)

    def remove(self, index):
        item = self[index]
        del self[index]
        self.trigger('remove', index, item)
        self.trigger('update', self)
        if len(self) == 0:
            self.trigger('empty')
        return item

    def last(self, n):
        return self[-n:]

    def change(self, index, newItem):
        oldItem = self[index]
        self[index] = newItem
        self.trigger('change', oldItem, newItem)
        self.trigger('update', self)
        return oldItem

    def pick(self, index):
        return self[index]

    def clear(self):
        while len(self):
            self.remove(0)

    def update(self, expire = None):
        change = False
        expire = expire if expire else self.expire
        for i, item in enumerate(self):
            if expire(item):
                self.remove(i)
                self.trigger('expired', item)
                change = True

        if change:
            self.trigger('update', self)


@subscribe(['update','full'])
class View:
    def __init__(self, flow, height, offset=0, overflow=False, scroll=False):
        self.flow = flow
        self.height = height
        self.offset = offset
        self.overflow = overflow 
        self.scroll = scroll
        self.mark = 0
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

    def curs_down(self, n=1, force=False):
        if force or self.overflow or (self.offset + self.height < len(self.flow)):
            self.offset += n
            return True
        else:
            return False

    def curs_to(self, pos):
        if self.overflow or ((0 <= pos ) and (pos <= len(self.flow) - self.height)):
            self.offset = pos
        else:
            self.offset = max(0, min(len(self.flow) - self.height, pos))

    def autoscroll(self):
        self.scroll = True

    def window(self):
        return self.flow[self.offset:self.offset + self.height]

    def update(self):
        if self.scroll:
            self.offset += self.mark
        self.mark = 0
        if len(self) == self.height:
            self.trigger('full', self)
        self.trigger('update', self)

    def __len__(self):
        return min(self.height, max(0, len(self.flow) - self.offset))

