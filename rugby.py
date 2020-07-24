import numpy as np
import random
import time
from functools import wraps
import ast


def memoize(function):
    memo = {}
    @wraps(function)
    def wrapper(*args):
        try:
            return memo[args]
        except KeyError:
            rv = function(*args)
            memo[args] = rv
            return rv
    return wrapper


def perform_action(state, player, action, speed):
	# actions = [fwd, bkw, left, right, pass1, pass2, pass3]
	# if action cannot be performed, perform nothing

	lose_flag = False
	
	def move(p, action, speed):
	
		lose_flag = False
		if action == 0:
			p[1] = p[1] + speed
			if p[1] > 128:
				p[1] = 128
				lose_flag = True
		elif action == 1:
			p[1] = p[1] - speed
			if p[1] < 0:
				p[1] = 0
		elif action == 2:
			p[0] = p[0] - speed
			if p[0] < 0:
				p[0] = 0
		elif action == 3:
			p[0] = p[0] + speed
			if p[0] > 128:
				p[0] = 128
		
		return p, lose_flag
	
	p1,p2,p3,e = np.asarray(state)
	if player == 1:
		if action <= 3:
			p1, lose_flag = move(p1, action, speed)
		
		# elif have ball
		elif p1[2] == 1:
			if action == 5:
				if check_between(p1,p2,e):
					# print "Enemy caught the ball"
					lose_flag = True
					return np.asarray(state), lose_flag
				p1[2] = 0
				p2[2] = 1
			elif action == 6:
				if check_between(p1,p3,e):
					# print "Enemy caught the ball"
					lose_flag = True
					return np.asarray(state), lose_flag
				p1[2] = 0
				p3[2] = 1
	elif player == 2:
		if action <= 3:
			p2, lose_flag = move(p2, action, speed)
		elif p2[2] == 1:
			if action == 4:
				if check_between(p2,p1,e):
					# print "Enemy caught the ball"
					lose_flag = True
					return np.asarray(state), lose_flag
				p2[2] = 0
				p1[2] = 1
			elif action == 6:
				if check_between(p2,p3,e):
					# print "Enemy caught the ball"
					lose_flag = True
					return np.asarray(state), lose_flag
				p2[2] = 0
				p3[2] = 1
	elif player == 3:
		if action <= 3:
			p3, lose_flag = move(p3, action, speed)
		elif p3[2] == 1:
			if action == 4:
				if check_between(p3,p1,e):
					# print "Enemy caught the ball"
					lose_flag = True
					return np.asarray(state), lose_flag
				p3[2] = 0
				p1[2] = 1
			elif action == 5:
				if check_between(p3,p2,e):
					# print "Enemy caught the ball"
					lose_flag = True
					return np.asarray(state), lose_flag
				p3[2] = 0
				p2[2] = 1
	else:
		print "Bad player", player
	
	state_arr = [p1,p2,p3,e]
	
	return state_arr, lose_flag
	
def get_ball_xy(state):
	for pos in state:
		pos = np.squeeze(np.asarray(pos))
		if pos[2]:
			return pos[0],pos[1]
	
	return None
	
def check_between(src, dst, mid):
	x1,y1 = src[:2]
	x2,y2 = dst[:2]
	x3,y3 = mid[:2]
	
	if x1 == x2:
		# vertical line
		if x3 == x1 and y3 >= min(y1,y2) and y3 <= max(y1,y2):
			return True
		return False
	if y1 == y2:
		# horizontal line
		if y3 == y1 and x3 >= min(x1,x2) and x3 <= max(x1,x2):
			return True
		return False
	
	alphax = (x3-x1)/(x2-x1)
	alphay = (y3-y1)/(y2-y1)
	
	if alphax == alphay:
		if alphax >= 0 and alphax <= 1:
			return True
	return False

def enemy_move(ex,ey,bx,by, speed):
	dx,dy = (bx-ex,by-ey)
	if dx == 0 and dy == 0:
		# on top of the ball
		# print "Enemy caught the ball"
		return False
	
	if abs(dx)+abs(dy) < speed:
		# within reach in this round
		return False
	
	stepx,stepy = 0,0
	
	for _ in range(speed):
		if abs(dx) > abs(dy):
			ex += dx/abs(dx)
			dx,dy = (bx-ex,by-ey)
		else:
			ey += dy/abs(dy)
			dx,dy = (bx-ex,by-ey)

	e = [ex, ey, 0]

	return e

def generate_gene(gene_length):
	gene = []
	for i in range(gene_length):
		gene.append(random.randint(0,1000) % 7)

	return gene

