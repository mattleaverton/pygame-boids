import math
import pygame
from random import randrange
from typing import List


class Boid(object):
    def __init__(self, position: tuple, velocity: tuple = (0.0, 0.0)):
        self.position = position
        self.velocity = velocity
        self.color = (randrange(0, 255), randrange(0, 255), randrange(0, 255))
        self.avoid_radius = 10
        self.align_radius = 50
        self.approach_radius = 100

    def __str__(self):
        x, y = self.position
        v_x, v_y = self.velocity
        return f"Boid | Position ({x:.1f}, {y:.1f}) | Velocity ({v_x:.1f}, {v_y:.1f})"

    def __repr__(self):
        x, y = self.position
        v_x, v_y = self.velocity
        return f"Boid | Position ({x:.1f}, {y:.1f}) | Velocity ({v_x:.1f}, {v_y:.1f})"


def initialize_positions(number: int, dimensions: tuple) -> List[Boid]:
    boids = []
    for idx in range(number):
        boids.append(Boid((randrange(dimensions[0]), randrange(dimensions[1]))))
    return boids


def draw_boids(screen: pygame.Surface, boids: List[Boid]):
    dim = (6, 6)
    for b in boids:
        point_center = (b.position[0] - dim[0] / 2.,
                        b.position[1] - dim[1] / 2.)
        pygame.draw.rect(screen, b.color, pygame.Rect(point_center[0], point_center[1], dim[0], dim[1]))


def rule1(idx: int, boids: List[Boid], strength: float = 1.0) -> tuple:
    """
    Seek center of all boids. Default move 1% of distance between target boid and center.

    idx - index of the target boid for the rule
    boids - all boids in system
    strength - 1.0 for max strength (1% of distance)
    """
    center_x = 0.0
    center_y = 0.0
    center_boids = 0
    target = boids[idx]
    for jdx, b in enumerate(boids):
        if idx != jdx:
            if math.dist(target.position, b.position) < target.approach_radius:
                center_x += b.position[0]
                center_y += b.position[1]
                center_boids += 1
    if center_boids > 1:
        center_x /= (center_boids - 1)
        center_y /= (center_boids - 1)

        x = (center_x - boids[idx].position[0]) / 100.0
        y = (center_y - boids[idx].position[1]) / 100.0
    else:
        x = y = 0.0
    return strength * x, strength * y


def rule2(idx: int, boids: List[Boid], strength=1.0) -> tuple:
    """ Flee nearby objects (collision avoidance) """
    x = 0.0
    y = 0.0

    for jdx, b in enumerate(boids):
        if idx != jdx:
            d = abs(math.dist(boids[idx].position, boids[jdx].position))
            if d < boids[idx].avoid_radius:
                x = x - (boids[jdx].position[0] - boids[idx].position[0])
                y = y - (boids[jdx].position[1] - boids[idx].position[1])

    return strength * x, strength * y


def rule3(idx: int, boids: List[Boid], strength=1.0) -> tuple:
    """ Match velocity with nearby boids """
    center_x = 0.0
    center_y = 0.0
    center_boids = 0
    target = boids[idx]
    for jdx, b in enumerate(boids):
        if idx != jdx:
            if math.dist(target.position, b.position) < target.align_radius:
                center_x += b.velocity[0]
                center_y += b.velocity[1]
                center_boids += 1
    if center_boids > 1:
        center_x /= (center_boids - 1)
        center_y /= (center_boids - 1)

        x = (center_x - boids[idx].velocity[0]) / 8.0
        y = (center_y - boids[idx].velocity[1]) / 8.0
    else:
        x = y = 0.0
    return strength * x, strength * y


def move_all_boids_to_new_positions(boids: List[Boid], dimensions: tuple, velocity_limit: float):
    for idx, b in enumerate(boids):
        velocities = [
            rule1(idx, boids, 1.0),
            rule2(idx, boids, 1.0),
            rule3(idx, boids, 1.0)
        ]
        vel_x, vel_y = sum_points(b.velocity, *velocities)
        b.velocity = limit(vel_x, velocity_limit), limit(vel_y, velocity_limit)
        x, y = sum_points(b.position, b.velocity)
        b.position = screen_wrap((x, y), dimensions)


def screen_wrap(point, screen):
    x, y = point
    w, h = screen

    if x > w:
        x -= w
    if x < 0:
        x += w
    if y > h:
        y -= h
    if y < 0:
        y += h

    return x, y


def limit(value, lim):
    value = min(value, lim)
    value = max(value, -lim)
    return value


def sum_points(*points):
    x = sum([p[0] for p in points])
    y = sum([p[1] for p in points])
    return x, y


def distance_between_points(one, two):
    x = pow((one[0] - two[0]), 2)
    y = pow((one[1] - two[1]), 2)
    return math.sqrt(x + y)


if __name__ == "__main__":
    from timeit import default_timer

    number_of_boids = 200
    screen_dimensions = (500, 500)

    pygame.init()
    clock = pygame.time.Clock()
    scr: pygame.Surface = pygame.display.set_mode(screen_dimensions)
    done = False

    boid_list = initialize_positions(number_of_boids, screen_dimensions)

    while not done:
        scr.fill((0, 0, 0))

        draw_boids(scr, boid_list)

        a = default_timer()
        move_all_boids_to_new_positions(boid_list, screen_dimensions,
                                        velocity_limit=3.0)
        # print(f"Move takes {default_timer() - a:.4f}s")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        pygame.display.flip()

        dt = clock.tick(30)

