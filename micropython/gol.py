import picounicorn as uni
import random
import time

w = uni.get_width()
h = uni.get_height()

class Cells:
    def __init__(self):
        self.cells = [[0]*h for i in range(w)]

    def clear_all(self):
        for x in range(w):
            for y in range(h):
                self.cells[x][y] = 0

    def set_random_cells_to_value(self, prob, value):
        for x in range(w):
            for y in range(h):
                if random.random() < prob:
                    self.cells[x][y] = value

    def is_alive(self,x,y):
        x = x % w
        y = y % h
        return self.cells[x][y] == 255

    def get_num_live_neighbours(self, x, y):
        num = 0
        num += (1 if self.is_alive(x-1,y-1) else 0)
        num += (1 if self.is_alive(x  ,y-1) else 0)
        num += (1 if self.is_alive(x+1,y-1) else 0)
        num += (1 if self.is_alive(x-1,y) else 0)
        num += (1 if self.is_alive(x+1,y) else 0)
        num += (1 if self.is_alive(x-1,y+1) else 0)
        num += (1 if self.is_alive(x  ,y+1) else 0)
        num += (1 if self.is_alive(x+1,y+1) else 0)
        return num
        
    def iterate_from(self, fromCells):
        for x in range(w):
            for y in range(h):
                num_live_nbrs = fromCells.get_num_live_neighbours(x,y)
                is_alive = fromCells.is_alive(x,y)
                if is_alive and (num_live_nbrs < 2 or num_live_nbrs > 3):
                    self.cells[x][y] = 0 # Died
                elif not is_alive and num_live_nbrs == 3:
                    self.cells[x][y] = 255 # Born
                else:
                    self.cells[x][y] = fromCells.cells[x][y] # Unchanged state

def ExportToLeds(cells):
    for x in range(w):
        for y in range(h):
            value = cells[x][y]
            uni.set_pixel_value(x,y,value)


def GameOfLife():
    cellsA = Cells()
    cellsB = Cells()
    start = True
    stop = False
    while True:
        if stop:
            return
        if start:
            cellsA.clear_all()
            cellsA.set_random_cells_to_value(0.2, 255)
            start = False
        ExportToLeds(cellsA.cells)
        time.sleep_ms(200)
        cellsB.iterate_from(cellsA)
        (cellsA, cellsB) = (cellsB, cellsA)
        start = uni.is_pressed(uni.BUTTON_A)
        stop = uni.is_pressed(uni.BUTTON_B)
