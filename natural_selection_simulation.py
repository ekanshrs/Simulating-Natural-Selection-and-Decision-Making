import random
import math
import matplotlib.pyplot as plt

class Environment:
    def __init__(self, width=100, height=100, num_food_particles=500):
        self.width = width
        self.height = height
        self.grid = [[None for _ in range(width)] for _ in range(height)]
        self.food_particles = self.place_food(num_food_particles)

    def place_food(self, num_food_particles):
        food_positions = []
        for _ in range(num_food_particles):
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            self.grid[y][x] = 'food'
            food_positions.append((x, y))
        return food_positions

    def is_food(self, x, y):
        return self.grid[y][x] == 'food'

    def remove_food(self, x, y):
        if self.is_food(x, y):
            self.grid[y][x] = None

class Organism:
    def __init__(self, id, mass=None, speed=None, sense=None, x=None, y=None, energy=500):
        self.id = id
        self.mass = mass if mass is not None else random.randint(1, 5)
        self.speed = speed if speed is not None else random.randint(1, 5)
        self.sense = sense if sense is not None else random.randint(1, 5)
        self.energy = energy
        self.x = x if x is not None else -1
        self.y = y if y is not None else -1
        self.at_home = True
        self.has_eaten = False

    def move_towards(self, environment, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        if dx == 0 and dy == 0:
            return
        if abs(dx) >= self.speed:
            if dx > 0:
                self.x += self.speed
                self.x = min(environment.width-1,self.x)
            else:
                self.x -= self.speed
                self.x = max(0,self.x)
        else:
            self.x += dx
            left = self.speed - dx
            if dy >= 0:
                self.y += min(left, dy)
                self.y = min(environment.height-1,self.y)
            else:
                self.y -= min(left, -dy)
                self.y = max(0,self.y)
        # self.x = max(0, min(environment.width - 1, self.x + move_x))
        # self.y = max(0, min(environment.height - 1, self.y + move_y))
        self.consume_energy()

    def random_move(self, environment):
        move_x = random.randint(-self.speed, self.speed)
        move_y = random.randint(-self.speed, self.speed)
        self.x = max(0, min(environment.width - 1, self.x + move_x))
        self.y = max(0, min(environment.height - 1, self.y + move_y))
        self.consume_energy()

    def consume_energy(self):
        self.energy -= self.mass*self.speed**2 + self.sense

    def is_alive(self):
        return self.energy > 0

def handle_collisions(organisms):
    position_map = {}
    for organism in organisms:
        if not organism.is_alive():
            continue
        pos = (organism.x, organism.y)
        if pos not in position_map:
            position_map[pos] = []
        position_map[pos].append(organism)
    
    for organisms_at_pos in position_map.values():
        if len(organisms_at_pos) > 1:
            organisms_at_pos.sort(key=lambda o: o.mass, reverse=True)
            largest_organism = organisms_at_pos[0]
            for other_organism in organisms_at_pos[1:]:
                largest_organism.energy += other_organism.mass * 10  # Gain energy from consuming
                other_organism.energy = 0  # The consumed organism dies
                other_organism.mass = 0

def run_daily_simulation(environment, organisms):
    for organism in organisms:
        if not organism.is_alive():
            continue
        while organism.is_alive() and not organism.has_eaten:
            food_found = False
            for dx in range(-organism.sense, organism.sense + 1):
                for dy in range(-organism.sense, organism.sense + 1):
                    if 0 <= organism.x + dx < environment.width and 0 <= organism.y + dy < environment.height:
                        if environment.is_food(organism.x + dx, organism.y + dy):
                            organism.move_towards(environment, organism.x + dx, organism.y + dy)
                            if organism.x == organism.x + dx and organism.y == organism.y + dy:
                                organism.has_eaten = True
                                environment.remove_food(organism.x, organism.y)
                                food_found = True
                                break
                if food_found:
                    break
            if not food_found:
                organism.random_move(environment)
            organism.consume_energy()
            if not organism.is_alive():
                break
        if organism.is_alive() and organism.has_eaten:
            # Move back to home (border)
            home_x, home_y = random.choice(border_positions)
            while (organism.x, organism.y) != (home_x, home_y):
                organism.move_towards(environment, home_x, home_y)
                organism.consume_energy()
                if not organism.is_alive():
                    break

def reproduce(organism):
    new_mass = max(1, min(5, organism.mass + random.choice([-1, 0, 1])))
    new_speed = max(1, min(5, organism.speed + random.choice([-1, 0, 1])))
    new_sense = max(1, min(5, organism.sense + random.choice([-1, 0, 1])))
    return Organism(id=organism.id + 100, mass=new_mass, speed=new_speed, sense=new_sense)

def initialize_organisms(num_organisms):
    organisms = []
    for i in range(num_organisms):
        organism = Organism(id=i)
        organisms.append(organism)
    return organisms

def place_organisms_on_border(environment, organisms):
    global border_positions
    border_positions = []
    for x in range(environment.width):
        border_positions.append((x, 0))
        border_positions.append((x, environment.height - 1))
    for y in range(1, environment.height - 1):
        border_positions.append((0, y))
        border_positions.append((environment.width - 1, y))
    for organism in organisms:
        x, y = random.choice(border_positions)
        organism.x, organism.y = x, y

def collect_data(organisms):
    mass_counts = [0] * 5
    speed_counts = [0] * 5
    sense_counts = [0] * 5

    for organism in organisms:
        if organism.is_alive():
            mass_counts[organism.mass - 1] += 1
            speed_counts[organism.speed - 1] += 1
            sense_counts[organism.sense - 1] += 1

    return mass_counts, speed_counts, sense_counts

def simulate(num_days, num_organisms=100):
    environment = Environment()
    organisms = initialize_organisms(num_organisms)
    place_organisms_on_border(environment, organisms)
    
    mass_progression = []
    speed_progression = []
    sense_progression = []

    for day in range(num_days):
        print(f"Day {day + 1}")
        run_daily_simulation(environment, organisms)
        handle_collisions(organisms)
        new_organisms = []
        for organism in organisms:
            if organism.is_alive() and organism.has_eaten:
                new_organisms.append(reproduce(organism))
            organism.energy = 500  # Replenish energy for the next day
        organisms.extend(new_organisms)
        
        mass_counts, speed_counts, sense_counts = collect_data(organisms)
        mass_progression.append(mass_counts)
        speed_progression.append(speed_counts)
        sense_progression.append(sense_counts)
        print_organisms(organisms)

    return mass_progression, speed_progression, sense_progression

def print_organisms(organisms):
    for organism in organisms:
        print(f"Organism {organism.id}: Mass={organism.mass}, Speed={organism.speed}, Sense={organism.sense}, Energy={organism.energy}, Alive={organism.is_alive()}")

def plot_progression(mass_progression, speed_progression, sense_progression):
    days = range(1, len(mass_progression) + 1)
    
    plt.figure(figsize=(18, 6))

    plt.subplot(1, 3, 1)
    for i in range(5):
        plt.plot(days, [mass[i] for mass in mass_progression], label=f'Mass {i+1}')
    plt.xlabel('Day')
    plt.ylabel('Number of Organisms')
    plt.title('Mass Progression')
    plt.legend()

    plt.subplot(1, 3, 2)
    for i in range(5):
        plt.plot(days, [speed[i] for speed in speed_progression], label=f'Speed {i+1}')
    plt.xlabel('Day')
    plt.ylabel('Number of Organisms')
    plt.title('Speed Progression')
    plt.legend()

    plt.subplot(1, 3, 3)
    for i in range(5):
        plt.plot(days, [sense[i] for sense in sense_progression], label=f'Sense {i+1}')
    plt.xlabel('Day')
    plt.ylabel('Number of Organisms')
    plt.title('Sense Progression')
    plt.legend()

    plt.tight_layout()
    plt.show()

# Run the simulation for 10 days
mass_progression, speed_progression, sense_progression = simulate(10)

# Plot the progression
plot_progression(mass_progression, speed_progression, sense_progression)
