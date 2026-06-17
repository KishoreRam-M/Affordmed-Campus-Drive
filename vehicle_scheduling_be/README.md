# Vehicle Maintenance Scheduler MVP

Production-ready minimal FastAPI service for selecting vehicle maintenance tasks that maximize impact within depot mechanic-hour limits.

## Features

- FastAPI REST API with Swagger at `/docs` and ReDoc at `/redoc`
- Async external API calls with `httpx`
- Pydantic request/response models
- 0/1 Knapsack Dynamic Programming optimizer with `O(n * capacity)` time complexity
- Global exception handling for API failures, timeouts, validation errors, and missing depots
- Unit and API tests with pytest
- Dockerized runtime

## Project Structure

```text
vehicle_scheduling_be/
├── app/
│   ├── main.py
│   ├── core/config.py
│   ├── api/routes.py
│   ├── clients/evaluation_client.py
│   ├── services/optimizer.py
│   ├── models/schemas.py
│   └── utils/exceptions.py
├── tests/
│   ├── test_optimizer.py
│   └── test_schedule.py
├── requirements.txt
├── Dockerfile
├── .env.example
├── README.md
└── notification_system_design.md
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

On macOS/Linux, activate with:

```bash
source .venv/bin/activate
```

## Run

```bash
uvicorn app.main:app --reload
```

Service URL:

```text
http://127.0.0.1:8000
```

## API Documentation

- Swagger: `http://127.0.0.1:8000/docs`
- ReDoc: `http://127.0.0.1:8000/redoc`

## Endpoints

### GET `/api/v1/depots`

Returns the raw response from:

```text
http://4.224.186.213/evaluation-service/depots
```

### GET `/api/v1/vehicles`

Returns the raw response from:

```text
http://4.224.186.213/evaluation-service/vehicles
```

### GET `/api/v1/schedule/{depot_id}`

Fetches depots and vehicles, finds the requested depot, extracts candidate maintenance tasks, and returns the optimal task schedule.

Example response:

```json
{
  "depot_id": "D1",
  "mechanic_hours": 7,
  "used_hours": 7,
  "remaining_hours": 0,
  "total_impact": 40,
  "selected_tasks": [
    {
      "task_id": "T1",
      "duration": 2,
      "impact": 10,
      "vehicle_id": "V1"
    },
    {
      "task_id": "T2",
      "duration": 5,
      "impact": 30,
      "vehicle_id": "V1"
    }
  ]
}
```

## Testing

```bash
pytest --cov=app --cov-report=term-missing
```

The tests cover:

- Optimizer normal case
- Empty task list
- Zero capacity
- Large capacity
- Valid schedule endpoint
- Missing depot
- External API failure
- Raw proxy endpoints

## Docker

Build:

```bash
docker build -t vehicle-scheduling-be .
```

Run:

```bash
docker run --rm -p 8000:8000 --env-file .env vehicle-scheduling-be
```

Open:

```text
http://127.0.0.1:8000/docs
```

## Architecture

The app follows a small clean architecture:

- `api/routes.py`: HTTP routes and dependency wiring
- `clients/evaluation_client.py`: external API access
- `services/optimizer.py`: pure business optimization logic
- `models/schemas.py`: Pydantic models and response normalization
- `utils/exceptions.py`: domain exceptions and global handlers
- `core/config.py`: environment-driven settings

The optimizer is pure and has no FastAPI or network dependency, which makes it easy to test and explain.

## Knapsack Explanation

Each maintenance task is treated as an item:

- `Duration` is the item weight
- `Impact` is the item value
- Depot mechanic hours are the knapsack capacity

The service uses 0/1 Knapsack Dynamic Programming, where each task can be selected at most once.

`dp[i][h]` stores the maximum impact possible using the first `i` tasks with `h` available mechanic hours.

Transition:

```text
dp[i][h] = max(
  dp[i - 1][h],
  dp[i - 1][h - task.duration] + task.impact
)
```

Time complexity is `O(n * capacity)`, where `n` is the number of tasks.
Space complexity is `O(n * capacity)` because the table is retained to reconstruct the selected tasks.

