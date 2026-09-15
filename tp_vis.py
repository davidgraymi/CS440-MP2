import matplotlib.pyplot as plt
import matplotlib.patches as patches

from task_planning import BooleanPredicatesState


BLOCK_SIZE = 1.0
COLUMN_GAP = 0.45
AXIS_PADDING = 0.5
ARM_GAP = 1.0
HELD_BLOCK_GAP = 0.2
LINE_WIDTH = 2
FIGSIZE = (5, 4)


def get_stacks(state: BooleanPredicatesState):
    """Return table stacks and the block currently held by the arm."""
    objects = state.world.objects_by_type["block"]
    facts = set(state.state)

    holding = None
    for block in objects:
        if f"arm_is_holding_{block}" in facts:
            holding = block

    above = {}
    for top in objects:
        for bottom in objects:
            if top != bottom and f"{top}_is_on_{bottom}" in facts:
                above[bottom] = top

    bottoms = [
        block for block in objects
        if block != holding and f"{block}_is_on_table" in facts
    ]
    bottoms += [
        block for block in objects
        if block != holding and block not in bottoms and block not in above.values()
    ]

    stacks = []
    placed = set()
    for bottom in sorted(bottoms):
        stack = []
        block = bottom
        while block is not None and block not in placed and block != holding:
            stack.append(block)
            placed.add(block)
            block = above.get(block)
        if stack:
            stacks.append(stack)

    for block in objects:
        if block != holding and block not in placed:
            stacks.append([block])

    return stacks, holding


def action_name(state: BooleanPredicatesState, step: int) -> str:
    if state.prev_action is None:
        return "Start"
    action, inputs = state.prev_action
    return f"Step {step}: {action.__name__}({', '.join(inputs)})"


def draw_state(ax: plt.Axes, state: BooleanPredicatesState, title=None):
    stacks, holding = get_stacks(state)
    objects = state.world.objects_by_type["block"]
    colors = {block: plt.cm.tab10(i) for i, block in enumerate(objects)}

    arm_slot = len(objects)
    arm_y = len(objects) * BLOCK_SIZE + ARM_GAP
    column_width = BLOCK_SIZE + COLUMN_GAP
    right_edge = (arm_slot + 1) * column_width - COLUMN_GAP

    ax.clear()
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_xlim(-AXIS_PADDING, right_edge + AXIS_PADDING)
    ax.set_ylim(-AXIS_PADDING, arm_y + AXIS_PADDING)
    ax.plot([0, right_edge], [0, 0], color="black", linewidth=LINE_WIDTH)
    ax.plot([0, right_edge], [arm_y, arm_y], color="black", linewidth=LINE_WIDTH)

    for stack in stacks:
        x = objects.index(stack[0]) * column_width
        for level, block in enumerate(stack):
            y = level * BLOCK_SIZE
            ax.add_patch(patches.Rectangle((x, y), BLOCK_SIZE, BLOCK_SIZE,
                                           facecolor=colors[block], edgecolor="black"))
            ax.text(x + BLOCK_SIZE / 2, y + BLOCK_SIZE / 2, block,
                    ha="center", va="center", weight="bold")

    if holding is not None:
        x = arm_slot * column_width
        y = arm_y - BLOCK_SIZE - HELD_BLOCK_GAP
        ax.add_patch(patches.Rectangle((x, y), BLOCK_SIZE, BLOCK_SIZE,
                                       facecolor=colors[holding], edgecolor="black"))
        ax.text(x + BLOCK_SIZE / 2, y + BLOCK_SIZE / 2, holding,
                ha="center", va="center", weight="bold")
    else:
        ax.text(right_edge, arm_y - BLOCK_SIZE / 3, "arm free",
                ha="right", va="center")

    if title is not None:
        ax.set_title(title)


def draw_path(path: list[BooleanPredicatesState], spf=1):
    if len(path) == 0:
        return

    fig, ax = plt.subplots(figsize=FIGSIZE)
    plt.show(block=False)
    for step, state in enumerate(path):
        draw_state(ax, state, action_name(state, step))
        fig.canvas.draw_idle()
        plt.pause(spf)
    plt.show(block=True)
