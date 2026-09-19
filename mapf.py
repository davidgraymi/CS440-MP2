from collections import deque
from itertools import product, combinations

from maze import Maze
from state import AbstractState

def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return sum(abs(x - y) for x, y in zip(a, b))

class MultiAgentGridState(AbstractState):
    _distance_cache = {}
    _pair_distance_cache = {}
    _free_cell_cache = {}

    # state: a tuple of agent locations
    # goal: a tuple of goal locations for each agent
    # maze: Maze object for the problem. You can call maze.neighboring_cells(...) and maze.is_free(...)
    def __init__(self, state, goal, dist_from_start, use_heuristic, maze: Maze, h_type="admissible") -> None:
        self.maze: Maze = maze
        self.h_type = h_type
        super().__init__(state, goal, dist_from_start, use_heuristic)
        
    def get_neighbors(self) -> list[AbstractState]:
        nbr_states = []
        # See the instructions for the expected neighbor-generation and collision checks.
        # You may find it useful to use itertools.product to generate all combinations of agent moves.
        for next_state in product(*(self.maze.neighboring_cells(*agent_state) for agent_state in self.state)):
            # check if there is a vertex collision
            if any(left == right for (left, right) in combinations(next_state, r=2)):
                continue

            # check if there is an swap
            if any(
                (a1_curr == a2_next) and (a1_next == a2_curr)
                for (a1_curr, a1_next), (a2_curr, a2_next) in combinations(zip(self.state, next_state), r=2)
            ):
                continue

            # check if next state is in a free cell
            if any(
                not self._is_free(next_agent_state)
                if cur_state != next_agent_state else False
                for cur_state, next_agent_state in zip(self.state, next_state)
            ):
                continue

            nbr_states.append(
                MultiAgentGridState(
                    state=next_state,
                    goal=self.goal,
                    dist_from_start=self.dist_from_start + 1,
                    use_heuristic=self.use_heuristic,
                    maze=self.maze,
                    h_type=self.h_type
                )
            )
        return nbr_states

    # Use cache through policy to avoid unnecessary `self.maze.is_free` calls
    def _is_free(self, location) -> bool:
        maze_cache = self._free_cell_cache.setdefault(self.maze.file_path, {})
        if location not in maze_cache:
            maze_cache[location] = self.maze.is_free(*location)
        return maze_cache[location]

    # Checks if all goals have been reached
    def is_goal(self) -> bool:
        return self.state == self.goal
    
    def compute_heuristic_admissible(self) -> float:
        individual_bound = max(
            self._distance_from_goal(state, goal)
            for state, goal in zip(self.state, self.goal)
        )
        pair_bound = max(
            self._pair_distance(first_state, second_state, first_goal, second_goal)
            for index, (first_state, first_goal) in enumerate(zip(self.state, self.goal))
            for second_state, second_goal in zip(self.state[index + 1:], self.goal[index + 1:])
        ) if len(self.state) > 1 else 0
        return max(individual_bound, pair_bound)
    
    def compute_heuristic_inadmissible(self) -> float:
        return max(
            self._pair_distance(first_state, second_state, first_goal, second_goal)
            for index, (first_state, first_goal) in enumerate(zip(self.state, self.goal))
            for second_state, second_goal in zip(self.state[index + 1:], self.goal[index + 1:])
        ) if len(self.state) > 1 else self._distance_from_goal(self.state[0], self.goal[0])

    def _distance_from_goal(self, location, goal) -> int:
        cache_key = (self.maze.file_path, goal)
        if cache_key not in self._distance_cache:
            distances = {goal: 0}
            frontier = deque([goal])
            while frontier:
                current = frontier.popleft()
                for neighbor in self.maze.neighboring_cells(*current):
                    if neighbor in distances or self.maze.grid[neighbor] == 1:
                        continue
                    distances[neighbor] = distances[current] + 1
                    frontier.append(neighbor)
            self._distance_cache[cache_key] = distances
        return self._distance_cache[cache_key][location]

    def _pair_distance(self, first_state, second_state, first_goal, second_goal) -> int:
        cache_key = (self.maze.file_path, first_goal, second_goal)
        if cache_key not in self._pair_distance_cache:
            distances = {(first_goal, second_goal): 0}
            frontier = deque([(first_goal, second_goal)])
            while frontier:
                current_first, current_second = frontier.popleft()
                for next_first, next_second in product(
                    self.maze.neighboring_cells(*current_first),
                    self.maze.neighboring_cells(*current_second),
                ):
                    if next_first == next_second:
                        continue
                    if (current_first, current_second) == (next_second, next_first):
                        continue
                    if self.maze.grid[next_first] == 1 or self.maze.grid[next_second] == 1:
                        continue
                    next_pair = (next_first, next_second)
                    if next_pair not in distances:
                        distances[next_pair] = distances[(current_first, current_second)] + 1
                        frontier.append(next_pair)
            self._pair_distance_cache[cache_key] = distances
        return self._pair_distance_cache[cache_key][(first_state, second_state)]

    # We override the compute_heuristic method to select between admissible and inadmissible heuristics
    def compute_heuristic(self) -> float:
        if self.h_type == "admissible":
            return self.compute_heuristic_admissible()
        elif self.h_type == "inadmissible":
            return self.compute_heuristic_inadmissible()
        else:
            raise ValueError("Invalid heuristic type")

    def __lt__(self, other) -> bool:
        if not isinstance(other, MultiAgentGridState):
            return super().__lt__(other)

        self_f = self.dist_from_start + self.h
        other_f = other.dist_from_start + other.h
        if self_f != other_f:
            return self_f < other_f

        self_sum = self.compute_heuristic_inadmissible()
        other_sum = other.compute_heuristic_inadmissible()
        if self_sum != other_sum:
            return self_sum < other_sum
        return self.tiebreak_idx < other.tiebreak_idx

    # Unlike MultiGoalGridState, now the goals are fixed so we can just hash self.state
    def __hash__(self) -> int:
        return hash(self.state)
    def __eq__(self, other) -> bool:
        return self.state == other.state
    
    # str and repr just make output more readable when your print out states
    def __str__(self) -> str:
        return str(list(zip(self.state, self.goal)))
    def __repr__(self) -> str:
        return str(list(zip(self.state, self.goal)))
