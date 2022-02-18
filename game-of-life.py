import os
import random
import time
from typing import Union

import numpy
import pylab
import imageio
import glob

from rich import print
from rich import progress

# TODO: make it faster by using numpy arrays and asyncio


class Patterns:
    """A class to store all the patterns"""

    def __init__(self):
        self.patterns = {}
        self.glider = numpy.array([[0,    0, 1],
                                   [1,  0, 1],
                                   [0,  1, 1],
                                   [0, 0, 1]])
        self.block = numpy.array([[1, 1], [1, 1]])
        self.beacon = numpy.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]])
        self.pulsar = numpy.array([
            [0, 1, 0, 1, 0],
            [1, 0, 0, 0, 1],
            [0, 1, 0, 1, 0],
            [1, 0, 0, 0, 1],
            [0, 1, 0, 1, 0],
        ])
        self.spaceship = numpy.array([[0, 1, 0], [1, 0, 1], [0, 1, 0]])

        self.unbounded = [[1, 1, 1, 0, 1],
                          [1, 0, 0, 0, 0],
                          [0, 0, 0, 1, 1],
                          [0, 1, 1, 0, 1],
                          [1, 0, 1, 0, 1]]

        glider_gun = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                       0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0,
                       0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,
                       0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
                      [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0,
                       0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 1, 1,
                       0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 1, 0,
                       0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0,
                       0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                      [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

        self.glider_gun = glider_gun


class GameOfLife:
    def __init__(
            self, N: Union[int, None] = 100, T: int = 200, render: bool = True, pattern=None
    ):
        """Set up Conway's Game of Life.
        :param N: The size of the grid.
        :param T: The number of generations to evolve."""
        if not pattern and not any([N, T]):
            print(
                "[red] Please provide a pattern or a size and a number of generations[/red]"
            )
            return

        # Here we create two grids to hold the old and new configurations.
        # This assumes an N*N grid of points.

        # Each point is either alive or dead, represented by integer values of 1 and 0, respectively.
        self.N = N if not pattern else (len(pattern) + 10)
        self.old_grid = numpy.zeros(N * N, dtype="i").reshape(N, N)
        self.new_grid = numpy.zeros(N * N, dtype="i").reshape(N, N)
        self.T = T  # The maximum number of generations
        # Whether or not to render the animation, if not, it will just save the generations
        self.render = render

        # Try to clear console
        try:
            os.system("cls" if os.name == "nt" else "clear")
        except:
            pass

        # Check if "generations" folder exists, if not, create it
        if not os.path.exists("generations"):
            os.makedirs("generations")
            print("[red]Generations folder was not found, so it was created[/red]")

        print(
            """
		_______________________________

		Conway's [bold blue]Game of Life[/bold blue]

		By [i green]Dhravya Shah[/i green]

		_______________________________
		"""
        )

        if pattern:
            self.patterns = Patterns()
            print("[bold blue]Using pattern:[/bold blue]", pattern)
            # Create numpy array from pattern but with the correct size
            pattern = self.patterns.__getattribute__(pattern)
            # Adjust N to match the pattern
            self.old_grid = numpy.zeros(N*N, dtype="i").reshape(N, N)
            # Add the pattern to middle
            for i in range(len(pattern)):
                for j in range(len(pattern[i])):
                    try:
                        self.old_grid[i+5][j+5] = pattern[i][j]
                    except IndexError:
                        continue
        else:
            for i in range(0, self.N):
                for j in range(0, self.N):
                    if random.randint(0, 100) < 15:
                        self.old_grid[i][j] = 1
                    else:
                        self.old_grid[i][j] = 0

        print("[blue]Initialised the Game of life[/blue]", ":white_check_mark:")

    def live_neighbours(self, i, j):
        """Count the number of live neighbours around point (i, j)."""
        s = 0  # The total number of live neighbours.
        # Loop over all the neighbours.
        for x in [i - 1, i, i + 1]:
            for y in [j - 1, j, j + 1]:
                if x == i and y == j:
                    continue  # Skip the current point itself - we only want to count the neighbours!
                if x != self.N and y != self.N:
                    s += self.old_grid[x][y]
                # The remaining branches handle the case where the neighbour is off the end of the grid.
                # In this case, we loop back round such that the grid becomes a "toroidal array".
                elif x == self.N and y != self.N:
                    s += self.old_grid[0][y]
                elif x != self.N and y == self.N:
                    s += self.old_grid[x][0]
                else:
                    s += self.old_grid[0][0]
        return s

    def play(self):
        """Play Conway's Game of Life."""

        # Write the initial configuration to file.
        pylab.pcolormesh(self.old_grid)
        pylab.colorbar()
        pylab.savefig("generation0.png")
        pylab.savefig("generations/generation0.png")

        t = 1  # Current time level
        # How frequently we want to output a grid configuration.
        write_frequency = 5
        for t in progress.track(
            range(0, self.T), description="[bold blue]Generating generations[/bold blue]"
        ):  # Evolve!

            # Convay's Game of Life rules:
            # 1. Any live cell with fewer than two live neighbours dies, as if caused by under-population/starvation.
            # 2. Any live cell with two or three live neighbours lives on to the next generation.
            # 3. Any live cell with more than three live neighbours dies, as if by overcrowding.

            # 4. New cells are born if a dead cell has exactly three live neighbours.

            # Loop over each cell of the grid and apply Conway's rules.
            for i in range(self.N):
                for j in range(self.N):
                    live = self.live_neighbours(i, j)
                    if self.old_grid[i][j] == 1 and live < 2:
                        self.new_grid[i][j] = 0  # Dead from starvation.
                    elif self.old_grid[i][j] == 1 and (live == 2 or live == 3):
                        self.new_grid[i][j] = 1  # Continue living.
                    elif self.old_grid[i][j] == 1 and live > 3:
                        self.new_grid[i][j] = 0  # Dead from overcrowding.

                    elif self.old_grid[i][j] == 0 and live == 3:
                        self.new_grid[i][j] = 1  # Alive from reproduction.

            # Output the new configuration.
            if t % write_frequency == 0:
                self.save_grid(self.new_grid, t)

            # The new configuration becomes the old configuration for the next generation.
            self.old_grid = self.new_grid.copy()

        print(
            "[green]Generations saved to folder generations[/green]", ":partying_face:"
        )
        if self.render:
            self.animate_folder()

    def save_grid(self, grid, t):
        """Save the grid to file."""
        pylab.pcolormesh(grid)
        pylab.savefig(f"generations/generation{t}.png", dpi=300)

    @staticmethod
    def animate_folder():
        """Makes an animated gif from a folder of images."""
        images = []

        for filename in progress.track(
                glob.glob("generations/*.png"),
                description="Rendering the animation :rocket: ...",
        ):
            images.append(imageio.imread(filename))

        # Removing the first image as it is the wrong size.
        images.pop(0)

        imageio.mimsave("animation.gif", images, "GIF", duration=0.5)

        # Delete all the images in generatinos folder.
        try:
            for file in progress.track(
                    glob.glob("generations/*.png"),
                    description="Attempting to delete the images ...",
            ):
                os.remove(file)
        except:
            print("[red]Error[/red] : Could not delete the images.")

        # FIXME: Only works on windows.
        print("[blue]Opening the animation[/blue]")
        os.system("start animation.gif")

        print(
            "[green]Done![/green] :white_check_mark: Closing in 5 seconds. Thanks for checking out my project."
        )
        time.sleep(5)


if __name__ == "__main__":
    # Calculate the time it takes to run the program.
    start_time = time.time()
    game = GameOfLife(N=50, T=500, pattern="glider_gun", render=True)
    game.play()
    print(
        "[green]Time taken to run the program[/green]",
        ":alarm_clock:",
        time.time() - start_time,
        "seconds.",
    )
