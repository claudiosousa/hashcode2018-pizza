from math import *
from pprint import pprint
import random
import itertools
from collections import Counter, defaultdict
import sys

PLOT = False
INITIAL_STATES = 50
ENLARGE_VARIANTS = 100


def run():
    [R, C, MIN, MAX] = map(int, input().split())
    lines = []  # True => Tomato, False => Mushroom
    for _ in range(R):
        lines.append(list(c == 'T' for c in list(input())))

    def get_possible_slices():
        possible_slices = []
        for i in range(R):
            for j in range(C):
                possible_slices += get_cell_possible_slices(i, j)
        return possible_slices

    def get_cell_possible_slices(i, j):
        min_size = MAX
        res = []

        cols_t = [0] * (MAX + 1)
        cols_m = [0] * (MAX + 1)
        for y in range(min(R - i, MAX + 1)):
            t = 0
            m = 0
            for x in range(min(C - j, MAX + 1)):
                t += cols_t[x]
                m += cols_m[x]
                size = (x + 1) * (y + 1)
                if size > min_size:
                    break
                if lines[i + y][j + x]:
                    t += 1
                    cols_t[x] += 1
                else:
                    m += 1
                    cols_m[x] += 1
                if t >= MIN and m >= MIN:
                    if size < min_size:
                        res = []
                        min_size = size
                    res.append([(i, j, y, x)])
                    break
        return res

        # def get_all_possible_slices(i, j):
        #     cols_t = [0] * (MAX + 1)
        #     cols_m = [0] * (MAX + 1)
        #     for y in range(min(R - i, MAX + 1)):
        #         t = 0
        #         m = 0
        #         for x in range(min(C - j, MAX + 1)):
        #             t += cols_t[x]
        #             m += cols_m[x]
        #             size = (x + 1) * (y + 1)
        #             if size > MAX:
        #                 break
        #             if lines[i + y][j + x]:
        #                 t += 1
        #                 cols_t[x] += 1
        #             else:
        #                 m += 1
        #                 cols_m[x] += 1
        #             if t >= MIN and m >= MIN:
        #                 yield [(i, j, y, x)]

    def get_possible_solutions(possible_slices):
        collisions = [[0] * C for _ in range(R)]
        for pos in possible_slices:
            (i, j, y, x) = pos[0]
            for k in range(y + 1):
                for l in range(x + 1):
                    collisions[i + k][j + l] += 1

        # plt.imshow(collisions, cmap='hot')
        # plt.show(collisions)

        for pos in possible_slices:
            (i, j, y, x) = pos[0]
            col = 0
            for k in range(y + 1):
                for l in range(x + 1):
                    col += collisions[i + k][j + l] - 1
            pos.append(col)

        while True:
            random.shuffle(possible_slices)
            possible_slices.sort(key=lambda s: (s[1], MAX - (s[0][2] + 1) * (s[0][3] + 1)))

            collisions = [[False] * C for _ in range(R)]
            slices = []
            for pos_slide, _ in possible_slices:
                (i, j, y, x) = pos_slide
                for k in range(y + 1):
                    for l in range(x + 1):
                        if collisions[i + k][j + l]:
                            break
                    else:
                        continue
                    break
                else:
                    for k in range(y + 1):
                        for l in range(x + 1):
                            collisions[i + k][j + l] = True
                    slices.append(pos_slide)
            yield slices, collisions

    def display_solution(solution):
        pizza = [[0] * C for _ in range(R)]
        for m, pos in enumerate(solution):
            (i, j, y, x) = pos
            for k in range(y + 1):
                for l in range(x + 1):
                    pizza[i + k][j + l] = m + 1
        plt.matshow(pizza)
        plt.title('Solution: ' + str(surface(solution)))

    def surface(solution):
        return sum((s[2] + 1) * (s[3] + 1) for s in solution)

    def enlarge_compact_solution(solution, occupied):
        dirs = [1, 2, 3, 4]
        while True:
            random.shuffle(solution)
            sol = solution[:]
            occ = [r[:] for r in occupied]
            for slice_pos, slic in enumerate(sol):
                random.shuffle(dirs)
                enlarged = True
                slice_size = (slic[2] + 1) * (slic[3] + 1)
                while enlarged:
                    enlarged = False
                    for d in dirs:
                        vertical = d % 2
                        neg = d <= 2
                        length = slic[2 + vertical] + 1
                        if length + slice_size > MAX:
                            continue
                        start = slic[vertical]
                        pos = slic[1 - vertical] - 1 if neg else slic[1 - vertical] + slic[3 - vertical] + 1
                        if pos < 0 or vertical and pos >= R or not vertical and pos >= C:
                            continue
                        for i in range(length):
                            if not vertical and occ[start + i][pos] or vertical and occ[pos][start + i]:
                                break
                        else:
                            for i in range(length):
                                if vertical:
                                    occ[pos][start + i] = True
                                else:
                                    occ[start + i][pos] = True
                            slice_size += length
                            if neg:
                                if vertical:
                                    slic = (slic[0] - 1, slic[1], slic[2] + 1, slic[3])
                                else:
                                    slic = (slic[0], slic[1] - 1, slic[2], slic[3] + 1)
                            else:
                                if vertical:
                                    slic = (slic[0], slic[1], slic[2] + 1, slic[3])
                                else:
                                    slic = (slic[0], slic[1], slic[2], slic[3] + 1)
                            sol[slice_pos] = slic
                            enlarged = True
            yield sol

    def print_result(sol):
        print(len(best))
        for slic in sol:
            print(slic[0], slic[1], slic[0] + slic[2], slic[1] + slic[3])

    possible_slices = get_possible_slices()
    #pprint(possible_slices)

    best_surface = 0
    best = None
    for i, (compact_sol, occupied) in enumerate(
            itertools.islice(get_possible_solutions(possible_slices), INITIAL_STATES)):
        print('Run: ' + str(i), file=sys.stderr)
        for solution in itertools.islice(enlarge_compact_solution(compact_sol, occupied), ENLARGE_VARIANTS):
            s = surface(solution)
            if s > best_surface:
                best_surface = s
                best = solution
                print('Result: ' + str(best_surface), file=sys.stderr)

    if PLOT:
        import matplotlib.pyplot as plt
        plt.matshow(lines)
        display_solution(best)
        plt.show()

    print_result(best)
    print('Result: ' + str(best_surface), file=sys.stderr)


if __name__ == '__main__':
    run()
