from __future__ import annotations
import pygame
from enum import Enum, auto
from typing import List, Tuple

Cell = Tuple[int, int]

class Tile(Enum):
    FREE = auto()
    BOUNDARY = auto()
    CLAIMED = auto()
    TRAIL = auto()

class World:
    def __init__(self, tile_size: int, width_tiles: int, height_tiles: int):
        self.tile_size = tile_size
        self.width_tiles = width_tiles
        self.height_tiles = height_tiles

        self.grid: List[List[Tile]] = [
            [Tile.FREE for _ in range(width_tiles)] for _ in range(height_tiles)
        ]
        for x in range(width_tiles):
            self.grid[0][x] = Tile.BOUNDARY
            self.grid[height_tiles - 1][x] = Tile.BOUNDARY
        for y in range(height_tiles):
            self.grid[y][0] = Tile.BOUNDARY
            self.grid[y][width_tiles - 1] = Tile.BOUNDARY

        self._total_tiles = width_tiles * height_tiles
        self._claimed_tiles = 0

        self.color_free = (18, 18, 18)
        self.color_boundary = (230, 230, 230)
        self.color_trail = (0, 200, 255)
        self.color_claimed = (60, 120, 60)
        self.color_grid = (35, 35, 35)
        self.show_grid = True

    def draw(self, surf: pygame.Surface) -> None:
        ts = self.tile_size
        for y in range(self.height_tiles):
            for x in range(self.width_tiles):
                t = self.grid[y][x]
                if t is Tile.FREE:      col = self.color_free
                elif t is Tile.BOUNDARY: col = self.color_boundary
                elif t is Tile.TRAIL:    col = self.color_trail
                else:                    col = self.color_claimed
                pygame.draw.rect(surf, col, pygame.Rect(x * ts, y * ts, ts, ts))
        if self.show_grid:
            for x in range(self.width_tiles + 1):
                pygame.draw.line(surf, self.color_grid, (x * ts, 0), (x * ts, self.height_tiles * ts))
            for y in range(self.height_tiles + 1):
                pygame.draw.line(surf, self.color_grid, (0, y * ts), (self.width_tiles * ts, y * ts))

