import math
import os.path
import statistics
import uuid
from datetime import timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
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
        self.runningLaps = self.getRunningLaps(data)
        self.subsessionId = self.getSubsessionId(data)
        self.medianDelta = self.getMedianDelta(data, self.userDriverIndex) # 1st y-Axis
        self.medianDeltaRunning = self.getMedianDeltaRunning(data, self.userDriverIndex)
        self.medians = self.getMedian(data) # 2nd y-Axis on the right for raw laptimes


        self.showRealName = kwargs.get('showRealName', None)
        self.showLaptimes = kwargs.get('showLaptimes', None)

        # colors
        self.boxplot_facecolor = "#1A88FF"
        self.boxplot_user_facecolor = "#BFDDFF"
        self.boxplot_line_color = "#000000"
        self.lap_color = "yellow"
        self.lap_edge_color = "#808000"
        self.boxplot_flier_color = "#000000"

        numberOfDrivers = len(self.driverNames)

        # about 50px per single boxplot
        if numberOfDrivers < 12:
            px_width = 50 * 13
        else:
            px_width = 50 * numberOfDrivers

        super().__init__(px_width, 700)

    def getDriverNames(self, data):
        return [driver["name"] for driver in data["service"]["drivers"]]

    def draw(self):

        self.barplot = self.drawBarplot()

        # format boxplot
        yMin, yMax = self.calculateYMinMax(self.medianDeltaRunning)

        self.limitYAxis(yMin, yMax)
        self.setYLabels(yMin, yMax)
        self.setXLabels(self.driverNames)
        self.setTitleTexts()

        self.colorNegativeDelta()
        self.colorPositiveDelta()

        showFakeName = not self.showRealName

        self.drawDISCDISQ()

        if (showFakeName):
            displayName = "----- Yourself ---->"
            self.replaceName(self.userDriverIndex, displayName)

        self.drivername_bold(self.userDriverIndex)

        plt.tight_layout()
        plt.subplots_adjust(top=0.96-0.032*3.5)

        imagePath = self.getImagePath()
        # plt.savefig(imagePath)
        plt.show()
        plt.close()
        return imagePath

    def setTitleTexts(self):
        locationSeriesName = 0.96
        space = 0.032
        self.fig.text(0.5, locationSeriesName,  self.seriesName, fontsize=16, fontweight="1000", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName-space, self.track, color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName-space*2, f"{self.sessionTime} | SOF: {self.sof}", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName-space*3, f"ID: {self.subsessionId}", color=self.text_color, horizontalalignment="center")

    def userBoxplot_brightBlue(self, index):
        if not self.finishPositions[index] == "DISC" or not self.finishPositions[index] == "DISQ":
            userBP = self.barplot["boxes"][index]
            userBP.set_facecolor(self.boxplot_user_facecolor)

    def drivername_bold(self, index):
        labelax1 = self.ax1.get_xticklabels()[index]
        labelax1.set_fontweight(1000)
        labelax1.set_color(self.text_highlight_color)

        labelax2 = self.ax2.get_xticklabels()[index]
        labelax2.set_fontweight(1000)
        labelax2.set_color(self.text_highlight_color)

    def getLaps(self, data):
        return [driver["laps"] for driver in data["service"]["drivers"]]

    def getMedian(self, data):
        return [statistics.median(driver["laps"]) for driver in data["service"]["drivers"]]
        # return [driver["median"] for driver in data["service"]["drivers"]]

    def setYLabels(self, ymin, ymax):
        number_of_seconds_shown = np.arange(ymin, ymax + 0.5, 0.5)
        self.ax1.set_yticks(number_of_seconds_shown)
        self.ax1.set_yticklabels(self.calculateMinutesYAxis(number_of_seconds_shown), fontsize="large", color=self.text_color)

    def drawBarplot(self):

        print(self.medianDelta)

        return self.ax1.bar(1 + np.arange(len(self.driverNames)),
                            self.medianDelta,
                            width=0.7,
                            zorder=2,
                            )

    def limitYAxis(self, ymin, ymax):
        self.ax1.set(ylim=(ymin, ymax))

    def setXLabels(self, driverNames):

        paddingToAx1 = 38 # finish pos
        paddingToAx2 = 20 # name

        # finish positions
        self.ax1.set_xticks([i for i in range(1, len(self.driverNames)+1)])
        self.ax1.tick_params(axis="x", pad=paddingToAx1)
        self.ax1.set_xticklabels(self.finishPositions, color=self.text_color, fontsize="large")

        # driver names
        self.ax2 = self.ax1.secondary_xaxis(location=0)
        self.ax2.set_xticks([i for i in range(1, len(self.driverNames)+1)])
        self.ax2.tick_params(axis="x", pad=paddingToAx2 + paddingToAx1)
        self.ax2.set_xticklabels(driverNames, rotation=45, rotation_mode="anchor", ha="right", color=self.text_color, fontsize="large")

        # car logos
        self.ax3 = self.ax1.secondary_xaxis(location=0)
        self.ax3.set_xticks([i for i in range(1, len(self.driverNames) + 1)])
        self.ax3.set_xticklabels(["" for i in range(1, len(self.driverNames) + 1)])
        imgs = readCarLogoImages(self.carIds)
        for i, im in enumerate(imgs):

            oi = OffsetImage(im, zoom=0.045, resample=True)
            oi.image.axes = self.ax3
            ab = AnnotationBbox(oi,
                                (i+1,0),
                                frameon=False,
                                box_alignment=(0.48, 1.47)
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

    def calculateYMinMax(self, medianDelta):
        largestNegativeDelta = min(medianDelta)
        yMin = self.roundDown(largestNegativeDelta)

        largestPositiveDelta = max(medianDelta)
        yMax = self.roundUp(largestPositiveDelta)

        return yMin, yMax

    def calculateMinutesYAxis(self, number_of_seconds_shown):

        yticks = []
        for sec in number_of_seconds_shown:
            sec_rounded = str(round(sec, 2)) + "s"
            yticks.append(sec_rounded)

        return yticks

    def getSeriesName(self, data):
        return data["service"]["metadata"]["series_name"]

    def getFinishPositions(self, data):
        return [driver["finish_position_in_class"] for driver in data["service"]["drivers"]]

    def getCarIds(self, data):
        return [driver["car_id"] for driver in data["service"]["drivers"]]

    def roundDown(self, delta):
        # round down to the next 0.5 step
        return math.floor(delta * 2) / 2

    def getUserDriverName(self, data):
        return data["service"]["metadata"]["user_driver_name"]

    def getSof(self, data):
        return data["service"]["metadata"]["sof"]

    def getTrack(self, data):
        return data["service"]["metadata"]["track"]

    def getSessionTime(self, data):
        return data["service"]["metadata"]["session_time"]

    def getRunningLaps(self, data):
        # all laps of drivers whose final status is not "Disqualified" or "Disconnected"
        return [driver["laps"] for driver in data["service"]["drivers"] if driver["result_status"] == "Running"]

    def replaceName(self, index, displayName):
        labels = [item.get_text() for item in self.ax2.get_xticklabels()]
        labels[index] = displayName
        self.ax2.set_xticklabels(labels)

    def getUserDriverIndex(self, driverNames, name):
        return driverNames.index(name)

    def getSubsessionId(self, data):
        return data["service"]["metadata"]["subsession_id"]

    def getImagePath(self):
        imagePath = Path().absolute().parent / 'images'
        figureName = f"boxplot_{str(uuid.uuid4())}.png"
        location = str(imagePath / figureName)
        return location

    def getMedianDelta(self, data, userIndex):
        medianDeltas = [statistics.median(driver["laps"]) for driver in data["service"]["drivers"]]
        # medianDeltas = [driver["median"] for driver in data["service"]["drivers"]]
        userMedianVal = medianDeltas[userIndex]
        return [self.medianDeltaToUserDriver(x, userMedianVal) for x in medianDeltas]

    def medianDeltaToUserDriver(self, medianVal, userMedianVal):
        return round(medianVal-userMedianVal, 3)

    def colorNegativeDelta(self):
        for medianDelta in self.barplot:
            if medianDelta.get_height() < 0:
                medianDelta.set_facecolor("red")

    def colorPositiveDelta(self):
        for medianDelta in self.barplot:
            if medianDelta.get_height() > 0:
                medianDelta.set_facecolor("green")

    def getMedianDeltaRunning(self, data, userIndex):
        medianDeltas = [statistics.median(driver["laps"]) for driver in data["service"]["drivers"] if driver["result_status"] == "Running"]
        # medianDeltas = [driver["median"] for driver in data["service"]["drivers"]]
        userMedianVal = medianDeltas[userIndex]
        return [self.medianDeltaToUserDriver(x, userMedianVal) for x in medianDeltas]

    def roundUp(self, delta):
        # round down to the next 0.5 step
        return math.ceil(delta * 2) / 2