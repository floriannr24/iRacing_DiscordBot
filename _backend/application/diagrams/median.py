import math
import statistics
import uuid
from datetime import timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.ticker import FuncFormatter
from skimage.transform import resize

from _backend.application.diagrams.diagram import Diagram
from _backend.application.diagrams.images.imageLoader import readCarLogoImages, readSeriesLogoImage

class MedianDiagram(Diagram):
    def __init__(self, originalData, params):

        # settings
        self.maxSeconds = params.get('max_seconds', None)
        self.showFakeName = not params.get('show_real_name', None)
        self.showDiscDisq = params.get('show_discdisq', None)

        # data
        self.data = self.prepareData(originalData, self.showDiscDisq)
        self.laps = self.getLaps(self.data)
        self.finishPositions = self.getFinishPositions(self.data)
        self.driverNames = self.getDriverNames(self.data)
        self.userDriverName = self.getUserDriverName(self.data)
        self.userDriverIndex = self.getUserDriverIndex(self.driverNames, self.userDriverName)
        self.seriesName = self.getSeriesName(self.data)
        self.sof =  self.getSof(self.data)
        self.track = self.getTrack(self.data)
        self.trackId = self.getTrackId(self.data)
        self.sessionTime = self.getSessionTime(self.data)
        self.carIds = self.getCarIds(self.data)
        self.seriesId = self.getSeriesId(self.data)
        self.subsessionId = self.getSubsessionId(self.data)
        self.medians = self.getMedian(self.data)
        self.medianDeltas = self.getMedianDelta(self.data, self.userDriverIndex) # x-Axis
        self.medianDeltaRunning = self.getMedianDeltaRunning(self.data, self.userDriverIndex)
        self.isRainySession = self.getRainInfo(self.data)

        self.px_width = 900
        self.px_height = self.calcPxHeight(self.driverNames)
        super().__init__(self.px_width, self.px_height)

    def draw(self):

        self.barplot = self.drawBarplot()

        # format boxplot
        xMin, xMax = self.calculateXMinMax(self.medianDeltaRunning)

        if self.maxSeconds:
            xMax = abs(self.maxSeconds)

        self.limitXAxis(xMin, xMax)
        self.limitYAxis()

        self.setXLabels()
        self.setYLabels(self.driverNames)

        self.setGrid()

        self.colorNegativeDelta()
        self.colorPositiveDelta()

        if self.showFakeName:
            displayName = "----- Yourself ---->"
            self.replaceName(self.userDriverIndex, displayName)

        self.highlightDrivername(self.userDriverIndex)
        self.colorDISCDISQ()

        plt.tight_layout()
        plt.subplots_adjust(top=1-self.convertPixelsToFigureCoords(156), right=0.82)
        # top = space for columnHeaders (28px), headerText and headerImages (128px)
        # right = space for 'Delta' and 'Median' cols

        self.setColumnHeaders()
        self.setHeaderText()
        self.setHeaderImages()

        imagePath = self.getImagePath()
        plt.savefig(imagePath)
        # plt.show()
        plt.close()
        return imagePath

    def getDriverNames(self, data):
        return [driver["name"] for driver in data["drivers"]]

    def calcPxHeight(self, driverNames):
        numberOfDrivers = len(driverNames)
        heightPerDriver = 35

        if numberOfDrivers < 12:
            px_height = heightPerDriver * 13
        else:
            px_height = heightPerDriver * numberOfDrivers

        return px_height

    def setColumnHeaders(self):
        color1 = "#41454C"
        color2 = "#494D55"
        fontsize = 13
        fontweight = "medium"
        spaceAboveColumnHeaders = 128
        textRectHeight = 28
        textDistanceToPlot = 8

        rect0YPos = 1 - self.convertPixelsToFigureCoords(spaceAboveColumnHeaders + textRectHeight)
        rectHeight = self.convertPixelsToFigureCoords(textRectHeight)
        text0YPos = 1 - self.convertPixelsToFigureCoords(spaceAboveColumnHeaders + textRectHeight - textDistanceToPlot)

        plotPosition = self.ax1.get_position()

        Ax1PaddingToPlot = 27
        Ax2PaddingToAx1 = 35

        distDrivername = self.convertPtToFigureCoords(Ax1PaddingToPlot + Ax2PaddingToAx1)
        distPos = self.convertPtToFigureCoords(Ax1PaddingToPlot)
        deltaPos = self.convertPtToFigureCoords(52)

        self.fig.text(plotPosition.x0 - distDrivername - 0.05, text0YPos, "Driver", color=self.text_color, horizontalalignment="right", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((0, rect0YPos), plotPosition.x0-distDrivername, rectHeight, facecolor=color2))

        self.fig.text(plotPosition.x0 - distPos - 0.02, text0YPos, "Pos", color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plotPosition.x0-distDrivername, rect0YPos), plotPosition.x0-distPos, rectHeight, facecolor=color1))

        self.fig.text(0.405, text0YPos, "Personal median relative delta", color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plotPosition.x0, rect0YPos), plotPosition.x1 - plotPosition.x0, rectHeight, facecolor=color2))

        self.fig.text(0.832, text0YPos, "Delta", color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plotPosition.x1, rect0YPos), plotPosition.x1 + deltaPos, rectHeight, facecolor=color1))

        self.fig.text(0.91, text0YPos, "Median", color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        self.fig.add_artist(patches.Rectangle((plotPosition.x1 + deltaPos, rect0YPos), 1 - deltaPos, rectHeight, facecolor=color2))

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

    def setXLabels(self):
        self.ax1.xaxis.set_major_locator(plt.MaxNLocator(nbins=12, steps=[1, 2, 2.5, 5, 10]))
        formatter = FuncFormatter(self.formatCustomTickLabels)
        self.ax1.xaxis.set_major_formatter(formatter)
        self.ax1.tick_params(labelsize='medium', labelcolor=self.text_color)

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
        medianDeltas_str = self.formatMedianDeltas(self.data, self.userDriverIndex)  # 1st y-Axis right
        self.ax4 = self.ax1.secondary_yaxis(location=1)
        self.ax4.spines['left'].set_visible(False)
        self.ax4.spines.left.set_position(('outward', -52))
        self.ax4.tick_params(axis="y", pad=47, size=0)
        self.ax4.set_yticks([i for i in range(1, len(medianDeltas_str) + 1)], medianDeltas_str, color=self.text_color, fontsize="11", ha="right")

        # medians
        medians_str = self.formatMedians(self.medians)  # 2nd y-Axis right
        self.ax5 = self.ax1.secondary_yaxis(location=1)
        self.ax5.spines['left'].set_visible(False)
        self.ax5.spines.left.set_position(('outward', -120))
        self.ax5.tick_params(axis="y", pad=106, size=0)
        self.ax5.set_yticks([i for i in range(1, len(medians_str)+1)], medians_str, ha="right", color=self.text_color, fontsize="11")

    def colorDISCDISQ(self):
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
            if sec > 0:
                value = str((-1)*round(sec, 2)) + "s"
            elif sec < 0:
                value = "+" + str((-1)*round(sec, 2)) + "s"
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
        imagePath = Path().absolute().parent / 'output'
        figureName = f"boxplot_{str(uuid.uuid4())}.png"
        location = str(imagePath / figureName)
        return location

    def getMedianDelta(self, data, userIndex):
        medians = [0 if driver["median"] == None else driver["median"] for driver in data["drivers"]]
        userMedianVal = medians[userIndex]
        return [self.calcMedianDeltaToUserDriver(x, userMedianVal) for x in medians]

    def calcMedianDeltaToUserDriver(self, medianVal, userMedianVal):
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

        return [self.calcMedianDeltaToUserDriver(x, userMedianVal) for x in medianDeltas]

    def roundUp(self, delta):
        # round down to the next 0.5 step
        return math.ceil(delta * 2) / 2

    def setGrid(self):
        self.ax1.grid(visible=False)
        self.ax1.grid(color=self.ax_gridlines_color, axis="x", zorder=0)
        self.ax1.axvline(0, color=self.text_color, linewidth=0.5)

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

    def formatMedianDeltas(self, data, userIndex):
        medians = [driver["median"] for driver in data["drivers"]]
        userMedianVal = medians[userIndex]

        if userMedianVal == None:
            userMedianVal = 0

        deltas = [None if x == None else self.calcMedianDeltaToUserDriver(x, userMedianVal) for x in medians]
        return [self.formatDelta(x) for x in deltas]

    def formatMedians(self, medians):
        return [self.formatLaptime(x) for x in medians]

    def formatDelta(self, delta):

        if delta == None:
            value = "N/A"
        else:
            if delta < 0:
                value = str(f"{delta:.3f}")
            elif delta > 0:
                value = str(f"+{delta:.3f}")
            else:
                value = ""

        return value

    def convertPtToFigureCoords(self, points):
        fig_width_inches = self.fig.get_size_inches()[0]
        inches = points / 72
        diff = inches / fig_width_inches
        return diff

    def convertPixelsToFigureCoords(self, pixels):
        return pixels / self.px_height

    def prepareData(self, originalData, showDiscDisq):
        if showDiscDisq:
            return originalData
        else: # always include userdriver, even if disc/disq
            user_driver_id = originalData["metadata"]["user_driver_id"]
            originalData["drivers"] = [driver for driver in originalData["drivers"] if driver["result_status"] == "Running" or driver["id"] == user_driver_id]
            return originalData

    def setHeaderImages(self):

        # series
        seriesImg = readSeriesLogoImage(self.seriesId)
        resizeFactor = 0.35
        seriesImg = resize(seriesImg, (int(seriesImg.shape[0] * resizeFactor), int(seriesImg.shape[1] * resizeFactor)), anti_aliasing=True)

        imageHeight = seriesImg.shape[0]
        top0Position = self.px_height-imageHeight
        spaceForMiddle = (126 - imageHeight) / 2
        top = top0Position - spaceForMiddle

        self.fig.figimage(seriesImg, xo=20, yo=top, zorder=3)

        # weather
        # seriesImg = readSeriesLogoImage(self.seriesId)
        # resizeFactor = 0.35
        # seriesImg = resize(seriesImg, (int(seriesImg.shape[0] * resizeFactor), int(seriesImg.shape[1] * resizeFactor)), anti_aliasing=True)
        #
        # imageHeight = seriesImg.shape[0]
        # top0Position = self.px_height-imageHeight
        # spaceForMiddle = (126 - imageHeight) / 2
        # top = top0Position - spaceForMiddle
        #
        # self.fig.figimage(seriesImg, xo=10, yo=top, zorder=3)

        # licence
        # seriesImg = readSeriesLogoImage(self.seriesId)
        # resizeFactor = 0.35
        # seriesImg = resize(seriesImg, (int(seriesImg.shape[0] * resizeFactor), int(seriesImg.shape[1] * resizeFactor)), anti_aliasing=True)
        #
        # imageHeight = seriesImg.shape[0]
        # top0Position = self.px_height-imageHeight
        # spaceForMiddle = (126 - imageHeight) / 2
        # top = top0Position - spaceForMiddle
        #
        # self.fig.figimage(seriesImg, xo=10, yo=top, zorder=3)

    def getSeriesId(self, data):
        return data["metadata"]["series_id"]

    def setHeaderText(self):
        locationSeriesNameY0 = 1-self.convertPixelsToFigureCoords(35)
        space = self.convertPixelsToFigureCoords(25)

        self.fig.text(0.5, locationSeriesNameY0,  self.seriesName, fontsize=16, fontweight="1000", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0-space, self.track, color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0-space*2, f"{self.sessionTime} | SOF: {self.sof}", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0-space*3, f"ID: {self.subsessionId}", color=self.text_color, horizontalalignment="center")

    def formatCustomTickLabels(self, value, pos):
        intValue = int(value) if value == int(value) else value
        stringValue = f"{intValue}s" if intValue <= 0 else  f"+{intValue}s"
        return stringValue

    def getRainInfo(self, data):
        return data["metadata"]["is_rainy_session"]

    def getTrackId(self, data):
        return data["metadata"]["track_id"]