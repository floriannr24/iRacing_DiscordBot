import math
import statistics
import uuid
from datetime import timedelta
from enum import Enum
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt, patches

from _backend.application.diagrams.diagram import Diagram

# ToDo: select only a handful of players for comparison

class LaptimeDiagram(Diagram):
    def __init__(self, originalData, **kwargs):
        self.simplePlot = None

        self.showRealName = kwargs.get('showRealName', None)
        self.showDiscDisq = kwargs.get('showDiscDisq', None)
        self.displayMode = kwargs.get('displayMode', None)

        self.showDiscDisq = False
        self.displayMode = DisplayMode.ME_NINE

        # data
        self.userDriverName = self.getUserDriverName(originalData)
        self.data = self.prepareData(originalData, self.showDiscDisq, self.displayMode)
        self.median = self.getMedian(originalData)
        self.numberOflaps = self.getNumberOfLaps(self.data)
        self.finishPositions = self.getFinishPositions(originalData)
        self.driverNames = self.getDriverNames(self.data)
        self.userDriverIndex = self.getUserDriverIndex(self.driverNames, self.userDriverName)
        self.seriesName = self.getSeriesName(originalData)
        self.sof = self.getSof(originalData)
        self.track = self.getTrack(originalData)
        self.sessionTime = self.getSessionTime(originalData)
        self.carIds = self.getCarIds(originalData)
        self.subsessionId = self.getSubsessionId(originalData)

        # colors
        self.boxplot_facecolor = "#1C77BD"
        self.boxplot_user_facecolor = "#BFDDFF"
        self.boxplot_line_color = "#000000"
        self.lap_color = "yellow"
        self.lap_edge_color = "#808000"
        self.boxplot_flier_color = "#000000"

        numberOfDrivers = len(self.driverNames)
        heightPerDriver = 35

        # about 50px per single boxplot
        if numberOfDrivers < 12:
            px_height = heightPerDriver * 13
        else:
            px_height = heightPerDriver * numberOfDrivers

        super().__init__(900, px_height)

    def getDriverNames(self, data):
        return [driver["name"] for driver in data["drivers"]]

    def formatYMax(self, numberOfSecondsShown):
        values = []

        for i in numberOfSecondsShown:
            if i < 0:
                val = str(i) + "s"
            elif i == 0:
                val = str(i) + "s"
            else:
                val = "+" + str(i) + "s"
            values.append(val)

        return values


    def draw(self):

        self.simplePlot = self.drawPlot()

        # format plot
        yMin, yMax = self.calculateXMinMax()

        self.limitYAxis(yMin, yMax)
        # self.limitXAxis()

        # self.setYLabels(yMin, yMax)
        # self.setXLabels()

        # self.setGrid()

        # self.colorNegativeDelta()
        # self.colorPositiveDelta()

        # showFakeName = not self.showRealName

        # if self.showDiscDisq:
        #     self.colorDiscDisq()

        # if (showFakeName):
        #     displayName = "----- Yourself ---->"
        #     self.replaceName(self.userDriverIndex, displayName)

        # self.highlightUsername(self.userDriverIndex)
        self.colorAllLines()
        self.highlightUserLine(self.userDriverIndex)

        plt.tight_layout()
        plt.subplots_adjust(top=0.96 - 0.022 * 5)

        # self.setColumnHeaders()

        imagePath = self.getImagePath()
        # plt.savefig(imagePath)
        plt.show()
        plt.close()
        return imagePath

    def setColumnHeaders(self):
        locationSeriesName = 0.96
        space = 0.022

        # session desc
        self.fig.text(0.5, locationSeriesName, self.seriesName, fontsize=16, fontweight="1000", color=self.text_color,
                      horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName - space, self.track, color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName - space * 2, f"{self.sessionTime} | SOF: {self.sof}",
                      color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName - space * 3, f"ID: {self.subsessionId}", color=self.text_color,
                      horizontalalignment="center")

        # data columns desc
        color1 = "#41454C"
        color2 = "#494D55"
        fontsize = 13
        fontweight = "medium"
        paddingFactor = 4.65
        rectYPos = 0.85
        rectHeight = 0.03

        plot = self.ax1.get_position()

        Ax1PaddingToPlot = 27
        Ax2PaddingToAx1 = 35

        distDrivername = self.convertInchesToFigureCoords(Ax1PaddingToPlot + Ax2PaddingToAx1)
        distPos = self.convertInchesToFigureCoords(Ax1PaddingToPlot)
        deltaPos = self.convertInchesToFigureCoords(52)

        self.fig.text(plot.x0 - distDrivername - 0.05, locationSeriesName - space * paddingFactor, "Driver",
                      color=self.text_color, horizontalalignment="right", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((0, rectYPos), plot.x0 - distDrivername, rectHeight, facecolor=color2))

        self.fig.text(plot.x0 - distPos - 0.02, locationSeriesName - space * paddingFactor, "Pos",
                      color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(
            patches.Rectangle((plot.x0 - distDrivername, rectYPos), plot.x0 - distPos, rectHeight, facecolor=color1))

        self.fig.text(0.405, locationSeriesName - space * paddingFactor, "Personal median relative delta",
                      color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plot.x0, rectYPos), plot.x1 - plot.x0, rectHeight, facecolor=color2))

        self.fig.text(0.832, locationSeriesName - space * paddingFactor, "Delta", color=self.text_color,
                      horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plot.x1, rectYPos), plot.x1 + deltaPos, rectHeight, facecolor=color1))

        self.fig.text(0.91, locationSeriesName - space * paddingFactor, "Median", color=self.text_color,
                      horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(
            patches.Rectangle((plot.x1 + deltaPos, rectYPos), 1 - deltaPos, rectHeight, facecolor=color2))

    def userBoxplot_brightBlue(self, index):
        if not self.finishPositions[index] == "DISC" or not self.finishPositions[index] == "DISQ":
            userBP = self.simplePlot["boxes"][index]
            userBP.set_facecolor(self.boxplot_user_facecolor)

    def highlightUsername(self, index):
        # labelax1 = self.ax1.get_yticklabels()[index]
        # labelax1.set_fontweight(1000)
        # labelax1.set_color(self.text_highlight_color)

        labelax2 = self.ax2.get_yticklabels()[index]
        labelax2.set_fontweight(1000)
        labelax2.set_color(self.text_highlight_color)

        # labelax5 = self.ax5.get_yticklabels()[index]
        # labelax5.set_color(self.text_highlight_color)

    def getNumberOfLaps(self, data):
        return len(data["drivers"][0]["laps"])

    def getMedian(self, data):
        return [driver["median"] for driver in data["drivers"]]

    def setXLabels(self):
        self.ax1.set_xticks(np.arange(0, self.numberOflaps))
        self.ax1.set_xticklabels(np.arange(1, self.numberOflaps+1), fontsize="large", color=self.text_color)

    def drawPlot(self):
        laptimes = np.array([driver["laps"] for driver in self.data["drivers"]])

        simplePlot = self.ax1.plot(laptimes.T)
        return simplePlot

    def limitYAxis(self, ymin, ymax):
        self.ax1.set(ylim=(ymin, ymax))

    def setYLabels(self, yMin, yMax):

        Ax1PaddingToPlot = 27  # finish pos
        Ax2PaddingToAx1 = 35  # name

        # delta
        step = 2.5
        yMinEven = yMin if (yMin/step) % 2 == 0 else yMin - 1
        number_of_seconds_shown = np.arange(yMinEven, yMax - 0.5, step)
        deltaLabels = self.formatYMax(number_of_seconds_shown)

        self.ax1.spines['left'].set_visible(True)
        self.ax1.tick_params(axis="y", size=0)
        self.ax1.set_yticks(number_of_seconds_shown, deltaLabels, color=self.text_color, fontsize="11")

        # driver names
        self.ax2 = self.ax1.secondary_yaxis(location=1)
        # self.ax2.spines.left.set_position(('outward', Ax1PaddingToPlot + Ax2PaddingToAx1))
        self.ax2.spines['left'].set_visible(False)
        self.ax2.tick_params(axis="y", size=0)
        self.ax2.set_yticks(range(0, len(self.driverNames)), self.driverNames, ha="left", color=self.text_color, fontsize="11")

        # # car logos
        # self.ax3 = self.ax1.secondary_yaxis(location=0)
        # self.ax3.spines['left'].set_visible(False)
        # self.ax3.set_yticks([i for i in range(1, len(self.driverNames) + 1)],
        #                     ["" for i in range(1, len(self.driverNames) + 1)], color=self.text_color)
        # self.ax3.tick_params(axis="y", color=self.text_color)
        # imgs = readCarLogoImages(self.carIds)
        # for i, im in enumerate(imgs):
        #     oi = OffsetImage(im, zoom=0.04, resample=True)
        #     oi.image.axes = self.ax3
        #     ab = AnnotationBbox(oi,
        #                         (0, i + 0.3),
        #                         frameon=False,
        #                         box_alignment=(1.25, 1.3)
        #                         )
        #     self.ax3.add_artist(ab)
        #
        # # relative deltas to median
        # self.ax4 = self.ax1.secondary_yaxis(location=1)
        # self.ax4.spines['left'].set_visible(False)
        # self.ax4.spines.left.set_position(('outward', -52))
        # self.ax4.tick_params(axis="y", pad=47, size=0)
        # self.ax4.set_yticks([i for i in range(1, len(self.medianDeltas_str) + 1)], self.medianDeltas_str,
        #                     color=self.text_color, fontsize="11", ha="right")
        #
        # raw medians
        # self.ax5 = self.ax1.secondary_yaxis(location=1)
        # self.ax5.spines['left'].set_visible(False)
        # self.ax5.spines.left.set_position(('outward', -120))
        # self.ax5.tick_params(axis="y", pad=106, size=0)
        # self.ax5.set_yticks([i for i in range(1, len(self.driverNames) + 1)], self.driverNames, ha="left",
        #                     color=self.text_color, fontsize="11")

    def drawLaptimes(self):
        scatter = []
        for i, lapdata in enumerate(self.numberOflaps):
            x = np.random.normal(i + 1, 0.05, len(lapdata))
            scatter.append(x)
        for i, data in enumerate(self.numberOflaps):
            self.ax1.scatter(scatter[i], self.numberOflaps[i],
                             zorder=4,
                             alpha=1,
                             c=self.lap_color,
                             s=20,
                             linewidths=0.6,
                             edgecolors=self.lap_edge_color
                             )

    def colorDiscDisq(self):
        indicesToColor = []

        for i, driver in enumerate(self.data["drivers"]):
            if driver["result_status"] == "Disconnected" or driver["result_status"] == "Disqualified":
                indicesToColor.append(i)

        for driverIndex in indicesToColor:
            box = self.simplePlot[driverIndex]
            box.set_color("#6F6F6F")

    def draw_medianLine(self):

        x1 = None
        y1 = None

        try:
            index = self.driverNames.index("Florian Niedermeier2")
            user_boxplot_data = self.numberOflaps[index]
            user_median = statistics.median(user_boxplot_data)
            y1 = [user_median, user_median]
            x1 = [0, 100]

        except ValueError:
            pass

        plt.plot(x1, y1, zorder=3, linestyle="dashed", color="#C2C5CA")

    def calculateXMinMax(self):

        lapsWithoutFirstLap = np.array([driver["laps"][1:] for driver in self.data["drivers"]]).flatten()

        lowestLaptime = min(lapsWithoutFirstLap)
        yMin = self.roundDown(lowestLaptime)

        highestLaptime = max(lapsWithoutFirstLap)
        yMax = self.roundUp(highestLaptime)

        return int(yMin), int(yMax-10)

    def calculateSecondsStr(self, number_of_seconds_shown):
        yticks = []

        for sec in number_of_seconds_shown:
            if sec > 0:
                value = str((-1) * round(sec, 2)) + "s"
            elif sec < 0:
                value = "+" + str((-1) * round(sec, 2)) + "s"
            else:
                value = str(round(sec, 2)) + "s"
            yticks.append(value)

        return yticks

    def getSeriesName(self, data):
        return data["metadata"]["series_name"]

    def getFinishPositions(self, data):
        return [driver["finish_position_in_class"] for driver in data["drivers"]]

    def getCarIds(self, data):
        return [driver["car_id"] for driver in data["drivers"]]

    def roundDown(self, delta):
        # round down to the next 0.5 step and subtract 5
        return math.floor(delta * 2) / 2

    def getUserDriverName(self, data):
        return data["metadata"]["user_driver_name"]

    def getSof(self, data):
        return data["metadata"]["sof"]

    def getTrack(self, data):
        return data["metadata"]["track"]

    def getSessionTime(self, data):
        return data["metadata"]["session_time"]

    def getRunningLaps(self, data):
        # all laps of drivers whose final status is not "Disqualified" or "Disconnected"
        return [driver["laps"] for driver in data["drivers"] if driver["result_status"] == "Running"]

    def replaceName(self, index, displayName):
        labels = [item.get_text() for item in self.ax2.get_yticklabels()]
        labels[index] = displayName
        self.ax2.set_yticklabels(labels)

    def getUserDriverIndex(self, driverNames, name):
        return driverNames.index(name)

    def getSubsessionId(self, data):
        return data["metadata"]["subsession_id"]

    def getImagePath(self):
        imagePath = Path().absolute().parent / 'output'
        figureName = f"boxplot_{str(uuid.uuid4())}.png"
        location = str(imagePath / figureName)
        return location

    def getMedianDelta(self, data, userIndex):
        medians = [0 if driver["median"] == None else driver["median"] for driver in data["drivers"]]
        userMedianVal = medians[userIndex]
        return [self.medianDeltaToUserDriver(x, userMedianVal) for x in medians]

    def medianDeltaToUserDriver(self, medianVal, userMedianVal):
        return round(medianVal - userMedianVal, 3)

    def colorNegativeDelta(self):
        for medianDelta in self.simplePlot:
            if medianDelta.get_width() < 0:
                medianDelta.set_facecolor("red")

    def colorPositiveDelta(self):
        for medianDelta in self.simplePlot:
            if medianDelta.get_width() > 0:
                medianDelta.set_facecolor("green")

    def getMedianDeltaRunning(self, data, userIndex):
        medianDeltas = [driver["median"] for driver in data["drivers"] if driver["result_status"] == "Running"]

        if userIndex > len(medianDeltas) - 1:
            userMedianVal = 0  # if userdriver has disq/disc
        else:
            userMedianVal = medianDeltas[userIndex]

        return [self.medianDeltaToUserDriver(x, userMedianVal) for x in medianDeltas]

    def roundUp(self, delta):
        # round down to the next 0.5 step
        return math.ceil(delta * 2) / 2

    def setGrid(self):
        self.ax1.grid(visible=False)
        self.ax1.grid(color=self.ax_gridlines_color, axis="x", zorder=0)
        self.ax1.grid(color=self.ax_gridlines_color, axis="y", zorder=0)

    def limitXAxis(self):
        self.ax1.set(xlim=(0,self.numberOflaps-1))

    def formatLaptime(self, medianLaptime):
        if medianLaptime:
            sec_rounded = round(medianLaptime, 3)
            td_raw = str(timedelta(seconds=sec_rounded))
            td_minutes = td_raw.split(":", 1)[1]
            td_minutes = td_minutes[1:-3]
            return td_minutes
        else:
            return "N/A"

    def medianDeltasToString(self, data, userIndex):
        medians = [driver["median"] for driver in data["drivers"]]
        userMedianVal = medians[userIndex]

        if userMedianVal == None:
            userMedianVal = 0

        deltas = [None if x == None else self.medianDeltaToUserDriver(x, userMedianVal) for x in medians]
        return [self.formatDelta(x) for x in deltas]

    def mediansToString(self, medians):
        return [self.formatLaptime(x) for x in medians]

    def formatDelta(self, delta):

        if delta == None:
            value = "N/A"
        else:
            if delta < 0:
                value = "+" + str(f"{(-1) * delta:.3f}")
            elif delta > 0:
                value = "-" + str(f"{delta:.3f}")
            else:
                value = ""

        return value

    def setTitle(self):
        pass

    def convertInchesToFigureCoords(self, points):
        fig_width_inches = self.fig.get_size_inches()[0]  # figure width in inches
        inches = points / 72
        diff = inches / fig_width_inches
        return diff

    def prepareData(self, dataOrig, showDiscDisq, displayMode):

        if showDiscDisq:
            drivers = [driver for driver in dataOrig["drivers"]]
        else:
            drivers = [driver for driver in dataOrig["drivers"] if driver["result_status"] == "Running"]

        driverIndex = [driver["name"] for driver in drivers].index(self.userDriverName)

        if displayMode == DisplayMode.ALL:
            drivers = drivers
        elif displayMode == DisplayMode.ME_FIVE:
            drivers = self.getDriverSubset(drivers, driverIndex, DisplayMode.ME_FIVE)
        elif displayMode == DisplayMode.ME_NINE:
            drivers = self.getDriverSubset(drivers, driverIndex, DisplayMode.ME_NINE)
        else:
            drivers = drivers

        numberOfLaps = len(dataOrig["drivers"][0]["laps"])

        for driver in drivers:
            laps = np.pad(driver["laps"], (0, numberOfLaps - len(driver["laps"])), mode='constant', constant_values=None)
            laps = np.ndarray.tolist(laps)
            driver["laps"] = laps

        dataPrepared = {
            "metadata": dataOrig["metadata"],
            "drivers": drivers
        }

        return dataPrepared

    def removeDiscDisq(self):

        indicesToRemove = []

        for i, driver in enumerate(self.data["drivers"]):
            if driver["result_status"] == "Disconnected" or driver["result_status"] == "Disqualified":
                indicesToRemove.append(i)

        for driverIndex in indicesToRemove:
            box = self.simplePlot[driverIndex]
            box.set_color("#6F6F6F")

    def getDriverSubset(self, drivers, driverIndex, displayMode):
        if displayMode == DisplayMode.ME_FIVE:
            min = driverIndex - 2
            max = driverIndex + 2
            return drivers[min:max + 1] # upper bound exclusive
        if displayMode == DisplayMode.ME_NINE:
            min = driverIndex - 4
            max = driverIndex + 4
            return drivers[min:max + 1]

    def highlightUserLine(self, userDriverIndex):
        userLine = self.simplePlot[userDriverIndex]
        userLine.set_color(self.boxplot_user_facecolor)
        userLine.set_linewidth(2)
        userLine.set(zorder=10)

    def colorAllLines(self):
        for line in self.simplePlot:
            line.set_color(self.boxplot_facecolor)


#     # set line color
#     colorList_top3 = ["#FFD900", "#CFCEC9", "#D4822A"]
#     colorList_rest = ['#1f77b4', '#2ca02c', '#A3E6A3', '#d62728', '#811818', '#8261FF', '#8c564b', '#e377c2',
#                       '#919191', '#CFCF4B', '#97ED27', '#17becf']
#
#     self.ax.set_prop_cycle("color", colorList_rest)
#
#     # split list into "top3" and "rest"
#     top3, rest = self.splitDataTop3(self.input)
#     top3.reverse()
#
#     # draw plots
#     counter = 2
#     for i in range(0, len(top3), 1):
#         data = top3[i]["delta"]
#         self.ax.plot(data, color=colorList_top3[counter])
#         counter = counter-1
#
#     for i in range(0, len(rest), 1):
#         self.ax.plot(rest[i]["delta"])
#
#     # formatting
#     steps = 5
#     bottom_border = self.calculateYMin()
#     y_ticklabels = self.createYTickLabels(list(np.arange(0, bottom_border, steps)))
#
#     self.ax.set(xlim=(-0.5, self.number_of_laps - 0.5), ylim=(-5, bottom_border))
#     self.ax.set_xticks(np.arange(0, self.number_of_laps))
#     self.ax.set_xlabel("Laps", color="white")
#     self.ax.set_yticks(np.arange(0, bottom_border, steps))
#     self.ax.set_yticklabels(y_ticklabels)
#     self.ax.set_ylabel("Cumulative gap to leader in seconds", color="white")
#     self.ax.legend(self.extractDrivers(), loc="center left", facecolor="#36393F", labelcolor="white",
#                    bbox_to_anchor=(1.05, 0.5), labelspacing=0.5, edgecolor="#7D8A93")
#     # ax.set_title("Race report", pad="20.0", color="white")
#     self.ax.invert_yaxis()
#     plt.tick_params(labelright=True)
#
#     plt.tight_layout()
#     plt._showMenu()
#
# def calculateYMin(self):
#     deltaAtEnd = []
#
#     for lapdata in self.input:
#         indexLastLap = len(lapdata["delta"]) - 1
#         deltaAtEnd.append(lapdata["delta"][indexLastLap])
#     return 5 * round(statistics.median(deltaAtEnd) * 1.5 / 5)
#
# def extractDrivers(self):
#     return [lapdata["driver"] for lapdata in self.input]
#
# def createYTickLabels(self, list):
#     for i, x in enumerate(list, 0):
#         if not i % 2 == 0:
#             list[i] = ""
#     return list
#
# def splitDataTop3(self, laps):
#
#     top3 = []
#     rest = []
#
#     for data in laps:
#         if data["finish_position"] <= 3:
#             top3.append(data)
#         else:
#             rest.append(data)
#
#     return top3, rest
#
# def unpackConfig(self):
#     pass

class DisplayMode(Enum):
    ALL = 1,
    ME_FIVE = 2,
    ME_NINE = 3,






