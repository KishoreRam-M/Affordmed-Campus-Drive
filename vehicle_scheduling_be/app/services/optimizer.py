from app.models.schemas import MaintenanceTask, ScheduledTask


def optimize_tasks(
    tasks: list[MaintenanceTask | ScheduledTask], mechanic_hours: int
) -> tuple[list[MaintenanceTask | ScheduledTask], int, int]:
    if mechanic_hours <= 0 or not tasks:
        return [], 0, 0

    capacity = int(mechanic_hours)
    item_count = len(tasks)
    dp: list[list[int]] = [[0] * (capacity + 1) for _ in range(item_count + 1)]

    for index, task in enumerate(tasks, start=1):
        for hours in range(capacity + 1):
            dp[index][hours] = dp[index - 1][hours]
            if task.duration <= hours:
                candidate = dp[index - 1][hours - task.duration] + task.impact
                if candidate > dp[index][hours]:
                    dp[index][hours] = candidate

    selected: list[MaintenanceTask | ScheduledTask] = []
    remaining_capacity = capacity
    for index in range(item_count, 0, -1):
        if dp[index][remaining_capacity] != dp[index - 1][remaining_capacity]:
            task = tasks[index - 1]
            selected.append(task)
            remaining_capacity -= task.duration

    selected.reverse()
    used_hours = sum(task.duration for task in selected)
    total_impact = dp[item_count][capacity]
    return selected, used_hours, total_impact

