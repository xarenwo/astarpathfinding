import pygame
import math
from queue import PriorityQueue


WIDTH = 800    # Width = Height, is a square.
WIN = pygame.display.set_mode((WIDTH,WIDTH))
pygame.display.set_caption("A* Path Finding")

RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,255,0)
YELLOW = (255,255,0)
WHITE = (255,255,255)
BLACK = (0,0,0)
PURPLE = (128,0,128)
ORANGE = (255,165,0)
GREY = (128,128,128)
TURQUOISE = (64,224,208)


class GridSpot:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows

    def get_position(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_start(self):
        self.color = ORANGE

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, win):
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        self.neighbors = []
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():    # Down a row
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():    # Up a row
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():    # Right a col
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():    # Down a row
            self.neighbors.append(grid[self.row][self.col - 1])

    def __lt__(self, other):
        return False


def h(point_1, point_2):
    # Using manhattan L distance
    x1, y1 = point_1
    x2, y2 = point_2
    return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(precedent_node, current, draw):
    while current in precedent_node:
        current = precedent_node[current]   # Traverse from end node back to the start node
        current.make_path()     # While traversing back, make the current spot PURPLE
        draw()


def algorithm(draw, grid, start, end):
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))
    precedent_node = {}
    g_score = {spot: float("inf") for row in grid for spot in row}
    g_score[start] = 0
    f_score = {spot: float("inf") for row in grid for spot in row}
    f_score[start] = h(start.get_position(), end.get_position())    # Shortest distance from start to goal is heuristic

    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]     # Lowest value f score
        open_set_hash.remove(current)   # take the node out of priority queue

        if current == end:
            # Make path
            reconstruct_path(precedent_node, end, draw)
            end.make_end()  # Don't draw purple on the end node
            return True

        for neighbor in current.neighbors:
            temp_g_score = g_score[current] + 1     # We assume distance between nodes is 1

            if temp_g_score < g_score[neighbor]:    # We found a better way to reach this neighbor, update track.
                precedent_node[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + h(neighbor.get_position(), end.get_position())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()  # Make it open so we know we already considered

        draw()

        if current != start:    # If the node we just looked at is not the start node, we make it red, we do not consider it ever again.
            current.make_closed()

    return False    # We did not find the path


def make_grid(rows, width):
    grid = []
    gap = width // rows     # Integer division

    for i in range(rows):
        grid.append([])
        for j in range(rows):
            spot = GridSpot(i, j, gap, rows)
            grid[i].append(spot)

    return grid


def draw_grid(win, rows, width):
    gap = width // rows

    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))

        for j in range(rows):
            pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
    win.fill(WHITE)

    for row in grid:
        for spot in row:
            spot.draw(win)

    draw_grid(win, rows, width)
    pygame.display.update()


def get_clicked_position(mouse_pos, rows, width):
    gap = width // rows
    y, x = mouse_pos

    row = y // gap
    col = x // gap

    return row,col


def main(win, width):
    ROWS = 40
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    started = False

    while run:      # If started, only allow quit button
        draw(win, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if started:
                continue

            if pygame.mouse.get_pressed()[0]:       # Left click
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                print('Row = {} |  Col = {} '. format(row,col))
                spot = grid[row][col]
                if not start and spot != end:
                    start = spot
                    start.make_start()

                elif not end and spot != start:
                    end = spot
                    end.make_end()

                elif spot != end and spot != start:
                    spot.make_barrier()

            elif pygame.mouse.get_pressed()[2]:     # Right click delete
                pos = pygame.mouse.get_pos()
                row, col = get_clicked_position(pos, ROWS, width)
                spot = grid[row][col]
                spot.reset()
                if spot == start:
                    start = None

                if spot == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:   # Assure we have a start and end node before running
                   for row in grid:     # Update neighbors of spot class, detect neighbors that are not neighbors (white squares)
                       for spot in row:
                           spot.update_neighbors(grid)

                   algorithm(lambda: draw(win, grid, ROWS, width), grid, start, end)


                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)


    pygame.quit()


main(WIN, WIDTH)


