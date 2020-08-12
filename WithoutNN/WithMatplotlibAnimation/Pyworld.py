import numpy as np
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# import console


# setting up the values for the grid
ON = 255
OFF = 0
DIRT = 54
FOOD_ON = 24
vals = [ON, OFF]
population = dict()
food_pot = dict()
new_grid = np.array([])
death_count = 0
max_fitness = 0
max_energy = 0
p_low = 0.05
p_high = 1 - p_low
prob_rand_food_gen = 0.0005
parent_num = 2
daily_energy_perc_loss = 0.001
# energy needed proportionate to fitness
energy_perc_for_child = 0.8
perc_of_char_given = 0.7
mouse_side = "None"
pause = False
bomb_set = False
thanos_on = False
mass_food_on = False

# set day
year = 0
day = 0
hour = 0
hours_per_day = 24
days_per_year = 356
# set grid size
x = 150
y = 175
ix = -1
iy = -1


class UserAction:
    @staticmethod
    def onclick(event):
        global food_pot
        global ix, iy
        global mouse_side

        if str(event.button) == "MouseButton.LEFT":
            mouse_side = "Left"
            ix, iy = int(event.xdata), int(event.ydata)
            # print('x = %d, y = %d' % (ix, iy))

            food_pot[(iy, ix)] = random.randint(10, 20)

        elif str(event.button) == "MouseButton.RIGHT":
            mouse_side = "Right"
            ix, iy = int(event.xdata), int(event.ydata)
            # print('x = %d, y = %d' % (ix, iy))

    @staticmethod
    def key_event(event):
        # ctrl+p for something different
        if str(event.key) == "p":
            global pause
            pause = not pause

        elif str(event.key) == "b":
            global bomb_set
            bomb_set = not bomb_set

        elif str(event.key) == "t":
            global thanos_on
            thanos_on = True

        elif str(event.key) == "m":
            global mass_food_on
            mass_food_on = not mass_food_on

    @staticmethod
    def update_user_actions():
        global mouse_side
        global thanos_on
        global food_pot
        global ix, iy
        global death_count

        if mouse_side == "Left":
            if bomb_set:
                for row in range(-8, 9):
                    for col in range(-8, 9):
                        pos = (iy + col, ix + row)
                        if pos in population:
                            del population[pos]
                            new_grid[pos] = DIRT
                            death_count += 1
                        if pos in food_pot:
                            del food_pot[pos]
                            new_grid[pos] = DIRT

            if mass_food_on:
                for row in range(-4, 5):
                    for col in range(-4, 5):
                        pos = (iy + col, ix + row)
                        food_pot[pos] = random.randint(2, 10)
                        new_grid[pos] = FOOD_ON

            # if we did not just start the program, hence ix and iy would be -1 if we did
            # then add the food_pot to the new grid
            if not mass_food_on and not bomb_set:
                new_grid[(iy, ix)] = FOOD_ON

            ix, iy = -1, -1

        elif mouse_side == "Right":
            if (iy, ix) in population:
                fitness_number = population[(iy, ix)]
                selected_creature_id = (iy, ix)
                display_fitness = True

            # ix, iy = -1, -1

        if thanos_on:
            keys = []
            for key in population:
                keys.append(key)

            for pos in keys:
                if random.random() <= 0.5:
                    del population[pos]
                    new_grid[pos] = DIRT
                    death_count += 1

            thanos_on = False

        mouse_side = "None"


