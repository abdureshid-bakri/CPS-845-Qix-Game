import pygame
from enum inport Enum, auto
from dataclasses import dataclass

## dependencies should be provided by teammates
## these are just minimal interfaces for main and everyone else should match them in their files

class Player:
  def input_handling(self, events): ...
  def update(self, dt, world): ...
  def draw(self, surf) ...
  @property 
  def on_edge(self) -> bool: ...
  @property
  def is_pushing(self) -> bool: ...
  @property
  def trail(self) -> list[tuple[int, int]]: ...
  def reset_after_hit(self): ...
  def start(self): ... 
  def stop(self): ... 
  @property
  def push_start_cell(self) -> tuple[int, int] ...
  @property
  def cell(self) -> tuple[int, int]: ... 
    
class Qix:
  def update(self, dt, world): ... 
  def draw(self, surf): ... 
  @property
  def cell(self) -> tuplr[int, int]: ... 

class SparxManager:
  def update(self, dt, world): ... 
  def draw(self, surf): ...
  def hits_player(self, player_cell) -> bool: ... 
  def hit_push_start(self, push_start_cell) -> bool: ...

#grid and rules
class world:
  tile_size: int
  width_size: int 
  height_tiles: int

  def draw(self, surf): ... 
  def reset_push(self): ... 
  def apply_trail(self, trail: list[tuple[int, int]]): ... 
  def seal_area(self, qix_cell, trail) -> None: ...
  def percent_claimed(self) -> float: ... 
  def qix_hits_trail(self, qix_cell, trail) -> bool: ... 
  def rebuild_boundry(self): ... 
    
###########game state

class Phase(Enum):
  PLAYING = auto()
  LIVES_LOST = auto()
  LEVELS_WON = auto()
  GAME_OVER = auto()

@dataclass
class Config:
  width = 900
  height = 700
  fps = 60
  targest_percent = 0.50
  lives = 3

class Game:
  def __init__(self, world: World, player: Player, qix: Qix, sparx: SparxManager, cfg: Config):
    self.world = world 
    self.player = player
    self.qix = qix 
    self.sparx = sparx
    self.cfg = cfg
    self.phase = phase.PLAYING
    self.lives = cfg.lives

def handle_input(self, events):
  if self.phase != Phase.PLAYING:
    for x in events:
      if x.type == pygame.KEYDOWN and x.key == pygame.K_SPACE:
        if self.phase == Phase.LIFE_LOST:
          self.phase = Phase.PLAYING
        elif self.phase == Phase.LEVEL_WON:
          self.phase = Phase.PLAYING 
    return
  self.player.handle_inputs(events)

def update(self, dt):
  if self.phase != Phase.PLAYING:
    return

  # update entities 
  self.player.update(dt, self.world)
  self.qix.update(dt, self.world)
  self.sparx.update(dt, self.world)
  
  if self.player.is_pushing and self.world.qix_hits_trail(self.qix.cell, self.player.trail):
    self._lose_life(cancel_push=True)
    return 

  if self.sparx.any_hits_player(self.player.cell):
    self._lose_life(cancel_push=False)
    return

if self.plsyer.is_pushing and self.sparx.hits_push_start(self.player.push_start_cell):
  self._cancel_push_only()
  return

if self.player.is_pushing and self._trail_reached_edge():
  trail = list(self.player.trail)
  self.player.stop_push()

  self.world.apply_trail_as_edge(trail)
  self.world.seal_area(self.qix.cell, trail)
  self.world.rebuild_boundry()

if self.world.claimed_percent() >= self.cfg.target_percent:
  self.phase = Phase.LEVEL_WON
  





  
