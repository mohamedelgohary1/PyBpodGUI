import pyqtgraph as pg
import logging
from PyQt5.QtCore import QObject, QThread, QTimer, pyqtSignal


logging.basicConfig(format="%(message)s", level=logging.INFO)


class ResultsPlotWorker(QObject):
    def __init__(self):
        super(ResultsPlotWorker, self).__init__()
        # QObject.__init__(self)  # super(...).__init() does this for you in the line above.
        self.graphWidget = pg.PlotWidget()
        self.pen = pg.mkPen(color='r', width=2)
        self.colors = ['r', 'g', 'b', 'c', 'm', 'y', 'k']
        styles = {'color':'blue', 'font-size': '10pt'}
        self.graphWidget.setBackground('w')
        self.graphWidget.setTitle('Percent Left Licks For Each Flow Rate', color='b', size='10pt')
        self.graphWidget.setLabel('left', 'Percent Left Licks', **styles)
        self.graphWidget.setLabel('bottom', 'Flow Rate', **styles)
        self.graphWidget.addLegend()
        self.xAxis = self.graphWidget.getAxis('bottom')
        self.graphWidget.setYRange(0, 100, padding=0)
        self.xAxisReady = False

    def getWidget(self):
        return self.graphWidget

    def updatePlot(self, resultsDict):
        if not self.xAxisReady:
            flowrates = list(resultsDict.values())  # Get a list of each vial's sub dictionary whose keys are flowrates, instead of doing resultsDict['vial_5'] since vial number '5' might not always exist.
            ticks = list(flowrates[0].keys())  #  flowrates is a list of dictionaries that contain the flowrates, but the values are all the same because they are the same set of flowrates. So just take the first element in that list and then make a list of the flowrates.
            xdict = dict(enumerate(ticks))
            self.xAxis.setTicks([xdict.items()])
            self.graphWidget.setXRange(-1, len(ticks), padding=0)
            self.xAxisReady = True
        
        colorIndex = 0
        self.graphWidget.clear()

        for vialNum, flowrateDict in resultsDict.items():
            xValues = []
            yValues = []
            index = 0
            for k, v in flowrateDict.items():
                numLeft = v['left']
                # numTotal = v['Total']  # I do not want to use this because if the mouse does not response many times, it will increase the denominator and lower the percentage.
                numResponses = v['Correct'] + v['Wrong']  # I only want the denominator to be the total number of actual responses.
                if not (numResponses == 0):
                    percent = round((float(numLeft) / float(numResponses) * 100), 2)
                else:
                    percent = 0.0  # To handle divide-by-zero-error that occurs when the flow has not yet been used.
                xValues.append(index)  # I use index instead of 'int(k)' because I setup custom tick labels for each flow rate in the ResultsPlot class and inside it, there is a dict with integers as keys and strings as values for the flow rate.
                yValues.append(percent)
                index += 1

            self.pen = pg.mkPen(color=self.colors[colorIndex], width=2)
            self.graphWidget.plot(xValues, yValues, name=f'Vial {vialNum}', pen=self.pen, symbol='s', symbolSize=10, symbolBrush=self.colors[colorIndex])
            colorIndex += 1
        
        logging.info('results plot updated')
