import heapq
from state import AbstractState

def best_first_search(starting_state: AbstractState) -> list[AbstractState]:
    '''
    Implementation of best first search algorithm

    Input:
        starting_state: an AbstractState object

    Return:
        A path consisting of a list of AbstractState states
        The first state should be starting_state
        The last state should have state.is_goal() == True
    '''
    # we will use this visited_states dictionary to serve multiple purposes
    # - visited_states[state] = (parent_state, distance_of_state_from_start)
    #   - keep track of which states have been visited by the search algorithm
    #   - keep track of the parent of each state, so we can call backtrack(visited_states, goal_state) and obtain the path
    #   - keep track of the distance of each state from start node
    #       - if we find a shorter path to the same state we can update with the new state 
    # NOTE: we can hash states because the __hash__/__eq__ method of AbstractState is implemented
    visited_states: dict[AbstractState, tuple[AbstractState | None, int]] = {starting_state: (None, 0)}

    # The frontier is a priority queue
    # You can pop from the queue using "heapq.heappop(frontier)"
    # You can push onto the queue using "heapq.heappush(frontier, state)"
    # NOTE: states are ordered because the __lt__ method of AbstractState is implemented
    frontier: list[AbstractState] = []
    heapq.heappush(frontier, starting_state)
    
    while len(frontier) > 0:
        state = heapq.heappop(frontier)
        # print(f"State: {state}")

        if visited_states[state][1] != state.dist_from_start:
            continue

        if state.is_goal():
            print(f"Visited states: {len(visited_states)}")
            return backtrack(visited_states, state)

        for neighbor in state.get_neighbors():
            if neighbor in visited_states:
                _, neighbor_distance_of_state_from_start = visited_states[neighbor]

                if neighbor_distance_of_state_from_start <= neighbor.dist_from_start:
                    continue

            visited_states[neighbor] = (state, neighbor.dist_from_start)
            heapq.heappush(frontier, neighbor)
    
    # if you do not find the goal return an empty list
    return []

def backtrack(visited_states: dict, goal_state: AbstractState) -> list[AbstractState]:
    '''
    Implementation of the backtrack method

    Input:
        visited_states: a dictionary mapping AbstractState objects to (parent_state, distance_from_start) tuples
        goal_state: an AbstractState object

    Return:
        A path consisting of a list of AbstractState states
        The first state should be starting_state
        The last state should have state.is_goal() == True
    '''
    path = []
    state = goal_state
    while True:
        path.insert(0, state)

        if state not in visited_states:
            raise ValueError("State has not been visited.")

        parent_state, distance_of_state_from_start = visited_states[state]
        if distance_of_state_from_start == 0:
            break

        state = parent_state
    return path
