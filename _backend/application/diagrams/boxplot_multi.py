import statistics
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np

from diagrams.base import Base


# todo: iRating next to names?

class BoxplotMulti(Base):
    def __init__(self, input, config):
        # init
        self.boxplot = None
        self.race_completed_laps = input[0]
        self.race_not_completed_laps = input[1]
        self.drivers_raw = input[2]
        self.number_Of_Drivers = len(input[2])
        self.ymin, self.ymax, self.interval, self.showMean, self.showMedianLine = self.unpackConfig(config.options)

        # draw
        super().__init__(input, config.options.get("px_width"), config.options.get("px_height"))
        self.draw(config.name, config.options)

    def draw(self, name, options):

        self.draw_boxplot()
        self.format(options, name)

        if options.get("showLaptimes") == 1:
            self.draw_laptimes()

        if options.get("showDISC") == 1:
            self.draw_DISCDISQ()

        if self.showMedianLine:
            self.draw_medianLine()

        if options.get("showDISC") == 0:
            self.ax.set_xticks(np.arange(1, self.number_Of_Drivers + 1))
            self.ax.set_xticklabels(self.drivers_raw, rotation=45, rotation_mode="anchor", ha="right")
        else:
            self.ax.set_xticks(np.arange(1, self.number_Of_Drivers + 1))
            self.ax.set_xticklabels(self.drivers_raw, rotation=45, rotation_mode="anchor", ha="right")

        try:
            self.drivername_bold(name)
            self.userBoxplot_brightBlue(name)
        except ValueError:
            pass

        plt.tight_layout()
        plt._showMenu()

    def userBoxplot_brightBlue(self, name):
        index = self.drivers_raw.index(name)
        userBP = self.boxplot["boxes"][index]
        userBP.set_facecolor("#90C6F0")

    def drivername_bold(self, name):
        index = self.drivers_raw.index(name)
        userBP = self.ax.get_xticklabels()[index]
        userBP.set_fontweight("bold")

    def draw_boxplot(self):

        self.boxplot = self.ax.boxplot(self.race_completed_laps,
                                       patch_artist=True,
                                       boxprops=dict(facecolor="#0084F2", color="#000000"),
                                       flierprops=dict(markeredgecolor='#000000'),
                                       medianprops=dict(color="#000000"),
                                       whiskerprops=dict(color="#000000"),
                                       capprops=dict(color="#000000"),
                                       zorder=2,
                                       widths=0.7,
                                       showmeans=self.showMean,
                                       meanprops=dict(marker="o", markerfacecolor="red", fillstyle="full",
                                                      markeredgecolor="None")
                                       )

    def format(self, options, name):

        try:
            if options.get("setYAxis") == 0:
                self.calculateYMaxMin(name)
        except ValueError:
            self.ymin = 0
            self.ymax = 150

        number_of_seconds_shown = np.arange(self.ymin, self.ymax + self.interval, self.interval)
        self.ax.set(xlim=(0, self.number_Of_Drivers + 1), ylim=(self.ymin, self.ymax))
        self.ax.set_yticks(number_of_seconds_shown)
        self.ax.set_yticklabels(self.calculateMinutesYAxis(number_of_seconds_shown))

    def draw_laptimes(self):
        scatter = []
        for i, lapdata in enumerate(self.race_completed_laps):
            x = np.random.normal(i + 1, 0.06, len(lapdata))
            scatter.append(x)
        for i, data in enumerate(self.race_completed_laps):
            self.ax.scatter(scatter[i], self.race_completed_laps[i],
                            zorder=4,
                            alpha=0.5,
                            c="yellow",
                            s=8
                            )

    def draw_DISCDISQ(self):
        self.ax.boxplot(self.race_not_completed_laps,
                        patch_artist=True,
                        boxprops=dict(facecolor="#6F6F6F", color="#000000"),
                        flierprops=dict(markeredgecolor='#000000'),
                        medianprops=dict(color="#000000", linewidth=2),
                        whiskerprops=dict(color="#000000"),
                        capprops=dict(color="#000000"),
                        zorder=2,
                        widths=0.7
                        )

    def draw_medianLine(self):

        x1 = None
        y1 = None

        try:
            index = self.drivers_raw.index("Florian Niedermeier2")
            user_boxplot_data = self.race_completed_laps[index]
            user_median = statistics.median(user_boxplot_data)
            y1 = [user_median, user_median]
            x1 = [0, 100]

        except ValueError:
            pass

        plt.plot(x1, y1, zorder=3, linestyle="dashed", color="#C2C5CA")

    def calculateYMaxMin(self, name):
        index = self.drivers_raw.index(name) * 2
        self.ymin = round(self.boxplot["caps"][0].get_ydata()[0], 0) - 1
        self.ymax = round(self.boxplot["caps"][index + 1].get_ydata()[0], 0) + 2

    def calculateMinutesYAxis(self, number_of_seconds_shown):

        yticks = []
        for sec in number_of_seconds_shown:
            sec_rounded = round(sec, 2)
            td_raw = str(timedelta(seconds=sec_rounded))

            if "." not in td_raw:
                td_raw = td_raw + ".000000"

            td_minutes = td_raw.split(":", 1)[1]
            yticks.append(td_minutes[:-3])

        return yticks

    def unpackConfig(self, options):

        if options.get("setYAxis") == 1:
            ymin = options.get("minVal")
            ymax = options.get("maxVal")
        else:
            ymin, ymax = None, None

        if options.get("setYAxisInterval") == 1:
            interval = options.get("interval")
        else:
            interval = 0.5

        if options.get("showDISC") == 0:
            number_Of_Drivers_Not_Completed = len([data for data in self.race_not_completed_laps if not not data])
            self.number_Of_Drivers = self.number_Of_Drivers - number_Of_Drivers_Not_Completed
            self.drivers_raw = self.drivers_raw[:-number_Of_Drivers_Not_Completed or None]

        if options.get("showMedianLine") == 1:
            showMedianLine = True
        else:
            showMedianLine = False

        if options.get("showMean") == 1:
            showMean = True
        else:
            showMean = False

        return ymin, ymax, interval, showMean, showMedianLine
