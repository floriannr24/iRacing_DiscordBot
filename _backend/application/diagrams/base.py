from matplotlib import pyplot as plt


class Base:

    def __init__(self, input, px_width, px_height):
        self.input = input
        self.fig, self.ax = plt.subplots(figsize=(px_width / 100, px_height / 100))

        # define color scheme
        self.ax_color = "#2F3136"
        self.ax_gridlines_color = "#3F434A"
        self.ax_spines_color = "#3F434A"
        self.ax_tick_color = "#C8CBD0"
        self.fig_color = "#36393F"

        self.ax.set_facecolor(self.ax_color)
        self.ax.grid(color=self.ax_gridlines_color, axis="y", zorder=0)
        self.ax.spines["left"].set_color(self.ax_spines_color)
        self.ax.spines["bottom"].set_color(self.ax_spines_color)
        self.ax.spines["right"].set_color(self.ax_spines_color)
        self.ax.spines["top"].set_color(self.ax_spines_color)
        self.ax.tick_params(axis="x", colors=self.ax_tick_color)
        self.ax.tick_params(axis="y", colors=self.ax_tick_color)
        self.fig.set_facecolor(self.fig_color)


