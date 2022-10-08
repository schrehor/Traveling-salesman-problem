from math import sqrt, exp
from itertools import combinations
import copy
import random


class Node:
    def __init__(self, x, y):
        self.y = y
        self.x = x


class Path:
    def __init__(self, path, distance):
        self.path = path
        self.distance = distance


def calc_distance(node1, node2):
    """
    Vypocita vzdialenost dvoch miest s vyuzitim class Node

    :param node1: mesto 1
    :param node2: mesto 2
    :return: vzdialenost
    """
    return sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)


def calc_distance_tuple(x, y):
    """
    Vypocita vzdialenost dvoch miest s vyuzitim dat. struktory tuple

    :param x: x-ove suradnice
    :param y: y-ove suradnice
    :return: vzdialenost
    """
    return sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)


def create_dist_dict(group_nodes):
    """
    Ulozi vsetky vzdialenosti od vsetkych miest

    :param group_nodes: zoznam miest
    :return: zoznam vzdialenosti miest
    """
    distance = {}
    for node in group_nodes:
        node_distance = {}
        for compare_node in group_nodes:
            if node == compare_node:
                continue
            else:
                node_distance[compare_node.x, compare_node.y] = calc_distance(node, compare_node)
        distance[node.x, node.y] = node_distance

    return distance


def create_first_path(distance):
    """
    Vytvori prvu cestu

    :param distance: zoznam vzdialenosti miest
    :return: cesta a jej dlzka
    """
    path = []
    node = list(distance)[0]
    path.append(node)
    length = 0

    for index in range(len(distance)):
        if len(distance) == len(path):
            length += distance[path[len(path) - 1]][path[0]]
            break
        while range(1):
            closest = min(distance[node], key=distance[node].get)
            if closest not in path:
                path.append(closest)
                length += distance[node][closest]
                node = closest
                break
            else:
                del distance[node][closest]

    return path, length


def get_new_paths(path):
    """
    Generuje zoznam ciest z aktualneho s vyuzitim kombinacneho cisla

    :param path: aktualna cesta, s ktorou pracujem
    :return: zoznam ciest
    """
    new_paths = []

    path_comb = combinations(path, 2)
    for item in path_comb:
        path_curr = copy.deepcopy(path)
        index1 = path_curr.index(item[0])
        index2 = path_curr.index(item[1])
        path_curr[index1], path_curr[index2] = path_curr[index2], path_curr[index1]
        new_paths.append(path_curr)

    return new_paths

def get_random_path(path):
    """
    Vytvori nahodnu cestu z existujucej tym, ze vymeni dva nahodne prvky v zozname

    :param path: aktualna cesta
    :return: nova cesta
    """
    orig_path = copy.deepcopy(path)
    rand1, rand2 = random.choices(orig_path, k=2)
    index1 = orig_path.index(rand1)
    index2 = orig_path.index(rand2)
    orig_path[index1], orig_path[index2] = orig_path[index2], orig_path[index1]

    return orig_path


def get_len_path(path):
    """
    Vypocita dlzku jednej cesty

    :param path: cesta, ktorej dlzku chceme vypocitat
    :return: dlzku cesty
    """
    distance = 0

    for index_path in range(len(path)):
        distance += calc_distance_tuple(path[index_path], path[(index_path + 1) % len(path)])

    return distance


def get_new_len(new_paths, distance):
    """
    Vypocita vzdialenosti vsetkych ciest a zoradi ich vzostupne

    :param new_paths: zoznam novych ciest
    :param distance: zoznam vzdialenosti ciest
    :return: zoznam zoradenych ciest a zoznam vzdialenosti
    """
    length_and_nodes = [[] for i in range(len(new_paths))]
    sort_len = []
    sort_path = []

    for index_path in range(len(new_paths)):
        partial_length = 0
        for node_index in range(len(new_paths[index_path])):
            next_node = (node_index + 1) % len(new_paths[index_path])
            partial_length += distance[new_paths[index_path][node_index]][new_paths[index_path][next_node]]
        length_and_nodes[index_path] = [partial_length, new_paths[index_path]]


    length_and_nodes.sort()

    for item in length_and_nodes:
        sort_len.append(item[0])
        sort_path.append(item[1])


    return sort_path, sort_len


