# cpu_scheduler_simulator

This is a Python code for a scheduler implementation that simulates different scheduling algorithms such as Priority Queue, Round Robin, and First Come First Serve. The scheduler schedules tasks based on their arrival time, service time, and priority. The code uses the SimPy library for discrete-event simulation.

## Installation

To run the code, you need to have Python installed on your system. Additionally, you need to install the following libraries:

- numpy
- simpy
- matplotlib

You can install these libraries using pip:

```
pip install numpy simpy matplotlib
```

## Usage

```python
python scheduler.py
```

The code will simulate the scheduling of tasks using different algorithms and display the results.

## Description

The code defines a class `Scheduler` that represents the scheduler. The constructor of the `Scheduler` class takes several parameters:

- `env`: The SimPy environment object.
- `task_count`: The total number of tasks to be scheduled.
- `y_mean`: The mean value for the service time distribution.
- `x_rate`: The rate parameter for the arrival time distribution.
- `z_mean`: The mean value for the timeout distribution.
- `k`: The number of tasks to be loaded into the round-robin queues at each period.
- `quantum1`: The time quantum for the first round-robin queue.
- `quantum2`: The time quantum for the second round-robin queue.
- `duration`: The total simulation duration.

The `Scheduler` class has several methods:

- `job_creator`: Generates a new task with random arrival time, service time, priority, and timeout.
- `run`: The main simulation loop that runs until the specified duration. It creates the initial tasks, checks for timeout tasks, and dispatches tasks to different queues.
- `check_timeout`: Checks if any task has timed out and removes it from the corresponding queue.
- `dispatcher`: Randomly selects a scheduling algorithm (priority queue, round robin T1, or round robin T2) and dispatches the process.
- `job_loader`: Loads tasks from the priority queue into the round-robin queues based on the specified number `k`.
- `__update_service_time_in_tuple`: Helper method to update the service time in a task tuple.
- `round_robin_t1_process`: Implements the round-robin T1 scheduling algorithm.
- `round_robin_t2_process`: Implements the round-robin T2 scheduling algorithm.
- `first_come_first_serve_process`: Implements the first-come-first-serve scheduling algorithm.
- `__sort_priority_queue`: Sorts the priority queue based on priority and service time.
- `analyse`: Analyzes and displays the results of the simulation, including queue counts, mean delay, expired processes percentage, waiting time mean, and CPU worked time.
