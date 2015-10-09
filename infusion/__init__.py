import functools
import itertools


# Item quality enum
class Quality:
    rare = 1
    legendary = 2
    exotic = 3


class Item():
    """Item wrapper to store light/quality properties"""

    def __init__(self, item, quality=None):
        """Extract light value and quality flag"""

        # Shortcut if quality flag is provided to streamline objects
        if quality is not None:
            self.quality = quality
            self.light = item
            return

        # Quality flag is based on '+' or '-' prefix or none
        if item[0] == '+':
            self.quality = Quality.exotic
        elif item[0] == '-':
            self.quality = Quality.rare
        else:
            self.quality = Quality.legendary

        # Make sure light is an integer
        try:
            # Light is rest of string if quality provided, else whole string
            self.light = int(item[1:]
                             if self.quality is not Quality.legendary
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
        """
        Infuse base item with target item

        exotic <- !exotic: <= 4 or 70%
          290 <- 298 = 296
          296 <- 300 = 300
          290 <- 295 = 294
        exotic <- exotic: <= 5 or 70%
          300 <- 310 = 307
          290 <- 310 = 304
        !exotic <- !exotic: <= 6 or 80%
          294 <- 300 = 300
          290 <- 295 = 295
        !exotic <- exotic: <= 7 or 80%
          299 <- 310 = 308
          293 <- 300 = 300
          298 <- 310 = 308
        """

        # Store difference in item light
        diff = target.light - base.light

        # Calculate close light range
        comp = (6 -
                (2 if base.quality is Quality.exotic else 0) +
                (1 if target.quality is Quality.exotic else 0))

        # Calculate far light percentage
        perc = 0.7 if base.quality is Quality.exotic else 0.8

        if diff <= comp:
            # No penalty, just return target light
            return target
        # Otherwise assess penalty
        else:
            # Resulting light is calculated percentage of the difference
            return Item(base.light + round(diff * perc), base.quality)

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

        # Get unique list of items to consider
        self.items = Paths.uniquify(self.base, items)

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
    def uniquify(base, items):
        """Get unique sorted list of Items, tossing items < base"""

        unique = [item for item in sorted(map(Item, set(items)),
                                          key=lambda item: item.light)
                  if item.light > base.light]

        # Bail if base is the highest light item provided
        if len(unique) == 0:
            raise Exception("Base item is highest light level")

        return unique

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