class CreatureAction:
    @staticmethod
    def generate_population(x, y):
        """returns a grid of NxN random values"""
        random_grid = np.random.choice(vals, x * y, p=[p_low, p_high]).reshape(x, y)
        for i in range(y):
            for j in range(x):
                if random_grid[j, i] == ON:
                    key = (j, i)
                    characterisitcs = []
                    # add fitness
                    characterisitcs.append(random.randint(10, 100))
                    # add energy
                    characterisitcs.append(random.randint(20, 50))
                    population[key] = characterisitcs

        return random_grid

    def generate_food(self, pos):
        food_pot[pos] = random.randint(2, 10)
        new_grid[pos] = FOOD_ON

    def update_by_hour(self, grid):
        global year
        global day
        global hour
        global death_count
        global new_grid
        global max_fitness
        global max_energy

        # copy food keys so we can edit the dictionary
        keys = []
        for key in food_pot:
            keys.append(key)

        # check all of the creatures to see if they reached food
        for food_loc in keys:
            for creature_loc in population:
                if food_loc == creature_loc:
                    # creature fitness is at index 0 and creature energy is at index 1
                    population[creature_loc][0] += food_pot[food_loc]
                    population[creature_loc][1] += food_pot[food_loc]
                    del food_pot[food_loc]
                    # since the creature is at the food location, simply turn it from food on to just on for the creature
                    # to now be displayed instead of the food
                    new_grid[food_loc] = ON

        for i in range(y):
            for j in range(x):

                # generate our food in this loop. We could generate it elsewhere, but it that would be n^2 + n^2 time
                # since it is a nested loop and we are doing it twice. Thus this was we are doing n^2 instead
                # also do not do a generate_food if condition else action because those are acutally a tiny tiny bit
                # slower. When it comes to lots of food and creatures, each nanosecond matters
                if random.random() <= prob_rand_food_gen:
                    self.generate_food((j, i))

                # compute 8-neighbor sum
                # using toroidal boundary conditions - x and y wrap around
                # so that the simulaton takes place on a toroidal surface.
                total = 0
                if grid[j, (i - 1) % y] == ON:
                    total += 1
                if grid[j, (i + 1) % y] == ON:
                    total += 1
                if grid[(j - 1) % x, i] == ON:
                    total += 1
                if grid[(j + 1) % x, i] == ON:
                    total += 1
                if grid[(j - 1) % x, (i - 1) % y] == ON:
                    total += 1
                if grid[(j - 1) % x, (i + 1) % y] == ON:
                    total += 1
                if grid[(j + 1) % x, (i - 1) % y] == ON:
                    total += 1
                if grid[(j + 1) % x, (i + 1) % y] == ON:
                    total += 1

                # create new creatures randomly next to the parent if there is the needed number of parents and
                # the energy is higher proportionally compared to the fitness of the creature at j, i
                # if the world is filling up to fast change the total == to a higher number so there must be a greater
                # of other creatures next to the creature for it to procreate
                if grid[j, i] == ON and total == parent_num and population[j, i][1] > population[j, i][0] * energy_perc_for_child:
                    new_key = 0
                    r = random.randint(0, 7)
                    if r == 0:
                        new_key = (j, (i - 1) % y)
                    if r == 1:
                        new_key = (j, (i + 1) % y)
                    if r == 2:
                        new_key = ((j - 1) % x, i)
                    if r == 3:
                        new_key = ((j + 1) % x, i)
                    if r == 4:
                        new_key = ((j - 1) % x, (i - 1) % y)
                    if r == 5:
                        new_key = ((j - 1) % x, (i + 1) % y)
                    if r == 6:
                        new_key = ((j + 1) % x, (i - 1) % y)
                    if r == 7:
                        new_key = ((j + 1) % x, (i + 1) % y)

                    key = (j, i)
                    parent = population[key]
                    parent_fitness = parent[0]
                    parent_energy = parent[1]
                    fitness_given = int(parent_fitness * perc_of_char_given)
                    energy_given = int(parent_energy * perc_of_char_given)
                    # create the child first and add some of the parent fitness/energy
                    child_fitness = parent_fitness + random.randint(-fitness_given, fitness_given)
                    child_energy = parent_energy + random.randint(-energy_given, energy_given)
                    child = [child_fitness, child_energy]
                    # remove fitness from parent even if child does not make it
                    parent_fitness -= fitness_given
                    parent_energy -= energy_given
                    population[key] = [parent_fitness, parent_energy]
                    if new_key in population:
                        # get creature at new_key as thats the position the child will go to
                        other = population[new_key]
                        # fitness is at position 0
                        other_fitness = other[0]
                        if child_fitness > other_fitness:
                            # keep the key as the key does not change, but change the fitness as that does
                            population[new_key] = child
                            death_count += 1
                        # else, if other fitness is greater than child fitness than do nothing as other stays there and
                        # child dies, hence not added to board but forgotten
                    else:
                        # if there is not another creature there add the child to the population and to the new grid
                        population[new_key] = child
                        new_grid[new_key] = ON

        # have the creatures move about the world
        keys = []
        max_fitness = 0
        max_energy = 0
        for key in population:
            # fitness is at index 0 and energy is at index 1
            creature_fitness = population[key][0]
            creature_energy = population[key][1]
            if creature_fitness > max_fitness:
                max_fitness = creature_fitness
            if creature_energy > max_energy:
                max_energy = creature_energy
            keys.append(key)

        for key in keys:
            r = random.randint(0, 7)
            new_key = 0
            j = key[0]
            i = key[1]
            if r == 0:
                new_key = (j, (i - 1) % y)
            elif r == 1:
                new_key = (j, (i + 1) % y)
            elif r == 2:
                new_key = ((j - 1) % x, i)
            elif r == 3:
                new_key = ((j + 1) % x, i)
            elif r == 4:
                new_key = ((j - 1) % x, (i - 1) % y)
            elif r == 5:
                new_key = ((j - 1) % x, (i + 1) % y)
            elif r == 6:
                new_key = ((j + 1) % x, (i - 1) % y)
            elif r == 7:
                new_key = ((j + 1) % x, (i + 1) % y)

            original_creature = population[key]
            final_alive_creature = []
            if new_key in population:
                original_creature_fitness = original_creature[0]
                challenger_creature = population[new_key]
                challenger_creature_fitness = challenger_creature[0]
                if original_creature_fitness < challenger_creature_fitness:
                    # if the challenger is fitter than the creature currently at the position then set the final alive
                    # creature to the challenger
                    # remove daily energy
                    challenger_creature[1] = challenger_creature[1] * daily_energy_perc_loss
                    final_alive_creature = challenger_creature
                # add to the death count as regardless one creature will die if there are two creatures fighting for a
                # position
                else:
                    final_alive_creature = original_creature
                death_count += 1

            else:
                # if the new creature does not meet another creature when moving then del old and replace creature at
                # new position
                del population[key]
                # remove daily energy
                original_creature[1] -= original_creature[1] * daily_energy_perc_loss
                final_alive_creature = original_creature
                new_grid[key] = DIRT

            # take the final alive creature and check if its energy is at or below 0, if so, kill it
            final_alive_creature_energy = final_alive_creature[1]
            if final_alive_creature_energy > 0:
                population[new_key] = final_alive_creature
                # set the new grid at the new key on if the creature lives, because if it does not then its old position
                # will be deleted and turned off, and the new position will not be added to population of the new grid
                new_grid[new_key] = ON
            else:
                death_count += 1

        # hour completed, so add to hour count
        hour += 1
        if hour % hours_per_day == 0:
            day += 1
            hour = 0
        if day != 0 and day % days_per_year == 0:
            year += 1
            day = 0


