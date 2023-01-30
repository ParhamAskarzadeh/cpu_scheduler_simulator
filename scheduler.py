from numpy import random, arange
import simpy
import operator
import matplotlib.pyplot as plt


class Scheduler(object):
    def __init__(self, env, task_count, y_mean, x_rate, z_mean, k, quantum1, quantum2, duration):
        self.count = task_count
        self.y_mean = y_mean
        self.x_rate = x_rate
        self.z_mean = z_mean
        self.k = k
        self.quantum1 = quantum1
        self.quantum2 = quantum2
        self.env = env
        self.priority_queue = []
        self.round_robin_t1 = []
        self.round_robin_t2 = []
        self.first_come_first_serve = []
        self.priority_queue_count = []
        self.round_robin_t1_count = []
        self.round_robin_t2_count = []
        self.cpu_work_count = []
        self.waiting_time = []
        self.expired_processes = 0
        self.first_come_first_serve_count = []
        self.action = env.process(self.run())
        self.idle_status = True
        self.duration = duration

    def job_creator(self, x_rate, y_mean, z_mean):
        # (enter arrival time, service time, priority, timeout)
        task_generated = (random.poisson(lam=x_rate, size=1)[0], int(random.exponential(scale=y_mean, size=1)[0]),
                          random.choice(arange(1, 4), p=[0.7, 0.2, 0.1], size=1)[0],
                          int(random.exponential(scale=z_mean, size=1)[0]))
        self.priority_queue.append(task_generated)

    def run(self):
        time = 0
        period_time = 2
        for _ in range(self.count):
            self.job_creator(y_mean=self.y_mean, x_rate=self.x_rate, z_mean=self.z_mean)
        while True:
            self.check_timeout()
            if time % period_time == 0 or time == 0:
                self.job_loader(k=self.k)
            time = self.env.now
            yield self.env.process(self.dispatcher())
            if self.idle_status:
                self.cpu_work_count.append(1)
            if time == self.env.now:
                yield self.env.timeout(1)
            if time + self.env.now > time + period_time:
                time += period_time

    def check_timeout(self):
        for queue in [self.round_robin_t1, self.round_robin_t2, self.priority_queue, self.first_come_first_serve]:
            for task in queue:
                if task[3] < self.env.now:
                    queue.remove(task)
                    self.expired_processes += 1

    def dispatcher(self):
        process = random.choice([self.round_robin_t1_process(self.quantum1), self.round_robin_t2_process(self.quantum2),
                                 self.first_come_first_serve_process()], p=[0.8, 0.1, 0.1], size=1)[0]
        yield self.env.process(process)

    def job_loader(self, k):
        self.__sort_priority_queue()
        self.priority_queue_count.extend(
            [len(self.priority_queue)] * (self.env.now - len(self.priority_queue_count) - 1))
        if len(self.round_robin_t1 + self.round_robin_t2 + self.first_come_first_serve) < k:
            counter = 0
            for idx, task in enumerate(self.priority_queue):
                if counter == k:
                    break
                if task[0] <= self.env.now:
                    self.round_robin_t1.append(self.priority_queue.pop(idx))
                    counter += 1

    def __update_service_time_in_tuple(self, main_tuple, service_time):
        new_tuple = list(main_tuple)
        new_tuple[1] = service_time
        return tuple(new_tuple)

    def round_robin_t1_process(self, quantum_time):
        if len(self.round_robin_t1) == 0:
            self.round_robin_t1_count.extend([0] * (self.env.now - len(self.round_robin_t1_count)))
            self.idle_status = True
        for task in self.round_robin_t1:
            if task[1] <= quantum_time:
                self.round_robin_t1_count.extend(
                    [len(self.round_robin_t1)] * (self.env.now - len(self.round_robin_t1_count) - 1))
                self.waiting_time.append((self.env.now + task[1]) - task[0])
                self.round_robin_t1.remove(task)
                self.round_robin_t1_count.append(len(self.round_robin_t1))
                self.idle_status = False
                yield self.env.timeout(task[1])
            else:
                self.round_robin_t1_count.extend(
                    [len(self.round_robin_t1)] * (self.env.now - len(self.round_robin_t1_count) - 1))
                self.round_robin_t2.append(self.__update_service_time_in_tuple(task, task[1] - quantum_time))
                self.round_robin_t1.remove(task)
                self.round_robin_t1_count.append(len(self.round_robin_t1))
                self.idle_status = False
                yield self.env.timeout(quantum_time)

    def round_robin_t2_process(self, quantum_time):
        if len(self.round_robin_t2) == 0:
            self.round_robin_t2_count.extend([0] * (self.env.now - len(self.round_robin_t2_count)))
            self.idle_status = True
        for task in self.round_robin_t2:
            if task[1] <= quantum_time:
                self.round_robin_t2_count.extend(
                    [len(self.round_robin_t2)] * (self.env.now - len(self.round_robin_t2_count) - 1))
                self.waiting_time.append((self.env.now + task[1]) - task[0])
                self.round_robin_t2.remove(task)
                self.round_robin_t2_count.append(len(self.round_robin_t2))
                self.idle_status = False
                yield self.env.timeout(task[1])
            else:
                self.round_robin_t2_count.extend(
                    [len(self.round_robin_t2)] * (self.env.now - len(self.round_robin_t2_count) - 1))
                self.first_come_first_serve.append(self.__update_service_time_in_tuple(task, task[1] - quantum_time))
                self.round_robin_t2.remove(task)
                self.round_robin_t2_count.append(len(self.round_robin_t2))
                self.idle_status = False
                yield self.env.timeout(quantum_time)

    def first_come_first_serve_process(self):
        if len(self.first_come_first_serve) > 0:
            self.first_come_first_serve_count.extend(
                [len(self.first_come_first_serve)] * (self.env.now - len(self.first_come_first_serve_count) - 1))
            task = self.first_come_first_serve.pop()
            self.waiting_time.append((self.env.now + task[1]) - task[0])
            self.first_come_first_serve_count.append(len(self.first_come_first_serve_count))
            self.idle_status = False
            yield self.env.timeout(task[1])
        else:
            self.first_come_first_serve_count.extend([0] * (self.env.now - len(self.first_come_first_serve_count)))
            self.idle_status = True

    def __sort_priority_queue(self):
        self.priority_queue = sorted(self.priority_queue, key=operator.itemgetter(2, 1), reverse=True)

    def analyse(self):
        queues = {
            'priority queue': self.priority_queue_count,
            'round robin t1 queue': self.round_robin_t1_count,
            'round robin t2 queue': self.round_robin_t2_count,
            'first come first serve queue': self.first_come_first_serve_count,
        }
        for i in queues:
            plt.bar(list(range(len(queues[i]))), queues[i])
            plt.xlabel('time')
            plt.ylabel('count')
            plt.title(i)
            plt.show()
            try:
                print('mean', i, 'delay =', sum(queues[i]) / len(queues[i]))
            except ZeroDivisionError:
                print('mean', i, 'delay =', 0)
        print('Percentage of expired processes =', self.expired_processes / self.count * 100)
        print('waiting time mean =', sum(self.waiting_time) / len(self.waiting_time))
        print('cpu worked time=', 100 - (len(self.cpu_work_count) / self.duration) * 100)


if __name__ == '__main__':
    env = simpy.Environment()
    duration = 50
    simulation = Scheduler(env=env, task_count=25, y_mean=2, z_mean=10, x_rate=3, k=2, quantum1=1, quantum2=2,
                           duration=duration)
    env.run(until=duration)
    simulation.analyse()
