import math
import os
import statistics
import uuid
from datetime import timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.ticker import FuncFormatter
from skimage.transform import resize

from _backend.application.diagrams.diagram import Diagram
from _backend.application.diagrams.images.imageLoader import readCarLogoImages, readSeriesLogoImage


class BoxplotDiagram(Diagram):
    def __init__(self, originalData, params):

        self._SHOW_IMAGE_ON_SYSTEM = os.environ.get("SHOW_IMAGE_ON_SYSTEM", False) == "True"
        self._DISABLE_DISCORD_FRONTEND = os.environ.get("DISABLE_DISCORD_FRONTEND", False) == "True"

        # settings
        self.maxSeconds = params.get('max_seconds', None)
        self.showFakeName = not params.get('show_real_name', None)
        self.showLaptimes = params.get('show_laptimes', None)
        self.showDiscDisq = params.get('show_discdisq', None)

        # data
        self.data = self.prepareData(originalData, self.showDiscDisq)
        self.laps = self.getLaps(self.data)
        self.finishPositions = self.getFinishPositions(self.data)
        self.driverNames = self.getDriverNames(self.data)
        self.userDriverName = self.getUserDriverName(self.data)
        self.userDriverIndex = self.getUserDriverIndex(self.driverNames, self.userDriverName)
        self.seriesName = self.getSeriesName(self.data)
        self.seriesId = self.getSeriesId(self.data)
        self.sof =  self.getSof(self.data)
        self.track = self.getTrack(self.data)
        self.sessionTime = self.getSessionTime(self.data)
        self.carIds = self.getCarIds(self.data)
        self.runningLaps = self.getRunningLaps(self.data)
        self.subsessionId = self.getSubsessionId(self.data)
        self.isRainySession = self.getRainInfo(self.data)

        # colors
        self.boxplot_facecolor = "#1A88FF"
        self.boxplot_user_facecolor = "#BFDDFF"
        self.boxplot_line_color = "#000000"
        self.lap_color = "yellow"
        self.lap_edge_color = "#808000"
        self.boxplot_flier_color = "#000000"

        self.px_height = 700
        self.px_width = self.calcPxWidth(self.driverNames)
        super().__init__(self.px_width, self.px_height)

    def draw(self):

        self.boxplot = self.drawBoxplot()

        # format boxplot
        yMin, yMax = self.calculateYMinMax(self.runningLaps)

        if self.maxSeconds:
            yMax = abs(self.maxSeconds)

        self.limitYAxis(yMin, yMax)

        self.setYLabels()
        self.setXLabels(self.driverNames)

        if self.showLaptimes:
            self.drawLaptimes()

        if self.showFakeName:
            displayName = "----- You ---->"
            self.replaceName(self.userDriverIndex, displayName)

        self.drivername_bold(self.userDriverIndex)
        self.userBoxplot_brightBlue(self.userDriverIndex)
        
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

    def calcPxWidth(self, driverNames):
        numberOfDrivers = len(driverNames)

        # about 50px per single boxplot
        if numberOfDrivers < 12:
            px_width = 50 * 13
        else:
            px_width = 50 * numberOfDrivers
        return px_width

    def getDriverNames(self, data):
        return [driver["name"] for driver in data["drivers"]]

    def setHeaderImages(self):

        seriesImgObj = None

        # series
        seriesImg = readSeriesLogoImage(self.seriesId)

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

    def setTitleTexts(self):
        locationSeriesName = 0.96
        space = 0.032
        self.fig.text(0.5, locationSeriesName,  self.seriesName, fontsize=16, fontweight="1000", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName-space, self.track, color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName-space*2, f"{self.sessionTime} | SOF: {self.sof}", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName-space*3, f"ID: {self.subsessionId}", color=self.text_color, horizontalalignment="center")

    def userBoxplot_brightBlue(self, index):
        if not self.finishPositions[index] == "DISC" or not self.finishPositions[index] == "DISQ":
            userBP = self.boxplot["boxes"][index]
            userBP.set_facecolor(self.boxplot_user_facecolor)

    def drivername_bold(self, index):
        labelax1 = self.ax1.get_xticklabels()[index]
        labelax1.set_fontweight(1000)
        labelax1.set_color(self.text_highlight_color)

        labelax2 = self.ax2.get_xticklabels()[index]
        labelax2.set_fontweight(1000)
        labelax2.set_color(self.text_highlight_color)

    def getLaps(self, data):
        return [driver["laps"] for driver in data["drivers"]]

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

        return self.ax1.boxplot(self.laps,
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

    def colorDISCDISQ(self):
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

    def calculateYMinMax(self, runningLaps):
        capLaptimes = [cap.get_ydata()[0] for cap in self.boxplot["caps"]]
        fastestLaptimeCap = min(capLaptimes)
        yMin = self.roundDown(fastestLaptimeCap)

        allLaps = [item for sublist in runningLaps for item in sublist]
        topXpercentOfLaps = np.quantile(allLaps, 0.82) # top x% of laps (non disq/disc)
        #todo: stddeviation?
        #todo: more drivers = more slower laps?
        yMax = round(topXpercentOfLaps, 0)

        return yMin, yMax

    def getSeriesName(self, data):
        return data["metadata"]["series_name"]

    def getFinishPositions(self, data):
        return [driver["finish_position_in_class"] for driver in data["drivers"]]

    def getCarIds(self, data):
        return [driver["car_id"] for driver in data["drivers"]]

    def roundDown(self, laptime):
        # round down to the next 0.5 step
        return math.floor(laptime * 2) / 2

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
        labels = [item.get_text() for item in self.ax2.get_xticklabels()]
        labels[index] = displayName
        self.ax2.set_xticklabels(labels)

    def getUserDriverIndex(self, driverNames, name):
        return driverNames.index(name)

    def getSubsessionId(self, data):
        return data["metadata"]["subsession_id"]

    def getImagePath(self):
        imagePath = Path().absolute() / 'output'
        figureName = f"boxplot_{str(uuid.uuid4())}.png"
        location = str(imagePath / figureName)
        return location

    def prepareData(self, originalData, showDiscDisq):
        if showDiscDisq:
            return originalData
        else: # always include userdriver, even if disc/disq
            user_driver_id = originalData["metadata"]["user_driver_id"]
            originalData["drivers"] = [driver for driver in originalData["drivers"] if driver["result_status"] == "Running" or driver["id"] == user_driver_id]
            return originalData

    def getSeriesId(self, data):
        return data["metadata"]["series_id"]

    def setHeaderText(self):
        locationSeriesNameY0 = 1 - self.convertPixelsToFigureCoords(35)
        space = self.convertPixelsToFigureCoords(25)

        text_obj = self.fig.text(0.5, locationSeriesNameY0, self.seriesName, fontsize=16, fontweight="1000", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0 - space, self.track, color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0 - space * 2, f"{self.sessionTime} | SOF: {self.sof}", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesNameY0 - space * 3, f"ID: {self.subsessionId}", color=self.text_color, horizontalalignment="center")

        return text_obj

    def getRainInfo(self, data):
        return data["metadata"]["is_rainy_session"]

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