import asyncio

from _api.apiMock import read_file_content
from _backend.application.dataprocessors.boxplot import Boxplot
from _backend.application.diagrams.boxplot import BoxplotDiagram

async def getBoxplotData(**kwargs):

    selectedSession = kwargs.get('selectedSession', None)
    subsessionId = kwargs.get('subsessionId', None)
    userId = kwargs.get('userId', None)
    showRealName = kwargs.get('showRealName', None)

    userId = 817394
    selectedSession = -1
    # subsessionId = 50881221

    responseData = await Boxplot().get_Boxplot_Data(userId=userId, selectedSession=selectedSession, subsessionId=subsessionId)

    # write_file_content(responseData)
    # responseData = read_file_content()

    fileLocation = BoxplotDiagram(responseData, showRealName=showRealName).draw()

    return fileLocation