def mate(p1, p2, mutate_percent):

	# cross over at random point
	cross = random.randint(1,len(p1)-1)
	c1 = p1[:cross]+p2[cross:len(p2)]

	# # 5% chance to mutate
	for _ in range(3):
		if roll_percentage(mutate_percent):
			i = random.randint(0,len(c1)-1)
			c1[i] = random.randint(0,1000) % 7

	return c1
	
def mutate(gene, mutation_percent):
	for i in range(len(gene)):
		if roll_percentage(mutation_percent):
			gene[i] = random.randint(0,1000) % 7
	return gene


def roll_percentage(chance):
	if chance <= 0:
		return False
	if chance > 100:
		return True
	if random.randint(0,1000) % (1/float(chance)*100) == 0:
		return True
	return False

@memoize
def play_game(state, gene_set):
	gene_set = ast.literal_eval(gene_set)
	state = ast.literal_eval(state)
	state = np.matrix(state)
	p1_gene, p2_gene, p3_gene = gene_set

	
	enemy_speed = 2
	player_speed = 1
	
	ticks = 0
	while True:
		ticks = ticks+1
		ball_x, ball_y = get_ball_xy(state)
		p1,p2,p3,e = np.asarray(state)
		
		# enemy move
		ex,ey = e[:2]
		e = enemy_move(ex,ey,ball_x,ball_y, enemy_speed)
		if not e:
			break
		state = np.matrix([p1,p2,p3,e])
	
		# player moves
		action = p1_gene[ticks]

		state, lose_flag  = perform_action(state, 1, action, player_speed)
		state  = np.matrix(state)
		if lose_flag:
			break

		action = p2_gene[ticks]
		state, lose_flag  = perform_action(state, 2, action, player_speed)
		state  = np.matrix(state)
		if lose_flag:
			break
		
		action = p3_gene[ticks]
		state, lose_flag  = perform_action(state, 3, action, player_speed)
		state  = np.matrix(state)
		if lose_flag:
			break
		
		if ticks > 150:
			break
	
	ball_x,ball_y = get_ball_xy(state)
	score = ball_y
	return score, state, ticks

# start_time = time.time()

# p1 = [64,50,1]
# p2 = [32,25,0]
# p3 = [96,25,0]
# e   = [64,100,0]
# enemy_speed = 2
# player_speed = 1

# state = str([p1,p2,p3,e]) 

# gene_set = [generate_gene(310),generate_gene(310),generate_gene(310)]
# gene_set = str(gene_set)


# score, state, ticks = play_game(state, gene_set)
# print score, ticks

# print ("cache 100 rounds result --- %s seconds ---" % (time.time() - start_time))


