# Game-Dev_Prototype
Pygame prototype for Godot project. 

___

## 📂 Project Structure

```text
wizard_prototype/
│
├── assets/                  # 3D Models, Textures, Sound Effects
│   ├── models/
│   └── audio/
│
├── src/                     # All source code
│   ├── __init__.py
│   ├── main.py              # Entry point (initializes engine & loops)
│   │
│   ├── core/                # Core engine wrappers & orchestrators
│   │   ├── __init__.py
│   │   ├── engine.py        # Raylib window initialization, main game loop
│   │   └── camera.py        # Isometric camera tracking logic
│   │
│   ├── systems/             # Pure game mechanics (Engine-agnostic logic)
│   │   ├── __init__.py
│   │   ├── combat.py        # Spell casting, damage resolution, hitboxes
│   │   └── map_gen.py       # Procedural dungeon/grid layout generation
│   │
│   └── entities/            # Game Objects (Data + localized state)
│       ├── __init__.py
│       ├── base_entity.py   # Parent class for anything with a 3D position
│       ├── player.py        # Player stats, inputs, and spell state
│       ├── enemy.py         # Enemy AI state machines
│       └── projectile.py    # Spell/Fireball movement arrays
│
├── requirements.txt         # For managing `pyray` dependency
└── README.md
```

___

## 🏗️ Object Architecture Blueprint

```mermaid
graph TD
    %% Base Orchestration %%
    Engine[Engine <br><i>Handles Raylib window & loops</i>] --> GameWorld[GameWorld <br><i>Holds map grid & Entity collections</i>]
    
    %% Systems %%
    GameWorld --> MapGen[MapGenerator <br><i>Generates grids / walls</i>]
    GameWorld --> CombatSys[CombatSystem <br><i>Spawns spells / checks bounds</i>]
    GameWorld --> CamSys[CameraSystem <br><i>Sets fixed 45 Degree isometric offset</i>]

    %% Entities %%
    CombatSys --> BaseEntity[BaseEntity <br><i>position: Vector3 <br> bounding_box: BoundingBox</i>]
    
    %% Inheritances %%
    BaseEntity --> Player[Player <br><i>health, mana <br> cast_spell</i>]
    BaseEntity --> Enemy[Enemy <br><i>ai_state: Str <br> target: Player</i>]
    BaseEntity --> Projectile[Projectile <br><i>velocity: Vector3 <br> damage: Int</i>]

    %% Styling %%
    style Engine fill:#2c3e50,stroke:#34495e,stroke-width:2px,color:#fff
    style GameWorld fill:#16a085,stroke:#1abc9c,stroke-width:2px,color:#fff
    style BaseEntity fill:#2980b9,stroke:#3498db,stroke-width:2px,color:#fff
```