import csv
import datetime
import math


def all_lines(file_elems):  # список із всіх ліній файлу
    return set(i['line'] for i in file_elems)


def elems_of_line(line, file_elems):
    return list(filter(lambda x: x['line'] == line, file_elems))    # повертає всі точки із заданої лінії


def call_algorithm(algorithm, start_point, end_point, start_time, file_elems, optimization_criterion='t'):  # виклик потрібного алгоритму
    if algorithm == 'd':
        al = Dijkstra(start_point, end_point, start_time, file_elems).dijkstra_with_time()
        if al != None:
            return al
    elif algorithm == 'a':
        al = Astar(start_point, end_point, optimization_criterion, start_time, file_elems).ast_algorithm()
        if al != None:
            return al


def call_tabu(start_point, list_of_stations, optimization_criterion, start_time, file_elements):
    al = Tabu(start_point, list_of_stations, optimization_criterion, start_time, file_elements).tabu()
    if al != None:
        return al


class ReadCSV:      # читання файлу
    def __init__(self, csv_file):
        self.csv_file = csv_file

    def read_csv(self):
        rows = []
        with open(self.csv_file, 'r', encoding='utf-8') as file:
            csvreader = csv.reader(file)
            header = next(csvreader)
            for row in csvreader:
                rows.append(dict(zip(header, row)))
        return rows


class Algorithm:
    def __init__(self, start_point, end_point, start_time, file_elems):
        self.start_point = start_point
        self.end_point = end_point
        self.start_time = start_time
        self.file_elems = file_elems


class StaticMethods:

    @staticmethod
    def work_with_time(dep_time: str, arr_time: str):  # пошук пройденого часу в хв від dep_time до arr_time
        dep_h, dep_m = map(int, dep_time[:-3].split(':'))
        arr_h, arr_m = map(int, arr_time[:-3].split(':'))
        return abs(arr_h - dep_h) * 60 + abs(arr_m - dep_m)

    @staticmethod
    def del_elem(file_elems, start_point, end_point):
        o = 0
        for i in range(len(file_elems)):  # шукаємо першу точку із заданим міцем старту
            if file_elems[i]['start_stop'] == start_point:
                o = i
                break
        del file_elems[:o]  # видаляємо лишнє
        for i in range(len(file_elems) - 1, 0, -1):  # шукаємо останню точку із заданим міцем фінішу
            if file_elems[i]['end_stop'] == end_point:
                o = i
                break
        del file_elems[o + 1:]  # видаляємо лишнє
        return file_elems

    def open_point(self, file_elems, start_point, end_point, start_time):    # створення списка із кортежів (коеф, інформація про зупинку) із доданим першим елементом, який підходить по часу та місці
        self.del_elem(file_elems, start_point, end_point)
        return file_elems, [(float(0), i) for i in file_elems if i['start_stop'] == start_point
                            and i['departure_time'] == start_time] # повертає зменшений список елементів

    @staticmethod
    def str_to_time(time: str):     # перетворення тексту на час
        return datetime.time(*[int(i) for i in time.split(':')])


