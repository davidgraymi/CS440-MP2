from hard_mapf import solve_hard_mapf_instance
from mapf import MultiAgentGridState
from task_planning import BooleanPredicatesState, BlockWorld
from search import best_first_search
from maze import Maze
from tp_vis import draw_path

import time
import argparse
import json

def main(args):
    # multi agent search
    if "Grid" in args.problem_type:
        # 1. Get problem info
        filename = args.maze_file
        print(f"Doing Maze search for file {filename}")
        maze = Maze(filename, allow_waiting=not args.disallow_waiting)
        # maze.starts is a dictionary mapping characters to locations
        # maze.goals is a dictionary mapping characters to a tuple of locations
        tasks = [(maze.starts[c], maze.goals[c]) for c in maze.starts]
        starts, goals = zip(*tasks)
        # NOTE: enforce that each agent has only one goal for this MP
        goals = tuple(g[0] for g in goals)

        # 2. Begin timer, time includes setup time
        start_time = time.time()  
        # COUPLED MAPF
        if args.problem_type == "GridMultiAgent":
            # 3. Create starting state
            starting_state = MultiAgentGridState(
                starts, goals, 
                dist_from_start = 0, 
                use_heuristic = args.use_heuristic,
                maze = maze,
                h_type = args.heuristic_type)
            # 4. Search for path
            path = best_first_search(starting_state)
            # 5. Postprocess path to be a list of paths, one per agent
            path = [[s.state[i] for s in path] for i in range(len(starts))]
        
        # CBS/PBS/PrioritizedSearch/whatever you implement for "hard" MAPF
        elif args.problem_type == "GridHard":
            # NOTE: we do not pass parameters such as use_heuristic or heuristic_type here 
            # since you should just make this method work as fast as possible 
            path = solve_hard_mapf_instance(starts=starts, goals=goals, maze=maze)
        
        # End timer
        end_time = time.time()

        print("\tStart: ", starts)
        print("\tGoal: ", goals)
        print("\tAgent path lengths:", [len(p) for p in path])
        for i in range(len(starts)):
            print(f"\t\tAgent {i} path: {path[i]}")
        print("\tStates explored: ", maze.num_states_validated)
        print("\tTime:", end_time-start_time)
        
        if args.show_maze_vis or args.save_maze:
            maze.draw_maze(path=path, save=args.save_maze, show=args.show_maze_vis)
        if args.animate_maze:
            maze.animate_maze(path=path)
    
    elif args.problem_type == "BlockWorld":
        filename = args.block_file
        print(f"Doing task planning search for file {filename}")
        with open(filename, 'r') as f:
            data = json.load(f)
        objects = data["objects"]
        start_predicates = set(data["start_predicates"])
        goal_predicates = set(data["goal_predicates"])
        world = BlockWorld(objects_by_type={"block": objects})
        
        starting_state = BooleanPredicatesState(
            state=start_predicates,
            goal=goal_predicates,
            world=world,
            delete_relaxation=False, # this should only be set to true inside compute_heuristic when needed
            heuristic_type=args.heuristic_type,
            prev_action=None, # first state has no previous action
            dist_from_start=0,
            use_heuristic=args.use_heuristic)
        start_time = time.time()
        path = best_first_search(starting_state)
        end_time = time.time()
        print("\tStart: ", start_predicates)
        print("\tGoal: ", goal_predicates)
        print("\tPath length: ", len(path))
        print("\tTime:", end_time-start_time)
        
        if args.spf > 0.0:
            draw_path(path, spf=args.spf)
    else:
        print("Problem type must be one of [GridMultiAgent, BlockWorld, GridHard]")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CS440 MP2 MAPF and TP', allow_abbrev=False)
    parser.add_argument('--h', action='help', help=argparse.SUPPRESS)
    parser.add_argument('--problem_type',dest="problem_type", type=str, default="GridMultiAgent",
                        help='Which search problem (i.e., AbstractState) to solve: [GridMultiAgent, BlockWorld, GridHard]')
    parser.add_argument('--use_heuristic', action = 'store_true',
                        help = 'use heuristic h in best_first_search')
    parser.add_argument('--maze_file', type=str, default="data/grid_multi_agent/swap_small",
                        help = 'path to maze file')
    parser.add_argument('--show_maze_vis', action = 'store_true',
                        help = 'show maze visualization')
    parser.add_argument('--animate_maze', action = 'store_true',
                        help = 'show animated maze visualization')
    parser.add_argument('--disallow_waiting', action = 'store_true',
                        help = 'disallow waiting action for the agent')
    parser.add_argument('--heuristic_type', type=str, default=None,
                        help = 'which heuristic to use; defaults to admissible for MAPF and num_unsatisfied_goals for BlockWorld')
    parser.add_argument('--save_maze', dest = 'save_maze', type = str, default = None,
                        help = 'save output to image file')
    parser.add_argument('--block_file', type=str, default="data/block_world/block_world_1.json",
                        help = 'path to block world problem file')
    parser.add_argument('--spf', dest = 'spf', type = float, default = 1.0,
                        help = 'seconds per frame in block world visualization - set this to less than or equal to 0 to not visualize')

    args = parser.parse_args()
    if args.heuristic_type is None:
        args.heuristic_type = "admissible" if "Grid" in args.problem_type else "num_unsatisfied_goals"
    print("Parsed Arguments:")
    for arg_name, arg_value in sorted(vars(args).items()):
        print(f"  {arg_name}: {arg_value}")
    main(args)
