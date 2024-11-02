import json

import matplotlib
from fastapi import FastAPI, status, Response
from fastapi.middleware.cors import CORSMiddleware

from _backend.api.apiMock import read_file_content
from _backend.application.data.driver import Driver
from _backend.application.data.recent_races import RecentRaces
from _backend.application.dataprocessors.boxplot import Boxplot
from _backend.application.dataprocessors.sessionInfo import SessionInfo
from _backend.application.diagrams.boxplot import BoxplotDiagram
from _backend.application.sessionbuilder.session_builder import SessionBuilder, responseIsValid
from _backend.application.utils.configurator import Configurator

app = FastAPI()

origins = [
    "http://localhost:4200",
]

sessionBuilder = SessionBuilder()
sessionBuilder.authenticate()
session = sessionBuilder.session

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/data/recentRaces/{cust_id}", status_code=status.HTTP_200_OK)
def getRecentRaces(cust_id: int):
    responseData = RecentRaces(session).get_RecentRaces(cust_id)

    # print(responseData)

    # if responseIsValid(responseData["response"]):
    #     return responseData["data"]
    # else:
    #     response.status_code = responseData["response"].status_code
    #     return


@app.get("/diagram/boxplot/{subsession_id}", status_code=status.HTTP_200_OK)
def getBoxplotData(subsession_id: int):
    responseData = Boxplot(session).get_Boxplot_Data(subsession_id)

    # responseData = read_file_content()

    BoxplotDiagram(data=responseData)

    # if responseIsValid(responseData["response"]):
    #     return responseData["data"]
    # else:
    #     response.status_code = responseData["response"].status_code
    #     return


@app.get("/data/subsessionInfo/{subsession_id}", status_code=status.HTTP_200_OK)
def getSubsessionInfo(subsession_id: int, response: Response):
    responseData = SessionInfo(session).get_SessionInfo_Data(subsession_id)

    # if responseIsValid(responseData["response"]):
    #     return responseData["data"]
    # else:
    #     response.status_code = responseData["response"].status_code
    #     return


@app.get("/accountInfo/{cust_id}", status_code=status.HTTP_200_OK)
def getAccountInfo(cust_id: int, response: Response):
    responseData = Driver(session).get_AccountInfo(cust_id)

    # if responseIsValid(responseData["response"]):
    #     return responseData["data"]
    # else:
    #     response.status_code = responseData["response"].status_code
    #     return

# getBoxplotData(72424281) # sinlgeclass
getBoxplotData(72423313) # multiclass

# getRecentRaces(817320)
