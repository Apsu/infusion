import functools
import itertools


# Item rarity enum
class Rarity:
    rare = 1
    legendary = 2
    exotic = 3


class Item():
    """Item wrapper to store light/rarity properties"""

    def __init__(self, item, rarity=None):
        """Extract light value and rarity flag"""

        # Shortcut if rarity flag is provided to streamline objects
        if rarity is not None:
            self.rarity = rarity
            self.light = item
            return

        # Rarity flag is based on '+' or '-' prefix or none
        if item[0] == '+':
            self.rarity = Rarity.exotic
        elif item[0] == '-':
            self.rarity = Rarity.rare
        else:
            self.rarity = Rarity.legendary

        # Make sure light is an integer
        try:
            # Light is rest of string if rarity provided, else whole string
            self.light = int(item[1:]
                             if self.rarity is not Rarity.legendary
                             else item)
        # If item is not an integer
        except ValueError as e:
            raise Exception("Invalid item {}; items must be integers.".format(
                str(e).split()[-1]))

    def __repr__(self):
        return self.light

    def __str__(self):
        return str(self.light)


class Path():
    """Path wrapper to store light/cost/path properties"""

    # Legendary Mark cost per infusion
    COST = 3

    # Class function
    def infuse(base, target):
        """Infuse base item with target item"""

        # Store difference in item light
        diff = target.light - base.light

        # Calculate close light range
        comp = 4 if base.rarity is Rarity.exotic else 6

        # Calculate far light percentage
        perc = 0.7 if base.rarity is Rarity.exotic else 0.8

        if diff <= comp:
            # No penalty, result is target light
            return Item(target.light, base.rarity)
        # Otherwise assess penalty
        else:
            # Result is half-even rounded percentage of difference plus base
            return Item(base.light + round(diff * perc), base.rarity)

    def __init__(self, steps):
        # Store steps and calculate cost
        self.steps = steps
        self.cost = (len(steps) - 1) * Path.COST

        # Store path reduction by chaining infusions
        self.item = functools.reduce(Path.infuse, steps)

        # Store reduced light directly for convenience
        self.light = self.item.light


class Paths():
    """Class wrapper to store multiple Path objects"""

    def __init__(self, base, items):
        # Store base item
        self.base = Item(base)

        # Get pruned list of items to consider
        self.items = Paths.prune(self.base, items)

        # Store target and inbetween items
        self.target = self.items[-1]
        self.others = self.items[:-1]

        # Get permutations
        perms = Paths.permutate(self.base, self.others, self.target)

        # Walk each path and store results, sorted by light result
        self.paths = sorted([Path(perm) for perm in perms],
                            key=lambda path: path.light)

        # Initialize best-light/least-cost with first path
        self.best_light = self.least_cost = self.paths[0]

        # For each path
        for path in self.paths:
            # If light is best we've seen, or same light but least cost
            if (path.light > self.best_light.light or
                    (path.light == self.best_light.light and
                     path.cost < self.best_light.cost)):
                # Store it
                self.best_light = path

            # If cost is least we've seen, or same cost but best light
            if (path.cost < self.least_cost.cost or
                    (path.cost == self.least_cost.cost and
                     path.light > self.least_cost.light)):
                # Store it
                self.least_cost = path

    # Class functions
    def prune(base, items):
        """Get sorted list of Items, tossing items < base"""

        pruned = [item for item in sorted(map(Item, items),
                                          key=lambda item: item.light)
                  if item.light > base.light]

        # Bail if base is the highest light item provided
        if len(pruned) == 0:
            raise Exception("Base item is highest light level")

        return pruned

    def permutate(low, mid, high):
        """
        Calculate permutations

        <- low:1, mid: 2 3, high:5
        1 5
        1 2 5
        1 3 5
        1 2 3 5
        """

        # Initialize permutations
        perms = [[low, high]]

        # For each sublist of middle values
        for l in range(1, len(mid) + 1):
            # For each permutation of sublist
            for perm in itertools.combinations(mid, l):
                # Store [low, permutation, high] list
                perms.append(list(itertools.chain([low], perm, [high])))

        return perms
