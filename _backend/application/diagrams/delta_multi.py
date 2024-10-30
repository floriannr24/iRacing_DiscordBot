import statistics
import matplotlib.pyplot as plt
import numpy as np

from diagrams.base import Base


# ToDo: select only a handful of players for comparison


class DeltaMulti(Base):
    def __init__(self, input, px_width, px_height):
        super().__init__(input, px_width, px_height)
        self.number_of_laps = input[0]["laps_completed"] + 1

        for x in input:
            print(x)

        self.draw()

    def draw(self):

        # set line color
        colorList_top3 = ["#FFD900", "#CFCEC9", "#D4822A"]
        colorList_rest = ['#1f77b4', '#2ca02c', '#A3E6A3', '#d62728', '#811818', '#8261FF', '#8c564b', '#e377c2',
                          '#919191', '#CFCF4B', '#97ED27', '#17becf']

        self.ax.set_prop_cycle("color", colorList_rest)

        # split list into "top3" and "rest"
        top3, rest = self.splitDataTop3(self.input)
        top3.reverse()

        # draw plots
        counter = 2
        for i in range(0, len(top3), 1):
            data = top3[i]["delta"]
            self.ax.plot(data, color=colorList_top3[counter])
            counter = counter-1

        for i in range(0, len(rest), 1):
            self.ax.plot(rest[i]["delta"])

        # formatting
        steps = 5
        bottom_border = self.calculateYMin()
        y_ticklabels = self.createYTickLabels(list(np.arange(0, bottom_border, steps)))

        self.ax.set(xlim=(-0.5, self.number_of_laps - 0.5), ylim=(-5, bottom_border))
        self.ax.set_xticks(np.arange(0, self.number_of_laps))
        self.ax.set_xlabel("Laps", color="white")
        self.ax.set_yticks(np.arange(0, bottom_border, steps))
        self.ax.set_yticklabels(y_ticklabels)
        self.ax.set_ylabel("Cumulative gap to leader in seconds", color="white")
        self.ax.legend(self.extractDrivers(), loc="center left", facecolor="#36393F", labelcolor="white",
                       bbox_to_anchor=(1.05, 0.5), labelspacing=0.5, edgecolor="#7D8A93")
        # ax.set_title("Race report", pad="20.0", color="white")
        self.ax.invert_yaxis()
        plt.tick_params(labelright=True)

        plt.tight_layout()
        plt._showMenu()

    def calculateYMin(self):
        deltaAtEnd = []

        for lapdata in self.input:
            indexLastLap = len(lapdata["delta"]) - 1
            deltaAtEnd.append(lapdata["delta"][indexLastLap])
        return 5 * round(statistics.median(deltaAtEnd) * 1.5 / 5)

    def extractDrivers(self):
        return [lapdata["driver"] for lapdata in self.input]

    def createYTickLabels(self, list):
        for i, x in enumerate(list, 0):
            if not i % 2 == 0:
                list[i] = ""
        return list

    def splitDataTop3(self, laps):

        top3 = []
        rest = []

        for data in laps:
            if data["finish_position"] <= 3:
                top3.append(data)
            else:
                rest.append(data)

        return top3, rest

    def unpackConfig(self):
        pass



