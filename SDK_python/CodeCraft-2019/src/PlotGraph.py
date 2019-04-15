import networkx as nx
import matplotlib.pyplot as plt
import HandleFile
import Graph
import GridMap


# 绘图，网格
def plot_graph(road, cross, map_grid):
    cross2 = dict(zip(cross.keys(), [[] for n in range(len(cross))]))
    for key in cross:
        s = cross[key]
        for i in range(len(s)):
            if s[i] == -1:
                cross2[key].append(-1)
                continue
            r = road[s[i]]
            if r[-3] == key:
                cross2[key].append(r[-2])
            else:
                cross2[key].append(r[-3])
    G = nx.Graph()
    for key in road:
        start = road[key][-3]
        end = road[key][-2]
        G.add_edge(start, end)
    nx.draw(G, pos=map_grid, with_labels=True)
    plt.figure()
    plt.show()


# 绘图，边长
def plot_graph2(road, cross):
    cross2 = dict(zip(cross.keys(), [[] for n in range(len(cross))]))
    for key in cross:
        s = cross[key]
        for i in range(len(s)):
            if s[i] == -1:
                cross2[key].append(-1)
                continue
            r = road[s[i]]
            if r[-3] == key:
                cross2[key].append(r[-2])
            else:
                cross2[key].append(r[-3])
    G = nx.Graph()
    for key in road:
        start = road[key][-3]
        end = road[key][-2]
        edge = road[key][0]
        # G.add_edge(start, end)
        G.add_weighted_edges_from([(start, end, edge)])
    nx.draw(G, with_labels=True)
    plt.figure()
    plt.show()


def main():
    # 地图1
    car_path = "../config/car.txt"
    road_path = "../config/road.txt"
    cross_path = "../config/cross.txt"
    preset_answer_path = "../config/presetAnswer.txt"
    answer_path = "../config/answer.txt"

    # 地图2
    car_path = "../config_1/car.txt"
    road_path = "../config_1/road.txt"
    cross_path = "../config_1/cross.txt"
    preset_answer_path = "../config_1/presetAnswer.txt"
    answer_path = "../config_1/answer.txt"

    car, road, cross, preset_answer = HandleFile.read_all_data(car_path, road_path, cross_path, preset_answer_path)
    map_grid = GridMap.grid_map(road, cross)
    plot_graph(road, cross, map_grid)
    plot_graph2(road, cross)


if __name__ == "__main__":
    main()
