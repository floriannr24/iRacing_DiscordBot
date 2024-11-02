from matplotlib import pyplot as plt


class Diagram:

    def __init__(self, px_width, px_height):
        self.fig, self.ax1 = plt.subplots(figsize=(px_width / 100, px_height / 100))
        self.ax2 = None # 2nd x-axis
        self.ax3 = None # 3rd x-axis

        # define color scheme
        self.ax_color = "#2F3136"
        self.ax_gridlines_color = "#3F434A"
        self.ax_spines_color = "#3F434A"
        self.ax_tick_color = "#C8CBD0"
        self.fig_color = "#36393F"

        self.ax1.set_facecolor(self.ax_color)
        self.ax1.grid(color=self.ax_gridlines_color, axis="y", zorder=0)
        self.ax1.spines["left"].set_color(self.ax_spines_color)
        self.ax1.spines["bottom"].set_color(self.ax_spines_color)
        self.ax1.spines["right"].set_color(self.ax_spines_color)
        self.ax1.spines["top"].set_color(self.ax_spines_color)
        self.ax1.tick_params(axis="x", colors=self.ax_tick_color)
        self.ax1.tick_params(axis="y", colors=self.ax_tick_color)
        self.fig.set_facecolor(self.fig_color)



