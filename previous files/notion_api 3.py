import requests, json
import re


def _GET_HEADERS_FROM_TOKEN(token):
    headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13"
        }
    return headers


def _GET_FIRST_MATCH(pattern, string):
    pattern = re.compile(pattern)
    match = re.search(pattern,string)
    span = match.span()
    return string[span[0]+1 :span[1]-2]


def _DUMP_JSON_TO_FILE(data, name):
    file = f'./{name}'
    with open(file, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False)
        print(f"Dumped JSON to {file}")


"""HIERARCHY
NotionUserObject(object)
|
NotionDataBase(object):
|
NotionPage(object):
|
NotionBlocks:
|
.....
"""

class NotionBase(object):
    """docstring for NotionAPI_Headers"""
    def __init__(self, token):
        super(NotionBase, self).__init__()
        self.token = token
        self.headers = headers = {
            "Authorization": "Bearer " + token,
            "Content-Type": "application/json",
            "Notion-Version": "2021-05-13"
        }

    def __repr__(self):
        return json.dumps(self.headers, indent=3)



class NotionDatabase(NotionBase):
    """DATABASE_OBJECT
    {
        object:
        results: [PAGE_OBJECT_1, PAGE_OBJECT_2]
        next_cursor: null
        has_more: false
    }
    """
    def __init__(self, databaseID, notionBase):
        super(NotionDatabase, self).__init__(notionBase.token)
        self.databaseID = databaseID
        self.data = None

    @classmethod
    def from_a_view_URL(cls, url, notionBase):
        """
        SAMPLE URL:
        https://www.notion.so/rysav/36ecfe52ed5e44cc98ab4f22a87eb4ea?v=23a032978ccc4cc78ff238163bb25bbc
        """
        dbPattern = r'/[^/]*\?v'
        databaseID = _GET_FIRST_MATCH(dbPattern, url)
        return cls(databaseID, notionBase)

    def readDatabase(self):
        readUrl = f"https://api.notion.com/v1/databases/{self.databaseID}/query"
        res = requests.request("POST", readUrl, headers=self.headers)
        statusCode = res.status_code
        # print(res.text)
        if statusCode == 200:
            print(f"-Reading Database Completed : Status {statusCode}")
            data = res.json()
            self.data = data
            return data
        else:
            print(f"-Reading Database Failed : Status {statusCode}")
            return None

    def createDatabase():
        _BLANK_DATABASE_TEMPLATE = {
            "object": "list",
            "results":
            [
                "PAGE_DATA_1",
                "PAGE_DATA_2",
                "..........."
            ],
            "next_cursor": null,
            "has_more": false
        }

    def updateDatabase():
        pass

    def getIDObject():
        info = {
            "type": "database_id",
            "database_id": self.databaseID
        }
        return info

    def __repr__(self):
        return json.dumps(self.data, indent=3)



class NotionPage(object):
    """PAGE OBJECT
    {
        object:
        id:
        created_time:
        last_edited_time:
        created_by:
        last_edited_by:
        cover:
        icon:
        parent:
    }
    """
    def __init__(self, pageID, token):
        super(NotionPage, self).__init__()
        self.pageID = pageID
        self.headers = _GET_HEADERS_FROM_TOKEN(token)
        self.data = None

    def createPage(self, newPageData, databaseID):
        #TODO - Update self.data after create page
        _BLANK_PAGE_TEMPLATE = {
            "object": "page",
            "id": "0e2475ec-cb6c-457d-ba50-09990f54fd4f",
            "created_time": "2022-04-12T10:21:00.000Z",
            "last_edited_time": "2022-04-12T10:21:00.000Z",
            "created_by":
            {
                "object": "user",
                "id": "20f3bc22-ba63-4f66-98b7-e665387b3138"
            },
            "last_edited_by":
            {
                "object": "user",
                "id": "20f3bc22-ba63-4f66-98b7-e665387b3138"
            },
            "cover": null,
            "icon": null,
            "parent":
            {
                "type": "database_id",
                "database_id": "6ee7657b-d396-47aa-991e-51edcc3167a3"
            },
            "archived": false,
            "properties":
            {
                "Name":
                {
                    "id": "title",
                    "type": "title",
                    "title":
                    []
                }
            },
            "url": "https://www.notion.so/0e2475eccb6c457dba5009990f54fd4f"
        }

        createUrl = 'https://api.notion.com/v1/pages'
        data = json.dumps(newPageData)
        res = requests.request("POST", createUrl, headers=self.headers, data=data)
        statusCode = res.status_code
        # print(res.text)
        if statusCode == 200:
            print(f"--Page Creation Completed : Status {statusCode}")
            self.data["results"].append(newPageData)
            return
        else:
            print(f"--Page Creation Failed : Status {statusCode}")
            return None

    def updatePage(self, updateData, pageId):
        updateUrl = f"https://api.notion.com/v1/pages/{pageId}"
        data = json.dumps(updateData)
        response = requests.request("PATCH", updateUrl, headers=self.headers, data=data)
        print(response.status_code)
        # print(response.text)







if __name__ == "__main__":
    notionBase = NotionBase('secret_wFBrBJ2HvixP9R8eZvo5WFzLqkiyQWzC46eFH9QWDp7')

    testURL = "https://www.notion.so/rysav/6ee7657bd39647aa991e51edcc3167a3?v=cf2aa57ea6234b01a0703797e4850ba3"
    notionDatabase = NotionDatabase.from_a_view_URL(testURL, notionBase)

    # print(notionBase)
    databaseData = notionDatabase.readDatabase()
    # print(notionDatabase)
    # newPageData =     {
    #     "object": "page",
    #     "id": "0e2475ec-cb6c-457d-ba50-09990f54fd4f",
    #     "created_time": "2022-04-12T10:21:00.000Z",
    #     "last_edited_time": "2022-04-12T10:21:00.000Z",
    #     "created_by":
    #     {
    #         "object": "user",
    #         "id": "20f3bc22-ba63-4f66-98b7-e665387b3138"
    #     },
    #     "last_edited_by":
    #     {
    #         "object": "user",
    #         "id": "20f3bc22-ba63-4f66-98b7-e665387b3138"
    #     },
    #     "parent":
    #     {
    #         "type": "database_id",
    #         "database_id": "6ee7657b-d396-47aa-991e-51edcc3167a3"
    #     },
    #     "archived": false,
    #     "properties":
    #     {
    #         "Name":
    #         {
    #             "id": "title",
    #             "type": "title",
    #             "title":
    #             []
    #         }
    #     },
    #     "url": "https://www.notion.so/0e2475eccb6c457dba5009990f54fd4f"
    # }

    # notionDB.createPage(newPageData)










