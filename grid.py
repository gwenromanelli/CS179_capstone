from PySide2.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from PySide2.QtCore import QTimer
from PySide2.QtGui import QFont

from buffer import BufferWindow
import container as cont

# TESTING_PATH = [[(3,4), (3,3),(3,2), (4,2),(5,2),(6,2),(7,2),(8,2),(-2,-2)],
#                 [(3,7),(3,8),(3,9),(3,10),(4,10),(5,10),(6,10),(6,9),(6,8)],
#                 [(1,5),(1,6),(1,7),(1,8),(1,9),(100,100),(200,100),(300,100),(400,100)],
#                 [(2,6), (3,6), (4,6), (5,6), (-2,-2), (6,6), (7,6), (8,6), (9,6), (9,7)],
#                 [(11,3), (10,3), (9,3), (8,3), (7,3), (6,3), (5,3), (5,4), (5,5), (5,6), (5,7), (5,8), (5,9)],
#                 [(1,5), (2,5), (3,5), (4,5), (5,5), (6,5), (7,5)]]

TESTING_PATH = [[(3,4), (3,3),(3,2), (4,2),(5,2),(6,2),(7,2),(8,2),(-2,-2)],
                [(3,7),(3,8),(3,9),(3,10),(4,10),(5,10),(6,10),(6,9),(6,8)],
                [(11,3), (10,3), (9,3), (8,3), (7,3), (6,3), (5,3), (5,4), (5,5), (5,6), (5,7), (5,8), (5,9)]]

