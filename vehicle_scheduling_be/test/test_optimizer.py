from app.models.schemas import MaintenanceTask
from app.services.optimizer import optimize_tasks


def test_optimize_tasks_normal_case() -> None:
    tasks = [
        MaintenanceTask(task_id="T1", duration=2, impact=10),
        MaintenanceTask(task_id="T2", duration=3, impact=14),
        MaintenanceTask(task_id="T3", duration=4, impact=16),
        MaintenanceTask(task_id="T4", duration=5, impact=30),
    ]

    selected, used_hours, total_impact = optimize_tasks(tasks, 7)

    assert [task.task_id for task in selected] == ["T1", "T4"]
    assert used_hours == 7
    assert total_impact == 40


def test_optimize_tasks_empty_tasks() -> None:
    selected, used_hours, total_impact = optimize_tasks([], 10)

    assert selected == []
    assert used_hours == 0
    assert total_impact == 0


def test_optimize_tasks_zero_capacity() -> None:
    tasks = [MaintenanceTask(task_id="T1", duration=2, impact=10)]

    selected, used_hours, total_impact = optimize_tasks(tasks, 0)

    assert selected == []
    assert used_hours == 0
    assert total_impact == 0


def test_optimize_tasks_large_capacity_selects_all_positive_tasks() -> None:
    tasks = [
        MaintenanceTask(task_id="T1", duration=2, impact=10),
        MaintenanceTask(task_id="T2", duration=3, impact=14),
    ]

    selected, used_hours, total_impact = optimize_tasks(tasks, 100)

    assert [task.task_id for task in selected] == ["T1", "T2"]
    assert used_hours == 5
    assert total_impact == 24