class Dijkstra(Algorithm, StaticMethods):

    def __init__(self, start_point, end_point, start_time, file_elems):
        super().__init__(start_point, end_point, start_time, file_elems)

    def dijkstra_with_time(self):
        self.file_elems, open_points = self.open_point(self.file_elems, self.start_point,
                                                       self.end_point, self.start_time)     # елементи файлу та список із кортежів (коеф, інформація про зупинку)
        list_n = []
        if len(open_points) > 0:    # проходимо по списку, якщо він не порожній
            while len(self.file_elems) != 0:
                list_of_points = [i[1] for i in open_points]
                for i in self.file_elems:
                    k = open_points[0][0]   # початкова точка
                    if open_points[0][1]['end_stop'] == i['start_stop']:    #рухаємось тільки по тих точках, які з'єднані початковою та останньою зупинкою
                        k += self.work_with_time(open_points[0][1]['departure_time'], i['departure_time'])  # збільшення коефіцієнта за часом
                        if i in list_of_points:
                            if open_points[list_of_points.index(i)][0] > k:      # якщо точка вже є в списку, але з більшим коеф, то замінюємо
                                open_points.pop(list_of_points.index(i))    # видаляємо стару
                                open_points.append((k, i))      # ставим на її місце іншу
                        else:
                            open_points.append((k, i))      # просто додаємо елем
                if open_points[0][1]['end_stop'] == self.end_point:     # коли знаходимо фініш, то повертаємо інфу про дану точку
                    list_n.append(open_points[0][1])
                    list_n.reverse()
                    n = list_n[0]
                    i = 1
                    while i != len(list_n):
                        if n['start_stop'] != list_n[i]['end_stop']:
                            list_n.pop(i)
                        else:
                            n = list_n[i]
                            i += 1
                    list_n.reverse()
                    return list_n
                list_n.append(open_points[0][1])       # видаляємо елемент зі списку ел-тів з файлу
                self.file_elems.remove(open_points[0][1])
                open_points.pop(0)      # видаляємо першу точку з файлу відкритих
                open_points = sorted(open_points, key=lambda item: item[0])  # сортування по коефіцієнту
            return None
        return None


class Astar(Algorithm, StaticMethods):
    def __init__(self, start_point, end_point, optimization_criterion, start_time, file_elems):
        if optimization_criterion == 'p' or optimization_criterion == 't':
            super().__init__(start_point, end_point, start_time, file_elems)
            self.optimization_criterion = optimization_criterion
            self.end_point_info = self.end_p(file_elems, end_point) # інформація по фінішній точці
        else:
            raise ValueError

    def ast_algorithm(self):
        self.file_elems, open_points = self.open_point(self.file_elems, self.start_point,
                                                       self.end_point, self.start_time)     # елементи файлу та список із кортежів (коеф, інформація про зупинку)
        list_n = []
        if len(open_points) > 0:
            while len(self.file_elems) != 0:
                list_of_points = [i[1] for i in open_points]
                for i in self.file_elems:
                    n = 0
                    if open_points[0][1]['end_stop'] == i['start_stop']:
                        n += 1 if self.optimization_criterion == 'p' \
                                  and self.str_to_time(open_points[0][1]['departure_time']) \
                                  < self.str_to_time(i['departure_time'])else \
                                  self.work_with_time(open_points[0][1]['departure_time'], i['departure_time'])     # якщо по пересадках, то просто додаємо +1, як по часу, то додаємочасову різницю між зупинками
                        h = self.h(*map(float, [i['start_stop_lat'],
                                                i['start_stop_lon'],
                                                self.end_point_info['end_stop_lat'],
                                                self.end_point_info['end_stop_lon']]))       # теорема Піфагора по точках
                        if i in list_of_points:
                            if open_points[list_of_points.index(i)][0] > h+n:
                                open_points.pop(list_of_points.index(i))
                                open_points.append((n+h, i))
                        else:
                            open_points.append((n+h, i))
                if open_points[0][1]['end_stop'] == self.end_point:
                    list_n.append(open_points[0][1])
                    list_n.reverse()
                    n = list_n[0]
                    i = 1
                    while i != len(list_n):
                        if n['start_stop'] != list_n[i]['end_stop']:
                            list_n.pop(i)
                        else:
                            n = list_n[i]
                            i += 1
                    list_n.reverse()
                    return list_n
                list_n.append(open_points[0][1])
                self.file_elems.remove(open_points[0][1])
                open_points.pop(0)
                open_points = sorted(open_points, key=lambda item: item[0])
            return None
        return None

    @staticmethod
    def end_p(file_elems, end_point):   # інформація по ост точці
        for i in file_elems:
            if i['end_stop'] == end_point:
                return i

    @staticmethod
    def h(x1: float, y1: float, x2: float, y2: float):   # start_stop_lat, start_stop_lon, end_stop_lat, end_stop_lon
        b = abs(x2 - x1)
        c = abs(y2-y1)
        return math.sqrt(b**2+c**2)
