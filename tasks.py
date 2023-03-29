from algorithms import *
from custom_thread import *


def task_1(elements, algorithm, start_point,end_point,start_time, optimization_criterion='t'):  # ф-ція для виклику першого завдання
    thrds = []
    for i in all_lines(elements):
        el = elems_of_line(i, elements)
        if algorithm == 'd':
            thr = CustomThread(target=call_algorithm, args=(algorithm, start_point, end_point, start_time, el))
        else:
            thr = CustomThread(target=call_algorithm,
                               args=(algorithm, start_point, end_point, start_time, el, optimization_criterion))
        thrds.append(thr)
        thr.start()
    thrds = [i for i in thrds if i.join() != None]
    n = []
    for i in thrds:
        n.append(i.join())
    if optimization_criterion == 't':
        n = sorted(n, key=lambda x: StaticMethods.str_to_time(x[-1]['arrival_time']))
    else:
        n = sorted(n, key=lambda x: len(x))
    for i in n[0]:
        print(i)
