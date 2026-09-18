# ----------------------------------------------------------------------------
# Returns a list of paths, one per agent.
# Each path is a list of grid locations (tuples)
#   e.g., [[(x1,y1), (x2,y2), ...],  # path for agent 0
#          [(x1,y1), (x2,y2), ...],  # path for agent 1
#          ... # paths for other agents
#         ]

from collections import deque

from maze import Maze

type Path = list[tuple[int, int]]
# Current positions of all agents
type Config = tuple[tuple[int, int], ...]

def get_new_config(node: HighNode, constraint: ConstraintNode, goals: tuple[tuple[int, int]], maze: Maze) -> Config | None:
    forced: dict[int, tuple[int, int]] = {}
    next_positions: list[tuple[int, int] | None] = [None] * len(node.config)
    current = constraint

    while current is not None and current.who is not None:
        if current.where is None:
            return None
        forced[current.who] = current.where
        current = current.parent

    def assign(agent_index: int) -> Config | None:
        if agent_index == len(node.config):
            return tuple(position for position in next_positions if position is not None)

        current_position = node.config[agent_index]
        if agent_index in forced:
            candidates = (forced[agent_index],)
        else:
            candidates = sorted(
                maze.neighboring_cells(*current_position),
                key=lambda candidate: manhattan(candidate, goals[agent_index]),
            )

        for candidate in candidates:
            if not maze.is_free(*candidate):
                continue

            if candidate in next_positions[:agent_index]:
                continue

            creates_swap = False
            for other_index in range(agent_index):
                other_destination = next_positions[other_index]
                if (
                    node.config[agent_index] == other_destination
                    and candidate == node.config[other_index]
                ):
                    creates_swap = True
                    break
            if creates_swap:
                continue

            next_positions[agent_index] = candidate
            successor = assign(agent_index + 1)
            if successor is not None:
                return successor
            next_positions[agent_index] = None

        return None

    return assign(0)

def constraint_depth(node: ConstraintNode) -> int:
    depth = 0
    current: ConstraintNode | None = node
    while current is not None and current.who is not None:
        depth += 1
        current = current.parent
    return depth

def backtrack_high_nodes(goal_node: HighNode) -> list[Config]:
    configs: list[Config] = []

    node: HighNode | None = goal_node
    while node is not None:
        configs.append(node.config)
        node = node.parent

    configs.reverse()
    return configs

def solve_hard_mapf_instance(starts: tuple[tuple[int, int]], goals: tuple[tuple[int, int]], maze: Maze) -> list[Path]:
    # TODO(VII): implement a solver for hard MAPF instances here
    # You may use any algorithm, but every returned path must satisfy the format,
    # endpoint, movement, wall, and collision requirements in the instructions.
    # Your objective is to be fast and complete; path length and optimality are not graded.

    initial_order = tuple(sorted(
        range(len(starts)),
        key=lambda i: manhattan(starts[i], goals[i]),
        reverse=True,
    ))

    root_constraint = ConstraintNode()
    initial_node = HighNode(
        config=starts,
        parent=None,
        order=initial_order,
        tree=deque([root_constraint]),
    )
    explored: dict[Config, HighNode] = {starts: initial_node}
    open: list[HighNode] = [initial_node]

    # DFS
    while len(open) != 0:
        hinode = open[-1]
        if hinode.config == goals:
            configs = backtrack_high_nodes(hinode)
            return [
                [config[agent_index] for config in configs]
                for agent_index in range(len(starts))
            ]

        if not hinode.tree:
            _ = open.pop()
            continue

        # BFS
        constraint = hinode.tree.popleft()
        depth = constraint_depth(constraint)
        if depth < len(hinode.config):
            agent = hinode.order[depth]
            for destination in maze.neighboring_cells(*hinode.config[agent]):
                hinode.tree.append(
                    ConstraintNode(
                        parent=constraint,
                        who=agent,
                        where=destination,
                    )
                )

        successor = get_new_config(hinode, constraint, goals, maze)
        if successor is None:
            continue

        new_config: Config = successor

        if new_config in explored:
            continue

        child_order = tuple(sorted(
            range(len(new_config)),
            key=lambda i: new_config[i] == goals[i],
        ))

        child = HighNode(
            config=new_config,
            parent=hinode,
            order=child_order,
            tree=deque([ConstraintNode()])
        )
        open.append(child)
        explored[new_config] = child
    
    # if you do not find the goal return an empty list
    return []


def manhattan(a: tuple[int, int], b: tuple[int, int]) -> int:
    return sum(abs(x - y) for x, y in zip(a, b))

class ConstraintNode():
    def __init__(
        self,
        parent: ConstraintNode | None = None,
        who: int | None = None,
        where: tuple[int, int] | None | None = None,
    ) -> None:
        self.parent: ConstraintNode | None = parent
        self.who: int | None = who
        self.where: tuple[int, int] | None = where

class HighNode():
    def __init__(
        self,
        config: Config,
        order: tuple[int, ...],
        tree: deque[ConstraintNode],
        parent: HighNode | None = None,
    ) -> None:
        self.config: Config = config
        self.order: tuple[int, ...] = order
        self.tree: deque[ConstraintNode] = tree
        self.parent: HighNode | None = parent
