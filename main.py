import tkinter as tk
from gui.grid_ui import GridUI

def main():
    root = tk.Tk()
    root.title("AI Navigation System")

    app = GridUI(root)

    root.mainloop()

if __name__ == "__main__":
    main()