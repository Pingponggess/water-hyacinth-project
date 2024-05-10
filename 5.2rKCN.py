#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov  3 01:42:57 2023

@author: pingpongges
"""


import pygame
import random
import math
import csv
from pygame.locals import *
from sklearn.cluster import KMeans
import numpy as np
import os
import sys


pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600

# Colors
WHITE = (255, 255, 255)
COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 0, 255),
    (0, 255, 255),
    (128, 128, 128),
    (0, 128, 128),
    (128, 0, 128),
    (128, 128, 0),
]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Automatic Water Hyacinth Collecting Boat Model')

# Number of clusters (K) and colors
#K = max(1, len(triangles) // 10)
K = 5

# Triangle and ship sizes
TRIANGLE_SIZE = 20
SHIP_SIZE = 25

# Ship speed
SHIP_SPEED = 2

# Time interval for generating new triangles (in milliseconds)
# 10 seconds
NEW_TRIANGLE_INTERVAL = 10000

def draw_triangle(position, color):
    x, y = position #x,y เป็นพิกัดของจุดยอดแรกของสามเหลี่ยม
    pygame.draw.polygon(screen, color, [(x, y), (x + TRIANGLE_SIZE, y), (x + TRIANGLE_SIZE // 2, y - TRIANGLE_SIZE)], 0)

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

def kmeans_clustering(triangles, K):
    kmeans = KMeans(n_clusters=K, random_state=0).fit(triangles)
    return kmeans.labels_

def render_text(text, position, color=WHITE, size=20):
    font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    screen.blit(text_surface, position)

def find_nearest_triangle_color(new_triangle_pos, triangles, triangle_colors):
    if len(triangles) == 0:
        return None
    nearest_triangle = triangles[0] #ให้สามเหลี่ยมที่ใกล้ที่สุดเป็นสามเหลี่ยมแรก
    min_distance = distance(new_triangle_pos, nearest_triangle)
    nearest_triangle_color = triangle_colors[0] #ให้nearest_triangle_colorเป็นสีของสามเหลี่ยมนั้น
    for i, triangle in enumerate(triangles):
        current_distance = distance(new_triangle_pos, triangle)
        if current_distance < min_distance and i < len(triangle_colors):
            min_distance = current_distance
            nearest_triangle = triangle
            nearest_triangle_color = triangle_colors[i]
    return nearest_triangle_color

def find_nearest_triangle_group(ship_pos, triangles, triangle_colors):
    if len(triangles) == 0:
        return None, None

    nearest_group_triangle = None
    nearest_group_color = None
    min_group_distance = float("inf")

    for color in set(triangle_colors):
        color_triangles = [triangle for i, triangle in enumerate(triangles) if triangle_colors[i] == color]
        if not color_triangles:
            continue
        nearest_color_triangle = find_nearest_triangle(ship_pos, color_triangles)
        if nearest_color_triangle is not None:
            distance_to_color_triangle = distance(ship_pos, nearest_color_triangle)
            if distance_to_color_triangle < min_group_distance:
                min_group_distance = distance_to_color_triangle
                nearest_group_triangle = nearest_color_triangle
                nearest_group_color = color

    # Return None if no nearest group was found
    if nearest_group_triangle is None:
        return None, None

    return nearest_group_triangle, nearest_group_color

def reset_game():
    global triangles, ship_pos, total_displacement, eliminated_triangles, direction, rotation_angle, rotation_angle_previous, total_rotation_angle, triangle_generations, triangle_colors, collected_triangles
    triangles = np.array([(random.randint(0, WIDTH - TRIANGLE_SIZE), random.randint(TRIANGLE_SIZE, HEIGHT - TRIANGLE_SIZE)) for _ in range(50)])
    K = max(1, len(triangles) // 10)
    triangle_colors = [COLORS[label] for label in kmeans_clustering(triangles, K)]
    
    ship_pos = STATION_POS.copy()
    total_displacement = 0
    eliminated_triangles = 0
    direction = "N/A"
    rotation_angle = 0
    rotation_angle_previous = 0
    total_rotation_angle = 0
    triangle_generations = 0
    collected_triangles = 0

STATION_POS = [WIDTH // 2, HEIGHT - SHIP_SIZE * 2]  # Station is placed at the bottom center of the screen
triangles = np.array([(random.randint(0, WIDTH - TRIANGLE_SIZE), random.randint(TRIANGLE_SIZE, HEIGHT - TRIANGLE_SIZE)) for _ in range(50)])
triangle_colors = [COLORS[label] for label in kmeans_clustering(triangles, K)]
ship_pos = STATION_POS.copy()

clock = pygame.time.Clock()
pygame.time.set_timer(USEREVENT + 1, NEW_TRIANGLE_INTERVAL)

total_displacement = 0
eliminated_triangles = 0
direction = "N/A"
rotation_angle = 0
rotation_angle_previous = 0
total_rotation_angle = 0
triangle_generations = 0
collected_triangles = 0

# Initialize CSV file
script_name = os.path.basename(sys.argv[0])  # This gets the name of the currently running script
csv_filename = os.path.splitext(script_name)[0] + "_data.csv"  # This removes the file extension from the script name and appends "_data.csv"

with open(csv_filename, mode='w', newline='') as csv_file:
    fieldnames = ['Run', 'Total Displacement', 'Total Rotation Angle']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()

running = True
completed_runs = 0
current_group_color = None

while running and completed_runs < 100:
    screen.fill((0, 0, 0))

    # Draw the station (green square).
    pygame.draw.rect(screen, (0, 255, 0), (STATION_POS[0] - SHIP_SIZE//2, STATION_POS[1], SHIP_SIZE, SHIP_SIZE))  # Draws a green square representing the station

    for i, triangle in enumerate(triangles):
        draw_triangle(triangle, triangle_colors[i])

    draw_ship(ship_pos)

    # If there's a current group, find the nearest triangle within this group.
    # Otherwise, find the nearest group.
    if current_group_color is not None:
        current_group_triangles = [triangle for i, triangle in enumerate(triangles) if triangle_colors[i] == current_group_color]
        nearest_triangle = find_nearest_triangle(ship_pos, current_group_triangles)
    else:
        nearest_triangle, current_group_color = find_nearest_triangle_group(ship_pos, triangles, triangle_colors)

    if nearest_triangle is not None:
        if collected_triangles < 10:
            idx = np.where((triangles == nearest_triangle).all(axis=1))[0][0]
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
                triangles = np.delete(triangles, idx, 0)
                triangle_colors.pop(idx)
                collected_triangles += 1  # Increment collected_triangles when a triangle is collected
        
                # Check if the current group is exhausted.
                if len([color for color in triangle_colors if color == current_group_color]) == 0:
                    current_group_color = None
        else: # When collected_triangles is 10
            if distance(ship_pos, STATION_POS) > SHIP_SPEED:  # Moving back to station immediately
                dx = STATION_POS[0] - ship_pos[0]
                dy = STATION_POS[1] - ship_pos[1]
                ship_pos[0] += SHIP_SPEED * dx / distance(ship_pos, STATION_POS)
                ship_pos[1] += SHIP_SPEED * dy / distance(ship_pos, STATION_POS)
            else:
                collected_triangles = 0  # Reset collected_triangles 
                current_group_color = None  # Reset current group color
                K = max(1, len(triangles) // 10)
                labels = kmeans_clustering(triangles, K)
                triangle_colors = [COLORS[label] for label in labels]
                
        
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == USEREVENT + 1:
            if triangle_generations < 5:
                if len(triangles) < 110:
                    new_triangles = np.array([(random.randint(0, WIDTH - TRIANGLE_SIZE), random.randint(TRIANGLE_SIZE, HEIGHT - TRIANGLE_SIZE)) for _ in range(10)])
                    triangles = np.concatenate((triangles, new_triangles), axis=0)
                    K = max(1, len(triangles) // 10)
                    labels = kmeans_clustering(triangles, K)
                    triangle_colors = [COLORS[label] for label in labels]  # ปรับปรุงสีของทุกสามเหลี่ยมตาม clustering ใหม่
                    triangle_generations += 1
                    current_group_color = None
                    
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
    render_text(f"K: {K}", (10, 130))

    pygame.display.flip()
    clock.tick(300)

pygame.quit()
