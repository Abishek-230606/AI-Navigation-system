import random
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

from logic.agent import Agent


class GridUI:
    CELL_COLORS = {
        "empty": "#F1F5F9",
        "obstacle": "#1E293B",
        "start": "#10B981",
        "goal": "#EF4444",
        "trail": "#FDE047",
        "current": "#0EA5E9",
    }

    def __init__(self, root, size=6):
        self.root = root
        self.size = size
        self.agent = Agent()

        self.buttons = []
        self.obstacles = set()
        self.start = None
        self.goal = None
        self.current = None
        self.last_result = None
        self.animation_index = 0
        self.animation_job = None
        self.path_history = []
        self.decision_history = []

        self.status_var = tk.StringVar()
        self.selection_var = tk.StringVar()
        self.algorithm_var = tk.StringVar()
        self.summary_var = tk.StringVar()
        self.goal_var = tk.StringVar()
        self.step_var = tk.StringVar()

        self._configure_root()
        self._build_layout()
        self._create_grid()
        self._new_board()

    def _configure_root(self):
        self.root.configure(bg="#E2E8F0")
        self.root.minsize(1450, 920)

        style = ttk.Style()
        style.theme_use("clam")

        style.configure("App.TFrame", background="#E2E8F0")
        style.configure("Panel.TFrame", background="#FFFFFF")
        style.configure("SoftPanel.TFrame", background="#F8FAFC")
        style.configure(
            "Title.TLabel",
            background="#E2E8F0",
            foreground="#0F172A",
            font=("Segoe UI Semibold", 30),
        )
        style.configure(
            "Subtitle.TLabel",
            background="#E2E8F0",
            foreground="#475569",
            font=("Segoe UI", 15),
        )
        style.configure(
            "PanelTitle.TLabel",
            background="#FFFFFF",
            foreground="#0F172A",
            font=("Segoe UI Semibold", 18),
        )
        style.configure(
            "PanelText.TLabel",
            background="#FFFFFF",
            foreground="#475569",
            font=("Segoe UI", 13),
        )
        style.configure(
            "SectionHint.TLabel",
            background="#FFFFFF",
            foreground="#64748B",
            font=("Segoe UI", 11),
        )
        style.configure(
            "Status.TLabel",
            background="#FFFFFF",
            foreground="#1E293B",
            font=("Segoe UI Semibold", 14),
        )
        style.configure(
            "DecisionHero.TLabel",
            background="#F8FAFC",
            foreground="#0284C7",
            font=("Segoe UI Semibold", 22),
        )
        style.configure(
            "DecisionMeta.TLabel",
            background="#F8FAFC",
            foreground="#475569",
            font=("Segoe UI", 13),
        )
        style.configure(
            "Primary.TButton",
            font=("Segoe UI Semibold", 12),
            padding=(16, 11),
        )
        style.configure(
            "Summary.TButton",
            font=("Segoe UI Semibold", 10),
            padding=(8, 6),
        )
        style.configure(
            "MetricValue.TLabel",
            background="#F8FAFC",
            foreground="#0F172A",
            font=("Segoe UI Semibold", 18),
        )
        style.configure(
            "MetricLabel.TLabel",
            background="#F8FAFC",
            foreground="#64748B",
            font=("Segoe UI", 11),
        )

    def _build_layout(self):
        self.container = ttk.Frame(self.root, style="App.TFrame", padding=30)
        self.container.pack(fill="both", expand=True)

        header = ttk.Frame(self.container, style="App.TFrame")
        header.pack(fill="x", pady=(0, 22))

        ttk.Label(
            header,
            text="AI Navigation Simulator",
            style="Title.TLabel",
        ).pack(anchor="w")
        ttk.Label(
            header,
            text="Select a start cell, then a goal cell. The agent compares DFS, BFS and A* before animating the chosen path.",
            style="Subtitle.TLabel",
            wraplength=1400,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))

        body = ttk.Frame(self.container, style="App.TFrame")
        body.pack(fill="both", expand=True)
        body.columnconfigure(0, weight=7)
        body.columnconfigure(1, weight=15)
        body.columnconfigure(2, weight=17)
        body.rowconfigure(0, weight=1)

        self.grid_card = ttk.Frame(body, style="Panel.TFrame", padding=24)
        self.grid_card.grid(row=0, column=0, sticky="nsew", padx=(0, 22))
        self.grid_card.columnconfigure(0, weight=1)
        self.grid_card.rowconfigure(2, weight=1)

        ttk.Label(self.grid_card, text="Grid World", style="PanelTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            self.grid_card,
            text="Obstacle cells are blocked. The blue cell is the active simulation position.",
            style="PanelText.TLabel",
            wraplength=780,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(6, 16))

        legend = ttk.Frame(self.grid_card, style="Panel.TFrame")
        legend.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        for column in range(5):
            legend.columnconfigure(column, weight=1)

        self._build_legend_item(legend, 0, "Start", self.CELL_COLORS["start"])
        self._build_legend_item(legend, 1, "Goal", self.CELL_COLORS["goal"])
        self._build_legend_item(legend, 2, "Obstacle", self.CELL_COLORS["obstacle"])
        self._build_legend_item(legend, 3, "Visited", self.CELL_COLORS["trail"])
        self._build_legend_item(legend, 4, "Current", self.CELL_COLORS["current"])

        self.grid_frame = tk.Frame(self.grid_card, bg="#FFFFFF")
        self.grid_frame.grid(row=3, column=0, sticky="nsew")
        self.grid_card.rowconfigure(3, weight=1)

        self.decision_card = ttk.Frame(body, style="Panel.TFrame", padding=24)
        self.decision_card.grid(row=0, column=1, sticky="nsew", padx=(0, 22))
        self.decision_card.columnconfigure(0, weight=1)
        self.decision_card.rowconfigure(3, weight=1)

        ttk.Label(
            self.decision_card,
            text="Decision Agent",
            style="PanelTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.decision_card,
            text="Each step shows the selected algorithm, the chosen next move, and the reasoning behind it.",
            style="SectionHint.TLabel",
            wraplength=430,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(6, 16))

        hero = ttk.Frame(self.decision_card, style="SoftPanel.TFrame", padding=16)
        hero.grid(row=2, column=0, sticky="ew", pady=(0, 16))
        hero.columnconfigure(0, weight=1)

        ttk.Label(
            hero,
            textvariable=self.algorithm_var,
            style="DecisionHero.TLabel",
            wraplength=390,
            justify="left",
        ).grid(row=0, column=0, sticky="ew")
        ttk.Label(
            hero,
            textvariable=self.summary_var,
            style="DecisionMeta.TLabel",
            wraplength=390,
            justify="left",
        ).grid(row=1, column=0, sticky="ew", pady=(8, 0))

        self.decision_box = ScrolledText(
            self.decision_card,
            wrap="word",
            font=("Segoe UI", 12),
            bg="#F8FAFC",
            fg="#1E293B",
            relief="flat",
            padx=16,
            pady=16,
        )
        self.decision_box.grid(row=3, column=0, sticky="nsew")
        self.decision_box.tag_configure(
            "bold",
            font=("Segoe UI Semibold", 13, "bold"),
            foreground="#0F172A",
        )
        self.decision_box.config(state="disabled")

        self.sidebar = ttk.Frame(body, style="App.TFrame")
        self.sidebar.grid(row=0, column=2, sticky="nsew")
        self.sidebar.columnconfigure(0, weight=1)
        self.sidebar.rowconfigure(1, weight=1)

        self.summary_card = ttk.Frame(self.sidebar, style="Panel.TFrame", padding=7)
        self.summary_card.grid(row=0, column=0, sticky="ew", pady=(0, 22))
        self.summary_card.columnconfigure(0, weight=1)

        ttk.Label(
            self.summary_card,
            text="Simulation Summary",
            style="PanelTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.summary_card,
            text="Goal status, step count and the main controls stay here throughout the run.",
            style="SectionHint.TLabel",
            wraplength=320,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(3, 6))

        metrics = ttk.Frame(self.summary_card, style="Panel.TFrame")
        metrics.grid(row=2, column=0, sticky="ew", pady=(0, 8))
        metrics.columnconfigure(0, weight=1)
        metrics.columnconfigure(1, weight=1)

        goal_card = ttk.Frame(metrics, style="SoftPanel.TFrame", padding=8)
        goal_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ttk.Label(goal_card, textvariable=self.goal_var, style="MetricValue.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(goal_card, text="Goal", style="MetricLabel.TLabel").grid(
            row=1, column=0, sticky="w"
        )

        step_card = ttk.Frame(metrics, style="SoftPanel.TFrame", padding=8)
        step_card.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        ttk.Label(step_card, textvariable=self.step_var, style="MetricValue.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(step_card, text="Steps", style="MetricLabel.TLabel").grid(
            row=1, column=0, sticky="w"
        )

        ttk.Label(
            self.summary_card,
            textvariable=self.status_var,
            style="Status.TLabel",
            wraplength=320,
            justify="left",
        ).grid(row=3, column=0, sticky="ew", pady=(0, 8))

        ttk.Label(
            self.summary_card,
            textvariable=self.selection_var,
            style="PanelText.TLabel",
            justify="left",
        ).grid(row=4, column=0, sticky="w", pady=(0, 8))

        button_frame = ttk.Frame(self.summary_card, style="Panel.TFrame")
        button_frame.grid(row=5, column=0, sticky="ew")
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        ttk.Button(
            button_frame,
            text="Run Again",
            style="Summary.TButton",
            command=self._rerun_simulation,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))
        ttk.Button(
            button_frame,
            text="Reset Points",
            style="Summary.TButton",
            command=self._reset_points,
        ).grid(row=0, column=1, sticky="ew", padx=4)
        ttk.Button(
            button_frame,
            text="New Map",
            style="Summary.TButton",
            command=self._new_board,
        ).grid(row=0, column=2, sticky="ew", padx=(4, 0))

        self.path_card = ttk.Frame(self.sidebar, style="Panel.TFrame", padding=15)
        self.path_card.grid(row=1, column=0, sticky="nsew")
        self.path_card.columnconfigure(0, weight=1)
        self.path_card.rowconfigure(2, weight=1)

        ttk.Label(
            self.path_card,
            text="Algorithm Paths",
            style="PanelTitle.TLabel",
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            self.path_card,
            text="Full routes generated by DFS, BFS and A* from the current cell.",
            style="SectionHint.TLabel",
            wraplength=320,
            justify="left",
        ).grid(row=1, column=0, sticky="w", pady=(6, 12))

        self.path_box = ScrolledText(
            self.path_card,
            wrap="word",
            font=("Consolas", 11),
            bg="#F8FAFC",
            fg="#1E293B",
            relief="flat",
            padx=12,
            pady=12,
        )
        self.path_box.grid(row=2, column=0, sticky="nsew")
        self.path_box.config(state="disabled")

    def _build_legend_item(self, parent, column, label, color):
        item = ttk.Frame(parent, style="SoftPanel.TFrame", padding=10)
        item.grid(row=0, column=column, sticky="ew", padx=4)

        swatch = tk.Label(item, bg=color, width=2, height=1, relief="flat")
        swatch.grid(row=0, column=0, padx=(0, 8), sticky="w")
        ttk.Label(item, text=label, style="MetricLabel.TLabel").grid(
            row=0, column=1, sticky="w"
        )

    def _create_grid(self):
        for row in range(self.size):
            self.grid_frame.grid_rowconfigure(row, weight=1)
            self.grid_frame.grid_columnconfigure(row, weight=1)
            button_row = []

            for col in range(self.size):
                button = tk.Button(
                    self.grid_frame,
                    text=f"{row},{col}",
                    font=("Segoe UI Semibold", 13),
                    width=8,
                    height=4,
                    bg=self.CELL_COLORS["empty"],
                    fg="#475569",
                    activebackground="#CBD5E1",
                    relief="flat",
                    bd=0,
                    highlightthickness=0,
                    command=lambda r=row, c=col: self.on_click(r, c),
                )
                button.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                button_row.append(button)

            self.buttons.append(button_row)

    def _new_board(self):
        self._cancel_animation()
        self.start = None
        self.goal = None
        self.current = None
        self.last_result = None
        self.animation_index = 0
        self.path_history = []
        self.decision_history = []
        self.obstacles = self._generate_obstacles()
        self._update_selection_text()
        self._set_status("Choose a start cell to begin the simulation.")
        self.algorithm_var.set("Waiting for start and goal")
        self.summary_var.set("The chosen algorithm and next move will be shown here.")
        self.goal_var.set("Not reached")
        self.step_var.set("0")
        self._write_text(
            self.path_box,
            "Paths for DFS, BFS and A* will appear here after you choose the goal.",
        )
        self._write_text(
            self.decision_box,
            [("Choose start and goal to begin.", "")],
        )
        self._refresh_grid()

    def _reset_points(self):
        self._cancel_animation()
        self.start = None
        self.goal = None
        self.current = None
        self.last_result = None
        self.animation_index = 0
        self.path_history = []
        self.decision_history = []
        self._update_selection_text()
        self._set_status("Start and goal cleared. Choose a new start cell.")
        self.algorithm_var.set("Waiting for start and goal")
        self.summary_var.set("The chosen algorithm and next move will be shown here.")
        self.goal_var.set("Not reached")
        self.step_var.set("0")
        self._write_text(
            self.path_box,
            "Paths for DFS, BFS and A* will appear here after you choose the goal.",
        )
        self._write_text(
            self.decision_box,
            [("Start and goal cleared.", "")],
        )
        self._refresh_grid()

    def _rerun_simulation(self):
        if not self.start or not self.goal:
            self._set_status("Select both start and goal cells before running the simulation.")
            return

        self._run_simulation()

    def _generate_obstacles(self):
        obstacle_target = max(4, self.size + 1)
        available_cells = [
            (row, col) for row in range(self.size) for col in range(self.size)
        ]
        return set(random.sample(available_cells, k=min(obstacle_target, len(available_cells) - 2)))

    def on_click(self, row, col):
        cell = (row, col)

        if cell in self.obstacles:
            return

        if self.start is not None and self.goal is not None:
            self._reset_points()

        if self.start is None:
            self.start = cell
            self.current = cell
            self._update_selection_text()
            self._set_status(f"Start selected at {self.start}. Now choose the goal cell.")
            self._refresh_grid()
            return

        if cell == self.start:
            self._set_status("Choose a different cell for the goal.")
            return

        if self.goal is None:
            self.goal = cell
            self._update_selection_text()
            self._run_simulation()

    def _run_simulation(self):
        self._cancel_animation()
        self.current = self.start
        self.last_result = None
        self.animation_index = 0
        self.path_history = [self.start]
        self.decision_history = []
        self._refresh_grid()
        self._write_text(
            self.decision_box,
            [
                ("Simulation started.\n\n", "bold"),
                ("The decision agent will compare DFS, BFS and A* at every move.", ""),
            ],
        )
        self._write_text(
            self.path_box,
            "Evaluating paths from the start position...",
        )
        self.algorithm_var.set("Evaluating routes...")
        self.summary_var.set("Comparing DFS, BFS and A* for the first move.")
        self.goal_var.set("Running")
        self.step_var.set("0")
        self._animate_path()

    def _animate_path(self):
        if self.current == self.goal:
            self._refresh_grid()
            self.algorithm_var.set("Goal reached")
            self.summary_var.set("The agent reached the goal successfully.")
            self.goal_var.set(str(self.goal))
            self.step_var.set(str(max(len(self.path_history) - 1, 0)))
            self._set_status(f"Navigation complete: reached {self.goal}.")
            return

        step_number = len(self.path_history) - 1
        self.last_result = self.agent.decide_step(
            self.current, self.goal, self.obstacles, self.size, step_number
        )
        self._show_results()

        if not self.last_result["best_path"] or self.last_result["next_move"] is None:
            self._refresh_grid()
            self.algorithm_var.set("No path found")
            self.summary_var.set("All algorithms failed to produce a valid next step.")
            self.goal_var.set("Blocked")
            self._set_status(
                "No valid path was found from the current position. Try resetting the points or generating a new map."
            )
            return

        next_move = self.last_result["next_move"]
        self.current = next_move
        self.path_history.append(next_move)
        self.animation_index = len(self.path_history)
        self._refresh_grid()

        self._set_status(
            f"Step {step_number + 1}: moved to {self.current} using {self.last_result['best_algorithm']}."
        )
        self.step_var.set(str(step_number + 1))

        self.animation_job = self.root.after(450, self._animate_path)

    def _cancel_animation(self):
        if self.animation_job is not None:
            self.root.after_cancel(self.animation_job)
            self.animation_job = None

    def _refresh_grid(self):
        visited_path = self.path_history[:]

        for row in range(self.size):
            for col in range(self.size):
                cell = (row, col)
                button = self.buttons[row][col]

                color = self.CELL_COLORS["empty"]
                state = "normal"

                if cell in self.obstacles:
                    color = self.CELL_COLORS["obstacle"]
                    state = "disabled"
                elif cell == self.start:
                    color = self.CELL_COLORS["start"]
                elif cell == self.goal:
                    color = self.CELL_COLORS["goal"]
                elif cell in visited_path:
                    color = self.CELL_COLORS["trail"]

                if cell == self.current and cell not in {self.start, self.goal}:
                    color = self.CELL_COLORS["current"]

                button.config(
                    bg=color,
                    state=state,
                    disabledforeground="#FFFFFF",
                    fg="#FFFFFF" if color in {
                        self.CELL_COLORS["obstacle"],
                        self.CELL_COLORS["start"],
                        self.CELL_COLORS["goal"],
                    } else "#0F172A",
                    activeforeground="#0F172A",
                )

    def _show_results(self):
        paths = self.last_result["paths"]
        path_lines = []

        for algorithm in ("DFS", "BFS", "A*"):
            path = paths.get(algorithm)
            if path:
                path_lines.append(
                    f"{algorithm} from {self.last_result['current']} ({len(path) - 1} step(s)):\n{self._format_path(path)}"
                )
            else:
                path_lines.append(
                    f"{algorithm} from {self.last_result['current']}:\nNo valid path found."
                )

        self._write_text(self.path_box, "\n\n".join(path_lines))
        self._update_current_decision()

        step_log_parts = self._format_step_log()
        self.decision_history.extend(step_log_parts)
        self.decision_history.append(("\n", ""))
        self._write_text(self.decision_box, self.decision_history)

    def _update_current_decision(self):
        best_algorithm = self.last_result["best_algorithm"]
        next_move = self.last_result["next_move"]
        current = self.last_result["current"]

        if best_algorithm and next_move is not None:
            self.algorithm_var.set(f"{best_algorithm} selected")
            self.summary_var.set(
                f"Step {self.last_result['step_number'] + 1}: move from {current} to {next_move}."
            )
        else:
            self.algorithm_var.set("No path found")
            self.summary_var.set("No valid next move is available from the current state.")

    def _format_step_log(self):
        parts = []
        step_number = self.last_result["step_number"] + 1
        current = self.last_result["current"]
        best_algorithm = self.last_result["best_algorithm"]
        next_move = self.last_result["next_move"]

        parts.append((f"Step {step_number}\n", "bold"))
        parts.append((f"Current cell: {current}\n", ""))
        parts.append((f"Chosen algorithm: {best_algorithm or 'none'}\n", ""))
        parts.append((f"Next move: {next_move if next_move is not None else 'no valid move'}\n", ""))
        parts.append(("Decision details:\n", "bold"))

        for detail in self.last_result["step_log"][1:]:
            parts.append((f"{detail}\n", ""))

        return parts

    def _update_selection_text(self):
        start_text = str(self.start) if self.start else "not selected"
        goal_text = str(self.goal) if self.goal else "not selected"
        self.selection_var.set(f"Start: {start_text}\nGoal: {goal_text}")

    def _set_status(self, message):
        self.status_var.set(message)

    @staticmethod
    def _format_path(path):
        return " -> ".join(f"({row},{col})" for row, col in path)

    @staticmethod
    def _write_text(widget, content):
        widget.config(state="normal")
        widget.delete("1.0", tk.END)

        if isinstance(content, list):
            for text, tag in content:
                widget.insert(tk.END, text, tag if tag else "")
        else:
            widget.insert(tk.END, content)

        widget.config(state="disabled")
        widget.see(tk.END)
