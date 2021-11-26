from matplotlib import pyplot
from enum import Enum
from random import randrange
import time

class Item(Enum):
    NONE = 0
    PLAYER = 1
    ENEMY = 2
    OBSTACLE = 3
    PATH = 4

class Node:
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position
        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position

class Game:
    def __init__(self, board_x, board_y, enemy_count=0, player_count=0):
        self.board_size = (board_x, board_y)
        self.clear_grid()

    def _valid_moves(self):
        moves = [
            [0,1],   # up
            [1,1],   # right-up
            [1,0],   # right
            [1,-1],  # right-down
            [0,-1],  # down
            [-1,-1], # left-down
            [-1,0],  # left
            [-1,1],  #left-up
        ]
        return moves

    def clear_grid(self):
        self.grid = [[0 for i in range(self.board_size[0])] for j in range(self.board_size[1] )] # list of lists all with 0 meaning it doesn't have data
        self.grid_x = self.board_size[0]
        self.grid_y = self.board_size[1]

    def show_grid(self):
        pyplot.figure(figsize=(5,5))
        pyplot.imshow(self.grid)
        pyplot.show()

    def print_grid(self):
        print('='*20)
        print(self.grid)

    def place_on_grid(self, item_type, location): 
        if location:
            x,y = location
        else: # no location. put it somewhere random
            x,y = randrange(0,self.grid_x-1), randrange(0,self.grid_y-1) 
        if self.grid[x][y] == Item.NONE.value: # if there is nothing there already
            self.grid[x][y] = item_type.value
        return x,y

    def create_item(self, item_type, location=None):
        if item_type:
            location = self.place_on_grid( item_type=item_type, location=location )
            return location

    def non_walkable_tiles(self): #TODO: put this on the tile object instead of game
        return [Item.OBSTACLE.value]

    def path_calc(self, current_node):
        path = []
        current = current_node
        while current is not None:
            path.append(current.position)
            current = current.parent
        return path[::-1] # reverse it

    def get_neighbors(self, current_node):
        children = []
        for move in self._valid_moves():
            node_position = (current_node.position[0] + move[0],
                            current_node.position[1] + move[1])
            # check node is still on board
            if (node_position[0] > self.grid_x-1 or
                node_position[0] < 0 or
                node_position[1] > self.grid_y-1 or
                node_position[1] < 0 ):
                continue

            # check if we can walk on it 
            tile_numeric = self.grid[node_position[0]][node_position[1]]
            if tile_numeric in self.non_walkable_tiles():
                continue


            new_node = Node(current_node, node_position)
            children.append(new_node)
        return children

    def search(self, start, end, cost=1):
        print('starting search..')
        start_time = time.time()
        start_node = Node(None, start)
        end_node = Node(None, end)

        to_visit_list = [start_node] # begin with start node
        visited_list = []

        iterations = 0
        while len(to_visit_list) > 0:
            iterations += 1 

            current_node = to_visit_list[0]
            for next_node in to_visit_list:
                if next_node.f < current_node.f:
                    current_node = next_node

            if iterations > self.grid_x**10:
                print('too long to compute')
                return

            if current_node.position == end_node.position:
                end_time = time.time()
                print( 'found path in time: {}'.format(end_time-start_time) )
                path = self.path_calc( current_node )
                [self.place_on_grid(Item.PATH, location) for location in path if location not in [start_node.position, end_node.position]] # color the grid
                return path

            #get neighbors
            neighbors = self.get_neighbors(current_node)
            for neighbor in neighbors:
                if neighbor in visited_list: # if we've already checked it
                    continue
                neighbor.g = current_node.g + cost
                neighbor.h = ( (neighbor.position[0] - end_node.position[0])**2 + (neighbor.position[1] - end_node.position[1])**2 )**0.5
                neighbor.f = neighbor.g + neighbor.h
                if len([visit_node for visit_node in to_visit_list if neighbor == visit_node and neighbor.g > visit_node.g]) > 0:
                    continue
                to_visit_list.append(neighbor)

            to_visit_list.remove(current_node)
            visited_list.append(current_node)


game = Game(board_x=1000,board_y=1000)
player = game.create_item(Item.PLAYER, location=(900,654))
enemy = game.create_item(Item.ENEMY, location=(1,1))

percent_map = 0.40
number_of_objstacles = percent_map * game.grid_x * game.grid_y
random_objstacles = [game.create_item(Item.OBSTACLE) for _ in range(round(number_of_objstacles))]
game.show_grid()

game.search(player, enemy)
game.show_grid()
