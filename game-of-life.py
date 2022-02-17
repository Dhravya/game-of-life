import os
import random

import numpy
import pylab
import imageio
import glob

class GameOfLife:

	def __init__(self, N=100, T=200, render=True):
		""" Set up Conway's Game of Life. """
		# Here we create two grids to hold the old and new configurations.
		# This assumes an N*N grid of points.
		# Each point is either alive or dead, represented by integer values of 1 and 0, respectively.
		self.N = N
		self.old_grid = numpy.zeros(N*N, dtype='i').reshape(N,N)
		self.new_grid = numpy.zeros(N*N, dtype='i').reshape(N,N)
		self.T = T # The maximum number of generations
		self.render = render # Whether or not to render the animation, if not, it will just save the generations

		# Set up a random initial configuration for the grid.
		for i in range(0, self.N):
			for j in range(0, self.N):
				if(random.randint(0, 100) < 15):
					self.old_grid[i][j] = 1
				else:
					self.old_grid[i][j] = 0
		
	def live_neighbours(self, i, j):
		""" Count the number of live neighbours around point (i, j). """
		s = 0 # The total number of live neighbours.
		# Loop over all the neighbours.
		for x in [i-1, i, i+1]:
			for y in [j-1, j, j+1]:
				if(x == i and y == j):
					continue # Skip the current point itself - we only want to count the neighbours!
				if(x != self.N and y != self.N):
					s += self.old_grid[x][y]
				# The remaining branches handle the case where the neighbour is off the end of the grid.
				# In this case, we loop back round such that the grid becomes a "toroidal array".
				elif(x == self.N and y != self.N):
					s += self.old_grid[0][y]
				elif(x != self.N and y == self.N):
					s += self.old_grid[x][0]
				else:
					s += self.old_grid[0][0]
		return s


	def play(self):
		""" Play Conway's Game of Life. """

		# Write the initial configuration to file.
		pylab.pcolormesh(self.old_grid)
		pylab.colorbar()
		pylab.savefig("generation0.png")
		pylab.savefig("generations/generation0.png")

		t = 1 # Current time level
		write_frequency = 5 # How frequently we want to output a grid configuration.
		while t <= self.T: # Evolve!
			print(f"At time level {t}")

			# Convay's Game of Life rules:
			# 1. Any live cell with fewer than two live neighbours dies, as if caused by under-population/starvation.
			# 2. Any live cell with two or three live neighbours lives on to the next generation.
			# 3. Any live cell with more than three live neighbours dies, as if by overcrowding.

			# 4. New cells are born if a dead cell has exactly three live neighbours.

			# Loop over each cell of the grid and apply Conway's rules.
			for i in range(self.N):
				for j in range(self.N):
					live = self.live_neighbours(i, j)
					if(self.old_grid[i][j] == 1 and live < 2):
						self.new_grid[i][j] = 0 # Dead from starvation.
					elif(self.old_grid[i][j] == 1 and (live == 2 or live == 3)):
						self.new_grid[i][j] = 1 # Continue living.
					elif(self.old_grid[i][j] == 1 and live > 3):
						self.new_grid[i][j] = 0 # Dead from overcrowding.

					elif(self.old_grid[i][j] == 0 and live == 3):
						self.new_grid[i][j] = 1 # Alive from reproduction.

			# Output the new configuration.
			if(t % write_frequency == 0):
				self.save_grid(self.new_grid, t)

			# The new configuration becomes the old configuration for the next generation.
			self.old_grid = self.new_grid.copy()

			# Move on to the next time level
			t += 1

		if self.render:
			self.animate_folder()

	def save_grid(self, grid, t):
		""" Save the grid to file. """
		pylab.pcolormesh(grid)
		pylab.savefig(f"generations/generation{t}.png", dpi=300)

	@staticmethod
	def animate_folder():
		"""Makes an animated gif from a folder of images."""
		images = []
		for filename in glob.glob('generations/*.png'):
			images.append(imageio.imread(filename))

		# Removing the first image as it is the wrong size.
		images.pop(0)

		imageio.mimsave('animation.gif', images, 'GIF', duration=0.5)

		# Delete all the images in generatinos folder.
		for file in glob.glob('generations/*.png'):
			os.remove(file)

		# FIXME: Only works on windows.
		os.system("start animation.gif")
		

if __name__ == "__main__" :
	game = GameOfLife(N = 100, T = 100)
	game.play()
