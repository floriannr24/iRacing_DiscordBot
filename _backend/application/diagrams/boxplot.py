import math
import statistics
from datetime import timedelta
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from _backend.application.diagrams.diagram import Diagram
from _backend.application.diagrams.images.imageSrc import readImagesForCarId


# todo: iRating next to names?

class BoxplotDiagram(Diagram):
    def __init__(self, data):
        self.boxplot = None

        self.laps = self.getLaps(data)
        self.finishPositions = self.getFinishPositions(data)
        self.driverNames = self.getDriverNames(data)
        self.userDriverName = self.getUserDriverName(data)
        self.seriesName = self. getSeriesName(data)
        self.carIds = self.getCarIds(data)

        numberOfDrivers = len(self.driverNames)

        super().__init__(50*numberOfDrivers, 650)
        self.draw()

    def getDriverNames(self, data):
        return [driver["name"] for driver in data["data"]["drivers"]]

    def draw(self):

        self.boxplot = self.drawBoxplot()

        # format boxplot
        yMin, yMax = self.calculateYMinMax(self.laps)

        self.limitYAxis(yMin, yMax)
        self.setYLabels(yMin, yMax)
        self.setXLabels(self.driverNames)
        self.setTitle()

        # if options.get("showLaptimes") == 1:
        #     self.draw_laptimes()
        #
        #
        # self.draw_medianLine()
        #
        # if options.get("showDISC") == 0:
        #     self.ax.set_xticks(np.arange(1, self.number_Of_Drivers + 1))
        #     self.ax.set_xticklabels(self.drivers_raw, rotation=45, rotation_mode="anchor", ha="right")
        # else:
        #     self.ax.set_xticks(np.arange(1, self.number_Of_Drivers + 1))
        #     self.ax.set_xticklabels(self.drivers_raw, rotation=45, rotation_mode="anchor", ha="right")

        # todo: parameterize
        showLaptimes = True
        showMedian = False

        self.drawDISCDISQ()

        if (showLaptimes):
            self.drawLaptimes()

        if (showMedian and self.userDriverName):
            self.colorMedianLineFasterSlower()

        if (self.userDriverName):
            try:
                self.drivername_bold(self.userDriverName)
                self.userBoxplot_brightBlue(self.userDriverName)
            except ValueError:
                pass

        plt.tight_layout()
        # plt.subplots_adjust(left=0.08, right=0.98, top=0.93, bottom=0.38)
        plt.show()
        # plt.savefig("figure.png")

    def setTitle(self):
        self.ax1.set_title(self.seriesName, color="#C8CBD0", size=15, fontweight="1000", pad=10)

    def userBoxplot_brightBlue(self, name):
        index = self.driverNames.index(name)
        if not self.finishPositions[index] == "DISC" or not self.finishPositions[index] == "DISQ":
            userBP = self.boxplot["boxes"][index]
            userBP.set_facecolor("#a6cfff")

    def drivername_bold(self, name):
        index = self.driverNames.index(name)
        ax1 = self.ax1.get_xticklabels()[index]
        ax1.set_fontweight(1000)
        ax2 = self.ax2.get_xticklabels()[index]
        ax2.set_fontweight(1000)

    def colorMedianLineFasterSlower(self):
        medianTimeOfUserdriver = self.findMedianOfUserdriver(self.userDriverName)
        for median in self.boxplot["medians"]:
            medianTime = median.get_ydata()[0]
            if medianTime == medianTimeOfUserdriver:
                continue
            elif medianTime < medianTimeOfUserdriver:
                median.set(color="#ff0000")
            elif medianTime > medianTimeOfUserdriver:
                median.set(color="#22ff1a")

    def findMedianOfUserdriver(self, name):
        index = self.driverNames.index(name)
        return self.boxplot["medians"][index].get_ydata()[0]

    def getLaps(self, data):
        return [driver["laps"] for driver in data["data"]["drivers"]]

    def setYLabels(self, ymin, ymax):
        number_of_seconds_shown = np.arange(ymin, ymax + 0.5, 0.5)
        self.ax1.set_yticks(number_of_seconds_shown)
        self.ax1.set_yticklabels(self.calculateMinutesYAxis(number_of_seconds_shown), fontsize="large")

    def drawBoxplot(self):

        lineColor = "#000000"

        return self.ax1.boxplot(self.laps,
                                patch_artist=True,
                                boxprops=dict(facecolor="#1a88ff", color=lineColor),
                                flierprops=dict(markeredgecolor='#000000'),
                                medianprops=dict(color=lineColor, linewidth=1.5),
                                whiskerprops=dict(color=lineColor),
                                capprops=dict(color=lineColor),
                                zorder=2,
                                widths=0.8,
                                meanprops=dict(marker="o", markerfacecolor="red", fillstyle="full", markeredgecolor="None")
                                )

    def limitYAxis(self, ymin, ymax):
        self.ax1.set(ylim=(ymin, ymax))

    def setXLabels(self, driverNames):

        paddingToAx1 = 38 # finish pos
        paddingToAx2 = 18 # name

        # finish positions
        self.ax1.set_xticks([i for i in range(1, len(self.driverNames)+1)])
        self.ax1.tick_params(axis="x", pad=paddingToAx1)
        self.ax1.set_xticklabels(self.finishPositions, color="#C8CBD0", fontsize="large")

        # driver names
        self.ax2 = self.ax1.secondary_xaxis(location=0)
        self.ax2.set_xticks([i for i in range(1, len(self.driverNames)+1)])
        self.ax2.tick_params(axis="x", pad=paddingToAx2 + paddingToAx1)
        self.ax2.set_xticklabels(driverNames, rotation=45, rotation_mode="anchor", ha="right", color="#C8CBD0", fontsize="large")

        # car logos
        self.ax3 = self.ax1.secondary_xaxis(location=0)
        self.ax3.set_xticks([i for i in range(1, len(self.driverNames) + 1)])
        self.ax3.set_xticklabels(["" for i in range(1, len(self.driverNames) + 1)])
        imgs = readImagesForCarId(self.carIds)
        for i, im in enumerate(imgs):

            oi = OffsetImage(im, zoom=0.05)
            oi.image.axes = self.ax3
            ab = AnnotationBbox(oi,
                                (i+1,0),
                                frameon=False,
                                box_alignment=(0.48, 1.45)
                                )
            self.ax3.add_artist(ab)

    def drawLaptimes(self):
        scatter = []
        for i, lapdata in enumerate(self.laps):
            x = np.random.normal(i + 1, 0.05, len(lapdata))
            scatter.append(x)
        for i, data in enumerate(self.laps):
            self.ax1.scatter(scatter[i], self.laps[i],
                             zorder=4,
                             alpha=1,
                             c="yellow",
                             s=20,
                             linewidths=0.6,
                             edgecolors="#808000"
                             )

    def drawDISCDISQ(self):
        indices = []
        for i, value in enumerate(self.finishPositions):
            if value == "DISC" or value == "DISQ":
                indices.append(i)

        for driverIndex in indices:
            box = self.boxplot["boxes"][driverIndex]
            box.set_facecolor("#6F6F6F")


    def draw_medianLine(self):

        x1 = None
        y1 = None

        try:
            index = self.driverNames.index("Florian Niedermeier2")
            user_boxplot_data = self.laps[index]
            user_median = statistics.median(user_boxplot_data)
            y1 = [user_median, user_median]
            x1 = [0, 100]

        except ValueError:
            pass

        plt.plot(x1, y1, zorder=3, linestyle="dashed", color="#C2C5CA")

    def calculateYMinMax(self, laps):
        fastestLaptime = self.boxplot["caps"][0].get_ydata()[0]
        yMin = self.roundDown(fastestLaptime)

        allLaps = [item for sublist in laps for item in sublist]
        percentile_85 = np.quantile(allLaps, 0.85) # top 85% of laps
        yMax = round(percentile_85, 0)

        return yMin, yMax

    def calculateMinutesYAxis(self, number_of_seconds_shown):

        yticks = []
        for sec in number_of_seconds_shown:
            sec_rounded = round(sec, 2)
            td_raw = str(timedelta(seconds=sec_rounded))
            td_minutes = td_raw.split(":", 1)[1]

            if ".5" in td_minutes:
                td_minutes = ""
            else:
                td_minutes = td_minutes + ".0"

            td_minutes = td_minutes[1:]

            yticks.append(td_minutes)

        return yticks

    def getSeriesName(self, data):
        return data["data"]["metadata"]["series_name"]

    def getFinishPositions(self, data):
        return [driver["finish_position_in_class"] for driver in data["data"]["drivers"]]

    def getCarIds(self, data):
        return [driver["car_id"] for driver in data["data"]["drivers"]]

    def roundDown(self, laptime):
        # round down to the next 0.5 step
        return math.floor(laptime * 2) / 2

    def getUserDriverName(self, data):
        return data["data"]["metadata"]["user_driver_name"]
