from logic.search import a_star, bfs, dfs


class Agent:
    def evaluate_paths(self, start, goal, obstacles, size):
        algorithm_paths = {
            "BFS": bfs(start, goal, obstacles, size),
            "DFS": dfs(start, goal, obstacles, size),
            "A*": a_star(start, goal, obstacles, size),
        }

        decision_log = [
            f"Decision agent evaluating routes from {start} to {goal}.",
        ]
        valid_results = []

        for name, path in algorithm_paths.items():
            if path:
                steps = max(len(path) - 1, 0)
                valid_results.append((name, path))
                decision_log.append(
                    f"{name} found a valid path with {steps} step(s): {self._format_path(path)}"
                )
            else:
                decision_log.append(f"{name} could not find a valid path.")

        if not valid_results:
            decision_log.append("No algorithm found a path, so the agent cannot move.")
            return {
                "paths": algorithm_paths,
                "best_algorithm": None,
                "best_path": None,
                "next_move": None,
                "decision_log": decision_log,
            }

        best_algorithm, best_path = min(
            valid_results,
            key=lambda item: (len(item[1]), self._priority(item[0])),
        )
        next_move = best_path[1] if len(best_path) > 1 else best_path[0]

        decision_log.append(
            f"Selected {best_algorithm} because it produced the shortest path."
        )
        if len(best_path) > 1:
            decision_log.append(f"Next move chosen by the agent: {next_move}.")
        else:
            decision_log.append("The agent is already on the goal cell.")

        return {
            "paths": algorithm_paths,
            "best_algorithm": best_algorithm,
            "best_path": best_path,
            "next_move": next_move,
            "decision_log": decision_log,
        }

    def get_next_move(self, current, goal, obstacles, size):
        result = self.evaluate_paths(current, goal, obstacles, size)
        return result["next_move"], result["best_algorithm"]

    def decide_step(self, current, goal, obstacles, size, step_number):
        result = self.evaluate_paths(current, goal, obstacles, size)

        header = f"Step {step_number}: evaluating from {current} toward {goal}."
        detailed_log = [header, *result["decision_log"]]

        result["step_number"] = step_number
        result["current"] = current
        result["step_log"] = detailed_log
        return result

    @staticmethod
    def _priority(name):
        order = {"A*": 0, "BFS": 1, "DFS": 2}
        return order.get(name, 99)

    @staticmethod
    def _format_path(path):
        return " -> ".join(str(node) for node in path)
