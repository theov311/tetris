# Tetris à deux joueurs (Humain vs IA)

Ce projet est un jeu Tetris à deux joueurs où un joueur humain affronte une IA sur deux grilles côte à côte.

## Description

"Tetris à deux joueurs" offre une expérience de jeu interactive avec les fonctionnalités suivantes:

- Deux grilles de jeu côte à côte: une pour le joueur humain et une pour l'IA
- Systèmes de points et de niveaux
- Pièces spéciales rigolotes (cœur et étoile) qui apparaissent périodiquement
- Modes spéciaux comme le "Mode Arc-en-ciel" et la "Pause douceur" qui s'activent au cours du jeu
- Un tableau de score central affichant les statistiques des deux joueurs

## Prérequis

- Python 3.6 ou supérieur
- Tkinter (généralement inclus avec Python)
- cx_Freeze (pour créer l'exécutable)

## Installation

1. Clonez ce dépôt ou téléchargez les fichiers source
2. Assurez-vous que Python est installé sur votre système
3. Installez cx_Freeze si nécessaire:

```bash
pip install cx_Freeze
```

## Lancer le jeu

### Utiliser un exécutable

```bash
..\tetris\build\exe.win-amd64-3.11\tetris_game.exe
```

## Contrôles

- **Flèches gauche/droite**: Déplacer la pièce horizontalement
- **Flèche bas**: Accélérer la descente de la pièce
- **Flèche haut**: Faire pivoter la pièce
- **P**: Mettre le jeu en pause/reprendre

## Fonctionnalités spéciales

- **Mode Arc-en-ciel**: S'active toutes les 2 minutes et dure 20 secondes. Les pièces changent constamment de couleur.
- **Pause douceur**: S'active lorsqu'un joueur atteint un multiple de 1000 points. Ralentit la vitesse de chute des pièces pendant 10 secondes.
- **Pièces spéciales**: Des pièces en forme de cœur ou d'étoile apparaissent périodiquement lorsqu'un joueur atteint un multiple de 3000 points.
- **Système de combo**: Lorsqu'un joueur élimine 2 lignes ou plus à la fois, l'adversaire reçoit une pièce plus facile à placer (I ou O).

## Architecture du code

- `tetris_game.py`: Contient tout le code du jeu, y compris la logique du jeu et l'interface graphique
- `setup.py`: Script pour créer l'exécutable avec cx_Freeze

## Notes de développement

Ce projet utilise Tkinter pour l'interface graphique et est conçu pour être facilement exécutable sur différentes plateformes. L'IA utilise un algorithme d'évaluation de position simple qui considère plusieurs facteurs comme la hauteur des piles, les trous, et les lignes complètes potentielles.
