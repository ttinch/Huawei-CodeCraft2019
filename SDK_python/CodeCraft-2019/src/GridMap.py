# 生成网格，建立节点到坐标的对应关系
def grid_map(road, cross):
    map_grid = dict(zip(cross.keys(), [[] for n in range(len(cross))]))
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
    tmp = list(cross2.keys())
    c = tmp[0]
    map_grid[c] = [0, 0]
    des_grid = [[0, 1], [1, 0], [0, -1], [-1, 0]]
    for i in range(4):
        if cross2[c][i] == -1:
            continue
        map_grid[cross2[c][i]] = des_grid[i]
        build_cross(cross2[c][i], cross2, map_grid)
    return map_grid


def build_cross(current, cross2, map_grid):
    x = map_grid[current][0]
    y = map_grid[current][1]
    des = [-1, -1, -1, -1]
    des_grid = [[x, y+1], [x+1, y], [x, y-1], [x-1, y]]
    for i in range(4):
        des = cross2[current][i]
        if des != -1 and map_grid[des]:
            des_position = i
            break
    for j in range(4):
        if map_grid[des] == des_grid[j]:
            grid_position = j
            break
    for k in range(3):
        des_position = des_position + 1
        grid_position = grid_position + 1
        if des_position == 4:
            des_position = 0
        if grid_position == 4:
            grid_position = 0
        des = cross2[current][des_position]
        if des == -1 or map_grid[des]:
            continue
        map_grid[des] = des_grid[grid_position]
        build_cross(des, cross2, map_grid)


# 对路口进行排序，让未选路口距离已选路口的最短路径最长
def cross_sort(map_grid):
    x = 10000
    y = 10000
    c = -1
    for key in map_grid:
        if map_grid[key][0] <= x and map_grid[key][1] <= y:
            x = map_grid[key][0]
            y = map_grid[key][1]
            c = key
    cross_list = [c]
    unvisited = dict(zip(map_grid.keys(), [0 for n in range(len(map_grid))]))
    del unvisited[c]
    for i in range(len(map_grid)-1):
        len_max = 0
        current = -1
        for key in unvisited:
            x = map_grid[key][0]
            y = map_grid[key][1]
            length = 100000
            for c in cross_list:
                xx = map_grid[c][0]
                yy = map_grid[c][1]
                # l = numpy.sqrt(pow(x - xx, 2) + pow(y - yy, 2))
                l = abs(x-xx)+abs(y-yy)
                if l < length:
                    length = l
            if length > len_max:
                len_max = length
                current = key
        cross_list.append(current)
        del unvisited[current]
    return cross_list
