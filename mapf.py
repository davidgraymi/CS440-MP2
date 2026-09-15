from itertools import product

from state import AbstractState

# TODO(III): copy over your manhattan function from MP1 here
def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    raise NotImplementedError("You should copy over your manhattan function from MP1 here")

class MultiAgentGridState(AbstractState):
    # state: a tuple of agent locations
    # goal: a tuple of goal locations for each agent
    # maze: Maze object for the problem. You can call maze.neighboring_cells(...) and maze.is_free(...)
    def __init__(self, state, goal, dist_from_start, use_heuristic, maze, h_type="admissible") -> None:
        self.maze = maze
        self.h_type = h_type
        super().__init__(state, goal, dist_from_start, use_heuristic)
        
    # TODO(IV): implement get_neighbors
    def get_neighbors(self) -> list[AbstractState]:
        nbr_states = []
        # See the instructions for the expected neighbor-generation and collision checks.
        # You may find it useful to use itertools.product to generate all combinations of agent moves.
        # Your code here ---------------
        
        # ------------------------------
        return nbr_states

    # Checks if all goals have been reached
    def is_goal(self) -> bool:
        # TODO(IV): implement is_goal method
        # Your code here ---------------
        pass
        # ------------------------------
    
    def compute_heuristic_admissible(self) -> float:
        # TODO(IV): implement compute_heuristic_admissible
        return 0
    
    def compute_heuristic_inadmissible(self) -> float:
        # TODO(IV): implement compute_heuristic_inadmissible
        return 0

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
