import random
import tkinter as tk

from logic.search import a_star, bfs, dfs, calculate_risk


class GridUI:
    def __init__(self, root, size=4, obstacle_count=3):
        self.root = root
        self.size = size
        self.obstacle_count = min(obstacle_count, (size * size) - 2)

        self.colors = {
            "bg": "#0f172a",
            "panel": "#111827",
            "panel_alt": "#1f2937",
            "text": "#e5e7eb",
            "muted": "#94a3b8",
            "accent": "#22c55e",
            "goal": "#ef4444",
            "obstacle": "#020617",
            "path": "#38bdf8",
            "cell": "#e2e8f0",
            "cell_text": "#0f172a",
            "border": "#334155",
            "warning": "#f59e0b",
        }

        self.root.configure(bg=self.colors["bg"])
        self.root.title("AI Navigation System")

        self.buttons = []
        self.start = None
        self.goal = None
        self.obstacles = set()
        self.performance = {
            "A*": [],
            "BFS": [],
            "DFS": [],
        }

        self.last_paths = {"A*": None, "BFS": None, "DFS": None}
        self.status_var = tk.StringVar(value="Select the start cell.")
        self.best_algo_var = tk.StringVar(value="Best Algorithm: Waiting...")
        self.results_var = tk.StringVar(value="A*: -\nBFS: -\nDFS: -")
        self.learning_var = tk.StringVar(
            value="Learning Summary:\nA*: -\nBFS: -\nDFS: -"
        )

        self.build_layout()
        self.create_grid()

    def build_layout(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors["bg"], padx=20, pady=20)
        self.main_frame.pack(fill="both", expand=True)

        self.header_frame = tk.Frame(self.main_frame, bg=self.colors["bg"])
        self.header_frame.pack(fill="x", pady=(0, 16))

        title_label = tk.Label(
            self.header_frame,
            text="AI Navigation System",
            font=("Segoe UI", 20, "bold"),
            fg=self.colors["text"],
            bg=self.colors["bg"],
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            self.header_frame,
            text="Choose a start point and a goal point to compare A*, BFS, and DFS.",
            font=("Segoe UI", 10),
            fg=self.colors["muted"],
            bg=self.colors["bg"],
        )
        subtitle_label.pack(anchor="w", pady=(4, 0))

        self.content_frame = tk.Frame(self.main_frame, bg=self.colors["bg"])
        self.content_frame.pack(fill="both", expand=True)

        self.grid_card = tk.Frame(
            self.content_frame,
            bg=self.colors["panel"],
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            padx=18,
            pady=18,
        )
        self.grid_card.pack(side="left", padx=(0, 16), fill="both")

        grid_title = tk.Label(
            self.grid_card,
            text="Grid",
            font=("Segoe UI", 14, "bold"),
            fg=self.colors["text"],
            bg=self.colors["panel"],
        )
        grid_title.pack(anchor="w", pady=(0, 12))

        self.grid_frame = tk.Frame(self.grid_card, bg=self.colors["panel"])
        self.grid_frame.pack()

        self.side_panel = tk.Frame(
            self.content_frame,
            bg=self.colors["panel_alt"],
            bd=0,
            highlightthickness=1,
            highlightbackground=self.colors["border"],
            padx=18,
            pady=18,
            width=280,
        )
        self.side_panel.pack(side="right", fill="y")
        self.side_panel.pack_propagate(False)

        status_title = tk.Label(
            self.side_panel,
            text="Live Results",
            font=("Segoe UI", 14, "bold"),
            fg=self.colors["text"],
            bg=self.colors["panel_alt"],
        )
        status_title.pack(anchor="w")

        self.status_label = tk.Label(
            self.side_panel,
            textvariable=self.status_var,
            font=("Segoe UI", 10),
            fg=self.colors["accent"],
            bg=self.colors["panel_alt"],
            justify="left",
            wraplength=240,
        )
        self.status_label.pack(anchor="w", pady=(8, 14))

        self.best_algo_label = tk.Label(
            self.side_panel,
            textvariable=self.best_algo_var,
            font=("Segoe UI", 11, "bold"),
            fg=self.colors["warning"],
            bg=self.colors["panel_alt"],
            justify="left",
            wraplength=240,
        )
        self.best_algo_label.pack(anchor="w", pady=(0, 14))

        results_title = tk.Label(
            self.side_panel,
            text="Algorithm Results",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors["text"],
            bg=self.colors["panel_alt"],
        )
        results_title.pack(anchor="w")

        self.results_label = tk.Label(
            self.side_panel,
            textvariable=self.results_var,
            font=("Consolas", 10),
            fg=self.colors["text"],
            bg=self.colors["panel_alt"],
            justify="left",
            anchor="w",
        )
        self.results_label.pack(anchor="w", pady=(8, 14), fill="x")

        learning_title = tk.Label(
            self.side_panel,
            text="Learning Summary",
            font=("Segoe UI", 11, "bold"),
            fg=self.colors["text"],
            bg=self.colors["panel_alt"],
        )
        learning_title.pack(anchor="w")

        self.learning_label = tk.Label(
            self.side_panel,
            textvariable=self.learning_var,
            font=("Consolas", 10),
            fg=self.colors["muted"],
            bg=self.colors["panel_alt"],
            justify="left",
            anchor="w",
        )
        self.learning_label.pack(anchor="w", pady=(8, 16), fill="x")

        self.reset_button = tk.Button(
            self.side_panel,
            text="Reset Board",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors["accent"],
            fg="#052e16",
            activebackground="#16a34a",
            activeforeground="#ffffff",
            relief="flat",
            padx=12,
            pady=8,
            command=self.reset_board,
            cursor="hand2",
        )
        self.reset_button.pack(anchor="w")

        # Compare and view controls
        self.compare_button = tk.Button(
            self.side_panel,
            text="Compare Algorithms",
            font=("Segoe UI", 10, "bold"),
            bg="#3b82f6",
            fg="#ffffff",
            activebackground="#2563eb",
            relief="flat",
            padx=10,
            pady=8,
            command=self.find_path,
            cursor="hand2",
        )
        self.compare_button.pack(anchor="w", pady=(10, 6))

        btn_frame = tk.Frame(self.side_panel, bg=self.colors["panel_alt"])
        btn_frame.pack(anchor="w", pady=(0, 12))

        self.view_astar_btn = tk.Button(
            btn_frame,
            text="View A*",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            relief="flat",
            padx=8,
            pady=6,
            command=lambda: self.view_path("A*"),
            state="disabled",
            cursor="hand2",
        )
        self.view_astar_btn.grid(row=0, column=0, padx=(0, 6))

        self.view_bfs_btn = tk.Button(
            btn_frame,
            text="View BFS",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            relief="flat",
            padx=8,
            pady=6,
            command=lambda: self.view_path("BFS"),
            state="disabled",
            cursor="hand2",
        )
        self.view_bfs_btn.grid(row=0, column=1, padx=(0, 6))

        self.view_dfs_btn = tk.Button(
            btn_frame,
            text="View DFS",
            font=("Segoe UI", 9, "bold"),
            bg=self.colors["panel"],
            fg=self.colors["text"],
            relief="flat",
            padx=8,
            pady=6,
            command=lambda: self.view_path("DFS"),
            state="disabled",
            cursor="hand2",
        )
        self.view_dfs_btn.grid(row=0, column=2)

        # Legend
        legend_frame = tk.Frame(self.side_panel, bg=self.colors["panel_alt"])
        legend_frame.pack(anchor="w", pady=(6, 0), fill="x")

        def legend_item(parent, color, text):
            f = tk.Frame(parent, bg=self.colors["panel_alt"])
            c = tk.Label(f, bg=color, width=2, height=1, bd=0)
            c.pack(side="left", padx=(0, 6))
            l = tk.Label(f, text=text, fg=self.colors["muted"], bg=self.colors["panel_alt"], font=("Segoe UI", 9))
            l.pack(side="left")
            return f

        legend_item(legend_frame, self.colors["accent"], "Start (S)").pack(side="left", padx=(0,8))
        legend_item(legend_frame, self.colors["goal"], "Goal (G)").pack(side="left", padx=(0,8))
        legend_item(legend_frame, self.colors["obstacle"], "Obstacle (X)").pack(side="left", padx=(0,8))
        legend_item(legend_frame, self.colors["path"], "Path (*)").pack(side="left")
    def generate_obstacles(self):
        while len(self.obstacles) < self.obstacle_count:
            row = random.randint(0, self.size - 1)
            col = random.randint(0, self.size - 1)
            self.obstacles.add((row, col))

    def create_grid(self):
        self.generate_obstacles()

        for row_index in range(self.size):
            row_buttons = []
            for col_index in range(self.size):
                button = tk.Button(
                    self.grid_frame,
                    text="",
                    width=6,
                    height=3,
                    font=("Segoe UI", 11, "bold"),
                    bg=self.colors["cell"],
                    fg=self.colors["cell_text"],
                    activebackground="#cbd5e1",
                    relief="flat",
                    bd=0,
                    cursor="hand2",
                    command=lambda r=row_index, c=col_index: self.on_click(r, c),
                )

                if (row_index, col_index) in self.obstacles:
                    button.config(
                        bg=self.colors["obstacle"],
                        state="disabled",
                        disabledforeground="#ffffff",
                        text="X",
                    )

                button.grid(row=row_index, column=col_index, padx=4, pady=4)
                row_buttons.append(button)

            self.buttons.append(row_buttons)

    def reset_board(self):
        for row in self.buttons:
            for button in row:
                button.destroy()

        self.buttons = []
        self.start = None
        self.goal = None
        self.obstacles = set()
        self.last_paths = {"A*": None, "BFS": None, "DFS": None}

        self.results_var.set("A*: -\nBFS: -\nDFS: -")
        self.best_algo_var.set("Best Algorithm: Waiting...")
        self.learning_var.set(self.get_learning_summary())
        self.status_var.set("Select the start cell.")

        # disable view buttons until new results
        try:
            self.view_astar_btn.config(state="disabled")
            self.view_bfs_btn.config(state="disabled")
            self.view_dfs_btn.config(state="disabled")
        except Exception:
            pass

        self.create_grid()

    def on_click(self, row, col):
        if self.start is None:
            self.start = (row, col)
            self.buttons[row][col].config(bg=self.colors["accent"], fg="white", text="S")
            self.status_var.set(f"Start selected at {self.start}. Now select the goal cell.")
            return

        if self.goal is None:
            self.goal = (row, col)
            self.buttons[row][col].config(bg=self.colors["goal"], fg="white", text="G")
            self.status_var.set(f"Goal selected at {self.goal}. Running search...")
            self.find_path()
            return

        self.status_var.set("Start and goal are already selected. Press Reset Board to try again.")

    def find_path(self):
        if self.start and self.goal:
            path_astar = a_star(self.start, self.goal, self.obstacles, self.size)
            path_bfs = bfs(self.start, self.goal, self.obstacles, self.size)
            path_dfs = dfs(self.start, self.goal, self.obstacles, self.size)

            self.last_paths["A*"] = path_astar
            self.last_paths["BFS"] = path_bfs
            self.last_paths["DFS"] = path_dfs

            print("\n--- Agent Results ---")

            results = []
            result_lines = []

            if path_astar:
                risk = calculate_risk(path_astar, self.obstacles, self.size)
                results.append(("A*", path_astar, len(path_astar), risk))
                self.performance["A*"].append(len(path_astar))
                print(f"A*: Length={len(path_astar)}, Risk={risk}")
                result_lines.append(f"A*: Length {len(path_astar)} | Risk {risk}")
                self.view_astar_btn.config(state="normal")
            else:
                result_lines.append("A*: Failed")
                self.view_astar_btn.config(state="disabled")

            if path_bfs:
                risk = calculate_risk(path_bfs, self.obstacles, self.size)
                results.append(("BFS", path_bfs, len(path_bfs), risk))
                self.performance["BFS"].append(len(path_bfs))
                print(f"BFS: Length={len(path_bfs)}, Risk={risk}")
                result_lines.append(f"BFS: Length {len(path_bfs)} | Risk {risk}")
                self.view_bfs_btn.config(state="normal")
            else:
                result_lines.append("BFS: Failed")
                self.view_bfs_btn.config(state="disabled")

            if path_dfs:
                risk = calculate_risk(path_dfs, self.obstacles, self.size)
                results.append(("DFS", path_dfs, len(path_dfs), risk))
                self.performance["DFS"].append(len(path_dfs))
                print(f"DFS: Length={len(path_dfs)}, Risk={risk}")
                result_lines.append(f"DFS: Length {len(path_dfs)} | Risk {risk}")
                self.view_dfs_btn.config(state="normal")
            else:
                result_lines.append("DFS: Failed")
                self.view_dfs_btn.config(state="disabled")

            self.results_var.set("\n".join(result_lines))
            self.learning_var.set(self.get_learning_summary())

            if not results:
                print("No path found")
                self.best_algo_var.set("Best Algorithm: No path found")
                self.status_var.set("No algorithm found a valid path.")
                return

            best = min(results, key=lambda x: (x[2], x[3]))
            best_algo, best_path, best_len, best_risk = best

            print(f"\nBest Algorithm: {best_algo}")
            print(f"Best Path Length: {best_len}, Risk: {best_risk}")

            self.best_algo_var.set(
                f"Best Algorithm: {best_algo}\nBest Path Length: {best_len} | Risk: {best_risk}"
            )
            self.status_var.set(f"{best_algo} found the best route. Animating path now...")
            self.show_path(best_path)
            self.animate_path(best_path)

    def view_path(self, algo_name):
        """Animate the path for a specific algorithm if available."""
        path = self.last_paths.get(algo_name)
        if not path:
            self.status_var.set(f"{algo_name} did not find a path.")
            return

        # clear any previous temporary markers
        self.clear_path_markers()
        self.status_var.set(f"Animating path from {algo_name}...")
        self.animate_path(path)

    def clear_path_markers(self):
        for r in range(len(self.buttons)):
            for c in range(len(self.buttons[r])):
                if (r, c) not in (self.start, self.goal) and (r, c) not in self.obstacles:
                    self.buttons[r][c].config(bg=self.colors["cell"], fg=self.colors["cell_text"], text="")

    def get_learning_summary(self):
        lines = ["Learning Summary:"]
        for algo, values in self.performance.items():
            if values:
                avg = sum(values) / len(values)
                lines.append(f"{algo}: avg {avg:.2f}")
            else:
                lines.append(f"{algo}: -")
        return "\n".join(lines)

    def animate_path(self, path, index=0):
        if index < len(path):
            row, col = path[index]

            if (row, col) not in (self.start, self.goal):
                self.buttons[row][col].config(bg=self.colors["path"], fg="white", text="*")

            self.root.after(400, lambda: self.animate_path(path, index + 1))
        else:
            self.status_var.set("Path animation complete. Press Reset Board to try another run.")
