import tkinter as tk
import random
import time
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
import copy

# Constantes
BLOCK_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
GAME_WIDTH = GRID_WIDTH * BLOCK_SIZE * 2 + 200  # Espace pour deux grilles + tableau de score
GAME_HEIGHT = GRID_HEIGHT * BLOCK_SIZE + 100    # Hauteur de la grille + espace pour le texte

# Couleurs
COLORS = {
    'I': '#00FFFF',  # Cyan
    'J': '#0000FF',  # Bleu
    'L': '#FF8000',  # Orange
    'O': '#FFFF00',  # Jaune
    'S': '#00FF00',  # Vert
    'T': '#8000FF',  # Violet
    'Z': '#FF0000',  # Rouge
    'Heart': '#FF69B4',  # Rose (pour la pièce rigolote en forme de cœur)
    'Star': '#FFD700'   # Or (pour la pièce rigolote en forme d'étoile)
}

# Formes des pièces standard
SHAPES = {
    'I': [
        [(0, 0), (0, 1), (0, 2), (0, 3)],
        [(0, 0), (1, 0), (2, 0), (3, 0)]
    ],
    'J': [
        [(0, 0), (1, 0), (1, 1), (1, 2)],
        [(0, 0), (0, 1), (1, 0), (2, 0)],
        [(0, 0), (0, 1), (0, 2), (1, 2)],
        [(0, 1), (1, 1), (2, 0), (2, 1)]
    ],
    'L': [
        [(0, 0), (0, 1), (0, 2), (1, 0)],
        [(0, 0), (1, 0), (2, 0), (2, 1)],
        [(0, 2), (1, 0), (1, 1), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (2, 1)]
    ],
    'O': [
        [(0, 0), (0, 1), (1, 0), (1, 1)]
    ],
    'S': [
        [(0, 1), (0, 2), (1, 0), (1, 1)],
        [(0, 0), (1, 0), (1, 1), (2, 1)]
    ],
    'Z': [
        [(0, 0), (0, 1), (1, 1), (1, 2)],
        [(0, 1), (1, 0), (1, 1), (2, 0)]
    ],
    'T': [
        [(0, 1), (1, 0), (1, 1), (1, 2)],
        [(0, 0), (1, 0), (1, 1), (2, 0)],
        [(0, 0), (0, 1), (0, 2), (1, 1)],
        [(0, 1), (1, 0), (1, 1), (2, 1)]
    ],
    # Pièces rigolotes
    'Heart': [
        [(0, 1), (1, 0), (1, 2), (2, 1), (2, 2), (3, 1)]  # Forme approximative d'un cœur
    ],
    'Star': [
        [(0, 1), (1, 0), (1, 2), (2, 0), (2, 1), (2, 2)]  # Forme approximative d'une étoile
    ]
}

# Classe pour représenter une pièce
@dataclass
class Piece:
    shape_type: str
    rotation: int
    x: int
    y: int
    is_special: bool = False
    
    def get_blocks(self) -> List[Tuple[int, int]]:
        shape = SHAPES[self.shape_type][self.rotation % len(SHAPES[self.shape_type])]
        return [(self.x + dx, self.y + dy) for dx, dy in shape]
    
    def rotate(self):
        self.rotation = (self.rotation + 1) % len(SHAPES[self.shape_type])
    
    def move(self, dx, dy):
        self.x += dx
        self.y += dy

