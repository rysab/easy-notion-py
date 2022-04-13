import requests, json

class NotionDatabase(object):
    """docstring for NotionDatabase"""
    def __init__(self, databaseID, token):
        super(NotionDatabase, self).__init__()
        self.databaseID = databaseID
        token = token #am20s009
        self.headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13"
        }

    def readDatabase(self):
        readUrl = f"https://api.notion.com/v1/databases/{self.databaseID}/query"
        res = requests.request("POST", readUrl, headers=self.headers)
        data = res.json()
        print(res.status_code)
        # print(res.text)
        return data

    def createPage(self, newPageData):
        createUrl = 'https://api.notion.com/v1/pages'
        data = json.dumps(newPageData)
        # print(str(uploadData))
        res = requests.request("POST", createUrl, headers=self.headers, data=data)
        print(res.status_code)
        print(res.text)

    def updatePage(self, updateData, pageId):
        updateUrl = f"https://api.notion.com/v1/pages/{pageId}"
        data = json.dumps(updateData)
        response = requests.request("PATCH", updateUrl, headers=self.headers, data=data)
        print(response.status_code)
        # print(response.text)


