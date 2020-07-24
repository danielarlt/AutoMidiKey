import tkinter as tk
from client import threadedClient


if __name__ == '__main__':
    root = tk.Tk()
    client = threadedClient(root)
    root.mainloop()
