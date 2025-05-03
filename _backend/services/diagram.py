from matplotlib import pyplot as plt


class Diagram:

    def __init__(self, px_width, px_height):
        self.fig, self.ax1 = plt.subplots(figsize=(px_width / 100, px_height / 100))
        self.ax2 = None # 2nd x-axis
        self.ax3 = None # 3rd x-axis

        # define color scheme
        self.fig_color = "#36393F"
        self.ax_color = "#41454C"
        self.ax_gridlines_color = "#656B6F"
        self.ax_spines_color = "#41454C"
        self.ax_tick_color = "#8F979B"
        self.text_color = "#E9E9F0"
        self.text_highlight_color = "white"
        # plt.rcParams['font.family'] = 'impact'

        self.ax1.set_facecolor(self.ax_color)
        self.ax1.grid(color=self.ax_gridlines_color, axis="y", zorder=0)
        self.ax1.spines["left"].set_color(self.ax_spines_color)
        self.ax1.spines["bottom"].set_color(self.ax_spines_color)
        self.ax1.spines["right"].set_color(self.ax_spines_color)
        self.ax1.spines["top"].set_color(self.ax_spines_color)
        self.ax1.tick_params(axis="x", colors=self.ax_tick_color)
        self.ax1.tick_params(axis="y", colors=self.ax_tick_color)
        self.fig.set_facecolor(self.fig_color)



