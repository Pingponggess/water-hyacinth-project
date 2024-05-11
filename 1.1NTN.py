#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  2 15:36:19 2023

@author: pingpongges
"""

import pygame
import random
import math
import csv
from pygame.locals import *
import os
import sys


pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Automatic Water Hyacinth Collecting Boat Model')

# Triangle and ship sizes
TRIANGLE_SIZE = 20
SHIP_SIZE = 25

# Ship speed
SHIP_SPEED = 2

# Time interval for generating new triangles (in milliseconds)
# 10 seconds
NEW_TRIANGLE_INTERVAL = 10000

def draw_triangle(position):
    x, y = position
    pygame.draw.polygon(screen, RED, [(x, y), (x + TRIANGLE_SIZE, y), (x + TRIANGLE_SIZE // 2, y - TRIANGLE_SIZE)], 0)

def draw_ship(position):
    x, y = position
    pygame.draw.rect(screen, WHITE, (x, y, SHIP_SIZE, SHIP_SIZE))

def distance(pos1, pos2):
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def find_nearest_triangle(ship_pos, triangles):
    if not triangles:
        return None
    nearest_triangle = triangles[0]
    min_distance = distance(ship_pos, nearest_triangle)
    for triangle in triangles:
        current_distance = distance(ship_pos, triangle)
        if current_distance < min_distance:
            min_distance = current_distance
            nearest_triangle = triangle
    return nearest_triangle

def render_text(text, position, color=WHITE, size=20):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def reset_game():
    global triangles, ship_pos, total_displacement, eliminated_triangles, direction, rotation_angle, rotation_angle_previous, total_rotation_angle, triangle_generations

    triangles = [(random.randint(0, WIDTH - TRIANGLE_SIZE), random.randint(TRIANGLE_SIZE, HEIGHT - TRIANGLE_SIZE)) for _ in range(50)]
    ship_pos = [WIDTH // 2, HEIGHT // 2]
    total_displacement = 0
    eliminated_triangles = 0
    direction = "N/A"
    rotation_angle = 0
    rotation_angle_previous = 0
    total_rotation_angle = 0
    triangle_generations = 0

triangles = [(random.randint(0, WIDTH - TRIANGLE_SIZE), random.randint(TRIANGLE_SIZE, HEIGHT - TRIANGLE_SIZE)) for _ in range(50)]
ship_pos = [WIDTH // 2, HEIGHT // 2]

clock = pygame.time.Clock()
pygame.time.set_timer(USEREVENT + 1, NEW_TRIANGLE_INTERVAL)

total_displacement = 0
eliminated_triangles = 0
direction = "N/A"
rotation_angle = 0
rotation_angle_previous = 0
total_rotation_angle = 0
triangle_generations = 0

# Initialize CSV file
script_name = os.path.basename(sys.argv[0])  # This gets the name of the currently running script
csv_filename = os.path.splitext(script_name)[0] + "_data.csv"  # This removes the file extension from the script name and appends "_data.csv"

with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ['Run', 'Total Displacement', 'Total Rotation Angle']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

running = True
completed_runs = 0
while running and completed_runs < 100:
    screen.fill((0, 0, 0))

    for triangle in triangles:
        draw_triangle(triangle)

    draw_ship(ship_pos)

    nearest_triangle = find_nearest_triangle(ship_pos, triangles)
    if nearest_triangle:
        dx = nearest_triangle[0] - ship_pos[0]
        dy = nearest_triangle[1] - ship_pos[1]
        distance_to_triangle = distance(ship_pos, nearest_triangle)
        if distance_to_triangle > SHIP_SPEED:
            ship_pos[0] += SHIP_SPEED * dx / distance_to_triangle
            ship_pos[1] += SHIP_SPEED * dy / distance_to_triangle
            total_displacement += SHIP_SPEED
            direction = f"{math.degrees(math.atan2(dy, dx)):.2f}°"
            rotation_angle = (math.degrees(math.atan2(dy, dx)) + 90) % 360
            relative_rotation_angle = abs(rotation_angle - rotation_angle_previous)
            rotation_angle_previous = rotation_angle
            total_rotation_angle += relative_rotation_angle

        else:
            eliminated_triangles += 1
            triangles.remove(nearest_triangle)

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == USEREVENT + 1: # Comment out or remove this section
            if triangle_generations < 5:
                if len(triangles) < 110:
                    new_triangles = [(random.randint(0, WIDTH - TRIANGLE_SIZE), random.randint(TRIANGLE_SIZE, HEIGHT - TRIANGLE_SIZE)) for _ in range(10)]
                    triangles.extend(new_triangles)
                    triangle_generations += 1

    if len(triangles) == 0:
        with open(csv_filename, mode='a', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writerow({'Run': completed_runs + 1,
                             'Total Displacement': total_displacement,
                             'Total Rotation Angle': total_rotation_angle})
        completed_runs += 1
        reset_game()

    # Render information text on the screen
    render_text(f"Direction: {direction}", (10, 10))
    render_text(f"Rotation angle: {relative_rotation_angle:.2f}°", (10, 30))
    render_text(f"Total rotation angle: {total_rotation_angle:.2f}°", (10, 50))
    render_text(f"Eliminated triangles: {eliminated_triangles}", (10, 70))
    render_text(f"Total displacement: {total_displacement:.2f}", (10, 90))
    render_text(f"Remaining triangles: {len(triangles)}", (10, 110))

    pygame.display.flip()
    clock.tick(300)

pygame.quit()