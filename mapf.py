from itertools import product, combinations

from maze import Maze
from state import AbstractState

def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return sum(abs(x - y) for x, y in zip(a, b))

class MultiAgentGridState(AbstractState):
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
            # check if next state is in a free cell
            if any(not self.maze.is_free(*next_agent_state) for next_agent_state in next_state):
                continue

            # check if there is a vertex collision
            if any(left == right for (left, right) in combinations(next_state, r=2)):
                continue

            # check if there is an swap
            if any(
                (a1_curr == a2_next) and (a1_next == a2_curr)
                for (a1_curr, a1_next), (a2_curr, a2_next) in combinations(zip(self.state, next_state), r=2)
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

    # Checks if all goals have been reached
    def is_goal(self) -> bool:
        return self.state == self.goal
    
    def compute_heuristic_admissible(self) -> float:
        # TODO(IV): implement compute_heuristic_admissible
        return max(manhattan(state, goal) for state, goal in zip(self.state, self.goal))
    
    def compute_heuristic_inadmissible(self) -> float:
        # TODO(IV): implement compute_heuristic_inadmissible
        return sum(manhattan(state, goal) for state, goal in zip(self.state, self.goal))

    # We override the compute_heuristic method to select between admissible and inadmissible heuristics
    def compute_heuristic(self) -> float:
        if self.h_type == "admissible":
            return self.compute_heuristic_admissible()
        elif self.h_type == "inadmissible":
            return self.compute_heuristic_inadmissible()
        else:
            raise ValueError("Invalid heuristic type")

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
