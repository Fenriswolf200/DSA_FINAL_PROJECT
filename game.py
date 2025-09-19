import pygame 
import numpy as np


class MarbleGame:
    def __init__(self, size=7):
        self.selected_marble = None
        self.board = self.create_board(size)
        self.size = size
        

    def create_board(self, size) -> np.array:
        board = np.full((size, size), 1)
        board[size//2][size//2] = 0

        for row in range(size):
            for col in range(size):
                if (row < size // 3 or row >= size - size // 3) and (col < size // 3 or col >= size - size // 3):
                    board[row, col] = 2
        return board

        
    
    def check_movement(self, selected_marble:np.array, destination:np.array) -> bool:
        return True


    def move_marble(self, selected_marble:np.array, direction:str)-> None:
        pass


    def render(self):
        pass

if __name__ == "__main__":


    code = MarbleGame()

    print(code.board)