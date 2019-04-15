# 建立图谱
def build_map_equal(road, cross):
    map_cross = dict(zip(cross.keys(), [{} for n in range(len(cross))]))
    
    for key in road:
        # edge = road[key][0]
        edge = 10
        # edge = 10
        start = road[key][-3]
        end = road[key][-2]
        isDuplex = road[key][-1]
        map_cross[start][end] = [edge, key]
        if isDuplex == 1:
            # map_cross[start][end] = [edge, key]
            map_cross[end][start] = [edge, key]
    return map_cross


def del_road_duplex(road):
    del_key = []
    for key in road:
        if road[key][-1] == 0:
            del_key.append(key)
    for key in del_key:
        del road[key]


def dijkstra(map_cross, current, destination):
    nodes = map_cross.keys()
    unvisited = {node: None for node in nodes}  # 把None作为无穷大使用
    visited = {}  # 用来记录已经松弛过的数组
    path = {}  # 用来记录最短路径
    currentDistance = 0
    unvisited[current] = currentDistance  # B到B的距离记为0
    path[current] = [current]
    while True:
        for neighbour, distance in map_cross[current].items():
            if neighbour not in unvisited:
                continue  # 被访问过了，跳出本次循环
            newDistance = currentDistance + distance[0]  # 新的距离
            if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:  # 如果两个点之间的距离之前是无穷大或者新距离小于原来的距离
                unvisited[neighbour] = newDistance  # 更新距离
        visited[current] = currentDistance  # 这个点已经松弛过，记录
        for key in visited:
            if current in map_cross[key] and visited[key] + map_cross[key][current][0] == currentDistance:
                path[current] = path[key][:]
                path[current].append(current)
        if current == destination:
            break
        del unvisited[current]  # 从未访问过的字典中将这个点删除
        if not unvisited:
            break  # 如果所有点都松弛过，跳出此次循环
        candidates = [node for node in unvisited.items() if node[1]]  # 找出目前还有拿些点未松弛过
        if not candidates:
            break
        current, currentDistance = sorted(candidates, key=lambda x: x[1])[0]  # 找出目前可以用来松弛的点
    # return visited[destination],  path[destination]  # 返回int, 列表
    if destination in path:
        return [path[destination], cross_to_road(path[destination], map_cross)]  # 返回int, 列表
    else:
        return 0


def dijkstra2(map_cross, current):
    nodes = map_cross.keys()
    unvisited = {node: None for node in nodes}  # 把None作为无穷大使用
    visited = {}  # 用来记录已经松弛过的数组
    path = {}  # 用来记录最短路径
    currentDistance = 0
    unvisited[current] = currentDistance  # B到B的距离记为0
    path[current] = [current]
    while True:
        for neighbour, distance in map_cross[current].items():
            if neighbour not in unvisited:
                continue  # 被访问过了，跳出本次循环
            newDistance = currentDistance + distance[0]  # 新的距离
            if unvisited[neighbour] is None or unvisited[neighbour] > newDistance:  # 如果两个点之间的距离之前是无穷大或者新距离小于原来的距离
                unvisited[neighbour] = newDistance  # 更新距离
        visited[current] = currentDistance  # 这个点已经松弛过，记录
        for key in visited:
            if current in map_cross[key] and visited[key] + map_cross[key][current][0] == currentDistance:
                path[current] = path[key][:]
                path[current].append(current)
        del unvisited[current]  # 从未访问过的字典中将这个点删除
        if not unvisited:
            break  # 如果所有点都松弛过，跳出此次循环
        candidates = [node for node in unvisited.items() if node[1]]  # 找出目前还有拿些点未松弛过
        if not candidates:
            break
        current, currentDistance = sorted(candidates, key=lambda x: x[1])[0]  # 找出目前可以用来松弛的点
    return visited


def compute_shortest_path(map_cross):
    c = list(map_cross.keys())
    shortest_path = dict(zip(c, [{} for n in range(len(c))]))
    for key in shortest_path:
        shortest_path[key] = dijkstra2(map_cross, key)
    return shortest_path


def cross_to_road(path_cross, map_cross):
    path_road = []
    for i in range(0, len(path_cross)-1):
        # print(map_cross[path_cross[i]][map_cross[path_cross[i + 1]][1])
        start = path_cross[i]
        end = path_cross[i + 1]
        path_road.append(map_cross[start][end][1])
    return path_road


# 输入路口path，输出：0表示向下及水平，1表示向上
def judge_cross_direction(path, map_grid):
    total = judge_direction(path[0], path[-1], map_grid)
    for i in range(len(path)-2):
        start = path[i]
        end = path[i+1]
        if judge_direction(start, end, map_grid) == 2 or judge_direction(start, end, map_grid) == total:
            continue
        else:
            return 2
    return total


# 返回0说明向下，返回1说明向上，返回2说明水平
def judge_direction(start, end, map_grid):
    if map_grid[start][0] < map_grid[end][0] and map_grid[start][1] < map_grid[end][1]:
        return 0
    elif map_grid[start][0] < map_grid[end][0] and map_grid[start][1] > map_grid[end][1]:
        return 1
    elif map_grid[start][0] > map_grid[end][0] and map_grid[start][1] < map_grid[end][1]:
        return 2
    elif map_grid[start][0] > map_grid[end][0] and map_grid[start][1] > map_grid[end][1]:
        return 3
    else:
        return 4
