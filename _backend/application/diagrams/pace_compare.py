import statistics
from datetime import timedelta
import numpy as np
from matplotlib import pyplot as plt
from diagrams.base import Base


class PaceCompare(Base):
    def __init__(self, input, config):
        self.race_completed_laps, self.metaData = self.unpackData(input)
        self.number_Of_Races = len(input)
        self.boxplot = None
        self.ymin, self.ymax, self.interval, self.showMean = self.unpackConfig(config.options)

        # draw
        super().__init__(input, config.options.get("px_width"), config.options.get("px_height"))
        self.draw(config.options)

    def draw(self, options):

        xmin = 0
        xmax = self.number_Of_Races + 1

        self.boxplot = self.ax.boxplot(self.race_completed_laps,
                        patch_artist=True,
                        boxprops=dict(facecolor="#0084F2", color="#000000"),
                        flierprops=dict(markeredgecolor='#000000'),
                        medianprops=dict(color="#000000", linewidth=2),
                        whiskerprops=dict(color="#000000"),
                        capprops=dict(color="#000000"),
                        zorder=2,
                        widths=0.3,
                        showmeans=self.showMean,
                        meanprops=dict(marker="o", markerfacecolor="red", fillstyle="full", markeredgecolor="None")
                        )

        if options.get("showLaptimes") == 1:
            self.draw_laptimes()

        y_higherWhisker, y_75, y_median, y_25, y_lowerWhisker, x_coords = self.calcLines(self.race_completed_laps)

        self.draw_lines(y_higherWhisker, y_75, y_median, y_25, y_lowerWhisker, x_coords)

        # formatting
        number_of_seconds_shown = np.arange(self.ymin, self.ymax + self.interval, self.interval)

        self.ax.set(xlim=(xmin, xmax), ylim=(self.ymin, self.ymax))
        self.ax.set_yticks(number_of_seconds_shown)
        self.ax.set_yticklabels(self.calculateMinutesYAxis(number_of_seconds_shown))

        self.formatXTicks(self.metaData)

        plt.tight_layout()
        plt._showMenu()

    def draw_laptimes(self):

        showLapCountLabels = False
        showMedianLabels = True

        scatter = []
        for i, lapdata in enumerate(self.race_completed_laps):
            x = np.random.normal(i + 1, 0.03, len(lapdata))
            scatter.append(x)

        for i, data in enumerate(self.race_completed_laps):
            self.ax.scatter(scatter[i], self.race_completed_laps[i],
                            zorder=3,
                            alpha=0.5,
                            c="yellow",
                            s=15
                            )
            for x, txt in enumerate(range(1, len(data))):
                self.ax.annotate(round(txt, 2), (scatter[i][x]+0.1, self.race_completed_laps[i][x]), color="yellow", fontsize=8, visible=showLapCountLabels)

            self.ax.annotate(round(statistics.median(data), 2), (i+1.2, round(statistics.median(data), 2)),
                             color="#B3DFFF",
                             fontsize=11,
                             visible=showMedianLabels,
                             weight="bold"
                             )

    def draw_lines(self, y_higherWhisker, y_75, y_median, y_25, y_lowerWhisker, x_coords):

        plt.plot(x_coords, y_median, color="#0084F2", zorder=2)

        plt.fill_between(x_coords, np.array(y_higherWhisker), np.array(y_lowerWhisker), where=(np.array(y_higherWhisker) > np.array(y_lowerWhisker)), color="#202226", alpha=0.3)
        plt.fill_between(x_coords, np.array(y_75), np.array(y_25), where=(np.array(y_75) > np.array(y_25)), color="#202226", alpha=1)

    def calculateYMaxMin(self, lapdata, roundBase):

        result = []
        tempMax = []
        tempMin = []

        for laps in lapdata:

            if not laps:
                continue

            Q1, Q3 = np.percentile(laps, [25, 75])
            IQR = Q3 - Q1

            loval = Q1 - 1.5 * IQR
            hival = Q3 + 1.5 * IQR

            # find closest real laptime value compared to hival/loval
            candidates_for_top_border = max([item for item in laps if item < hival])
            tempMax.append(candidates_for_top_border)
            tempMin.append(min(laps, key=lambda x: abs(x - loval)))

        maxVal = max(tempMax)  # top border
        minVal = min(tempMin)  # bottom border

        # round min to the nearest base (= roundBase; 0.5)
        minVal_test = roundBase * round(minVal / roundBase)

        # if minVal has been rounded up, round down 0.5
        if minVal_test > minVal:
            minval_final = minVal_test - 0.5
            result.append(minval_final)
        else:
            result.append(minVal_test)
        result.append(roundBase * round(maxVal / roundBase))
        return result

    def calculateMinutesYAxis(self, number_of_seconds_shown):

        yticks = []
        for sec in number_of_seconds_shown:
            sec_rounded = round(sec, 2)
            td_raw = str(timedelta(seconds=sec_rounded))

            if "." not in td_raw:
                td_raw = td_raw + ".000000"

            td_minutes = td_raw.split(":", 1)[1]
            yticks.append(td_minutes[:-3])

        return yticks

    def unpackConfig(self, options):

        if options.get("setYAxis") == 1:
            ymin = options.get("minVal")
            ymax = options.get("maxVal")
        else:
            maxmin = self.calculateYMaxMin(self.race_completed_laps, 0.5)
            ymax = maxmin[1]
            ymin = maxmin[0]

        if options.get("setYAxisInterval") == 1:
            interval = options.get("interval")
        else:
            interval = 0.5

        if options.get("showDISC") == 0:
            number_Of_Drivers_Not_Completed = len([data for data in self.race_not_completed_laps if not not data])
            self.number_Of_Races = self.number_Of_Drivers - number_Of_Drivers_Not_Completed
            self.drivers_raw = self.drivers_raw[:-number_Of_Drivers_Not_Completed or None]

        if options.get("showMean") == 1:
            showMean = True
        else: showMean = False

        return ymin, ymax, interval, showMean

    def unpackData(self, input):
        data = []
        metaData = []
        for race in input:
            data.append(input[race]["laps"])
            metaData.append(input[race]["metaData"])

        return data, metaData

    def calcLines(self, race_completed_laps):

        y_median = []
        y_25 = []
        y_75 = []
        x_coords = list(range(1, len(race_completed_laps)+1, 1))

        for lap in race_completed_laps:
            y_median.append(statistics.median(lap))
            y_75.append(np.percentile(lap, 75))
            y_25.append(np.percentile(lap, 25))

        y_higherWhisker = [item.get_ydata()[1] for item in self.boxplot["whiskers"]][1::2]
        y_lowerWhisker = [item.get_ydata()[1] for item in self.boxplot["whiskers"]][0::2]

        return y_higherWhisker, y_75, y_median, y_25, y_lowerWhisker, x_coords

    def formatXTicks(self, metaData):

        weather = []

        for data in metaData:
            temp = data["weather"]["temp_value"]
            humid = data["weather"]["rel_humidity"]
            skies = data["weather"]["skies"]
            type = data["weather"]["type"]
            wind_dir = data["weather"]["wind_dir"]
            wind_value = data["weather"]["wind_value"]

            match skies:
                case 0:
                    skies = "Clear"
                case 1:
                    skies = "Partly cloudy"
                case 2:
                    skies = "Mostly cloudy"

            weather.append(f"{int(round(((temp-32)/1.8),0))}°C\n{temp}°F\n{skies}\n{humid}%")

        self.ax.set_xticks(np.arange(1, self.number_Of_Races + 1))
        self.ax.set_xticklabels(weather)

        pass