class BlockGrid(QWidget):
    def __init__(self, parent_canvas, driver, input_path, container_status, parent=None):
        super().__init__(parent)
        
        self.path = input_path
        self.driver = driver
        self.container_status = container_status
        
        
        self.costs = cost_calculator(self.path)
        
        rows = 12
        
        # 9 cols + 1 for above the ship area
        cols = 10
        
        # Set the default block_size to 96
        block_size = 96
        
        self.parent_canvas = parent_canvas
        
        # Count how many path have already complete, use to track the current path when update
        self.finish_path = 0
        
        # Index to track the current block in the path
        self.path_index = 0
        
        # 2 coordinates to track the path block
        self._track_block_x = self.path[self.finish_path][0][0]
        self._track_block_y = self.path[self.finish_path][0][1]
        
        # Create a canvas layout to hold the blocks and button 
        animation_page_layout = QHBoxLayout()
        self.setLayout(animation_page_layout)
        
        # Create the buffer and truck blocks and add them to the layout
        buffer_truck_layout = QGridLayout()
        buffer_truck_layout.setSpacing(0)
        animation_page_layout.addLayout(buffer_truck_layout)
        
        buffer_block = QLabel()
        truck_block = QLabel()
        
        # Specify the font size and boldness
        buffer_block.setText('Buffer')
        truck_block.setText('Truck')

        buffer_block.setFont(QFont("Arial", 12, QFont.Bold))
        truck_block.setFont(QFont("Arial", 12, QFont.Bold))
        
        buffer_block.setFixedSize(block_size, block_size)
        truck_block.setFixedSize(block_size, block_size)
        
        block_style = 'border: 1px solid black; '
        buffer_block.setStyleSheet(block_style)
        truck_block.setStyleSheet(block_style)
        
        # Set buffer and truck block property to -3, -2 to avoid conflict with the grid
        buffer_block.setProperty('row', -3)
        buffer_block.setProperty('col', -3)
        
        truck_block.setProperty('row', -2)
        truck_block.setProperty('col', -2)
        
        buffer_truck_layout.addWidget(buffer_block, 0, 0)
        buffer_truck_layout.addWidget(truck_block, 0, 1)
        

        # Create a grid layout to hold the blocks
        grid_layout = QGridLayout()
        grid_layout.setSpacing(0)
        animation_page_layout.addLayout(grid_layout)
        
        # Add the blocks to the grid layout
        for row in range(rows):
            for col in range(cols):
                label = QLabel()
                label.setFixedSize(block_size, block_size)
                transfered_row = row + 1
                transfered_col = 10 - col
                label.setProperty('row', transfered_row)
                label.setProperty('col', transfered_col)
                
                if col == 0:
                    block_style = 'border: none; background-color: transparent;'
                else:
                    block_style = 'border: 1px solid black; '

                label.setStyleSheet(block_style)
                grid_layout.addWidget(label, col, row)
                
        
        # Update the initial block and reset the path color
        self.update_blocks_color()
        
        # Update nan block
        self.update_NAN_blocks_color()
        
        # Update the label block name
        self.update_label_name()
        
        
        # Add total cost label to the layout
        total_cost = QLabel("Total Cost: " + str(sum(self.costs)) + " mins")
        total_cost.setFont(QFont("Arial", 20, QFont.Bold))
        total_cost.setStyleSheet("border: 1px solid black; ")
        
        # Add button to the layout
        next_button = QPushButton('Next')
        next_button.setFixedSize(300, 150)
        next_button.setFont(QFont("Arial", 20, QFont.Bold))
        next_button.clicked.connect(self.next_path)
        
        # Button holder layout
        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(total_cost)
        buttons_layout.addWidget(next_button)
        animation_page_layout.addLayout(buttons_layout,3)
        
        
        self.setFixedSize(25 * block_size, 10 * block_size)
        
        # Call the buffer window if needed, this only run for the first path
        if self.buffer_require():
            self.show_Buffer_window()
                
        # Create a QTimer to update the labels every second
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_labels)
        self.timer.start(500)

    def update_blocks_color(self):
        for label in self.findChildren(QLabel):
            row = label.property('row')
            col = label.property('col')
            
            # block_style = 'border: none; background-color: transparent;'
            block_style = 'border: 1px solid black; '
            if col == 10:
                block_style = 'border: none; background-color: transparent;'
            elif (row, col) == (self.path[self.finish_path][0][0], self.path[self.finish_path][0][1]):
                block_style = 'border: 1px solid black; background-color: green;'
            elif (row,col) == (self.path[self.finish_path][-1][0], self.path[self.finish_path][-1][1]):
                block_style = 'border: 1px solid black; background-color: yellow;'
            label.setStyleSheet(block_style)
    
    # Update the labels
    def update_labels(self):
        
        # print(self._track_block_x, self._track_block_y)
        
        # Finish one cycle of path, clear the color and tracking block
        if self.path_index == len(self.path[self.finish_path]):
            # print("Finish one cycle")
            self.path_index = 0
            
            # Reset the tracking block to initial position
            self._track_block_x = self.path[self.finish_path][self.path_index][0]
            self._track_block_y = self.path[self.finish_path][self.path_index][1]
            
            # Update the initial block and reset the path color
            self.update_blocks_color()
            self.update_NAN_blocks_color()
                
            # Reset the buffer window
            if self.buffer_require():
                self.Buffer_window.clear_grid()
        
        # Otherwise, update the path block
        else:            
            self._track_block_x = self.path[self.finish_path][self.path_index][0]
            self._track_block_y = self.path[self.finish_path][self.path_index][1]
            
            # Skip the first and last block
            if self.path_index != 0 and self.path_index != len(self.path[self.finish_path]) - 1:
                if self._track_block_x < 100:
                    for label in self.findChildren(QLabel):
                        row = label.property('row')
                        col = label.property('col')
                        
                        if (row , col) == (self._track_block_x, self._track_block_y):
                            label.setStyleSheet('border: 1px solid black; background-color: red;')
                        elif row == self._track_block_x and col == self._track_block_y:
                            label.setStyleSheet('border: 1px solid black; background-color: red;')
                            
                else:
                    if hasattr(self, 'Buffer_window'):
                        block_style = 'border: 1px solid black; background-color: red;'  # Customize this style as needed
                        self.Buffer_window.update_buffer_labels(block_style, self._track_block_x, self._track_block_y)
            # Inceament the path index
            self.path_index += 1
    
    def update_label_name(self):
        
        # Format: [[name, [x,y]], [name, [x,y]], ...]
        exist_contains =[]
        # Format: [x,y], [x,y], ...]
        empty_contains = []
        for x in range(len(self.container_status)) :
            for y in range(len(self.container_status[x])):
                if type(self.container_status[x][y]) is cont.container:
                    exist_contains.append([self.container_status[x][y].name, [x,y]])
                elif self.container_status[x][y] == 0:
                    empty_contains.append([x,y])
        
        # convert x, y cords
        for item in exist_contains:
            coord = item[1]
            coord[0], coord[1] = coord[1], coord[0]
            coord[0] = coord[0] + 1
            coord[1] = 9 - coord[1] 
        
        for item in empty_contains:
            item[0], item[1] = item[1], item[0]
            item[0] = item[0] + 1
            item[1] = 9 - item[1]
        
        for label in self.findChildren(QLabel):
            row = label.property('row')
            col = label.property('col')
            for item in exist_contains:
                if (row, col) == (item[1][0], item[1][1]):
                    label.setText(item[0])
                    label.setFont(QFont("Arial", 12, QFont.Bold))
                    
            for item in empty_contains:
                if (row, col) == (item[0], item[1]):
                    label.setText("")
                    label.setFont(QFont("Arial", 12, QFont.Bold))

    # This function update all NAN block to black color, based on the input ship manifest
    def update_NAN_blocks_color(self):
        nan_contains =[]
        for x in range(len(self.container_status)) :
            for y in range(len(self.container_status[x])):
                if self.container_status[x][y] == -1:
                    nan_contains.append([x,y])

        # convert x, y cords
        for item in nan_contains:
            item[0], item[1] = item[1], item[0]
            item[0] = item[0] + 1
            item[1] = 9 - item[1] 
                
        for label in self.findChildren(QLabel):
            row = label.property('row')
            col = label.property('col')
            for item in nan_contains:
                if (row, col) == (item[0], item[1]):
                    block_style = 'border: 1px solid black; background-color: black;'
                    label.setStyleSheet(block_style)
    
    # Switch items in the container status
    def update_container_status_move(self, coord1, coord2):
        old_coord = coord1
        new_coord = coord2
        
        def reverse_coord(coord):
            coord[0] = coord[0] - 1
            coord[1] = 9 - coord[1]
            coord[0], coord[1] = coord[1], coord[0]

        reverse_coord(old_coord)
        reverse_coord(new_coord)
        
        self.container_status[old_coord[0]][old_coord[1]], self.container_status[new_coord[0]][new_coord[1]] = self.container_status[new_coord[0]][new_coord[1]], self.container_status[old_coord[0]][old_coord[1]]
        
    def next_path(self):
        old_coord = self.path[self.finish_path][0]
        new_coord = self.path[self.finish_path][-1]
        self.update_container_status_move(old_coord, new_coord)
        
        self.finish_path += 1
        self.path_index = 0
        
        if self.finish_path == len(self.path):
            finish_page = FinishPage(self.parent_canvas)
            # Set the finish page as index 5
            self.parent_canvas.insertWidget(5, finish_page)
            self.parent_canvas.setCurrentIndex(5)
            self.deleteLater()
            return
                
        if hasattr(self, 'Buffer_window'):
            self.Buffer_window.close()
                
        # Check if the current path require buffer
        if self.buffer_require():
            self.show_Buffer_window()
        
        # Clear blocks color
        self.update_blocks_color()
        self.update_NAN_blocks_color()
        self.update_label_name()

    # A helper function to check if the current path require buffer
    def buffer_require(self):
        for corr in self.path[self.finish_path]:
            if corr[0] > 100:
                return True
        return False
    
    # Add this function to create and show the Buffer window
    def show_Buffer_window(self):
        self.Buffer_window = BufferWindow()
        self.Buffer_window.show()

