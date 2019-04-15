import re


def read_data(path):
    data = {}
    f = open(path, 'r')
    f.readline()
    for line in f:
        pattern = re.compile(r'(-?[\d]+)')
        result = pattern.findall(line)
        result = [int(x) for x in result]
        data[result[0]] = result[1:]
    f.close()
    return data


# 读取preset_answer.txt
def read_preset_answer(path):
    data = dict(zip(range(1, 350), [{} for n in range(1, 350)]))
    f = open(path, 'r')
    f.readline()
    for line in f:
        pattern = re.compile(r'(-?[\d]+)')
        result = pattern.findall(line)
        result = [int(x) for x in result]
        if result[1] not in data:
            data[result[1]] = {}
        data[result[1]][result[0]] = result[2:]
    f.close()
    delete = []
    for t in data:
        if not len(data[t]):
            delete.append(t)
    for i in range(len(delete)):
        del data[delete[i]]
    return data


def read_all_data(car_path, road_path, cross_path, preset_answer_path):
    car = read_data(car_path)
    road = read_data(road_path)
    cross = read_data(cross_path)
    preset_answer = read_preset_answer(preset_answer_path)
    return car, road, cross, preset_answer


def write_data(answer, answer_path):
    f = open(answer_path, 'w')
    for key in answer:
        f.write("("+str(key)+','+str(answer[key][3]))
        for i in range(0, len(answer[key][2])):
            f.write(','+str(answer[key][2][i]))
        f.write(')\n')
    f.close()
