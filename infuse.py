#!/usr/bin/env python3

import argparse
from infusion import Paths, Quality


# ANSI color enum
class Color:
    black = '\033[0;30m'   # Black
    red = '\033[0;31m'     # Red
    green = '\033[0;32m'   # Green
    yellow = '\033[0;33m'  # Yellow
    blue = '\033[0;34m'    # Blue
    purple = '\033[0;35m'  # Purple
    cyan = '\033[0;36m'    # Cyan
    white = '\033[0;37m'   # White
    term = '\033[0m'       # Terminator


def printc(string, color=Color.white):
    """Print string with ANSI color escape codes"""

    print("{}{}{}".format(color, string, Color.term))


def render(item):
    """Render light with color based on quality"""

    if not hasattr(item, 'quality'):
        color = Color.red
    elif item.quality is Quality.rare:
        color = Color.cyan
    elif item.quality is Quality.exotic:
        color = Color.yellow
    else:  # item.quality is Quality.legendary
        color = Color.purple

    return "{}{}{}".format(color, item, Color.term)


def calculate(args):
    """Calculate infusion paths"""

    # Initialize paths
    try:
        paths = Paths(args.base, args.items)
    except Exception as e:
        printc("Error initializing paths: {}".format(e), Color.red)
        exit(2)

    printc("Possible infusion paths", Color.green)

    # Iterate over results
    for path in paths.paths:
        # Print each possible path
        printc('Light: {}, Marks: {}, Infusion: {}'.format(
            render(path.item),
            render(path.cost),
            ' <- '.join(map(render, path.steps))),
            Color.white)

    # Get bests
    best_light = paths.best_light
    least_cost = paths.least_cost

    # Show best light, but least marks
    print()
    printc('Best light with least marks', Color.green)
    printc('Light: {}, Marks: {}, Infusion: {}'.format(
        render(best_light.item),
        render(best_light.cost),
        ' <- '.join(map(render, best_light.steps))),
        Color.white)

    # Show least marks, but best light
    print()
    printc('Least marks with best light', Color.green)
    printc('Light: {}, Marks: {}, Infusion: {}'.format(
        render(least_cost.item),
        render(least_cost.cost),
        ' <- '.join(map(render, least_cost.steps))),
        Color.white)

# Entry point
if __name__ == '__main__':
    # Initialize the argument parser
    parser = argparse.ArgumentParser(
        description='Calculates infusion paths, '
                    'showing costs and final light.',
        epilog="""
            At least two items are required -- the base item and one other
            item -- but multiple items can be provided in any order; duplicates
            will be pruned. The base item should be the lowest light, any other
            items with lower light than the base will be discarded. The highest
            light item is considered the target. All infusion paths from base
            to target will be calculated.\n
        """)

    # Add some args
    parser.add_argument('-v', '--version', action='version', version='1.0')
    parser.add_argument('base', metavar='BASE', help='integer light level of '
                        'base item to infuse (ex: 200, +200 for exotic, -200 '
                        'for rare)')
    parser.add_argument('items', metavar='ITEM', nargs='+', help='integer '
                        'light level of other item to consider (ex: 220, '
                        '+220 for exotic, -220 for rare)')

    # Do the needful
    calculate(parser.parse_args())
