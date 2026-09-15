import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.colors import ListedColormap


class Maze:
    def __init__(self, file_path, allow_waiting = False):
        """
        Creates a maze instance given a `file_path` to a text file containing the ASCII representation of a maze.
        Key:
            - Walls are represented by %
            - Open paths by spaces
            - Starts by capital letters (at most one of each letter) 
            - Goals (waypoints) by lowercase letters matching one of the starts
        
        If `allow_waiting` is True, the agent can stay in place (not move) as a valid action.
        """
        self.file_path = file_path
        self.allow_waiting = allow_waiting
        with open(file_path) as file:
            lines = tuple(line.strip() for line in file.readlines() if line)
        
        wall_char = '%'
        free_char = ' '
        height = len(lines)
        width = len(lines[0])
        
        # check that we have a rectangular grid
        if any(len(line) != width for line in lines):
            raise ValueError(f'(maze {file_path}): all maze rows must be the same length')
        
        # read the maze from the file into a numpy array and store starts and goals
        self.grid = np.zeros((height, width))
        self.starts = {}
        self.goals = {}
        for i in range(height):
            for j in range(width):
                cur_char = lines[i][j]
                if cur_char == wall_char:
                    self.grid[i, j] = 1
                elif cur_char.isupper():
                    if cur_char.lower() in self.starts:
                        raise ValueError(f'(maze {file_path}): starts must be unique')
                    self.starts[cur_char.lower()] = (i, j)
                elif cur_char.islower():
                    if cur_char not in self.goals:
                        self.goals[cur_char] = ()
                    self.goals[cur_char] += ((i, j),)
                elif cur_char != free_char:
                    raise ValueError(f'(maze {file_path}): invalid character {cur_char}')        
                
        # check that every start has a corresponding goal
        for start in self.starts:
            if start not in self.goals:
                raise ValueError(f'(maze {file_path}): start {start} has no corresponding goal')

        # check that border contains walls
        if np.any(self.grid[0, :]==0) or\
            np.any(self.grid[-1, :]==0) or\
                np.any(self.grid[:, 0]==0) or\
                    np.any(self.grid[:, -1]==0):
            raise ValueError(f'(maze {file_path}): border of maze must be walls')

        # This is a helper to track number of times we call self.is_free(i, j)
        self.num_states_validated = 0
    
    def in_bounds(self, i, j):
        """Check if cell (i,j) is in bounds"""
        return 0 <= i < self.grid.shape[0] and 0 <= j < self.grid.shape[1]
    
    def is_free(self, i, j):
        """Check if in bounds cell (i,j) is free - not a wall"""
        self.num_states_validated += 1
        return self.grid[i, j] != 1

    def neighboring_cells(self, i, j):
        """Returns the in-bounds cells neighboring the given row,col."""
        possible_moves = [(i+1, j), (i-1, j), (i, j+1), (i, j-1)]
        if self.allow_waiting:
            possible_moves.append((i, j))
        return tuple(x for x in possible_moves if self.in_bounds(*x))

    def valid_path(self, path):
        # validate type and shape 
        if len(path) == 0:
            print(f'Invalid path: path must contain at least one element')
            return False
        if not all(len(vertex) == 2 for vertex in path):
            print(f'Invalid path: each path element must be a two-element sequence')
            return False
        
        # normalize path in case student used an element type that is not `tuple` 
        path = tuple(map(tuple, path))

        # check if path is contiguous
        for i, (a, b) in enumerate(zip(path[:-1], path[1:])):
            d = sum(abs(b_ - a_) for a_, b_ in zip(a, b)) 
            if d > 1:
                print(f'Invalid path: path vertex {i} {a} is too far from consecutive path vertex {i + 1} {b}')
                return False
            if d == 0 and not self.allow_waiting:
                print(f'Invalid path: path vertex {i} {a} is the same as consecutive path vertex {i + 1} {b}, and waiting is not allowed')
                return False

        # check if path is navigable 
        for i, x in enumerate(path):
            if not self.in_bounds(*x) or not self.is_free(*x):
                print(f'Invalid path: path vertex {i} {x} is not a navigable maze cell')
                return False
        
        # the path must start at a start location
        if path[0] not in self.starts.values():
            print(f'Invalid path: first path vertex {path[0]} must be a start location')
            return False
        
        # get the goal associated with the path start
        path_goals = None
        for c, start in self.starts.items(): # works for multi-agent (MP2)
            if start == path[0]:
                path_goals = self.goals[c]                
                break
        
        # check if the path ends at a goal 
        if path[-1] not in path_goals:
            print(f'Invalid path: last path vertex {path[-1]} must be a goal')
            return False
        
        # check for unnecessary path segments (looping back to a previous location without visiting a waypoint)
        if not self.allow_waiting:
            indices = {}
            for i, x in enumerate(path):
                if x in indices:
                    if all(x not in path_goals for x in path[indices[x] : i]):
                        print(f'Bad path: path segment [{indices[x]} : {i}] contains no waypoints but loops back to a previous location')
                        return False
                indices[x] = i 
        
        # check if path contains all waypoints 
        for goal in path_goals:
            if goal not in path:
                print(f'Bad path: path must contain all waypoints')
                return False
        
        return True

    def _draw_grid(self, ax):
        height, width = self.grid.shape
        ax.imshow(self.grid, cmap=ListedColormap(["white", "black"]), vmin=0, vmax=1)
        ax.set_xticks(np.arange(-0.5, width, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, height, 1), minor=True)
        ax.grid(which="minor", color="lightgray", linewidth=0.5)
        ax.tick_params(which="both", bottom=False, left=False, labelbottom=False, labelleft=False)
        ax.set_aspect("equal")
        ax.set_title(self.file_path)

    def _track_offset(self, idx, num_tracks):
        if num_tracks <= 1:
            return 0, 0
        track_spacing = 0.12
        offset = track_spacing * (idx - (num_tracks - 1) / 2)
        return offset, offset

    def draw_maze(self, path=None, save=None, show=True):
        """Draw a simple maze visualization, optionally with one path per agent."""
        paths = self._normalize_paths(path)
        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]

        fig, ax = plt.subplots(layout="constrained")
        self._draw_grid(ax)

        for idx, agent_path in enumerate(paths):
            if len(agent_path) == 0:
                continue
            row_offset, col_offset = self._track_offset(idx, len(paths))
            rows = [loc[0] + row_offset for loc in agent_path]
            cols = [loc[1] + col_offset for loc in agent_path]
            color = colors[idx % len(colors)]
            ax.plot(cols, rows, color=color, linewidth=2, alpha=0.85, zorder=3)
            ax.scatter(cols, rows, color=color, s=12, alpha=0.6, zorder=3)

        agent_keys = list(self.starts)
        for idx, agent_key in enumerate(agent_keys):
            color = colors[idx % len(colors)]
            row_offset, col_offset = self._track_offset(idx, len(agent_keys))
            row, col = self.starts[agent_key]
            ax.text(col + col_offset, row + row_offset, agent_key.upper(), color=color, ha="center", va="center",
                    weight="bold", zorder=5,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=color))
            for row, col in self.goals[agent_key]:
                ax.text(col + col_offset, row + row_offset, agent_key, color=color, ha="center", va="center",
                        weight="bold", zorder=5,
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=color))

        if save is not None:
            fig.savefig(save, dpi=150, bbox_inches="tight")
        if show:
            plt.show()
        else:
            plt.close(fig)
        return fig, ax

    def animate_maze(self, path, show=True, interval=400):
        """Animate one path per agent moving through the maze."""
        paths = self._normalize_paths(path)
        if len(paths) == 0 or any(len(agent_path) == 0 for agent_path in paths):
            raise ValueError("animate_maze expects at least one non-empty path")

        colors = plt.rcParams["axes.prop_cycle"].by_key()["color"]
        agent_keys = list(self.starts)
        max_path_length = max(len(agent_path) for agent_path in paths)
        padded_paths = [
            agent_path + (agent_path[-1],) * (max_path_length - len(agent_path))
            for agent_path in paths
        ]

        fig, ax = plt.subplots(layout="constrained")
        self._draw_grid(ax)

        for idx, agent_path in enumerate(paths):
            row_offset, col_offset = self._track_offset(idx, len(paths))
            rows = [loc[0] + row_offset for loc in agent_path]
            cols = [loc[1] + col_offset for loc in agent_path]
            color = colors[idx % len(colors)]
            ax.plot(cols, rows, color=color, linewidth=2, alpha=0.35, zorder=3)
            ax.scatter(cols, rows, color=color, s=10, alpha=0.25, zorder=3)

        for idx, agent_key in enumerate(agent_keys):
            color = colors[idx % len(colors)]
            row_offset, col_offset = self._track_offset(idx, len(agent_keys))
            for row, col in self.goals[agent_key]:
                ax.text(col + col_offset, row + row_offset, agent_key, color=color, ha="center", va="center",
                        weight="bold", zorder=5,
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", edgecolor=color))

        agent_artists = []
        for idx, agent_path in enumerate(padded_paths):
            row, col = agent_path[0]
            row_offset, col_offset = self._track_offset(idx, len(paths))
            color = colors[idx % len(colors)]
            label = agent_keys[idx].upper() if idx < len(agent_keys) else str(idx + 1)
            artist = ax.text(col + col_offset, row + row_offset, label, color=color, ha="center", va="center",
                             weight="bold", zorder=6,
                             bbox=dict(boxstyle="round,pad=0.25", facecolor="white", edgecolor=color))
            agent_artists.append(artist)

        step_text = ax.text(0.01, 0.99, "", transform=ax.transAxes,
                            ha="left", va="top", zorder=7,
                            bbox=dict(facecolor="white", edgecolor="none", alpha=0.8))

        def update(frame):
            for idx, (artist, agent_path) in enumerate(zip(agent_artists, padded_paths)):
                row, col = agent_path[frame]
                row_offset, col_offset = self._track_offset(idx, len(paths))
                artist.set_position((col + col_offset, row + row_offset))
            step_text.set_text(f"step {frame}")
            return agent_artists + [step_text]

        animation = FuncAnimation(fig, update, frames=max_path_length,
                                  interval=interval, blit=True)
        if show:
            plt.show()
        else:
            plt.close(fig)
        return animation

    def _normalize_paths(self, path):
        if path is None:
            return []

        path = list(path)
        if len(path) == 0:
            return []

        if hasattr(path[0], "state"):
            if len(path[0].state) > 0 and hasattr(path[0].state[0], "__len__"):
                paths = [[state.state[i] for state in path] for i in range(len(path[0].state))]
            else:
                paths = [[state.state for state in path]]
        elif len(path[0]) == 2 and all(isinstance(v, (int, np.integer)) for v in path[0]):
            paths = [path]
        else:
            paths = path

        normalized = []
        for agent_path in paths:
            normalized_path = []
            for loc in agent_path:
                if (
                    not hasattr(loc, "__len__")
                    or len(loc) != 2
                    or not all(isinstance(v, (int, np.integer)) for v in loc)
                ):
                    raise ValueError("draw_maze expects paths to contain 2-integer maze locations")
                normalized_path.append(tuple(loc))
            normalized.append(tuple(normalized_path))
        return normalized
