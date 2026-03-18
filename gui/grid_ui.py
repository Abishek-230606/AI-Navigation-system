import tkinter as tk

class GridUI:
    def __init__(self, root, size=4):
        self.root = root
        self.size = size
        self.buttons = []

        self.start = None
        self.goal = None

        self.create_grid()

    def create_grid(self):
        for i in range(self.size):
            row = []
            for j in range(self.size):
                btn = tk.Button(
                    self.root,
                    text=" ",
                    width=6,
                    height=3,
                    command=lambda r=i, c=j: self.on_click(r, c)
                )
                btn.grid(row=i, column=j)
                row.append(btn)
            self.buttons.append(row)

    def on_click(self, row, col):
        if self.start is None:
            self.start = (row, col)
            self.buttons[row][col].config(bg="green")
            print(f"Start set at {self.start}")

        elif self.goal is None:
            self.goal = (row, col)
            self.buttons[row][col].config(bg="red")
            print(f"Goal set at {self.goal}")

        else:
            print("Start and Goal already selected")

    def create_grid(self):
        for i in range(self.size):
            row = []
            for j in range(self.size):
                btn = tk.Button(self.root, text=" ", width=6, height=3)
                btn.grid(row=i, column=j)
                row.append(btn)
            self.buttons.append(row)