import numpy as np
import matplotlib.pyplot as plt

from argparse import ArgumentParser

from workplace import *

def parse_args():
    parser = ArgumentParser(description='Specify Input/Output')
    parser.add_argument('-i', '--input', default='frustration_low_good.json', type=str,
                        help='Specify the name of the input file.')
    parser.add_argument('-o', '--output', default='p', type=str,
                        help='Specify the desired output (p = performance, f = frustration).')
    return parser.parse_args()

def main():
    args = parse_args()
    
    input_file = '../IO/inputs/' + args.input

    my_workplace = Workplace(input_file, verbose=False)

    print("The input for the first experiment has been successfully loaded.")

    print("Processing tasks...")

    my_workplace.process_tasks()

    print("Tasks processed!")

    print("\nCreating outputs...")

    if args.output == 'p':
        my_workplace.plot_performance_matplotlib()
    elif args.output == 'f':
        my_workplace.plot_frustration_matplotlib()
    else:
        print("Unknown output format!")

    print("Outputs created! Feel free to close them to terminate the program.")
    plt.show()

if __name__ == '__main__':
    main()