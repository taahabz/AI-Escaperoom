from collections import deque
import heapq
import math
import time

class AI:
    def __init__(self):
        self.path = []
        self.current_goal = None
        self.collected_keys = {}
        self.has_key = False
        self.enemy_memory = {}
        self.danger_radius = 4  # Increased danger radius
        self.start_time = time.time()
        self.last_path_update = 0
        self.path_update_interval = 0.001# Update path more frequently

    def get_current_time(self):
        return time.time() - self.start_time

    def bfs_enemy_movement(self, enemy_pos, level_data, player_pos):
        """Implements BFS for enemy movement with very slow speed."""
        queue = deque([(enemy_pos[0], enemy_pos[1])])
        visited = set([(enemy_pos[0], enemy_pos[1])])
        parent = {(enemy_pos[0], enemy_pos[1]): None}
        
        target = (int(player_pos[0]), int(player_pos[1]))
        
        while queue:
            current = queue.popleft()
            
            if current == target:
                break
                
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_x = current[0] + dx
                next_y = current[1] + dy
                next_pos = (next_x, next_y)
                
                if (next_x < 0 or next_x >= level_data["width"] or 
                    next_y < 0 or next_y >= level_data["height"]):
                    continue
                    
                if next_pos in level_data["walls"]:
                    continue
                    
                if next_pos not in visited:
                    visited.add(next_pos)
                    queue.append(next_pos)
                    parent[next_pos] = current
        
        # Get the next position towards player
        current = target
        path = []
        while current and current in parent:
            path.append(current)
            current = parent[current]
        path.reverse()
        
        # Return very small movement towards the first step in path
        if len(path) > 1:
            dx = path[1][0] - enemy_pos[0]
            dy = path[1][1] - enemy_pos[1]
            # Very small movement - 0.05 units per frame
            return (enemy_pos[0] + (dx * 0.05), enemy_pos[1] + (dy * 0.05), enemy_pos[2])
        
        return enemy_pos

    def heuristic(self, start, goal):
        return abs(start[0] - goal[0]) + abs(start[1] - goal[1])

    def is_near_enemy(self, pos, enemy_positions):
        """Enhanced enemy proximity detection."""
        x, y = pos
        min_distance = float('inf')

        for enemy_x, enemy_y, _ in enemy_positions:
            # Calculate exact distance
            dx = x - enemy_x
            dy = y - enemy_y
            distance = math.sqrt(dx * dx + dy * dy)
            min_distance = min(min_distance, distance)

            if distance < self.danger_radius:
                return True, min_distance

        return False, min_distance

    def find_escape_direction(self, pos, enemy_positions, level_data):
        """Find the best direction to escape from nearby enemies."""
        x, y = pos
        best_direction = None
        max_safety = -float('inf')

        directions = [(0, 1), (1, 0), (0, -1), (-1, 0),
                      (1, 1), (1, -1), (-1, 1), (-1, -1)]  # Including diagonals

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            new_pos = (new_x, new_y)

            # Check if the new position is valid
            if (new_x < 0 or new_x >= level_data["width"] or 
                new_y < 0 or new_y >= level_data["height"]):
                continue

            if new_pos in level_data["walls"]:
                continue

            if not self.has_key:
                door_positions = {(door[0], door[1]) for door in level_data["doors"]}
                if new_pos in door_positions:
                    continue

            # Calculate safety score for this direction
            is_dangerous, min_enemy_dist = self.is_near_enemy(new_pos, enemy_positions)
            safety_score = min_enemy_dist

            if safety_score > max_safety:
                max_safety = safety_score
                best_direction = (dx, dy)

        return best_direction

    def get_neighbors(self, pos, level_data, enemy_positions):
        """Enhanced neighbor selection with better enemy avoidance."""
        x, y = pos
        neighbors = []
        base_directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

        for dx, dy in base_directions:
            new_x, new_y = x + dx, y + dy
            new_pos = (new_x, new_y)

            # Basic validity checks
            if (new_x < 0 or new_x >= level_data["width"] or 
                new_y < 0 or new_y >= level_data["height"]):
                continue

            if new_pos in level_data["walls"]:
                continue

            if not self.has_key:
                door_positions = {(door[0], door[1]) for door in level_data["doors"]}
                if new_pos in door_positions:
                    continue

            # Check enemy proximity
            is_dangerous, distance = self.is_near_enemy(new_pos, enemy_positions)

            if not is_dangerous:
                neighbors.append((new_pos, distance))
            elif distance > self.danger_radius * 0.5:  # Allow some closer positions if necessary
                neighbors.append((new_pos, distance - self.danger_radius))  # Penalty for being close

        # Sort neighbors by safety (distance from enemies)
        neighbors.sort(key=lambda x: x[1], reverse=True)
        return [pos for pos, _ in neighbors]

    def a_star(self, start, goal, level_data, enemy_positions):
        """Enhanced A* pathfinding with dynamic enemy avoidance."""
        start = (int(start[0]), int(start[1]))
        goal = (int(goal[0]), int(goal[1]))

        is_dangerous, _ = self.is_near_enemy(goal, enemy_positions)
        if is_dangerous:
            return []

        frontier = [(0, start)]
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current == goal:
                break

            for next_pos in self.get_neighbors(current, level_data, enemy_positions):
                is_dangerous, distance = self.is_near_enemy(next_pos, enemy_positions)

                # Base movement cost
                new_cost = cost_so_far[current] + 1

                # Add penalty for enemy proximity
                if is_dangerous:
                    new_cost += max(0, self.danger_radius - distance) * 5

                if next_pos not in cost_so_far or new_cost < cost_so_far[next_pos]:
                    cost_so_far[next_pos] = new_cost
                    priority = new_cost + self.heuristic(goal, next_pos)
                    heapq.heappush(frontier, (priority, next_pos))
                    came_from[next_pos] = current

        # Reconstruct path
        path = []
        current = goal
        while current is not None:
            path.append(current)
            current = came_from.get(current)
        path.reverse()

        # If no path found, try to find an escape route
        if not path and self.is_near_enemy(start, enemy_positions)[0]:
            escape_dir = self.find_escape_direction(start, enemy_positions, level_data)
            if escape_dir:
                dx, dy = escape_dir
                path = [start, (start[0] + dx, start[1] + dy)]

        return path

    def update(self, game_state):
        """Enhanced update method with balanced goal prioritization."""
        self.has_key = game_state.get("has_key", False)
        self.collected_keys = game_state["collected_keys"]
        enemy_positions = game_state["current_level_data"].get("enemies", set())
        current_time = self.get_current_time()

        current_pos = (game_state["player_rect"].x // 24, game_state["player_rect"].y // 24)

    # Check if we need to update the path
        should_update_path = (
            not self.path or
            len(self.path) <= 1 or
            current_time - self.last_path_update > self.path_update_interval or
            self.is_near_enemy(current_pos, enemy_positions)[0]
        )

        if should_update_path:
            self.last_path_update = current_time

        # Check for danger
            is_dangerous, min_distance = self.is_near_enemy(current_pos, enemy_positions)

        # Select the goal
            goal_info = self.choose_goal(game_state)
            if goal_info:
                goal_type, goal_pos = goal_info

            # Pathfinding to the goal
                self.path = self.a_star(current_pos, goal_pos, game_state["current_level_data"], enemy_positions)

            # If the goal is reachable and not blocked, prioritize it over escape
                if self.path and len(self.path) > 1:
                   goal_is_safe = not self.is_near_enemy(goal_pos, enemy_positions)[0]
                   if not is_dangerous or goal_is_safe:
                       return self.get_next_move(current_pos, self.path[1])

        # If danger is high and no safe path to goal, attempt to escape
            if is_dangerous and min_distance < self.danger_radius * 0.75:
                escape_dir = self.find_escape_direction(current_pos, enemy_positions, game_state["current_level_data"])
                if escape_dir:
                    dx, dy = escape_dir
                    self.path = [current_pos, (current_pos[0] + dx, current_pos[1] + dy)]
                    return self.get_next_move(current_pos, self.path[1])

    # Follow the current path if it exists
        if self.path and len(self.path) > 1:
            next_pos = self.path[1]
            if current_pos == self.path[0]:
                self.path.pop(0)
            return self.get_next_move(current_pos, next_pos)

        return 'idle'

    def choose_goal(self, game_state):
        """Choose the next goal based on game state."""
        player_pos = (game_state["player_rect"].x // 24, game_state["player_rect"].y // 24)
        level_data = game_state["current_level_data"]

    # Check for keys if we don't have the key
        if not game_state.get("has_key", False) and game_state["collected_keys"]:
            nearest_key = min(game_state["collected_keys"].keys(),
                              key=lambda k: self.heuristic(player_pos, k))
            return ("key", nearest_key)

    # If we have the key, go to the door
        if game_state.get("has_key", False) or not game_state["collected_keys"]:
            if level_data["doors"]:
                door_pos = (level_data["doors"][0][0], level_data["doors"][0][1])
                return ("door", door_pos)

        return None


    def get_next_move(self, current_pos, next_pos):
        """Convert path movement to game commands."""
        dx = next_pos[0] - current_pos[0]
        dy = next_pos[1] - current_pos[1]

        if dx > 0: return 'right'
        if dx < 0: return 'left'
        if dy > 0: return 'down'
        if dy < 0: return 'up'
        return 'idle'

def initialize_ai():
    return AI()
