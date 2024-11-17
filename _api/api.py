from _backend.application.dataprocessors.boxplot import Boxplot
from _backend.application.diagrams.boxplot import BoxplotDiagram


async def getBoxplotData(**kwargs):

    selectedSession = kwargs.get('selectedSession', None)
    subsessionId = kwargs.get('subsessionId', None)
    userId = kwargs.get('userId', None)
    showRealName = kwargs.get('showRealName', None)
    showLaptimes = kwargs.get('showLaptimes')

    responseData = await Boxplot().get_Boxplot_Data(userId=userId, selectedSession=selectedSession, subsessionId=subsessionId)
    fileLocation = BoxplotDiagram(responseData, showRealName=showRealName, showLaptimes=showLaptimes).draw()
    return fileLocation

async def getDeltaData(**kwargs):
    pass