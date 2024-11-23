import math
import os.path
import statistics
import uuid
from datetime import timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from jupyter_client.connect import port_names
from matplotlib import patches, pyplot
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

from _backend.application.diagrams.diagram import Diagram
from _backend.application.diagrams.images.imageSrc import readCarLogoImages


class MedianDiagram(Diagram):
    def __init__(self, data, **kwargs):
        self.barplot = None

        # data
        self.laps = self.getLaps(data)
        self.finishPositions = self.getFinishPositions(data)
        self.driverNames = self.getDriverNames(data)
        self.userDriverName = self.getUserDriverName(data)
        self.userDriverIndex = self.getUserDriverIndex(self.driverNames, self.userDriverName)
        self.seriesName = self.getSeriesName(data)
        self.sof =  self.getSof(data)
        self.track = self.getTrack(data)
        self.sessionTime = self.getSessionTime(data)
        self.carIds = self.getCarIds(data)
        self.subsessionId = self.getSubsessionId(data)
        self.medians = self.getMedian(data)
        self.medianDeltas = self.getMedianDelta(data, self.userDriverIndex) # x-Axis
        self.medianDeltaRunning = self.getMedianDeltaRunning(data, self.userDriverIndex)

        self.medianDeltas_str = self.medianDeltasToString(data, self.userDriverIndex) # 1st y-Axis right
        self.medians_str = self.mediansToString(self.medians) # 2nd y-Axis right

        self.showRealName = kwargs.get('showRealName', None)

        # colors
        self.boxplot_facecolor = "#1A88FF"
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

    def draw(self):

        self.barplot = self.drawBarplot()

        # format boxplot
        xMin, xMax = self.calculateXMinMax(self.medianDeltaRunning)

        self.limitXAxis(xMin, xMax)
        self.limitYAxis()

        self.setXLabels(xMin, xMax)
        self.setYLabels(self.driverNames)

        self.setGrid()

        self.colorNegativeDelta()
        self.colorPositiveDelta()

        showFakeName = not self.showRealName

        self.drawDISCDISQ()

        if (showFakeName):
            displayName = "----- Yourself ---->"
            self.replaceName(self.userDriverIndex, displayName)

        # self.highlightDrivername(self.userDriverIndex)

        plt.tight_layout()
        plt.subplots_adjust(top=0.96-0.022*5, right=0.82)

        self.setColumnHeaders()

        imagePath = self.getImagePath()
        # plt.savefig(imagePath)
        plt.show()
        plt.close()
        return imagePath

    def setColumnHeaders(self):
        locationSeriesName = 0.96
        space = 0.022

        # session desc
        self.fig.text(0.5, locationSeriesName,  self.seriesName, fontsize=16, fontweight="1000", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName-space, self.track, color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName-space*2, f"{self.sessionTime} | SOF: {self.sof}", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName-space*3, f"ID: {self.subsessionId}", color=self.text_color, horizontalalignment="center")

        # data columns desc
        color1 = "#41454C"
        color2 = "#494D55"
        fontsize = 13
        fontweight = "medium"
        paddingFactor = 4.65
        rectYPos = 0.85
        rectHeight = 0.03

        plot = self.ax1.get_position()

        print(plot)

        Ax1PaddingToPlot = 27
        Ax2PaddingToAx1 = 35

        distDrivername = self.convertInchesToFigureCoords(Ax1PaddingToPlot + Ax2PaddingToAx1)
        distPos = self.convertInchesToFigureCoords(Ax1PaddingToPlot)
        deltaPos = self.convertInchesToFigureCoords(52)

        self.fig.text(plot.x0 - distDrivername - 0.05, locationSeriesName-space * paddingFactor, "Driver", color=self.text_color, horizontalalignment="right", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((0, rectYPos), plot.x0-distDrivername, rectHeight, facecolor=color2))

        self.fig.text(plot.x0 - distPos - 0.02, locationSeriesName-space * paddingFactor, "Pos", color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plot.x0-distDrivername, rectYPos), plot.x0-distPos, rectHeight, facecolor=color1))

        self.fig.text(0.405, locationSeriesName-space * paddingFactor, "Relative delta to personal median", color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plot.x0, rectYPos), plot.x1 - plot.x0, rectHeight, facecolor=color2))

        self.fig.text(0.832, locationSeriesName-space * paddingFactor, "Delta", color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plot.x1, rectYPos), plot.x1 + deltaPos, rectHeight, facecolor=color1))

        self.fig.text(0.91, locationSeriesName-space * paddingFactor, "Median", color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plot.x1 + deltaPos, rectYPos), 1 - deltaPos, rectHeight, facecolor=color2))

    def userBoxplot_brightBlue(self, index):
        if not self.finishPositions[index] == "DISC" or not self.finishPositions[index] == "DISQ":
            userBP = self.barplot["boxes"][index]
            userBP.set_facecolor(self.boxplot_user_facecolor)

    def highlightDrivername(self, index):
        labelax1 = self.ax1.get_yticklabels()[index]
        labelax1.set_fontweight(1000)
        labelax1.set_color(self.text_highlight_color)

        labelax2 = self.ax2.get_yticklabels()[index]
        labelax2.set_fontweight(1000)
        labelax2.set_color(self.text_highlight_color)

        labelax5 = self.ax5.get_yticklabels()[index]
        labelax5.set_color(self.text_highlight_color)

    def getLaps(self, data):
        return [driver["laps"] for driver in data["drivers"]]

    def getMedian(self, data):
        return [driver["median"] for driver in data["drivers"]]

    def setXLabels(self, xmin, xmax):
        ticks = np.arange(xmin, xmax + 0.5, 0.5)
        self.ax1.set_xticks(ticks)
        self.ax1.set_xticklabels(self.calculateSecondsStr(ticks), fontsize="large", color=self.text_color)

    def drawBarplot(self):

        xMedians = [0 if x == None else x for x in self.medianDeltas]

        barplot = self.ax1.barh(y=1+np.arange(len(self.driverNames)),
                                width=xMedians,
                                zorder=2,
                                height=0.7,
                                )

        plt.gca().invert_yaxis()
        return barplot

    def limitXAxis(self, ymin, ymax):
        self.ax1.set(xlim=(ymin, ymax))

    def setYLabels(self, driverNames):

        Ax1PaddingToPlot = 27 # finish pos
        Ax2PaddingToAx1 = 35 # name

        # finish positions
        self.ax1.spines.left.set_position(('outward', Ax1PaddingToPlot))
        self.ax1.spines['left'].set_visible(False)
        self.ax1.tick_params(axis="y", size=0)
        self.ax1.set_yticks([i for i in range(1, len(self.driverNames)+1)], self.finishPositions, color=self.text_color, fontsize="11")

        # driver names
        self.ax2 = self.ax1.secondary_yaxis(location=0)
        self.ax2.spines.left.set_position(('outward', Ax1PaddingToPlot + Ax2PaddingToAx1))
        self.ax2.spines['left'].set_visible(False)
        self.ax2.tick_params(axis="y", size=0)
        self.ax2.set_yticks([i for i in range(1, len(self.driverNames)+1)], driverNames, ha="right", color=self.text_color, fontsize="11")

        # car logos
        self.ax3 = self.ax1.secondary_yaxis(location=0)
        self.ax3.spines['left'].set_visible(False)
        self.ax3.set_yticks([i for i in range(1, len(self.driverNames) + 1)], ["" for i in range(1, len(self.driverNames) + 1)], color=self.text_color)
        self.ax3.tick_params(axis="y", color=self.text_color)
        imgs = readCarLogoImages(self.carIds)
        for i, im in enumerate(imgs):

            oi = OffsetImage(im, zoom=0.04, resample=True)
            oi.image.axes = self.ax3
            ab = AnnotationBbox(oi,
                            (0,i+0.3),
                                frameon=False,
                                box_alignment=(1.25, 1.3)
                                )
            self.ax3.add_artist(ab)

        # relative deltas to median
        self.ax4 = self.ax1.secondary_yaxis(location=1)
        self.ax4.spines['left'].set_visible(False)
        self.ax4.spines.left.set_position(('outward', -52))
        self.ax4.tick_params(axis="y", pad=47, size=0)
        self.ax4.set_yticks([i for i in range(1, len(self.medianDeltas_str) + 1)], self.medianDeltas_str, color=self.text_color, fontsize="11", ha="right")

        # raw medians
        self.ax5 = self.ax1.secondary_yaxis(location=1)
        self.ax5.spines['left'].set_visible(False)
        self.ax5.spines.left.set_position(('outward', -120))
        self.ax5.tick_params(axis="y", pad=106, size=0)
        self.ax5.set_yticks([i for i in range(1, len(self.medians_str)+1)], self.medians_str, ha="right", color=self.text_color, fontsize="11")

    def drawLaptimes(self):
        scatter = []
        for i, lapdata in enumerate(self.laps):
            x = np.random.normal(i + 1, 0.05, len(lapdata))
            scatter.append(x)
        for i, data in enumerate(self.laps):
            self.ax1.scatter(scatter[i], self.laps[i],
                             zorder=4,
                             alpha=1,
                             c=self.lap_color,
                             s=20,
                             linewidths=0.6,
                             edgecolors=self.lap_edge_color
                             )

    def drawDISCDISQ(self):
        indices = []
        for i, value in enumerate(self.finishPositions):
            if value == "DISC" or value == "DISQ":
                indices.append(i)

        for driverIndex in indices:
            box = self.barplot[driverIndex]
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

    def calculateXMinMax(self, medianDelta):
        largestNegativeDelta = min(medianDelta)
        xMin = self.roundDown(largestNegativeDelta)

        if xMin >= -0.5:
            xMin = xMin - 0.5

        largestPositiveDelta = max(medianDelta)
        xMax = self.roundUp(largestPositiveDelta)

        return xMin, xMax

    def calculateSecondsStr(self, number_of_seconds_shown):

        yticks = []
        for sec in number_of_seconds_shown:
            sec_rounded = str(round(sec, 2)) + "s"
            yticks.append(sec_rounded)

        return yticks

    def getSeriesName(self, data):
        return data["metadata"]["series_name"]

    def getFinishPositions(self, data):
        return [driver["finish_position_in_class"] for driver in data["drivers"]]

    def getCarIds(self, data):
        return [driver["car_id"] for driver in data["drivers"]]

    def roundDown(self, delta):
        # round down to the next 0.5 step
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
        imagePath = Path().absolute().parent / 'images'
        figureName = f"boxplot_{str(uuid.uuid4())}.png"
        location = str(imagePath / figureName)
        return location

    def getMedianDelta(self, data, userIndex):
        medians = [0 if driver["median"] == None else driver["median"] for driver in data["drivers"]]
        userMedianVal = medians[userIndex]
        return [self.medianDeltaToUserDriver(x, userMedianVal) for x in medians]

    def medianDeltaToUserDriver(self, medianVal, userMedianVal):
        return round(medianVal-userMedianVal, 3)

    def colorNegativeDelta(self):
        for medianDelta in self.barplot:
            if medianDelta.get_width() < 0:
                medianDelta.set_facecolor("red")

    def colorPositiveDelta(self):
        for medianDelta in self.barplot:
            if medianDelta.get_width() > 0:
                medianDelta.set_facecolor("green")

    def getMedianDeltaRunning(self, data, userIndex):
        medianDeltas = [driver["median"] for driver in data["drivers"] if driver["result_status"] == "Running"]

        if userIndex > len(medianDeltas)-1:
            userMedianVal = 0 # if userdriver has disq/disc
        else:
            userMedianVal = medianDeltas[userIndex]

        return [self.medianDeltaToUserDriver(x, userMedianVal) for x in medianDeltas]

    def roundUp(self, delta):
        # round down to the next 0.5 step
        return math.ceil(delta * 2) / 2

    def setGrid(self):
        self.ax1.grid(visible=False)
        self.ax1.grid(color=self.ax_gridlines_color, axis="x", zorder=0)

    def limitYAxis(self):
        self.ax1.set(ylim=(len(self.driverNames)+0.7, 0.3))

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
        deltas = [None if x == None else self.medianDeltaToUserDriver(x, userMedianVal) for x in medians]
        return [self.formatDelta(x) for x in deltas]

    def mediansToString(self, medians):
        return [self.formatLaptime(x) for x in medians]

    def formatDelta(self, delta):

        if delta == None:
            value = "N/A"
        else:
            if delta < 0:
                value = "+" + str(f"{(-1)*delta:.3f}")
            elif delta > 0:
                value = "-" + str(f"{delta:.3f}")
            else:
                value = ""

        return value

    def setTitle(self):
        pass

    def convertInchesToFigureCoords(self, points):
        fig_width_inches = self.fig.get_size_inches()[0]  # get figure width in inches
        inches = points / 72
        diff = inches / fig_width_inches
        return diff