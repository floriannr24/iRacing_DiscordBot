import requests
from _backend.application.sessionbuilder.session_builder import responseIsValid


class Driver:

    def __init__(self, session):
        self.session = session
        self.licenses = None
        self.cust_id = None

    def requestDriver(self, session):
        response = session.get('https://members-ng.iracing.com/data/lookup/drivers', params={})
        response = response.json()
        response = requests.get(response["link"])
        response = response.json()[0]

        self.cust_id = response["cust_id"]
        self.licenses = response["licenses"]

    def get_AccountInfo(self, cust_id):
        response = self.session.get('https://members-ng.iracing.com/data/member/get', params={"cust_ids": cust_id})

        # check if iRacing API is up
        if not responseIsValid(response):
            return {
                "response": response,
                "data": None
            }

        responseLink = self.session.get(response.json()["link"])
        print(responseLink.json())
        data = responseLink.json()

        # if no user was found for cust_id
        if len(data["members"]) == 0:
            response.status_code = 400
            return {
                "response": response,
                "data": ""
            }

        return {
            "response": response,
            "data": data["members"][0]["display_name"]
        }