def tabu_search(first_path, path_len, distance, tabu_size, count_iter):
    """
    Vykona zakazane prehladavanie

    :param first_path: prva cesta
    :param path_len: dlzka prvej cesty
    :param distance: zoznam vzdialenosti miest
    :param tabu_size: maximalna velkost tabu tabulky
    :param count_iter: pocet iteracii v cykle
    :return: najlepsiu najdenu cestu a jej dlzku
    """
    current_path = Path(first_path, path_len)
    best_path = current_path
    tabu = [best_path.path]

    for iter in range(count_iter):
        new_paths = get_new_paths(current_path.path)
        sort_paths, new_len = get_new_len(new_paths, distance)

        paths = [Path(sort_paths[i], new_len[i]) for i in range(len(sort_paths))]

        for path in paths:
            if path.path not in tabu:
                current_path = path
                break

        if current_path.distance < best_path.distance:
            best_path = current_path

        tabu.append(current_path.path)
        if len(tabu) > tabu_size:
            tabu.pop(0)

    return best_path.path, best_path.distance


def sim_annealing(first_path, path_len, temperature, count_iter_outer, count_iter_inner):
    """
    Vykona simulovane zihanie

    :param first_path: prva cesta
    :param path_len: dlzka prvej cesty
    :param temperature: teplota
    :param count_iter_outer: pocet iteracii vonkajsieho cyklu
    :param count_iter_inner: pocet iteracii vnutorneho cyklu
    :return: najlepsiu cestu a jej dlzku
    """
    min_len = path_len
    min_path = first_path
    current_path = Path(first_path, path_len)

    for i in range(count_iter_outer):

        for j in range(count_iter_inner):
            new_path = get_random_path(current_path.path)
            new_len = get_len_path(new_path)

            if new_len < current_path.distance:
                current_path.path = new_path
                current_path.distance = new_len
            else:
                p = exp((current_path.distance - new_len) / temperature)
                r = random.random()
                if r < p:
                    current_path.path = new_path
                    current_path.distance = new_len
                    temperature *= 0.99

        if min_len > current_path.distance:
            min_len = current_path.distance
            min_path = current_path.path

        # vypis jednotlivych dlzok postupne
        print(current_path.distance)

    return min_path, min_len


def print_path(path, length):
    """
    Vypise celu cestu a jej dlzku

    :param path: najlepsia najdena cesta
    :param length: dlzka najlpsej cesty
    """
    print("Cesta ma dlzku", length)
    for line in path:
        print(line)



path20 = (Node(60, 200), Node(180, 200), Node(100, 180), Node(140, 180), Node(20, 160), Node(80, 160), Node(200, 160),
          Node(140, 140), Node(40, 120), Node(120, 120), Node(180, 100), Node(60, 80), Node(100, 80), Node(180, 60),
          Node(20, 40), Node(100, 40), Node(200, 40), Node(20, 20), Node(60, 20), Node(160, 20))

path30 = (Node(507, 230), Node(181, 235), Node(148, 183), Node(444, 666), Node(2300, 162), Node(87, 165), Node(258, 160),
          Node(840, 540), Node(400, 120), Node(720, 120), Node(180, 100), Node(600, 800), Node(100, 80), Node(180, 680),
          Node(200, 40), Node(100, 40), Node(200, 400), Node(20, 20), Node(608, 206), Node(173, 70), Node(500, 20),
          Node(1, 5), Node(177, 60), Node(73, 3300), Node(152, 41), Node(261, 450), Node(270, 240), Node(100, 234),
          Node(10, 10), Node(111, 222))


# Testovanie
name_test = path30

num_iter_tabu = 13
tabu_size = 4

num_iter_sim_anneal_out = 50
num_iter_sim_anneal_in = 50
temperature = 50

distance = create_dist_dict(name_test)
path, path_len = create_first_path(copy.deepcopy(distance))

# best_path, best_len = tabu_search(copy.deepcopy(path),
#                                   copy.deepcopy(path_len),
#                                   copy.deepcopy(distance),
#                                   tabu_size,
#                                   num_iter_tabu)
# print_path(best_path, best_len)
best_path, best_len = sim_annealing(copy.deepcopy(path),
                                    copy.deepcopy(path_len),
                                    temperature,
                                    num_iter_sim_anneal_out,
                                    num_iter_sim_anneal_in)
print_path(best_path, best_len)
