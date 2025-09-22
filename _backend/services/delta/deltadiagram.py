import os
import uuid
from pathlib import Path

import numpy as np
from matplotlib import pyplot as plt

from _backend.services.delta.deltadata import DeltaData
from _backend.services.delta.deltaoptions import DeltaOptions
from _backend.services.diagram import Diagram


class DeltaDiagram(Diagram):
    def __init__(self, deltaData: DeltaData, deltaOptions: DeltaOptions):

        self._SHOW_IMAGE_ON_SYSTEM = os.environ.get("SHOW_IMAGE_ON_SYSTEM", False) == "True"
        self._DISABLE_DISCORD_FRONTEND = os.environ.get("DISABLE_DISCORD_FRONTEND", False) == "True"

        # data
        self.data = deltaData
        self.options = deltaOptions

        # colors
        self.user_linecolor = "#BFDDFF"

        self.px_height = 900
        self.px_width = self.calcPxWidth()
        super().__init__(self.px_width, self.px_height)

    def draw(self):

        self.plot = self.drawPlot()

        # format boxplot
        self.limitYAxis()
        self.limitXAxis()

        self.setYLabels()
        self.setXLabels()

        self.setGrid()

        if self.options.showDiscDisq:
            self.colorDiscDisq()

        if not self.options.showRealName:
            self.replaceName()

        self.highlightUsername()
        self.highlightUserLine()
        self.colorDrivernames()

        plt.tight_layout()
        plt.subplots_adjust(top=0.96 - 0.022 * 4)

        self.setHeaderText()

        imagePath = self.getImagePath()

        if not self._DISABLE_DISCORD_FRONTEND:
            plt.savefig(imagePath)

        if self._SHOW_IMAGE_ON_SYSTEM and self._DISABLE_DISCORD_FRONTEND:
            plt.show()

        return imagePath

    def formatYMax(self, numberOfSecondsShown):
        values = []

        for i in numberOfSecondsShown:
            if i <= 0:
                val = str(i) + "s"
            else:
                val = "+" + str(i) + "s"
            values.append(val)

        return values

    def roundToNearest2Point5(self, val):
        return round(val / 2.5) * 2.5

    def setHeaderText(self):
        locationSeriesName = 0.96
        space = 0.022

        seriesName = self.data.seriesName
        trackName = self.data.trackName
        sessionTime = self.data.sessionTime
        sof = self.data.sof
        subsessionId = self.data.subsessionId

        # session desc
        self.fig.text(0.5, locationSeriesName, seriesName, fontsize=16, fontweight="1000", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName - space, trackName, color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName - space * 2, f"{sessionTime} | SOF: {sof}", color=self.text_color, horizontalalignment="center")
        self.fig.text(0.5, locationSeriesName - space * 3, f"ID: {subsessionId}", color=self.text_color, horizontalalignment="center")

        # data columns desc
        color1 = "#41454C"
        color2 = "#494D55"
        fontsize = 13
        fontweight = "medium"
        paddingFactor = 4.65
        rectYPos = 0.85
        rectHeight = 0.03

        # plot = self.ax1.get_position()
        #
        # Ax1PaddingToPlot = 27
        # Ax2PaddingToAx1 = 35
        #
        # distDrivername = self.convertInchesToFigureCoords(Ax1PaddingToPlot + Ax2PaddingToAx1)
        # distPos = self.convertInchesToFigureCoords(Ax1PaddingToPlot)
        # deltaPos = self.convertInchesToFigureCoords(52)
        #
        # self.fig.text(plot.x0 - distDrivername - 0.05, locationSeriesName - space * paddingFactor, "Driver",
        #               color=self.text_color, horizontalalignment="right", fontsize=fontsize, fontweight=fontweight)
        # self.fig.add_artist(patches.Rectangle((0, rectYPos), plot.x0 - distDrivername, rectHeight, facecolor=color2))
        #
        # self.fig.text(plot.x0 - distPos - 0.02, locationSeriesName - space * paddingFactor, "Pos",
        #               color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        # self.fig.add_artist(
        #     patches.Rectangle((plot.x0 - distDrivername, rectYPos), plot.x0 - distPos, rectHeight, facecolor=color1))
        #
        # self.fig.text(0.405, locationSeriesName - space * paddingFactor, "Personal median relative delta",
        #               color=self.text_color, horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        # self.fig.add_artist(patches.Rectangle((plot.x0, rectYPos), plot.x1 - plot.x0, rectHeight, facecolor=color2))
        #
        # self.fig.text(0.832, locationSeriesName - space * paddingFactor, "Delta", color=self.text_color,
        #               horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        # self.fig.add_artist(patches.Rectangle((plot.x1, rectYPos), plot.x1 + deltaPos, rectHeight, facecolor=color1))
        #
        # self.fig.text(0.91, locationSeriesName - space * paddingFactor, "Median", color=self.text_color,
        #               horizontalalignment="left", fontsize=fontsize, fontweight=fontweight)
        # self.fig.add_artist(
        #     patches.Rectangle((plot.x1 + deltaPos, rectYPos), 1 - deltaPos, rectHeight, facecolor=color2))

    def highlightUsername(self):

        index = self.data.userDriverIndex

        # labelax1 = self.ax1.get_yticklabels()[index]
        # labelax1.set_fontweight(1000)
        # labelax1.set_color(self.text_highlight_color)

        labelax2 = self.ax2.get_yticklabels()[index]
        labelax2.set_fontweight(1000)
        labelax2.set_color(self.text_highlight_color)

        # labelax5 = self.ax5.get_yticklabels()[index]
        # labelax5.set_color(self.text_highlight_color)

    def setXLabels(self):

        numberOfLaps = self.data.numberOfLaps

        self.ax1.set_xticks(np.arange(0, numberOfLaps + 1))
        self.ax1.set_xticklabels(np.arange(0, numberOfLaps + 1), fontsize="large", color=self.text_color)

    def drawPlot(self):

        drivers = self.data.drivers
        deltas = np.array([driver["deltaToTarget"] for driver in drivers])
        return self.ax1.plot(deltas.T)

    def limitYAxis(self):
        yMin = self.data.yMin
        yMax = self.data.yMax
        self.ax1.set(ylim=(yMin, yMax))

    def setYLabels(self):

        Ax1PaddingToPlot = 27  # finish pos
        Ax2PaddingToAx1 = 35  # name

        yMin = self.data.yMin
        yMax = self.data.yMax

        driverNames = self.data.driverNamesWithCarNumber

        step = 2.5

        if not yMin % step == 0:
            yMin = self.roundToNearest2Point5(yMin)

        if not yMax % step == 0:
            yMax = self.roundToNearest2Point5(yMax)

        number_of_seconds_shown = np.arange(yMin, yMax + step, step)
        ytickLabels = self.formatYMax(number_of_seconds_shown)

        self.ax1.spines['left'].set_visible(True)
        self.ax1.tick_params(axis="y", size=0)
        self.ax1.set_yticks(number_of_seconds_shown, ytickLabels, color=self.text_color, fontsize="11")

        # driver names
        self.ax2 = self.ax1.secondary_yaxis(location=1)
        # self.ax2.spines.left.set_position(('outward', Ax1PaddingToPlot + Ax2PaddingToAx1))
        self.ax2.spines['left'].set_visible(False)
        self.ax2.tick_params(axis="y", size=0)
        # maxYPosition = self.getMaxYPosition()
        driverNameYPositions = np.linspace(0, yMax, len(driverNames))
        self.ax2.set_yticks(driverNameYPositions, driverNames, ha="left", color=self.text_color, fontsize="11")

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

    def colorDiscDisq(self):

        indicesToColor = []
        drivers = self.data.drivers

        for i, driver in enumerate(drivers):
            if driver["result_status"] == "Disconnected" or driver["result_status"] == "Disqualified":
                indicesToColor.append(i)

        for driverIndex in indicesToColor:
            box = self.plot[driverIndex]
            box.set_color("#6F6F6F")

    def replaceName(self):

        index = self.data.userDriverIndex
        displayName = self.data.displayName

        labels = [item.get_text() for item in self.ax2.get_yticklabels()]
        labels[index] = displayName
        self.ax2.set_yticklabels(labels)

    def getImagePath(self):
        imagePath = Path().absolute() / 'output'
        figureName = f"delta_{str(uuid.uuid4())}.png"
        location = str(imagePath / figureName)
        return location

    def setGrid(self):
        self.ax1.grid(visible=False)
        self.ax1.grid(color=self.ax_gridlines_color, axis="x", zorder=0)
        self.ax1.grid(color=self.ax_gridlines_color, axis="y", zorder=0)

    def limitXAxis(self):
        numberOfLaps = self.data.numberOfLaps
        self.ax1.set(xlim=(0, numberOfLaps - 1))

    def convertInchesToFigureCoords(self, points):
        fig_width_inches = self.fig.get_size_inches()[0]  # figure width in inches
        inches = points / 72
        diff = inches / fig_width_inches
        return diff

    def highlightUserLine(self):

        index = self.data.userDriverIndex

        userLine = self.plot[index]
        userLine.set_color(self.user_linecolor)
        userLine.set_linewidth(2)
        userLine.set(zorder=10)

    def colorDrivernames(self):
        for i, line in enumerate(self.plot):
            color = line.get_c()
            label = self.ax2.get_yticklabels()[i]
            label.set_color(color)

    def calcPxWidth(self):
        widthPerLap = 65
        numberOfLaps = self.data.numberOfLaps

        if numberOfLaps < 10:
           px_width = widthPerLap * 10
        else:
            px_width = widthPerLap * numberOfLaps

        return px_width