while True:
	population_size = 100

	mutation_counter = 0

	p1_gene_pool = [generate_gene(151) for _ in range(population_size)]
	p2_gene_pool = [generate_gene(151) for _ in range(population_size)]
	p3_gene_pool = [generate_gene(151) for _ in range(population_size)]

	epoch = 0

	prev_top_score = 50


	for epoch in range(50000):
		scorelist_arr = []
		for i in range(len(p1_gene_pool)):
			# print "game ", i
			gene_set = [p1_gene_pool[i], p2_gene_pool[i], p3_gene_pool[i]]
			gene_set = str(gene_set) # allows for caching
			p1 = [64,50,1]
			p2 = [32,25,0]
			p3 = [96,25,0]
			e   = [64,100,0]
			enemy_speed = 2
			player_speed = 1

			#state = np.matrix([p1,p2,p3,e]) 
			state = str([p1,p2,p3,e]) # allows for caching

			score, state, ticks = play_game(state, gene_set)
			
			# calculate score
			ball_x, ball_y = get_ball_xy(state)
			score = ball_y
			scorelist = dict()
			scorelist["index"] = i
			scorelist["score"] = score
			scorelist["ball"] = (ball_x,ball_y)
			scorelist_arr.append(scorelist)



		
		
		# Creating next epoch
		
		top_candidates = sorted(scorelist_arr, key=lambda k: k['score'], reverse=True)
		
		# winning the game, record the gene set and reset
		if top_candidates[0]["score"] == 128:
			winning_index = top_candidates[0]["index"]
			print winning_index
			print p1_gene_pool[winning_index]
			print p2_gene_pool[winning_index]
			print p3_gene_pool[winning_index]
			with open("log.txt", "a+") as f:
				f.write("\n")
				f.write("Winning index "+str(winning_index) + "\nEpoch "+str(epoch)+"\n")
				f.write(str(p1_gene_pool[winning_index])+"\n")
				f.write(str(p2_gene_pool[winning_index])+"\n")
				f.write(str(p3_gene_pool[winning_index])+"\n")
				f.write("-"*80)
			break
		
		
		
		tier1 = top_candidates[:16]
		tier2 = top_candidates[16:26]
		tier3 = top_candidates[26:36]
		new_p1g = []
		new_p2g = []
		new_p3g = []
		
		
		
		homo_index1 = max([p1_gene_pool.count(x) for x in p1_gene_pool])
		homo_index2 = max([p2_gene_pool.count(x) for x in p2_gene_pool])
		homo_index3 = max([p3_gene_pool.count(x) for x in p3_gene_pool])
		for i in range(16):
			candidate_i = top_candidates[i]["index"]
			new_p1g.append(p1_gene_pool[candidate_i])
			new_p2g.append(p2_gene_pool[candidate_i])
			new_p3g.append(p3_gene_pool[candidate_i])
		
		# elitist reproductions
		not_mated = range(16)
		while not_mated:
			p1 = random.choice(not_mated)
			not_mated.remove(p1)
			p2 = random.choice(not_mated)
			not_mated.remove(p2)
			p1 = tier1[p1]["index"]
			p2 = tier1[p2]["index"]
			for _ in range(2):
				new_p1g.append(mate(p1_gene_pool[p1], p1_gene_pool[p2], max(5, mutation_counter/10, homo_index1)))
				new_p2g.append(mate(p2_gene_pool[p1], p2_gene_pool[p2], max(5, mutation_counter/10, homo_index2)))
				new_p3g.append(mate(p3_gene_pool[p1], p3_gene_pool[p2], max(5, mutation_counter/10, homo_index3)))
		
		not_mated = range(10)
		while not_mated:
			p1 = random.choice(not_mated)
			not_mated.remove(p1)
			p2 = random.choice(not_mated)
			not_mated.remove(p2)
			p1 = tier2[p1]["index"]
			p2 = tier2[p2]["index"]
			for _ in range(2):
				new_p1g.append(mate(p1_gene_pool[p1], p1_gene_pool[p2], max(5, mutation_counter/10, homo_index1)))
				new_p2g.append(mate(p2_gene_pool[p1], p2_gene_pool[p2], max(5, mutation_counter/10, homo_index2)))
				new_p3g.append(mate(p3_gene_pool[p1], p3_gene_pool[p2], max(5, mutation_counter/10, homo_index3)))
		
		
		not_mated = range(10)
		while not_mated:
			p1 = random.choice(not_mated)
			not_mated.remove(p1)
			p2 = random.choice(not_mated)
			not_mated.remove(p2)
			p1 = tier3[p1]["index"]
			p2 = tier3[p2]["index"]
			for _ in range(1):
				new_p1g.append(mate(p1_gene_pool[p1], p1_gene_pool[p2], max(5, mutation_counter/10, homo_index1)))
				new_p2g.append(mate(p2_gene_pool[p1], p2_gene_pool[p2], max(5, mutation_counter/10, homo_index2)))
				new_p3g.append(mate(p3_gene_pool[p1], p3_gene_pool[p2], max(5, mutation_counter/10, homo_index3)))
		
		
		
			
		
		# mutations
		new_pop_size = len(new_p1g)
		# chance to mutate. more likely to mutate early than later. 
		# explore early, prevent running out of minima late
		while new_pop_size < population_size:
			for j in top_candidates:
				candidate_j = j["index"]
				if roll_percentage(50-epoch/20):
					t_gene = p1_gene_pool[candidate_j]
					new_p1g.append(mutate(t_gene,50-epoch/20))
					t_gene = p2_gene_pool[candidate_j]
					new_p2g.append(mutate(t_gene,50-epoch/20))
					t_gene = p3_gene_pool[candidate_j]
					new_p3g.append(mutate(t_gene,50-epoch/20))
					new_pop_size += 1
					if new_pop_size > population_size: break
			
		p1_gene_pool = new_p1g
		p2_gene_pool = new_p2g
		p3_gene_pool = new_p3g

		if prev_top_score == top_candidates[0]["score"]:
			mutation_counter = mutation_counter + 1
			# if mutation_counter > 50:
				# for i in range(5):
					# print p1_gene_pool[i]
			# if mutation_counter > 50:
				# # nuke and restart
				
				# break
		else:
			prev_top_score = top_candidates[0]["score"]
			mutation_counter = 0
		
		print epoch, top_candidates[0]["ball"], len(p1_gene_pool), mutation_counter, homo_index1, homo_index2, homo_index3





















