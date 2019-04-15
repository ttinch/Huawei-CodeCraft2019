import Graph
import math


# 按时间分car
def time_grouping(car):
    time_group = {}
    for key in car:
        if car[key][5] == 1:
            continue
        t = car[key][3]
        if t in time_group:
            time_group[t].append(key)
        else:
            time_group[t] = [key]
    max_time = max(time_group.keys())
    return time_group, max_time


# 先将车分为优先车辆和普通车辆，再按照各个路口对当前可发的车进行分类
def grouping_up_down3(car_flag, cross, car):
    # 对car_flag排序，先按照长度升序，长度相同再按照车速降序
    car_tmp = sorted(car_flag.items(), key=lambda item: (-item[1][3], item[1][1], -item[1][2]))
    # 按照方向分为四个方向四组，加水平垂直方向
    group = [{},{}]
    group[0] = dict(zip(cross.keys(), [{} for n in range(len(cross))]))
    group[1] = dict(zip(cross.keys(), [{} for n in range(len(cross))]))
    for i in range(len(car_tmp)):
        key = car_tmp[i][0]
        start = car[key][0]
        pre = car[key][-2]
        if pre == 1:
            for c in group[0]:
                if c == start:
                    group[0][c][key] = 0
                    break
        else:
            for c in group[1]:
                if c == start:
                    group[1][c][key] = 0
                    break
    # 向下的组先按照长度升序，长度相同再按照车速降序
    # group[2].reverse()
    # group[3].reverse()
    # print(group)
    return group


# 按照路的容量和长度给出路的重要性
def road_import(road):
    road_importance = dict(zip(road.keys(), [0 for n in range(len(road))]))
    min_imp = 20000
    max_imp = 0
    for key in road_importance:
        road_importance[key] = 1000/(road[key][2]+road[key][1]/80)
        if road_importance[key] < min_imp:
            min_imp = road_importance[key]
        if road_importance[key] > max_imp:
            max_imp = road_importance[key]
    # 归一化到0.1-1
    min_dis = 0.1
    max_dis = 1
    if max_imp == min_imp:
        for key in road_importance:
            road_importance[key] = 1
        return road_importance
    for key in road_importance:
        road_importance[key] = min_dis + (road_importance[key] - min_imp) * (max_dis - min_dis) / (max_imp - min_imp)
    return road_importance


# 按照step分批预置车辆
def compute_pre_car(preset_answer, step):
    car_time = [0 for n in range(10000)]
    pre_time = list(preset_answer.keys())
    for i in range(len(pre_time)):
        t = pre_time[i]
        length = len(preset_answer[t])
        while 1:
            if length == 0:
                break
            if (step-car_time[t]) < length:
                if car_time[t] < step:
                    length = length-(step-car_time[t])
                    car_time[t] = step
                t = t+1
            else:
                car_time[t] = car_time[t]+length
                length = 0
                break
    return car_time


# 根据预置车辆修改地图
def modify_weight(map_cross, preset_answer, road, road_importance, car):
    for key in preset_answer:
        path = preset_answer[key]
        path_cross = [car[key][0]]
        for i in range(len(path)):
            key = path[i]
            start = road[key][3]
            end = road[key][4]
            if path_cross[i] == start:
                path_cross.append(end)
            elif path_cross[i] == end:
                path_cross.append(start)
        for i in range(len(path_cross) - 1):
            start = path_cross[i]
            end = path_cross[i + 1]
            map_cross[start][end][0] = map_cross[start][end][0] + road_importance[path[i]]


