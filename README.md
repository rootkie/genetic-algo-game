# Introduction
This is a toy project to apply genetic algorithm to a (badly) self programmed game.

# Game Description

Given a starting position of 3 players and 1 enemy and 1 player have a ball. Player objective is to reach the finishing line of y == 128 while enemy will always chase after the player with the ball. If the player can pass the ball to any other player. If the player is caught with the ball or enemy catch the player, the game is lost. Otherwise the player wins.

# Approach
Since the enemy is programmed to deterministically move towards the ball every round, I decided to try to find a fix sequence of action (genes) of each player that in collaboration will bring the ball to the end point. The genes set of 3 players are put through the simulation to be scored and ranked together for further selection.

### Intialisation
Generate 3 random lists of actions for the 3 players and put them as a gene set for 100 gene sets.

### Selection
Top 36 gene sets would be selected. Top 16 would live to the next epoch to maintain the top performing gene set until a more dominant gene set is found.

### Crossover
I chose a single point cross over to create the next generation of genes as I feel the first few action sequence will determine the result of most simulations. Thus too many incision point for crossover will create too large a diversity of next generations which might be very inconsistent. I also added a homogenous index whereby if the population is becoming too dominant by a set of genes, there is a higher chance for the next generation to have a small mutation. This is to avoid being stuck in a local optima.

### Mutation
About 20% of the population will go through a serious mutation to explore other possible optimal solutions. If the mutation perform well they will become one of the top 16 which gets to reproduce many times and live many generations. Creating the new dominant genetic material.

# Improvements
I think the numbers could be tweaked to trade exploration for more unstable result but faster result. However this is currently a working prototype that can find a solution in reasonable amount of time (about 5-10 min)
