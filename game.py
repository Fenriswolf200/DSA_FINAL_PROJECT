import pygame 
import numpy as np


class MarbleGame:
    def __init__(self, size=7):
        self.selected_marble = None
        self.board = self.create_board(size)
        self.size = size
        
        self.movement_vectors = {
            "up": np.array([-2,0]),
            "down": np.array([2,0]),
            "left": np.array([0,-2]),
            "right": np.array([0,2])
        }
        
        self.midpoint_movement_vectors = {
            "up": np.array([-1,0]),
            "down": np.array([1,0]),
            "left": np.array([0,-1]),
            "right": np.array([0,1])
        }

    def create_board(self, size) -> np.array:
        board = np.full((size, size), 1)
        board[size//2][size//2] = 0

        for row in range(size):
            for col in range(size):
                if (row < size // 3 or row >= size - size // 3) and (col < size // 3 or col >= size - size // 3):
                    board[row, col] = 2

        return board

    def check_movement_validity(self, selected_marble: np.array, new_position: np.array, midpoint: np.array):
        
        for pos in (selected_marble, new_position, midpoint):
            if pos[0] < 0 or pos[0] >= self.size or pos[1] < 0 or pos[1] >= self.size:
                return False

        if self.board[selected_marble[0], selected_marble[1]] != 1:
            return False
        if self.board[midpoint[0], midpoint[1]] != 1:
            return False
        if self.board[new_position[0], new_position[1]] != 0:
            return False

        return True


    def move_marble(self, selected_marble:np.array, direction:str)-> bool:
        
        new_position = np.sum(selected_marble, self.movement_vectors[direction])
        midpoint = np.sum(selected_marble, self.midpoint_movement_vectors[direction])
        
        if self.check_movement_validity(selected_marble, new_position, midpoint) == False:
            return False
        
        
        self.board[new_position[0]][new_position[1]]=1
        self.board[selected_marble[0]][selected_marble[1]]=0
        self.board[midpoint[0]][midpoint[1]]=0
        
        return True


    def render(self):
        pass

if __name__ == "__main__":


    code = MarbleGame()

    print(code.board)