# 发车阶段，根据当前各路口各跑了多少辆车来发车，优先跑优先车辆，所有优先车辆跑完后跑其余普通车辆
def modify_answer1(answer, group, car_flag, map_cross, car, length, t, road_importance, bias, cross_list):
    for i in range(length):
        # 对于优先车辆，跑路口已跑车辆最少的路口的车辆
        cro = -1
        value = 100000
        for j in range(len(cross_list)):
            c = cross_list[j]
            if bias[c] < value and group[0][c]:
                cro = c
                value = bias[c]
        if cro != -1:
            for key in group[0][cro]:
                bias[cro] = bias[cro] + 1
                break
            del group[0][cro][key]
        else:
            # 优先车辆全部跑完，对于普通车辆，跑路口已跑车辆最少的路口的车辆
            cro = -1
            value = 100000
            for j in range(len(cross_list)):
                c = cross_list[j]
                if bias[c] < value and group[1][c]:
                    cro = c
                    value = bias[c]
            for key in group[1][cro]:
                bias[cro] = bias[cro] + 1
                break
            del group[1][cro][key]
        # 删除已经跑过的车辆
        del car_flag[key]
        # 计算当前车的路径
        path = Graph.dijkstra(map_cross, car[key][0], car[key][1])
        # 按照路径修改map_cross
        l = math.log(len(path[0]) - 1, 7)
        for j in range(len(path[0]) - 1):
            start = path[0][j]
            end = path[0][j + 1]
            map_cross[start][end][0] = map_cross[start][end][0] + road_importance[path[1][j]]/l
        # 写入answer
        answer[key] = [car[key][3]]
        answer[key] = answer[key] + path
        answer[key].append(t)
    # print(bias)


def modify_answer2(answer, group, map_cross, car, t, pointer, pointer_s, road_importance, bias, cross_list):
    for i in range(pointer, pointer_s):
        # 对于优先车辆，跑路口已跑车辆最少的路口的车辆
        cro = -1
        value = 100000
        for j in range(len(cross_list)):
            c = cross_list[j]
            if bias[c] < value and group[0][c]:
                cro = c
                value = bias[c]
        if cro != -1:
            for key in group[0][cro]:
                bias[cro] = bias[cro] + 1
                break
            del group[0][cro][key]
        else:
            # 优先车辆全部跑完，对于普通车辆，跑路口已跑车辆最少的路口的车辆
            cro = -1
            value = 100000
            for j in range(len(cross_list)):
                c = cross_list[j]
                if bias[c] < value and group[1][c]:
                    cro = c
                    value = bias[c]
            if cro == -1:
                return 0
            for key in group[1][cro]:
                bias[cro] = bias[cro] + 1
                break
            del group[1][cro][key]

        # 计算当前车的路径
        path = Graph.dijkstra(map_cross, car[key][0], car[key][1])
        l = math.log(len(path[0]) - 1, 7)
        # 按照路径修改map_cross
        for j in range(len(path[0]) - 1):
            start = path[0][j]
            end = path[0][j + 1]
            map_cross[start][end][0] = map_cross[start][end][0] + road_importance[path[1][j]]/l
        # 写入answer
        answer[key] = [car[key][3]]
        answer[key] = answer[key] + path
        answer[key].append(t)
    return 1


# 初始化answer，删除预置车辆
def initialize_answer(car):
    answer = dict(zip(car.keys(), [[] for n in range(len(car))]))
    for key in car:
        if car[key][5] == 1:
            del answer[key]
    return answer


# 计算当前可发的车
def compute_car_flag(car_flag, car, shortest_path, time_group, t, map_grid):
    for i in range(len(time_group[t])):
        key = time_group[t][i]
        if car[key][5] == 1:
            continue
        start = car[key][0]
        end = car[key][1]
        direct = Graph.judge_direction(start, end, map_grid)
        length = shortest_path[start][end]
        car_flag[key] = [direct, length, car[key][2], car[key][-2]]


# 统计每秒预置车辆的路口出发情况
def judge_pre_cross(car, preset_answer, cross):
    preset_answer_cross = dict(zip(preset_answer.keys(), [{} for n in range(len(preset_answer))]))
    for t in preset_answer:
        preset_answer_cross[t] = dict(zip(cross.keys(), [0 for n in range(len(cross))]))
        for key in preset_answer[t]:
            start = car[key][0]
            preset_answer_cross[t][start] = preset_answer_cross[t][start] + 1
    return preset_answer_cross
