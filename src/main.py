import sys
import numpy as np
import random
from datetime import datetime
from PyQt5 import QtGui, QtCore
from PyQt5.QtWidgets import QApplication, QTableWidget, QTableWidgetItem, QGridLayout, QHeaderView


__author__ = "Carlos Manuel Molina Sotoca"
__email__ = "cmmolinas01@gmail.com"


# Seed for random numbers based on current datetime:
random.seed(str(datetime.now()))


class Game:
    def __init__(self, matrix_width=100, matrix_height=100):
        # Set game parameters:
        self.neighbours_for_underpopulation = 1
        self.neighbours_for_next_gen = [2, 3]
        self.neighbours_for_overpopulation = 4
        self.neighbours_for_reproduction = 3

        # Set matrix size variables:
        self.matrix_width = matrix_width
        self.matrix_height = matrix_height

        # Initialize matrix with dead (unpopulated) cells:
        self.matrix = np.full((self.matrix_width, self.matrix_height),
                              False,
                              dtype=bool)

    def update_matrix(self, data):
        self.matrix = data.copy()

    def set_matrix_initial_state(self):
        # Iterate over each cell:
        for x_coordinate in range(self.matrix_width):
            for y_coordinate in range(self.matrix_height):
                cell_coordinates = (x_coordinate, y_coordinate)
                self.matrix[cell_coordinates] = random.choice([True, False])

        # Correct initial state:
        matrix_discrete = self.matrix.copy()
        for x_coordinate in range(self.matrix_width):
            for y_coordinate in range(self.matrix_height):
                cell_coordinates = (x_coordinate, y_coordinate)
                cell_neighbours = self.get_cell_neighbours(cell_coordinates)

                # Set status:
                if self.matrix[cell_coordinates] and self.get_cell_overpopulation(cell_neighbours):
                    matrix_discrete[cell_coordinates] = False

        # Set state on iteration
        self.update_matrix(matrix_discrete)

    def get_cell_neighbours(self, coordinates):
        neighbours = 0
        x_coordinate = coordinates[0]
        y_coordinate = coordinates[1]

        # (x-1, y-1):
        if x_coordinate > 0 and y_coordinate > 0:
            neighbours += 1 if self.matrix[x_coordinate - 1, y_coordinate - 1] else 0
        # (x-1, y):
        if x_coordinate > 0:
            neighbours += 1 if self.matrix[x_coordinate - 1, y_coordinate] else 0
        # (x-1, y+1):
        if x_coordinate > 0 and y_coordinate < (self.matrix_height - 1):
            neighbours += 1 if self.matrix[x_coordinate - 1, y_coordinate + 1] else 0
        # (x, y+1):
        if y_coordinate < (self.matrix_height - 1):
            neighbours += 1 if self.matrix[x_coordinate, y_coordinate + 1] else 0
        # (x+1, y+1):
        if x_coordinate < (self.matrix_width - 1) and y_coordinate < (self.matrix_height - 1):
            neighbours += 1 if self.matrix[x_coordinate + 1, y_coordinate + 1] else 0
        # (x+1, y):
        if x_coordinate < (self.matrix_width - 1):
            neighbours += 1 if self.matrix[x_coordinate + 1, y_coordinate] else 0
        # (x+1, y-1):
        if x_coordinate < (self.matrix_width - 1) and y_coordinate > 0:
            neighbours += 1 if self.matrix[x_coordinate + 1, y_coordinate - 1] else 0
        # (x, y-1):
        if y_coordinate > 0:
            neighbours += 1 if self.matrix[x_coordinate, y_coordinate - 1] else 0
        return neighbours

    def get_cell_underpopulation(self, neighbours):
        if neighbours <= self.neighbours_for_underpopulation:
            return True
        else:
            return False

    def get_cell_next_generation(self, neighbours):
        if neighbours in self.neighbours_for_next_gen:
            return True
        else:
            return False

    def get_cell_overpopulation(self, neighbours):
        if neighbours >= self.neighbours_for_overpopulation:
            return True
        else:
            return False

    def get_cell_reproduction(self, neighbours):
        if neighbours == self.neighbours_for_reproduction:
            return True
        else:
            return False

    def set_cell_state(self, cell_coordinates):
        cell_status = self.matrix[cell_coordinates]
        cell_neighbours = self.get_cell_neighbours(cell_coordinates)

        # Any live cell with fewer than two live neighbours dies, as if by underpopulation.
        if cell_status and self.get_cell_underpopulation(cell_neighbours):
            cell_status = False

        # Any live cell with two or three live neighbours lives on to the next generation.
        if cell_status and self.get_cell_next_generation(cell_neighbours):
            cell_status = True

        # Any live cell with more than three live neighbours dies, as if by overpopulation.
        if cell_status and self.get_cell_overpopulation(cell_neighbours):
            cell_status = False

        # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
        if not cell_status and self.get_cell_reproduction(cell_neighbours):
            cell_status = True

        return cell_status

    def generate_iteration(self, *args):
        matrix_iteration = self.matrix.copy()

        # Iterate over each cell:
        for x_coordinate in range(self.matrix_width):
            for y_coordinate in range(self.matrix_height):
                # Set cell state:
                cell_coordinates = (x_coordinate, y_coordinate)
                matrix_iteration[cell_coordinates] = self.set_cell_state(cell_coordinates)

        # Set state on iteration
        self.update_matrix(matrix_iteration)


class ApplicationView(QTableWidget):
    def __init__(self, iterations=10000, matrix_width=40, matrix_height=40, *args):
        # Call the parent constructor
        QTableWidget.__init__(self, *args)
        self.resize(1920, 1080)

        # Initialize game:
        self.game = Game(matrix_width, matrix_height)

        # Set the size and title of the window
        self.setWindowTitle("Conway's Game of Life")

        # Create the table with necessary properties
        self.table = QTableWidget(self)
        self.table.setColumnCount(self.game.matrix_width)
        self.table.setRowCount(self.game.matrix_height)
        self.table.horizontalHeader().setVisible(False)
        self.table.verticalHeader().setVisible(False)

        # Initialize matrix:
        self.game.set_matrix_initial_state()
        self.set_data()

        # Show window:
        layout = QGridLayout()
        layout.addWidget(self.table, 0, 0)
        self.setLayout(layout)
        self.show()

        # Run:
        self.iterations = iterations
        self.run()

    def set_data(self):
        for index_row in range(self.game.matrix_width):
            for index_column in range(self.game.matrix_height):
                self.table.setItem(index_row, index_column, QTableWidgetItem())
                if self.game.matrix[index_row][index_column]:
                    self.table.item(index_row, index_column).setBackground(QtGui.QColor(0, 0, 0))
                else:
                    self.table.item(index_row, index_column).setBackground(QtGui.QColor(255, 255, 255))

        self.table.resizeColumnsToContents()
        self.table.resizeRowsToContents()

    def run(self, iteration=0, wait_time=200):
        # Better with threads:
        iteration += 1
        if iteration < self.iterations:
            self.game.generate_iteration()
            self.set_data()
            QtCore.QTimer.singleShot(wait_time, lambda: self.run(iteration))


def main():
    app = QApplication(sys.argv)
    mw = ApplicationView()
    mw.show()
    app.exec()


if __name__ == "__main__":
    main()