# Classe principale du jeu
class TetrisGame:
    def __init__(self, master):
        self.master = master
        master.title("Tetris à deux joueurs (Humain vs IA)")
        master.geometry(f"{GAME_WIDTH}x{GAME_HEIGHT}")
        master.resizable(False, False)
        
        # Initialisation des variables
        self.running = True
        self.paused = False
        self.game_over = False
        self.rainbow_mode = False
        self.rainbow_end_time = 0
        self.slow_mode = False
        self.slow_end_time = 0
        
        # Paramètres de jeu
        self.fall_speed = 500  # Temps en ms entre chaque chute
        self.fall_speed_ai = 500  # Temps en ms entre chaque chute pour l'IA
        self.last_fall_time = time.time()
        self.last_fall_time_ai = time.time()
        self.last_rainbow_check = time.time()
        
        # Scores et statistiques
        self.scores = {'human': 0, 'ai': 0}
        self.lines_cleared = {'human': 0, 'ai': 0}
        self.special_piece_threshold = 3000
        
        # Grilles de jeu (0 = vide, chaîne = couleur de la pièce)
        self.grids = {
            'human': [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)],
            'ai': [[None for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        }
        
        # Pièces actuelles et suivantes
        self.current_pieces = {'human': None, 'ai': None}
        self.next_pieces = {'human': None, 'ai': None}
        
        # Interface graphique
        self.setup_ui()
        
        # Démarrer le jeu
        self.start_game()
        
        # Configuration des contrôles
        master.bind("<Left>", lambda e: self.move_piece('human', -1, 0))
        master.bind("<Right>", lambda e: self.move_piece('human', 1, 0))
        master.bind("<Down>", lambda e: self.move_piece('human', 0, 1))
        master.bind("<Up>", lambda e: self.rotate_piece('human'))
        master.bind("<space>", lambda e: self.hard_drop('human'))
        master.bind("<p>", lambda e: self.toggle_pause())
        
        # Commencer la boucle principale
        self.update()
    
    def setup_ui(self):
        # Canvas pour les grilles de jeu
        self.canvas_human = tk.Canvas(self.master, width=GRID_WIDTH * BLOCK_SIZE, 
                                     height=GRID_HEIGHT * BLOCK_SIZE, bg="black")
        self.canvas_human.grid(row=0, column=0, padx=10, pady=10)
        
        # Canvas pour le tableau de score au milieu
        self.canvas_score = tk.Canvas(self.master, width=180, 
                                     height=GRID_HEIGHT * BLOCK_SIZE, bg="#EEEEEE")
        self.canvas_score.grid(row=0, column=1, padx=10, pady=10)
        
        # Canvas pour la grille de l'IA
        self.canvas_ai = tk.Canvas(self.master, width=GRID_WIDTH * BLOCK_SIZE, 
                                  height=GRID_HEIGHT * BLOCK_SIZE, bg="black")
        self.canvas_ai.grid(row=0, column=2, padx=10, pady=10)
        
        # Dessiner les indicateurs sur le canvas du score
        self.draw_score_board()
    
    def draw_score_board(self):
        self.canvas_score.delete("all")
        self.canvas_score.create_text(90, 30, text="SCORES", font=("Arial", 16, "bold"))
    
        self.canvas_score.create_text(90, 70, text=f"Humain: {self.scores['human']}", 
                                 font=("Arial", 12))
        self.canvas_score.create_text(90, 100, text=f"IA: {self.scores['ai']}", 
                                 font=("Arial", 12))
    
        self.canvas_score.create_text(90, 130, text=f"Lignes Humain: {self.lines_cleared['human']}", 
                                 font=("Arial", 10))
        self.canvas_score.create_text(90, 150, text=f"Lignes IA: {self.lines_cleared['ai']}", 
                                 font=("Arial", 10))
    
    # Cadres pour mieux séparer les pièces
        self.canvas_score.create_rectangle(10, 175, 170, 265, outline="#CCCCCC")
        self.canvas_score.create_rectangle(10, 275, 170, 365, outline="#CCCCCC")
    
    # Afficher les prochaines pièces avec un espacement significativement amélioré
        self.canvas_score.create_text(90, 185, text="Prochaine pièce:", font=("Arial", 10, "bold"))
        self.canvas_score.create_text(90, 200, text="(HUMAIN)", font=("Arial", 8))
    
    # Humain
        if self.next_pieces['human']:
            self.draw_next_piece(self.next_pieces['human'], 'human')
    
    # Titre pour l'IA beaucoup plus bas
        self.canvas_score.create_text(90, 285, text="Prochaine pièce:", font=("Arial", 10, "bold"))
        self.canvas_score.create_text(90, 300, text="(IA)", font=("Arial", 8))
    
    # IA
        if self.next_pieces['ai']:
            self.draw_next_piece(self.next_pieces['ai'], 'ai')
    
    # Indicateurs de statut encore plus bas
        y_pos = 380
    
        if self.rainbow_mode:
            self.canvas_score.create_text(90, y_pos, text="Mode Arc-en-ciel!", 
                                     font=("Arial", 10), fill="purple")
            y_pos += 25
    
        if self.slow_mode:
            self.canvas_score.create_text(90, y_pos, text="Pause douceur...", 
                                     font=("Arial", 10), fill="blue")

    def draw_next_piece(self, piece, player):
    # Positions complètement séparées pour chaque joueur
        y_offset = 240 if player == 'human' else 340
        color = COLORS[piece.shape_type]
    
    # Calculer le centre pour centrer la pièce
        min_x = min(dx for dx, _ in SHAPES[piece.shape_type][0])
        max_x = max(dx for dx, _ in SHAPES[piece.shape_type][0])
        min_y = min(dy for _, dy in SHAPES[piece.shape_type][0])
        max_y = max(dy for _, dy in SHAPES[piece.shape_type][0])
        width = max_x - min_x + 1
        height = max_y - min_y + 1
    
    # Centrer la pièce
        center_x = 90 - (width * BLOCK_SIZE / 3)  # Réduire encore la taille pour l'affichage
        center_y = y_offset - (height * BLOCK_SIZE / 3)
    
    # Taille de bloc réduite pour la prévisualisation
        block_size = BLOCK_SIZE / 2  # Diminuer davantage la taille des blocs
    
        for dx, dy in SHAPES[piece.shape_type][0]:
            x1 = center_x + dx * block_size
            y1 = center_y + dy * block_size
            x2 = x1 + block_size
            y2 = y1 + block_size
        
            if self.rainbow_mode:
                color = random.choice(list(COLORS.values()))
        
            self.canvas_score.create_rectangle(x1, y1, x2, y2, fill=color, outline="white")
    
    def draw_grid(self, player):
        canvas = self.canvas_human if player == 'human' else self.canvas_ai
        grid = self.grids[player]
        
        canvas.delete("all")
        
        # Dessiner les blocs fixes
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x]:
                    color = grid[y][x]
                    if self.rainbow_mode:
                        color = random.choice(list(COLORS.values()))
                    self.draw_block(canvas, x, y, color)
        
        # Dessiner la pièce courante
        if self.current_pieces[player]:
            piece = self.current_pieces[player]
            color = COLORS[piece.shape_type]
            
            if self.rainbow_mode:
                color = random.choice(list(COLORS.values()))
            
            for x, y in piece.get_blocks():
                if 0 <= y < GRID_HEIGHT:  # Ne dessiner que les blocs visibles
                    self.draw_block(canvas, x, y, color)
    
    def draw_block(self, canvas, x, y, color):
        x1 = x * BLOCK_SIZE
        y1 = y * BLOCK_SIZE
        x2 = x1 + BLOCK_SIZE
        y2 = y1 + BLOCK_SIZE
        
        canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="white")
    
    def start_game(self):
        # Générer les premières pièces
        self.generate_new_piece('human')
        self.generate_new_piece('ai')
        
        # Mettre à jour les affichages
        self.draw_grid('human')
        self.draw_grid('ai')
        self.draw_score_board()
    
    def generate_new_piece(self, player, force_type=None):
        # Si une pièce suivante existe, elle devient la pièce courante
        if self.next_pieces[player]:
            self.current_pieces[player] = self.next_pieces[player]
            # On repositionne la pièce en haut de la grille
            self.current_pieces[player].x = GRID_WIDTH // 2 - 2
            self.current_pieces[player].y = 0
        else:
            # Pour la première pièce, on en crée une directement
            shape_type = force_type if force_type else random.choice(list(SHAPES.keys())[:7])  # Exclure les pièces spéciales
            self.current_pieces[player] = Piece(shape_type, 0, GRID_WIDTH // 2 - 2, 0)
        
        # Vérifier si un seuil spécial est atteint pour les pièces rigolotes
        is_special = False
        if any(self.scores[p] % self.special_piece_threshold == 0 and self.scores[p] > 0 for p in ['human', 'ai']):
            shape_type = random.choice(['Heart', 'Star'])
            is_special = True
        else:
            # Générer une pièce normale (mais parfois facile si l'adversaire a fait un combo)
            shape_type = random.choice(['I', 'O']) if force_type == "easy" else random.choice(list(SHAPES.keys())[:7])
        
        # Créer la prochaine pièce
        self.next_pieces[player] = Piece(shape_type, 0, 0, 0, is_special)
    
    def move_piece(self, player, dx, dy):
        if self.paused or self.game_over or not self.current_pieces[player]:
            return False
        
        piece = self.current_pieces[player]
        original_x, original_y = piece.x, piece.y
        
        piece.move(dx, dy)
        
        if self.check_collision(player):
            # Annuler le mouvement en cas de collision
            piece.x, piece.y = original_x, original_y
            
            # Si c'était une tentative de descente, fixer la pièce
            if dy > 0:
                self.lock_piece(player)
                return True
            
            return False
        
        # Redessiner la grille après le mouvement
        self.draw_grid(player)
        return True
    
    def rotate_piece(self, player):
        if self.paused or self.game_over or not self.current_pieces[player]:
            return False
        
        piece = self.current_pieces[player]
        original_rotation = piece.rotation
        
        piece.rotate()
        
        # Essayer d'ajuster la position si la rotation cause une collision
        if self.check_collision(player):
            # Essayer de déplacer à gauche
            piece.x -= 1
            if self.check_collision(player):
                piece.x += 2  # Essayer à droite
                if self.check_collision(player):
                    piece.x -= 1  # Revenir au centre
                    piece.rotation = original_rotation  # Annuler la rotation
                    return False
        
        self.draw_grid(player)
        return True
    
    def hard_drop(self, player):
        if self.paused or self.game_over or not self.current_pieces[player]:
            return
        
        # Déplacer la pièce vers le bas jusqu'à collision
        while self.move_piece(player, 0, 1):
            pass
    
    def check_collision(self, player):
        piece = self.current_pieces[player]
        grid = self.grids[player]
        
        for x, y in piece.get_blocks():
            # Vérifier les limites horizontales
            if x < 0 or x >= GRID_WIDTH:
                return True
            
            # Vérifier la limite inférieure
            if y >= GRID_HEIGHT:
                return True
            
            # Vérifier la collision avec des blocs existants
            if y >= 0 and grid[y][x]:  # Ignorer les collisions au-dessus de la grille
                return True
        
        return False
    
    def lock_piece(self, player):
        piece = self.current_pieces[player]
        grid = self.grids[player]
        
        # Ajouter les blocs de la pièce à la grille
        for x, y in piece.get_blocks():
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                grid[y][x] = COLORS[piece.shape_type]
        
        # Vérifier les lignes complétées
        self.check_lines(player)
        
        # Vérifier si le jeu est terminé (collision au sommet)
        if self.check_game_over(player):
            self.handle_game_over()
            return
        
        # Générer une nouvelle pièce
        self.generate_new_piece(player)
        
        # Mettre à jour l'affichage
        self.draw_grid(player)
        self.draw_score_board()
    
    def check_lines(self, player):
        grid = self.grids[player]
        lines_cleared = 0
        
        for y in range(GRID_HEIGHT):
            if all(grid[y][x] for x in range(GRID_WIDTH)):
                # Supprimer la ligne
                for y2 in range(y, 0, -1):
                    for x in range(GRID_WIDTH):
                        grid[y2][x] = grid[y2-1][x]
                
                # Vider la ligne du haut
                for x in range(GRID_WIDTH):
                    grid[0][x] = None
                
                lines_cleared += 1
        
        if lines_cleared > 0:
            # Mettre à jour les statistiques
            self.lines_cleared[player] += lines_cleared
            
            # Calculer les points
            points = 0
            if lines_cleared == 1:
                points = 50
            elif lines_cleared == 2:
                points = 50 * 2 + 100  # 200 points
                # Donner une pièce facile à l'adversaire
                opponent = 'ai' if player == 'human' else 'human'
                if self.next_pieces[opponent]:
                    self.next_pieces[opponent] = Piece(random.choice(['I', 'O']), 0, 0, 0)
            elif lines_cleared == 3:
                points = 50 * 3 + 200  # 350 points
            elif lines_cleared == 4:
                points = 50 * 4 + 300  # 500 points
            
            # Bonus pour pièce spéciale bien placée
            if self.current_pieces[player] and self.current_pieces[player].is_special:
                points += 100
            
            self.scores[player] += points
            
            # Vérifier si on active le mode "Pause douceur"
            if any(self.scores[p] % 1000 == 0 and self.scores[p] > 0 for p in ['human', 'ai']):
                self.activate_slow_mode()
            
            # Mettre à jour l'affichage
            self.draw_score_board()
    
    def check_game_over(self, player):
        # Vérifier si des blocs sont présents dans la rangée invisible du haut
        return any(self.grids[player][0][x] for x in range(GRID_WIDTH))
    
    def handle_game_over(self):
        self.game_over = True
        winner = 'human' if self.scores['human'] > self.scores['ai'] else 'ai'
        
        # Afficher le message de fin de jeu sur le tableau de scores
        self.canvas_score.create_rectangle(10, 400, 170, 480, fill="#FFE4E1")
        self.canvas_score.create_text(90, 430, text="GAME OVER", font=("Arial", 14, "bold"), fill="red")
        self.canvas_score.create_text(90, 460, text=f"Gagnant: {winner.upper()}", font=("Arial", 12))
    
    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused:
            self.canvas_score.create_rectangle(40, 400, 140, 440, fill="#EEEEEE")
            self.canvas_score.create_text(90, 420, text="PAUSE", font=("Arial", 12, "bold"))
        else:
            self.draw_score_board()
    
    def activate_rainbow_mode(self):
        self.rainbow_mode = True
        self.rainbow_end_time = time.time() + 20  # Dure 20 secondes
    
    def activate_slow_mode(self):
        self.slow_mode = True
        self.slow_end_time = time.time() + 10  # Dure 10 secondes
        
        # Réduire la vitesse de chute de 20%
        self.fall_speed *= 1.2
        self.fall_speed_ai *= 1.2
    
    def ai_move(self):
        if not self.current_pieces['ai'] or self.paused or self.game_over:
            return
        
        # Simple IA qui évalue différentes positions et orientations
        piece = self.current_pieces['ai']
        best_score = float('-inf')
        best_rotation = 0
        best_x = 0
        
        # Copier la grille actuelle pour les simulations
        grid_copy = copy.deepcopy(self.grids['ai'])
        
        # Tester chaque rotation possible
        for rotation in range(len(SHAPES[piece.shape_type])):
            # Sauvegarder la rotation originale
            original_rotation = piece.rotation
            piece.rotation = rotation
            
            # Tester chaque position x possible
            for x in range(-2, GRID_WIDTH):
                # Sauvegarder la position originale
                original_x, original_y = piece.x, piece.y
                piece.x = x
                piece.y = 0
                
                # Vérifier si la position est valide
                if not self.check_collision('ai'):
                    # Simuler la chute
                    y = 0
                    while True:
                        piece.y = y
                        if self.check_collision('ai'):
                            piece.y = y - 1
                            break
                        y += 1
                    
                    # Évaluer cette position
                    score = self.evaluate_position(piece, grid_copy)
                    
                    if score > best_score:
                        best_score = score
                        best_rotation = rotation
                        best_x = x
                
                # Restaurer la position originale
                piece.x, piece.y = original_x, original_y
            
            # Restaurer la rotation originale
            piece.rotation = original_rotation
        
        # Appliquer le meilleur mouvement
        piece.rotation = best_rotation
        piece.x = best_x
        
        # Faire tomber la pièce jusqu'en bas
        while not self.check_collision('ai'):
            piece.y += 1
        
        piece.y -= 1  # Remonter d'une case pour sortir de la collision
        
        # Verrouiller la pièce
        self.lock_piece('ai')
    
    def evaluate_position(self, piece, grid):
        # Une heuristique simple pour évaluer une position
        # Critères : hauteur, trous, lignes complétées, etc.
        
        # Créer une copie de la grille avec la pièce placée
        temp_grid = copy.deepcopy(grid)
        
        for x, y in piece.get_blocks():
            if 0 <= y < GRID_HEIGHT and 0 <= x < GRID_WIDTH:
                temp_grid[y][x] = COLORS[piece.shape_type]
        
        # Compter les lignes complètes
        complete_lines = 0
        for y in range(GRID_HEIGHT):
            if all(temp_grid[y][x] for x in range(GRID_WIDTH)):
                complete_lines += 1
        
        # Calculer la hauteur agrégée
        aggregate_height = 0
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if temp_grid[y][x]:
                    aggregate_height += GRID_HEIGHT - y
                    break
        
        # Compter les trous (cellules vides avec des cellules remplies au-dessus)
        holes = 0
        for x in range(GRID_WIDTH):
            block_found = False
            for y in range(GRID_HEIGHT):
                if temp_grid[y][x]:
                    block_found = True
                elif block_found:
                    holes += 1
        
        # Compter les bosses (différences de hauteur entre colonnes adjacentes)
        bumpiness = 0
        heights = []
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if temp_grid[y][x]:
                    heights.append(GRID_HEIGHT - y)
                    break
            else:
                heights.append(0)
        
        for i in range(len(heights) - 1):
            bumpiness += abs(heights[i] - heights[i+1])
        
        # Poids pour chaque métrique (à ajuster pour différents comportements d'IA)
        line_weight = 2.0
        height_weight = -0.5
        hole_weight = -1.0
        bumpiness_weight = -0.2
        
        # Pour les pièces spéciales, favoriser les placements qui les mettent en valeur
        special_bonus = 0
        if piece.is_special:
            # Bonus si la pièce est bien visible (pas trop profond dans la grille)
            min_y = min(y for _, y in piece.get_blocks())
            if min_y < GRID_HEIGHT // 2:
                special_bonus = 50
        
        # Calculer le score final
        score = (
            line_weight * complete_lines +
            height_weight * aggregate_height +
            hole_weight * holes +
            bumpiness_weight * bumpiness +
            special_bonus
        )
        
        return score
    
    def update(self):
        if not self.game_over and not self.paused:
            current_time = time.time()
            
            # Vérifier si le mode arc-en-ciel doit être activé (toutes les 2 minutes)
            if current_time - self.last_rainbow_check >= 120:  # 2 minutes
                self.last_rainbow_check = current_time
                self.activate_rainbow_mode()
            
            # Vérifier si le mode arc-en-ciel doit être désactivé
            if self.rainbow_mode and current_time > self.rainbow_end_time:
                self.rainbow_mode = False
            
            # Vérifier si le mode lent doit être désactivé
            if self.slow_mode and current_time > self.slow_end_time:
                self.slow_mode = False
                self.fall_speed /= 1.2  # Restaurer la vitesse normale
                self.fall_speed_ai /= 1.2
            
            # Faire tomber la pièce du joueur humain
            fall_delay = self.fall_speed / 1000  # Convertir en secondes
            if current_time - self.last_fall_time >= fall_delay:
                self.last_fall_time = current_time
                self.move_piece('human', 0, 1)
            
            # Faire tomber la pièce de l'IA
            fall_delay_ai = self.fall_speed_ai / 1000  # Convertir en secondes
            if current_time - self.last_fall_time_ai >= fall_delay_ai:
                self.last_fall_time_ai = current_time
                self.ai_move()
            
            # Redessiner les grilles régulièrement en mode arc-en-ciel
            if self.rainbow_mode:
                self.draw_grid('human')
                self.draw_grid('ai')
                self.draw_score_board()
        
        # Programmer la prochaine mise à jour
        self.master.after(50, self.update)  # Mettre à jour environ 20 fois par seconde

# Fonction principale pour créer l'exécutable
def main():
    root = tk.Tk()
    app = TetrisGame(root)
    root.mainloop()

if __name__ == "__main__":
    main()