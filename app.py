input_file = open('data/example.in', "r")

import solver
solver.input = input_file.readline
solver.run()
