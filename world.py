# world.py
from __future__ import annotations
import pygame
from enum import Enum, auto
from collections import deque
from typing import List, Tuple, Deque

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

        # outer frame
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

    # --- small helpers ---
    def in_bounds(self, c: Cell) -> bool:
        x, y = c
        return 0 <= x < self.width_tiles and 0 <= y < self.height_tiles

    def get(self, c: Cell) -> Tile:
        x, y = c
        return self.grid[y][x]

    def set(self, c: Cell, val: Tile) -> None:
        x, y = c
        self.grid[y][x] = val

    def _n4(self, x: int, y: int):
        if x > 0: yield (x - 1, y)
        if x < self.width_tiles - 1: yield (x + 1, y)
        if y > 0: yield (x, y - 1)
        if y < self.height_tiles - 1: yield (x, y + 1)

    def _n8(self, x: int, y: int):
        for nx in (x - 1, x, x + 1):
            for ny in (y - 1, y, y + 1):
                if nx == x and ny == y:
                    continue
                if 0 <= nx < self.width_tiles and 0 <= ny < self.height_tiles:
                    yield (nx, ny)

    # --- required API ---
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

    def reset_push(self) -> None:
        for y in range(self.height_tiles):
            for x in range(self.width_tiles):
                if self.grid[y][x] is Tile.TRAIL:
                    self.grid[y][x] = Tile.FREE

    def apply_trail(self, trail: List[Cell]) -> None:
        for c in trail:
            if self.in_bounds(c) and self.get(c) is Tile.FREE:
                self.set(c, Tile.TRAIL)

    def qix_hits_trail(self, qix_cell: Cell, trail: List[Cell]) -> bool:
        return self.in_bounds(qix_cell) and (qix_cell in set(trail))

    def seal_area(self, qix_cell: Cell, trail: List[Cell]) -> None:
        # if qix invalid, just lock the trail in
        if not self.in_bounds(qix_cell):
            self._trail_to_boundary()
            trail.clear()
            return

        qx, qy = qix_cell
        if self.grid[qy][qx] is not Tile.FREE:
            self._trail_to_boundary()
            trail.clear()
            self.rebuild_boundary()
            self._recount_claimed()
            return

        # 1) flood from qix through FREE
        reach = [[False] * self.width_tiles for _ in range(self.height_tiles)]
        q: Deque[Cell] = deque([qix_cell])
        reach[qy][qx] = True

        while q:
            x, y = q.popleft()
            for nx, ny in self._n4(x, y):
                if not reach[ny][nx] and self.grid[ny][nx] is Tile.FREE:
                    reach[ny][nx] = True
                    q.append((nx, ny))

        # 2) non-reachable FREE -> CLAIMED
        for y in range(self.height_tiles):
            for x in range(self.width_tiles):
                if self.grid[y][x] is Tile.FREE and not reach[y][x]:
                    self.grid[y][x] = Tile.CLAIMED

        # 3) trail -> boundary
        self._trail_to_boundary()
        trail.clear()

        # 4) rebuild boundary + recount
        self.rebuild_boundary()
        self._recount_claimed()

    def _trail_to_boundary(self) -> None:
        for y in range(self.height_tiles):
            for x in range(self.width_tiles):
                if self.grid[y][x] is Tile.TRAIL:
                    self.grid[y][x] = Tile.BOUNDARY

    def percent_claimed(self) -> float:
        if self._total_tiles == 0:
            return 0.0
        return (self._claimed_tiles / self._total_tiles) * 100.0

    def _recount_claimed(self) -> None:
        self._claimed_tiles = sum(
            1
            for y in range(self.height_tiles)
            for x in range(self.width_tiles)
            if self.grid[y][x] is Tile.CLAIMED
        )

    def rebuild_boundary(self) -> None:
        # clear inner boundary
        for y in range(self.height_tiles):
            for x in range(self.width_tiles):
                if self.grid[y][x] is Tile.BOUNDARY and not self._is_outer(x, y):
                    self.grid[y][x] = Tile.FREE

        # reinstate outer frame
        for x in range(self.width_tiles):
            self.grid[0][x] = Tile.BOUNDARY
            self.grid[self.height_tiles - 1][x] = Tile.BOUNDARY
        for y in range(self.height_tiles):
            self.grid[y][0] = Tile.BOUNDARY
            self.grid[y][self.width_tiles - 1] = Tile.BOUNDARY

        # FREE next to CLAIMED (8-way) becomes boundary
        to_mark: List[Cell] = []
        for y in range(self.height_tiles):
            for x in range(self.width_tiles):
                if self.grid[y][x] is Tile.FREE:
                    if any(self.grid[ny][nx] is Tile.CLAIMED for nx, ny in self._n8(x, y)):
                        to_mark.append((x, y))
        for x, y in to_mark:
            self.grid[y][x] = Tile.BOUNDARY

    def _is_outer(self, x: int, y: int) -> bool:
        return x == 0 or y == 0 or x == self.width_tiles - 1 or y == self.height_tiles - 1