class FinishPage(QWidget):
    def __init__(self, parent_canvas, parent=None):
        super().__init__(parent)
        
        self.parent_canvas = parent_canvas
        
        # Create a QVBoxLayout to hold the finish message and a button to go back
        finish_page_layout = QVBoxLayout()
        self.setLayout(finish_page_layout)

        # Add a QLabel to display the finish message
        finish_message = QLabel("Transfer task is done! Remember to send the manifest to the ship company.")
        finish_message.setFont(QFont("Arial", 25, QFont.Bold))
        finish_page_layout.addWidget(finish_message)

        # Add a QPushButton to go back to the main page
        back_button = QPushButton("Back to home page")
        back_button.setFixedSize(800, 100)
        back_button.setFont(QFont("Arial", 20, QFont.Bold))
        back_button.clicked.connect(self.go_back)
        finish_page_layout.addWidget(back_button)

    def go_back(self):
        self.parent_canvas.setCurrentIndex(0)

'''
Algor:
    1. Sort all the block base on the ship, buffer area and truck
    2. If there is only ship, cost = # of ship_block - 1
    3. If there is ship and truck, cost = # of ship_block - 1 + 2 (for ship to truck)
    4: If there is ship and buffer, cost = # of ship_block - 1 + 4 (for ship to buffer) + # of buffer_block - 1
'''
def cost_calculator(paths):
    
    arr_costs = []
    for path in paths:
        
        blocks = {"truck": 0, "buffer": 0, "ship": 0}
        for move in path:
            if move[0] == -2:
                blocks["truck"] += 1
            elif move[0] >= 100:
                blocks["buffer"] += 1
            else:
                blocks["ship"] += 1

        total_cost = blocks["ship"] - 1
        if blocks["truck"] == 1:
            total_cost += 2
        elif blocks["buffer"] > 0:
            total_cost += blocks["buffer"] - 1
            total_cost += 4
        
        arr_costs.append(total_cost)

    return arr_costs