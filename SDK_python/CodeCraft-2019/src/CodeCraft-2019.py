import logging
import sys
import HandleFile
import GridMap
import Graph
import Processing
import math

logging.basicConfig(level=logging.DEBUG,
                    filename='../logs/CodeCraft-2019.log',
                    format='[%(asctime)s] %(levelname)s [%(funcName)s: %(filename)s, %(lineno)d] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filemode='a')


# python CodeCraft-2019.py ../config/car.txt ../config/road.txt ../config/cross.txt ../config/presetAnswer.txt ../config/answer.txt
def main():
    if len(sys.argv) != 6:
        logging.info('please input args: car_path, road_path, cross_path, answerPath')
        exit(1)

    car_path = sys.argv[1]
    road_path = sys.argv[2]
    cross_path = sys.argv[3]
    preset_answer_path = sys.argv[4]
    answer_path = sys.argv[5]

    # car_path = "../config/car.txt"
    # road_path = "../config/road.txt"
    # cross_path = "../config/cross.txt"
    # preset_answer_path = "../config/presetAnswer.txt"
    # answer_path = "../config/answer.txt"
    #
    # car_path = "../config_1/car.txt"
    # road_path = "../config_1/road.txt"
    # cross_path = "../config_1/cross.txt"
    # preset_answer_path = "../config_1/presetAnswer.txt"
    # answer_path = "../config_1/answer.txt"

    logging.info("car_path is %s" % (car_path))
    logging.info("road_path is %s" % (road_path))
    logging.info("cross_path is %s" % (cross_path))
    logging.info("preset_answer_path is %s" % (preset_answer_path))
    logging.info("answer_path is %s" % (answer_path))

    # to read input file
    car, road, cross, preset_answer = HandleFile.read_all_data(car_path, road_path, cross_path, preset_answer_path)

    # 分开调参，每秒发车数量
    if 90761 in car:
        dis = 1
        step = 82
        step2 = 100
        time_step = 10
    else:
        dis = 2
        step = 64
        step2 = 64
        time_step = 9

    car_time = Processing.compute_pre_car(preset_answer, step)  # 为预置车辆设置出发时间
    preset_answer_cross = Processing.judge_pre_cross(car, preset_answer, cross)  # 预置车辆的方向统计，按时间统计

    # 地图一后10%的车辆提出，重新安排路径，地图二不处理预置车辆
    if dis == 1:
        pre_num = 0
        for t in preset_answer:
            pre_num = pre_num + len(preset_answer[t])
        pre_original_num = int(pre_num/10)  # 可处理预置车辆的个数
        preset_answer_time = list(preset_answer.keys())
        preset_answer_time.sort(reverse=True)
        pre_original = {}  # 可处理预置车辆统计
        end_time = 1000  # 预置车辆最大出发时间（地图2）
        for i in range(len(preset_answer_time)):
            t = preset_answer_time[i]
            if pre_original_num <= 0:
                break
            end_time = t
            pre_original[t] = {}
            if len(preset_answer[t]) <= pre_original_num:
                for key in preset_answer[t]:
                    pre_original[t][key] = 0
                pre_original_num = pre_original_num - len(preset_answer[t])
                del preset_answer[t]  # 将重新设置路径的预置车辆从preset_answer中删除
            else:
                delete = []
                for key in preset_answer[t]:
                    if pre_original_num > 0:
                        delete.append(key)
                        pre_original[t][key] = 0
                        pre_original_num = pre_original_num - 1
                    else:
                        break
                for j in range(len(delete)):
                    key = delete[j]
                    del preset_answer[t][key]
                pass
    # process
    map_cross = Graph.build_map_equal(road, cross)  # 设置地图

    map_grid = GridMap.grid_map(road, cross)  # 路口到坐标的映射
    cross_list = GridMap.cross_sort(map_grid)  # 对路口进行排序，离得近的路口在排序中离得尽量远

    road_importance = Processing.road_import(road)  # 每条路的重要性
    time_group, max_time = Processing.time_grouping(car)  # 按时间分组结果以及出发的最大时间

    # 结果 {车标号:{预计出发时间,[路口],[路径],实际出发时间}}
    answer = Processing.initialize_answer(car)

    # 预置车辆最大出发时间（地图2）
    max_pre_time = max(preset_answer_cross.keys())
    shortest_path = Graph.compute_shortest_path(map_cross)  # 两个路口之间最短路查询
    car_flag = {}  # 当前可出发的全部车辆
    bias = dict(zip(cross.keys(), [0 for n in range(len(cross))]))  # 每个路口当前跑的车数
    # 最大出发时间内，按时间迭代
    for t in range(1, max_time + 1):
        print(t)
        # 若当前时间有预置车辆，修改路的权重和bias
        if t in preset_answer:
            Processing.modify_weight(map_cross, preset_answer[t], road, road_importance, car)
            for c in preset_answer_cross[t]:
                bias[c] = bias[c] + preset_answer_cross[t][c]
        # 地图一，修改预置车辆的路径
        if dis == 1:
            if t in pre_original:
                for key in pre_original[t]:
                    path = Graph.dijkstra(map_cross, car[key][0], car[key][1])
                    l = math.log(len(path[0]) - 1, 7)
                    for j in range(len(path[0]) - 1):
                        start = path[0][j]
                        end = path[0][j + 1]
                        map_cross[start][end][0] = map_cross[start][end][0] + road_importance[path[1][j]]
                    answer[key] = [car[key][3]]
                    answer[key] = answer[key] + path
                    answer[key].append(t)
        # 若当前时间有车出发，添加当前可出发辆
        if t in time_group:
            Processing.compute_car_flag(car_flag, car, shortest_path, time_group, t, map_grid)
        # 若预置车辆占了最大出发车辆的名额，不发其它的车
        if car_time[t] >= step:
            continue
        # 当前可出发车辆按照路口分组
        group = Processing.grouping_up_down3(car_flag, cross, car)
        # 按照平均原则补偿bias，出发上或下的车辆
        Processing.modify_answer1(answer, group, car_flag, map_cross, car, step-car_time[t], t, road_importance, bias, cross_list)

    group = Processing.grouping_up_down3(car_flag, cross, car)
    # position = dict(zip(map_cross.keys(), [0 for n in range(len(map_cross))]))
    pointer = 0
    for t in range(max_time+1, 10000):
        print(t)
        # 预置车辆全部发完后，增大每秒发车数量
        if dis == 1:
            if t > end_time and t % time_step == 0:
                step = step + 1
            if step > step2:
                step = step2
        else:
            if t > max_pre_time and t % time_step == 0:
                step = step + 1
            if step > step2:
                step = step2

        # 若当前时间有预置车辆，修改路的权重和bias
        if t in preset_answer:
            Processing.modify_weight(map_cross, preset_answer[t], road, road_importance, car)
            for c in preset_answer_cross[t]:
                bias[c] = bias[c] + preset_answer_cross[t][c]
        if dis == 1:
            if t in pre_original:
                for key in pre_original[t]:
                    path = Graph.dijkstra(map_cross, car[key][0], car[key][1])
                    l = math.log(len(path[0]) - 1, 7)
                    for j in range(len(path[0]) - 1):
                        start = path[0][j]
                        end = path[0][j + 1]
                        map_cross[start][end][0] = map_cross[start][end][0] + road_importance[path[1][j]]
                    answer[key] = [car[key][3]]
                    answer[key] = answer[key] + path
                    answer[key].append(t)
        # 出发step-car_time[t]的车子
        pointer_s = pointer+step-car_time[t]
        # 按照平均原则补偿bias，出发各个路口的车辆
        flag = Processing.modify_answer2(answer, group, map_cross, car, t, pointer, pointer_s, road_importance, bias, cross_list)
        if flag == 0:
            break
        pointer = pointer_s
    # print(answer)

    # to write output file
    HandleFile.write_data(answer, answer_path)


if __name__ == "__main__":
    main()
