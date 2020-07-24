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

def mate(p1, p2, kid_cancer):

	# cross over at random point
	cross = random.randint(1,len(p1)-1)
	c1 = p1[:cross]+p2[cross:len(p2)]

	# # 5% chance to mutate
	for _ in range(3):
		if roll_percentage(kid_cancer):
			i = random.randint(0,len(c1)-1)
			c1[i] = random.randint(0,1000) % 7

	return c1
	
def mutate(gene, mutation_percent):
	for i in range(len(gene)):
		if roll_percentage(mutation_percent):
			gene[i] = random.randint(0,1000) % 7
	return gene


def roll_percentage(chance):
	if chance == 0:
		chance = 0.000001
	if chance > 100:
		return True
	if random.randint(0,1000) % (1/float(chance)*100) == 0:
		return True
	return False

def pretty_print_state(state):
	state = np.asarray(state)
	res = "["
	for k,i in enumerate(state):
		s = ""
		for c,j in enumerate(i):
			if c < 2:
				s = s+ str(j) +","
			else:
				s = s+str(j)
		if k < 3:
			res = res + "[" + s+ "],"
		else:
			res = res + "[" + s+ "]"
	res += "]"
	print res
	return res

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
		
		with open ("replay.txt","a+") as f:
			res = pretty_print_state(state)
			f.write(res)
			f.write("\n")
	
	ball_x,ball_y = get_ball_xy(state)
	score = ball_y
	return score, state, ticks

start_time = time.time()

p1 = [64,50,1]
p2 = [32,25,0]
p3 = [96,25,0]
e   = [64,100,0]
enemy_speed = 2
player_speed = 1

state = str([p1,p2,p3,e]) 

gene_set = [[5, 0, 3, 0, 3, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 2, 0, 0, 6, 1, 2, 5, 3, 4, 0, 3, 6, 0, 1, 4, 0, 3, 3, 3, 0, 0, 4, 6, 4, 0, 2, 1, 6, 4, 2, 0, 0, 4, 0, 1, 4, 0, 5, 1, 0, 6, 2, 3, 1, 5, 1, 2, 4, 3, 2, 4, 1, 6, 4, 0, 5, 2, 4, 1, 5, 6, 1, 6, 4, 5, 3, 3, 3, 6, 3, 0, 6],
[2, 4, 6, 0, 5, 4, 6, 2, 2, 2, 6, 5, 0, 1, 1, 3, 0, 1, 5, 6, 3, 6, 3, 6, 4, 0, 0, 0, 0, 5, 5, 0, 0, 1, 0, 2, 6, 2, 2, 2, 2, 0, 4, 1, 6, 3, 5, 0, 4, 6, 3, 5, 3, 6, 6, 5, 2, 1, 5, 0, 4, 5, 4, 3, 5, 1, 4, 0, 0, 3, 0, 2, 5, 0, 3, 6, 5, 6, 1, 0, 5, 6, 5, 2, 1, 5, 6, 1, 6, 6, 2, 3, 1, 2, 5, 6, 1, 6, 4, 6, 0, 6, 5, 4, 6, 6, 3, 5, 4, 5, 0, 4, 0, 3, 6, 3, 6, 1, 0, 6, 3, 6, 4, 1, 3, 0, 1, 3, 1, 0, 3, 5, 5, 5, 1, 2, 3, 3, 0, 5, 6, 1, 1, 4, 1, 0, 6, 4, 0, 4, 0],
[1, 1, 6, 1, 0, 1, 1, 6, 2, 0, 1, 0, 6, 5, 3, 0, 2, 2, 5, 6, 6, 6, 3, 3, 0, 4, 0, 3, 3, 5, 0, 5, 6, 3, 1, 1, 3, 4, 3, 3, 2, 1, 2, 4, 4, 3, 0, 3, 3, 1, 2, 6, 5, 6, 0, 5, 3, 5, 3, 5, 2, 5, 4, 5, 4, 4, 5, 2, 4, 5, 5, 4, 2, 0, 0, 5, 2, 3, 6, 5, 3, 5, 2, 1, 5, 4, 5, 2, 1, 5, 4, 2, 6, 4, 2, 1, 0, 3, 3, 4, 5, 4, 5, 4, 4, 5, 4, 3, 3, 6, 3, 5, 2, 0, 0, 3, 3, 6, 3, 0, 2, 0, 2, 0, 1, 6, 3, 0, 6, 4, 3, 6, 3, 2, 5, 6, 3, 3, 5, 5, 3, 0, 4, 6, 6, 5, 0, 4, 3, 2, 5],]
gene_set = str(gene_set)


score, state, ticks = play_game(state, gene_set)
print score, ticks

print ("cache 100 rounds result --- %s seconds ---" % (time.time() - start_time))




















