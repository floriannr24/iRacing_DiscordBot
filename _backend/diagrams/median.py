import os
import statistics
import uuid
from datetime import timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import patches
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Ellipse
from matplotlib.ticker import FuncFormatter
from skimage.transform import resize

from _backend.diagrams.diagram import Diagram
from _backend.diagrams.images.imageLoader import readCarLogoImages, readSeriesLogoImage
from _backend.services.median import MedianData
from _backend.services.median import MedianOptions


class MedianDiagram(Diagram):
    def __init__(self, medianData: MedianData, medianOptions: MedianOptions):

        # env variables
        self._SHOW_IMAGE_ON_SYSTEM = os.environ.get("SHOW_IMAGE_ON_SYSTEM", False) == "True"
        self._DISABLE_DISCORD_FRONTEND = os.environ.get("DISABLE_DISCORD_FRONTEND", False) == "True"

        # data
        self.data = medianData
        self.options = medianOptions

        self.px_width = 900
        self.px_height = self.calcPxHeight(self.data.driverNames)
        super().__init__(self.px_width, self.px_height)

    def draw(self):

        self.barplot = self.drawBarplot()

        # format boxplot
        xMin = self.data.xMin
        xMax = self.data.xMax

        if not self.options.maxSeconds is None:
            xMax = abs(self.options.maxSeconds)

        self.limitXAxis(xMin, xMax)
        self.limitYAxis()

        self.setXLabels()
        self.setYLabels()

        self.setGrid()

        # self.markSelfAsDot(self.userDriverIndex)

        self.colorNegativeDelta()
        self.colorPositiveDelta()

        if self.options.showFakeName:
            self.replaceName()

        self.highlightDrivername()
        self.colorDISCDISQ()

        plt.tight_layout()
        plt.subplots_adjust(top=1-self.convertPixelsToFigureCoords(156), right=0.82)
        # top = space for columnHeaders (28px) + headerText, headerImages (128px)
        # right = space for 'Delta' and 'Median' cols

        self.setColumnHeaders()
        self.setHeaderText()
        self.setHeaderImages()

        imagePath = self.getImagePath()

        if not self._SHOW_IMAGE_ON_SYSTEM or not self._DISABLE_DISCORD_FRONTEND:
            plt.savefig(imagePath)
            plt.close()

        if self._SHOW_IMAGE_ON_SYSTEM and self._DISABLE_DISCORD_FRONTEND:
            plt.show()
            plt.close()

        return imagePath

    def calcPxHeight(self, driverNames):
        numberOfDrivers = len(driverNames)
        headerAndFooter = 194 # header (158px) + footer (38px)

        if numberOfDrivers < 12:
            heightPerDriver = 35
            px_height = headerAndFooter + heightPerDriver * numberOfDrivers
        else:
            heightPerDriver = 26
            px_height = headerAndFooter + heightPerDriver * numberOfDrivers

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

    def highlightDrivername(self):

        index = self.data.userDriverIndex

        labelax1 = self.ax1.get_yticklabels()[index]
        labelax1.set_fontweight(1000)
        labelax1.set_color(self.text_highlight_color)

        labelax2 = self.ax2.get_yticklabels()[index]
        labelax2.set_fontweight(1000)
        labelax2.set_color(self.text_highlight_color)

        labelax5 = self.ax5.get_yticklabels()[index]
        labelax5.set_color(self.text_highlight_color)

    def setXLabels(self):
        self.ax1.xaxis.set_major_locator(plt.MaxNLocator(nbins=12, steps=[1, 2, 2.5, 5, 10]))
        formatter = FuncFormatter(self.formatCustomTickLabels)
        self.ax1.xaxis.set_major_formatter(formatter)
        self.ax1.tick_params(labelsize='medium', labelcolor=self.text_color)

    def drawBarplot(self):

        barplot = self.ax1.barh(y=1 + np.arange(len(self.data.driverNames)),
                                width=self.data.xMedians,
                                zorder=2,
                                height=0.7,
                                )

        plt.gca().invert_yaxis()
        return barplot

    def limitXAxis(self, ymin, ymax):
        self.ax1.set(xlim=(ymin, ymax))

    def setYLabels(self):

        driverNames = self.data.driverNames
        carIds = self.data.carIds
        finishPositions = self.data.finishPositions

        Ax1PaddingToPlot = 27 # finish pos
        Ax2PaddingToAx1 = 35 # name

        # finish positions
        self.ax1.spines.left.set_position(('outward', Ax1PaddingToPlot))
        self.ax1.spines['left'].set_visible(False)
        self.ax1.tick_params(axis="y", size=0)
        self.ax1.set_yticks([i for i in range(1, len(driverNames) + 1)], finishPositions, color=self.text_color,
                            fontsize="11")

        # driver names
        self.ax2 = self.ax1.secondary_yaxis(location=0)
        self.ax2.spines.left.set_position(('outward', Ax1PaddingToPlot + Ax2PaddingToAx1))
        self.ax2.spines['left'].set_visible(False)
        self.ax2.tick_params(axis="y", size=0)
        self.ax2.set_yticks([i for i in range(1, len(driverNames) + 1)], driverNames, ha="right", color=self.text_color,
                            fontsize="11")

        # car logos
        self.ax3 = self.ax1.secondary_yaxis(location=0)
        self.ax3.spines['left'].set_visible(False)
        self.ax3.set_yticks([i for i in range(1, len(driverNames) + 1)], ["" for i in range(1, len(driverNames) + 1)],
                            color=self.text_color)
        self.ax3.tick_params(axis="y", color=self.text_color)
        imgs = readCarLogoImages(carIds)
        for i, im in enumerate(imgs):

            offsetImage = OffsetImage(im, zoom=0.035, resample=True)
            offsetImage.image.axes = self.ax3
            ab = AnnotationBbox(offsetImage,
                            (0, i+0.3),
                                frameon=False,
                                box_alignment=(1.25, 1.3)
                                )
            self.ax3.add_artist(ab)

        # relative deltas to median
        medianDeltas_str = self.data.medianDeltas_str  # 1st y-Axis right
        self.ax4 = self.ax1.secondary_yaxis(location=1)
        self.ax4.spines['left'].set_visible(False)
        self.ax4.spines.left.set_position(('outward', -52))
        self.ax4.tick_params(axis="y", pad=47, size=0)
        self.ax4.set_yticks([i for i in range(1, len(medianDeltas_str) + 1)], medianDeltas_str, color=self.text_color, fontsize="11", ha="right")

        # medians
        medians_str = self.data.medians_str  # 2nd y-Axis right
        self.ax5 = self.ax1.secondary_yaxis(location=1)
        self.ax5.spines['left'].set_visible(False)
        self.ax5.spines.left.set_position(('outward', -120))
        self.ax5.tick_params(axis="y", pad=106, size=0)
        self.ax5.set_yticks([i for i in range(1, len(medians_str)+1)], medians_str, ha="right", color=self.text_color, fontsize="11")

    def colorDISCDISQ(self):
        indices = []
        for i, value in enumerate(self.data.finishPositions):
            if value == "DISC" or value == "DISQ":
                indices.append(i)

        for driverIndex in indices:
            box = self.barplot[driverIndex]
            box.set_facecolor("#6F6F6F")

    def draw_medianLine(self):

        x1 = None
        y1 = None

        try:
            index = self.data.userDriverIndex
            user_boxplot_data = self.data.laps[index]
            user_median = statistics.median(user_boxplot_data)
            y1 = [user_median, user_median]
            x1 = [0, 100]

        except ValueError:
            pass

        plt.plot(x1, y1, zorder=3, linestyle="dashed", color="#C2C5CA")

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

    def getRunningLaps(self, data):
        # all laps of drivers whose final status is not "Disqualified" or "Disconnected"
        return [driver["laps"] for driver in data["drivers"] if driver["result_status"] == "Running"]

    def replaceName(self):

        index = self.data.userDriverIndex
        displayName = self.data.displayName

        labels = [item.get_text() for item in self.ax2.get_yticklabels()]
        labels[index] = displayName
        self.ax2.set_yticklabels(labels)

    def getImagePath(self):
        imagePath = Path().absolute() / 'output'
        figureName = f"median_{str(uuid.uuid4())}.png"
        location = str(imagePath / figureName)
        return location

    def colorNegativeDelta(self):
        for medianDelta in self.barplot:
            if medianDelta.get_width() < 0:
                medianDelta.set_facecolor("red")

    def colorPositiveDelta(self):
        for medianDelta in self.barplot:
            if medianDelta.get_width() > 0:
                medianDelta.set_facecolor("green")

    def setGrid(self):
        self.ax1.grid(visible=False)

        # repaint all vertical gridlines, apart from line at x=0
        xticks = self.ax1.get_xticks()
        for xtick in xticks:
            if xtick != 0:
                self.ax1.axvline(x=xtick, color=self.ax_gridlines_color, linestyle='-', alpha=1, zorder=0, linewidth=0.8)

        self.ax1.axvline(0, color=self.text_color, linewidth=0.5)

    def limitYAxis(self):
        self.ax1.set(ylim=(len(self.data.driverNames) + 0.7, 0.3))

    def formatLaptime(self, medianLaptime):
        if medianLaptime:
            sec_rounded = round(medianLaptime, 3)
            td_raw = str(timedelta(seconds=sec_rounded))
            td_minutes = td_raw.split(":", 1)[1]
            td_minutes = td_minutes[1:-3]
            return td_minutes
        else:
            return "N/A"

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
        seriesImg = readSeriesLogoImage(self.data.seriesId)

        if not seriesImg is None:

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

    def setHeaderText(self):
        locationSeriesNameY0 = 1-self.convertPixelsToFigureCoords(35)
        space = self.convertPixelsToFigureCoords(25)

        seriesName = self.data.seriesName
        track = self.data.trackName
        sessionTime = self.data.sessionTime
        sof = self.data.sof
        subsessionId = self.data.subsessionId

        self.fig.text(0.5, locationSeriesNameY0, seriesName, fontsize=16, fontweight="1000", color=self.text_color,
                      horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0 - space, track, color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0 - space * 2, f"{sessionTime} | SOF: {sof}", color=self.text_color,
                      horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0 - space * 3, f"ID: {subsessionId}", color=self.text_color,
                      horizontalalignment="center")

    def formatCustomTickLabels(self, value, pos):
        intValue = int(value) if value == int(value) else value
        stringValue = f"{intValue}s" if intValue <= 0 else  f"+{intValue}s"
        return stringValue

    def markSelfAsDot(self, userdriverindex):
        x0, y0 = self.ax1.transAxes.transform((0, 0))  # lower left in pixels
        x1, y1 = self.ax1.transAxes.transform((1, 1))  # upper right in pixes
        dx = x1 - x0
        dy = y1 - y0
        maxd = max(dx, dy)
        radius = 0.2
        width = radius * maxd / dx
        height = radius * maxd / dy

        ellipse = Ellipse((0.02, userdriverindex+1), width, height, color=self.text_color, zorder=1, alpha=1.0)
        self.ax1.add_patch(ellipse)