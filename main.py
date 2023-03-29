from tasks import *

n = ReadCSV('connection_graph (1).csv').read_csv()
# algorithm = input('Please, enter your choice: ')
# start_point = input('Start stop: ')
# end_point = input('End stop: ')
# start_time = input('Start time: ')
# optimization_criterion = input()
# algorithm = 'a'
# optimization_criterion = 'p'

task_1(n, 'a', 'KRZYKI', 'KRZYKI', '20:00:00')
