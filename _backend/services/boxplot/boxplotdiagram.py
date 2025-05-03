import math
import os
import uuid
from datetime import timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.ticker import FuncFormatter
from skimage.transform import resize

from _backend.images.imageLoader import readCarLogoImages, readSeriesLogoImage
from _backend.services.boxplot.boxplotdata import BoxplotData
from _backend.services.boxplot.boxplotoptions import BoxplotOptions
from _backend.services.diagram import Diagram


class BoxplotDiagram(Diagram):
    def __init__(self, boxplotData: BoxplotData, boxplotOptions: BoxplotOptions):

        self._SHOW_IMAGE_ON_SYSTEM = os.environ.get("SHOW_IMAGE_ON_SYSTEM", False) == "True"
        self._DISABLE_DISCORD_FRONTEND = os.environ.get("DISABLE_DISCORD_FRONTEND", False) == "True"

        # data
        self.data = boxplotData
        self.options = boxplotOptions

        # colors
        self.boxplot_facecolor = "#1A88FF"
        self.boxplot_user_facecolor = "#BFDDFF"
        self.boxplot_line_color = "#000000"
        self.boxplot_flier_color = "#000000"
        self.lap_color = "yellow"
        self.lap_edge_color = "#808000"

        self.px_height = 700
        self.px_width = self.calcPxWidth()
        super().__init__(self.px_width, self.px_height)

    def draw(self):

        self.boxplot = self.drawBoxplot()

        # format boxplot
        self.limitYAxis()

        self.setYLabels()
        self.setXLabels()

        if self.options.showLaptimes:
            self.drawLaptimes()

        if not self.options.showRealName:
            self.replaceName()

        self.drivername_bold()
        self.userBoxplot_brightBlue()
        
        self.colorDISCDISQ()

        plt.tight_layout()
        plt.subplots_adjust(top=1-self.convertPixelsToFigureCoords(128))

        textObj = self.setHeaderText()
        seriesImgObj = self.setHeaderImages()

        self.adjustWidthToPreventOverlap(textObj, seriesImgObj)

        imagePath = self.getImagePath()

        if not self._SHOW_IMAGE_ON_SYSTEM or not self._DISABLE_DISCORD_FRONTEND:
            plt.savefig(imagePath)
            plt.close()

        if self._SHOW_IMAGE_ON_SYSTEM and self._DISABLE_DISCORD_FRONTEND:
            plt.show()
            plt.close()

        return imagePath

    def calcPxWidth(self):
        numberOfDrivers = len(self.data.driverNames)

        # about 50px per single boxplot
        if numberOfDrivers < 12:
            px_width = 50 * 13
        else:
            px_width = 50 * numberOfDrivers
        return px_width

    def setHeaderImages(self):

        seriesImgObj = None

        # series
        seriesImg = readSeriesLogoImage(self.data.seriesId)

        if not seriesImg is None:

            resizeFactor = 0.35
            seriesImg = resize(seriesImg, (int(seriesImg.shape[0] * resizeFactor), int(seriesImg.shape[1] * resizeFactor)),
                               anti_aliasing=True)

            imageHeight = seriesImg.shape[0]
            top0Position = self.px_height - imageHeight
            spaceForMiddle = (126 - imageHeight) / 2
            top = top0Position - spaceForMiddle

            self.fig.figimage(seriesImg, xo=20, yo=top, zorder=3)

            seriesImgObj = seriesImg
        else:
            seriesImgObj = None

        return seriesImgObj

    def convertPixelsToFigureCoords(self, pixels):
        return pixels / self.px_height

    def convertPixelToInches(self, pixels):
        return pixels / self.fig.dpi

    def userBoxplot_brightBlue(self):

        index = self.data.userDriverIndex
        finishPositions = self.data.finishPositions

        if not finishPositions[index] == "DISC" or not finishPositions[index] == "DISQ":
            userBP = self.boxplot["boxes"][index]
            userBP.set_facecolor(self.boxplot_user_facecolor)

    def drivername_bold(self):

        index = self.data.userDriverIndex

        labelax1 = self.ax1.get_xticklabels()[index]
        labelax1.set_fontweight(1000)
        labelax1.set_color(self.text_highlight_color)

        labelax2 = self.ax2.get_xticklabels()[index]
        labelax2.set_fontweight(1000)
        labelax2.set_color(self.text_highlight_color)

    def setYLabels(self):
        # self.ax1.yaxis.set_major_locator(plt.MaxNLocator(nbins=12, steps=[1, 2, 2.5, 5, 10]))
        formatter = FuncFormatter(self.formatCustomTickLabels)
        self.ax1.yaxis.set_major_formatter(formatter)
        self.ax1.tick_params(labelsize='large', labelcolor=self.text_color)

    def formatCustomTickLabels(self, value, pos):
        sec_rounded = round(value, 2)
        minutesAndSeconds = str(timedelta(seconds=sec_rounded))
        minutesAndSecondsClean = minutesAndSeconds.split(":", 1)[1]

        # .5 without tick labels
        if (".5" in minutesAndSecondsClean or
            ".2" in minutesAndSecondsClean or
            ".4" in minutesAndSecondsClean or
            ".6" in minutesAndSecondsClean or
            ".8" in minutesAndSecondsClean or
            ".75" in minutesAndSecondsClean or
            ".25" in minutesAndSecondsClean):
            labelWithDecimal = ""
        else:
            labelWithDecimal = minutesAndSecondsClean + ".0"

        # special case: time >= 10 minutes
        if labelWithDecimal[:1] == '0':
            label = labelWithDecimal[1:]
        else:
            label = labelWithDecimal

        return label

    def drawBoxplot(self):

        return self.ax1.boxplot(self.data.laps,
                                patch_artist=True,
                                boxprops=dict(facecolor=self.boxplot_facecolor, color=self.boxplot_line_color),
                                flierprops=dict(markeredgecolor=self.boxplot_flier_color),
                                medianprops=dict(color=self.boxplot_line_color, linewidth=1.5),
                                whiskerprops=dict(color=self.boxplot_line_color),
                                capprops=dict(color=self.boxplot_line_color),
                                zorder=2,
                                widths=0.8,
                                meanprops=dict(marker="o", markerfacecolor="red", fillstyle="full", markeredgecolor="None")
                                )

    def limitYAxis(self):

        yMin, yMax = self.calculateYMinMax()

        if self.options.maxSeconds:
            yMax = abs(self.options.maxSeconds)

        self.ax1.set(ylim=(yMin, yMax))

    def setXLabels(self):

        driverNames = self.data.driverNames
        finishPositions = self.data.finishPositions

        paddingToAx1 = 38 # finish pos
        paddingToAx2 = 20 # name

        # finish positions
        self.ax1.set_xticks([i for i in range(1, len(driverNames) + 1)])
        self.ax1.tick_params(axis="x", pad=paddingToAx1)
        self.ax1.set_xticklabels(finishPositions, color=self.text_color, fontsize="large")

        # driver names
        self.ax2 = self.ax1.secondary_xaxis(location=0)
        self.ax2.set_xticks([i for i in range(1, len(driverNames) + 1)])
        self.ax2.tick_params(axis="x", pad=paddingToAx2 + paddingToAx1)
        self.ax2.set_xticklabels(driverNames, rotation=45, rotation_mode="anchor", ha="right", color=self.text_color, fontsize="large")

        # car logos
        self.ax3 = self.ax1.secondary_xaxis(location=0)
        self.ax3.set_xticks([i for i in range(1, len(driverNames) + 1)])
        self.ax3.set_xticklabels(["" for i in range(1, len(driverNames) + 1)])
        imgs = readCarLogoImages(self.data.carIds)
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
        laps = self.data.laps

        for i, lapdata in enumerate(laps):
            x = np.random.normal(i + 1, 0.05, len(lapdata))
            scatter.append(x)
        for i, data in enumerate(laps):
            self.ax1.scatter(scatter[i], laps[i],
                             zorder=4,
                             alpha=1,
                             c=self.lap_color,
                             s=20,
                             linewidths=0.6,
                             edgecolors=self.lap_edge_color
                             )

    def colorDISCDISQ(self):
        indices = []
        finishPositions = self.data.finishPositions

        for i, value in enumerate(finishPositions):
            if value == "DISC" or value == "DISQ":
                indices.append(i)

        for driverIndex in indices:
            box = self.boxplot["boxes"][driverIndex]
            box.set_facecolor("#6F6F6F")

    def calculateYMinMax(self):

        runningLaps = self.data.runningLaps

        capLaptimes = [cap.get_ydata()[0] for cap in self.boxplot["caps"]]
        fastestLaptimeCap = min(capLaptimes)
        yMin = self.roundDown(fastestLaptimeCap)

        allLaps = [item for sublist in runningLaps for item in sublist]
        topXpercentOfLaps = np.quantile(allLaps, 0.82) # top x% of laps (non disq/disc)
        #todo: stddeviation?
        #todo: more drivers = more slower laps?
        yMax = round(topXpercentOfLaps, 0)

        return yMin, yMax

    def roundDown(self, laptime):
        # round down to the next 0.5 step
        return math.floor(laptime * 2) / 2

    def replaceName(self):

        index = self.data.userDriverIndex
        displayName = self.data.displayName

        labels = [item.get_text() for item in self.ax2.get_xticklabels()]
        labels[index] = displayName
        self.ax2.set_xticklabels(labels)

    def getImagePath(self):
        imagePath = Path().absolute() / 'output'
        figureName = f"boxplot_{str(uuid.uuid4())}.png"
        location = str(imagePath / figureName)
        return location

    def setHeaderText(self):
        locationSeriesNameY0 = 1 - self.convertPixelsToFigureCoords(35)
        space = self.convertPixelsToFigureCoords(25)

        seriesName = self.data.seriesName
        trackName = self.data.trackName
        sessionTime = self.data.sessionTime
        sof = self.data.sof
        subsessionId = self.data.subsessionId

        text_obj = self.fig.text(0.5, locationSeriesNameY0, seriesName, fontsize=16, fontweight="1000",
                                 color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0 - space, trackName, color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0 - space * 2, f"{sessionTime} | SOF: {sof}", color=self.text_color,
                      horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0 - space * 3, f"ID: {subsessionId}", color=self.text_color,
                      horizontalalignment="center")

        return text_obj

    def adjustWidthToPreventOverlap(self, textobj, seriesimgobj):
        # adjust plot-width to prevent overlap between seriesText and seriesImage

        if not textobj is None and not seriesimgobj is None:

            textWidth = round(textobj.get_window_extent(renderer=self.fig.canvas.get_renderer()).width, 0)
            textX0 = round((self.px_width - textWidth) / 2, 0)
            imageWidth = round(seriesimgobj.shape[1], 0)
            imageX0 = 20 # as defined in setHeaderImages()

            if imageX0 + imageWidth >= textX0:
                # overlap detected
                overlapInPixels = imageX0 + imageWidth - textX0

                gap = 15
                increasePlotWidthByPixels = (overlapInPixels + gap)*2
                currentWidth = self.px_width
                self.fig.set_figwidth(self.convertPixelToInches(currentWidth + increasePlotWidthByPixels))
                self.px_width = currentWidth + increasePlotWidthByPixels