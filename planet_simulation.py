import pygame
import math

pygame.init()

# constants needed for pygame module
WIDTH, HEIGHT = 1300, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (226, 11, 26)
DARK_RED = (129, 29, 29)
ROSE = (218, 147, 197)

FONT = pygame.font.SysFont('comicsans', 18)


class Planet:
    AU = 149.6e6 * 1000  # Astronomic unit - distance Sun-Earth (149.6 million of km) expressed in meters
    G = 6.67428e-11  # Gravitational constant
    SCALE = 200 / AU  # Scaling solar system to fit in the simulation window
    TIMESTEP = 3600 * 24  # Time passed for each frame updating -> 1 day = 1 frame

    def __init__(self, x, y, radius, color, mass):
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0

    def draw(self, win):  # Draws the planet on the screen
        x = self.x * self.SCALE + WIDTH / 2  # point (0,0) is on upper left corner of the screen, so we center
        y = self.y * self.SCALE + HEIGHT / 2

        # draws the orbit line
        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                a, b = point
                a = a * self.SCALE + WIDTH / 2
                b = b * self.SCALE + HEIGHT / 2
                updated_points.append((a, b))

            pygame.draw.lines(win, self.color, False, updated_points, 2)

        pygame.draw.circle(win, self.color, (x, y), self.radius)

        # draws the km from the sun
        if not self.sun:
            distance_text = FONT.render(f'{round(self.distance_to_sun/1e9, 1)} 10^6 km', True, WHITE)
            win.blit(distance_text, (x - distance_text.get_width()/2, y - distance_text.get_height()/2))

    def attraction(self, other):  # Calculates the force of attraction between self and other
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_x**2 + distance_y**2)

        if other.sun:
            self.distance_to_sun = distance

        force = self.G * self.mass * other.mass / distance**2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):  # Updates the position of self based on force of attraction from other planets
        total_fx = 0
        total_fy = 0
        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))


# pygame module initialization
def main():
    run = True
    clock = pygame.time.Clock()

    # planets creation
    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30)
    sun.sun = True

    earth = Planet(-1*Planet.AU, 0, 16, BLUE, 5.9742 * 10**24)
    earth.y_vel = 29.783 * 1000

    mars = Planet(-1.534*Planet.AU, 0, 12, RED, 6.39 * 10**23)
    mars.y_vel = 24.077 * 1000

    mercury = Planet(0.387*Planet.AU, 0, 8, DARK_RED, 3.30 * 10**23)
    mercury.y_vel = -47.4 * 1000

    venus = Planet(0.723*Planet.AU, 0, 14, ROSE, 4.8685 * 10**24)
    venus.y_vel = -35.02 * 1000

    planets = [sun, earth, mars, mercury, venus]

    while run:  # infinite loop (until we press exit) that runs the simulation
        clock.tick(60)
        WIN.fill((0, 0, 0))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)

        pygame.display.update()

    pygame.quit()


main()