class Display:
    def __init__(self):
        self.creature_action = CreatureAction()
        self.user_action = UserAction()

    @staticmethod
    def display_info(img, fitness_number, selected_creature_id, display_fitness):
        # update data
        # print(f"Alive: {len(population)}\tDeath Count: {death_count}")
        plt.suptitle(f"Y:D:H: {year}:{day}:{hour} - Alive: {len(population):,} - Death Count: {death_count:,}", fontsize=11)
        if display_fitness:
            plt.xlabel(f"CreatureAction {selected_creature_id} Fitness: {fitness_number}", fontsize=11)
        else:
            plt.xlabel(f"Max Fitness: {max_fitness} - Max Energy: {round(max_energy, 1)}", fontsize=10)
        img.set_data(new_grid)

    def update(self, frameNum, fig, img, grid):
        global new_grid

        fitness_number = 0
        selected_creature_id = (-1, -1)
        display_fitness = False

        # copy grid since we require 8 neighbors
        # for calculation and we go line by line
        new_grid = grid.copy()
        self.creature_action.update_by_hour(grid) if not pause else None

        fig.canvas.mpl_connect('button_press_event', self.user_action.onclick)
        fig.canvas.mpl_connect('key_press_event', self.user_action.key_event)
        self.user_action.update_user_actions()

        self.display_info(img, fitness_number, selected_creature_id, display_fitness)
        grid[:] = new_grid[:]

        return img,


def main():
    creature = CreatureAction()
    display = Display()

    # set animation update interval
    updateInterval = 1

    # declare grid
    grid = creature.generate_population(x, y)

    # set up animation
    # count = 0
    fig, ax = plt.subplots()
    img = ax.imshow(grid, interpolation='nearest')
    # show animation
    count = 0
    while True:
        # show animation
        ani = animation.FuncAnimation(fig, display.update, fargs=(fig, img, grid,), frames=10, interval=updateInterval,
                                      save_count=50)

        plt.show()

        if count == 100:
            # console.clear()
            count = 0

        count += 1


# call main
if __name__ == '__main__':
    main()