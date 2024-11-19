import asyncio

from cssselect import Selector
from matplotlib.pyplot import boxplot

from _backend.application.dataprocessors.boxplot import Boxplot
from _backend.application.diagrams.boxplot import BoxplotDiagram
from _backend.application.diagrams.median import MedianDiagram
from _backend.application.service.recent_races import requestSubessionId
from _backend.application.session.sessionmanager import SessionManager
from devutils.dev import read_file_content, write_file_content


async def getBoxplotData(**kwargs):

    selectedSession = kwargs.get('selectedSession', None)
    subsessionId = kwargs.get('subsessionId', None)
    userId = kwargs.get('userId', None)
    showRealName = kwargs.get('showRealName', None)
    showLaptimes = kwargs.get('showLaptimes', None)
    sessionManager: SessionManager = kwargs.get("sessionManager")

    # sessionManager.newSession()

    # if not subsessionId:
    #     subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

    # boxplotData = await Boxplot().get_Boxplot_Data(userId, subsessionId, sessionManager)
    # write_file_content(boxplotData)
    boxplotData = read_file_content()
    fileLocation = BoxplotDiagram(boxplotData, showRealName=showRealName, showLaptimes=showLaptimes).draw()
    return fileLocation

async def getDeltaData(**kwargs):
    pass

async def getMedianData(**kwargs):
    selectedSession = kwargs.get('selectedSession', None)
    subsessionId = kwargs.get('subsessionId', None)
    userId = kwargs.get('userId', None)
    showRealName = kwargs.get('showRealName', None)
    showLaptimes = kwargs.get('showLaptimes', None)
    sessionManager: SessionManager = kwargs.get("sessionManager")

    # sessionManager.newSession()

    # if not subsessionId:
    #     subsessionId = await requestSubessionId(userId, selectedSession, sessionManager)

    # boxplotData = await Boxplot().get_Boxplot_Data(userId, subsessionId, sessionManager)
    boxplotData = read_file_content()
    fileLocation = MedianDiagram(boxplotData, showRealName=showRealName, showLaptimes=showLaptimes).draw()
    return fileLocation

asyncio.run(getMedianData(userId=817320, selectedSession=-1))
