from itertools import product

from search import best_first_search
from state import AbstractState

# A World is a collection of objects and actions that can be performed on those objects
class World:
    def __init__(
            self,
            objects_by_type: dict[str, list[str]],
            actions: list[callable],
            action_inputs: dict[callable, list[str]]) -> None:
        self.objects_by_type = objects_by_type
        self.actions = actions
        self.action_inputs = action_inputs

class BlockWorld(World):
    def __init__(self, objects_by_type: dict[str, list[str]]) -> None:
        # make sure our input is properly formed
        assert "block" in objects_by_type, "BlockWorld requires object type 'block'"
        assert len(objects_by_type) == 1, "BlockWorld only supports one object type 'block'"

        # initialize the World parent class
        super().__init__(
            # objects_by_type is a dict mapping just one object type "block" to a list of block names
            objects_by_type = objects_by_type, 
            # our blockworld consists of 4 actions: stack, unstack, place, pickup
            actions = [
                BlockWorld.stack,
                BlockWorld.unstack,
                BlockWorld.place,
                BlockWorld.pickup
            ],
            # our BlockWorld only has one object type: "block", though conceivably we could have more
            action_inputs = {
                BlockWorld.stack: ["block", "block"], # stack has 2 inputs of type block
                BlockWorld.unstack: ["block", "block"], # unstack has 2 inputs of type block
                BlockWorld.place: ["block"], # place has 1 input of type block
                BlockWorld.pickup: ["block"] # pickup has 1 input of type block
            }
        )
        
    # A predicate is a function that returns a fact string
    @staticmethod
    def block_on_block(blockA: str, blockB: str) -> str:
        return str(blockA)+"_is_on_"+str(blockB)

    @staticmethod
    def holding(block: str) -> str:
        return "arm_is_holding_"+str(block)

    @staticmethod
    def on_top(block: str) -> str:
        return str(block)+"_is_on_top"

    @staticmethod
    def arm_is_free() -> str:
        return "arm_is_free"
    
    @staticmethod
    def on_table(block: str) -> str:
        return str(block)+"_is_on_table"

    @staticmethod
    def place(block: str) -> tuple[set[str], dict[str, set[str]]]: # place a block on the table
        preconditions = set({
            BlockWorld.holding(block)
        })
        postconditions = {
            "delete": set({
                BlockWorld.holding(block)
            }), 
            "add": set({
                BlockWorld.on_table(block)
            })
        }
        return preconditions, postconditions

    @staticmethod
    def pickup(block: str) -> tuple[set[str], dict[str, set[str]]]: # pickup a block from the table
        preconditions = set({
            BlockWorld.arm_is_free(),
            BlockWorld.on_table(block)
        })
        postconditions = {
            "delete": set({
                BlockWorld.arm_is_free(),
                BlockWorld.on_table(block)
            }), 
            "add": set({
                BlockWorld.holding(block)
            })
        }
        return preconditions, postconditions

    @staticmethod
    def unstack(blockA: str, blockB: str) -> tuple[set[str], dict[str, set[str]]]: # unstack blockA from blockB
        preconditions = set({
            BlockWorld.block_on_block(blockA, blockB),
            BlockWorld.arm_is_free()
        })
        postconditions = {
            "delete": set({
                BlockWorld.block_on_block(blockA, blockB),
                BlockWorld.arm_is_free()
            }), 
            "add": set({
                BlockWorld.holding(blockA)
            })
        }
        return preconditions, postconditions

    @staticmethod
    def stack(blockA: str, blockB: str) -> tuple[set[str], dict[str, set[str]]]:
        preconditions = set(BlockWorld.holding(blockA))
        postconditions = {
            "delete": set(BlockWorld.holding(blockA)), 
            "add": set({
                BlockWorld.arm_is_free(),
                BlockWorld.block_on_block(blockA, blockB)
            })
        }
        return preconditions, postconditions

class BooleanPredicatesState(AbstractState):
    def __init__(self, 
                 state: set[str],
                 goal: set[str],
                 world: World,
                 delete_relaxation=False,
                 heuristic_type="num_unsatisfied_goals",
                 prev_action=None,
                 dist_from_start=0,
                 use_heuristic=False) -> None:
        self.world = world
        self.delete_relaxation = delete_relaxation
        self.heuristic_type = heuristic_type
        self.prev_action = prev_action # store for visualization purposes
        super().__init__(state, goal, dist_from_start, use_heuristic)

    def take_action(self, preconditions: set[str], postconditions: dict[str, set[str]]) -> set[str] | None:
        if any(pre not in self.state for pre in preconditions):
            return None

        ret_state = self.state.copy()
        ret_state.update(postconditions["add"])

        if not self.delete_relaxation:
            ret_state.difference_update(postconditions["delete"])

        return ret_state
    
    # TODO(VI): implement get_neighbors
    def get_neighbors(self) -> list[AbstractState]:
        # See the instructions for action grounding and prev_action.
        # Your code here ---------------
        pass
        # ------------------------------
    
    # TODO(VI): implement is_goal
    def is_goal(self) -> bool:
        # Your code here ---------------
        pass
        # ------------------------------
    
    # TODO(VI): implement compute_delete_relaxation_heuristic
    def compute_delete_relaxation_heuristic(self) -> float:
        # Your code here ---------------
        pass
        # ------------------------------

    # TODO(VI): implement compute_num_unsatisfied_goals_heuristic
    def compute_num_unsatisfied_goals_heuristic(self) -> float:
        # Your code here ---------------
        pass
        # ------------------------------

    def compute_heuristic(self) -> float:
        if self.heuristic_type == "delete_relaxation":
            return self.compute_delete_relaxation_heuristic()
        elif self.heuristic_type == "num_unsatisfied_goals":
            return self.compute_num_unsatisfied_goals_heuristic()
        else:
            raise ValueError("Invalid heuristic type")

    # our state is defined as a set of strings, sets are not hashable because they are unordered
    # so we can hash the tuple of sorted strings instead
    def __hash__(self) -> int:
        return hash(tuple(sorted(list(self.state))))
    # set equality works fine
    def __eq__(self, other) -> bool:
        return self.state == other.state
    
    def __repr__(self) -> str:
        return str(self.state)
