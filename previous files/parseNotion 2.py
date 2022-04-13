from gs_api import Scholar
from notion_api import NotionDatabase
import json

class NotionUniversity(NotionDatabase):
    """docstring for NotoionDatabase"""
    def __init__(self, databaseID, token):
        super(NotionUniversity, self).__init__(databaseID, token)
        self.universitiesData = self.readDatabase()
        self.databaseID = databaseID
        self.token = token

        with open('./db_old.json', 'w', encoding='utf8') as f:
            json.dump(self.universitiesData, f, ensure_ascii=False)

    @staticmethod
    def getPropertyTitle(page):
        pageProperties=page["properties"]["Name"]["title"]
        if not pageProperties:
            return 0
        return pageProperties[0]['text']['content']

    @staticmethod
    def getID(page):
        return page['id']

    def getPages(self):
        pages = self.universitiesData["results"]
        return pages

    def getPageByName(self, name):
        pages = self.universitiesData["results"]
        for page in pages:
            if self.getPropertyTitle(page) == name:
                return page


    def setPropertyTitle(self, page, name):
        pageProperties=page.get("properties")
        pageProperties["Name"] = {"title":[{"text":{"content": name}}]}
        print(f"**updating Title")
        self.updatePage(updateData={"properties":pageProperties}, pageId=page['id'])
        return 1

    def get_name_ID_pairs(self):
        pages = self.getPages()
        name_ID_pairs = {}
        for page in pages:
            title = self.getPropertyTitle(page)
            ID = self.getID(page)
            name_ID_pairs[title] = ID
        return name_ID_pairs

    def setIcon(self, page, picture_url):
        print(f"...... updating Icon")
        page["icon"]={"type": "external","external": {"url": picture_url}}
        self.updatePage(updateData={"icon": page["icon"]}, pageId=page['id'])
        return 1

    def setCover(self, page, picture_url):
        print(f"...... updating Cover")
        page["cover"]={"type": "external","external": {"url": picture_url}}
        self.updatePage(updateData={"cover": page["cover"]}, pageId=page['id'])
        return 1

    def createUniversityFromName(self, name):
        #page create template
        template = {
                        "object": "page",
                        "parent":
                        {
                            "type": "database_id",
                            "database_id": self.databaseID
                        },
                        "properties":
                        {
                            "Name":{"title":[{"text":{"content": name}}]}
                        }
                    }
        self.createPage(template)
        self.__init__(databaseID=self.databaseID, token=self.token)
        return self.get_name_ID_pairs()



class NotionScholar(NotionDatabase):
    """docstring for NotoionDatabase"""
    def __init__(self, databaseID, token):
        super(NotionScholar, self).__init__(databaseID, token)
        self.scholarsData = self.readDatabase()
        self.universityKeys = {}
        self.createUniversityFromName = None

        with open('./db_old.json', 'w', encoding='utf8') as f:
            json.dump(self.scholarsData, f, ensure_ascii=False)

    @staticmethod
    def evaluatePropertyTitle(pageProperties, scholar):
        if pageProperties["Name"]["title"]:
            return 0
        pageProperties["Name"] ={
          "id": "title",
          "type": "title",
          "title": [
            {
              "type": "text",
              "text": {
                "content": scholar.name,
              },
              "plain_text": scholar.name,
            }
          ]
        }
        print(f"...... updating Name for {scholar.name}")
        return 1

    @staticmethod
    def evaluatePropertyInterests(pageProperties, scholar):
        oldInterests=[i["name"].lower() for i in dict(pageProperties.get("Interests")).get("multi_select")]
        newInterests=scholar.interests

        # if set(newInterests) == set(oldInterests):
        #     return 0

        if oldInterests:
            return 0

        print(f"...... updating interests of {scholar.name}")
        pageProperties["Interests"]= {
              "type": "multi_select",
              "multi_select": [{"name":interest} for interest in newInterests]
            }
        return 1


    def evaluatePropertyUniversity(self, pageProperties, scholar):
        if dict(pageProperties.get("University")).get("relation"):
            return 0

        if not scholar.organizationName:
            return 0

        universityKey = self.universityKeys.get(scholar.organizationName)

        if not universityKey:
            if not self.createUniversityFromName:
                return 0
            self.universityKeys = self.createUniversityFromName(scholar.organizationName)
            universityKey = self.universityKeys.get(scholar.organizationName)

        pageProperties["University"]={"relation":[{"id": universityKey}]}
        print(f"...... updating University for {scholar.name} to {scholar.organizationName}")
        return 1


    @staticmethod
    def evaluatePropertyMetrics(pageProperties, scholar):
        citations = pageProperties.get("Citations")
        hindex = pageProperties.get("H-index")
        i10index = pageProperties.get("i10 index")
        citations_5y = pageProperties.get("5Y-Citations")
        hindex_5y = pageProperties.get("5Y-H-index")
        i10index_5y = pageProperties.get("5Y-i10 index")

        if all([citations, hindex, i10index, citations_5y, hindex_5y, i10index_5y]):
            return 0

        print(f"...... updating indices for {scholar.name}")
        pageProperties["Citations"] = {"number": int(scholar.indices[0])}
        pageProperties["H-index"] = {"number": int(scholar.indices[1])}
        pageProperties["i10 index"] = {"number": int(scholar.indices[2])}
        pageProperties["5Y-Citations"] = {"number": int(scholar.indices_5y[0])}
        pageProperties["5Y-H-index"] = {"number": int(scholar.indices_5y[1])}
        pageProperties["5Y-i10 index"] = {"number": int(scholar.indices_5y[2])}
        return 1

    @staticmethod
    def evaluatePropertyHomepage(pageProperties, scholar):
        if pageProperties.get("website"):
            return 0

        pageProperties["website"] = {
          "type": "url",
          "url": scholar.homepage
        }
        print(f"...... updating Webpage for {scholar.name} to {scholar.homepage}")
        return 1

    @staticmethod
    def evaluateIcon(page, scholar):
        if page.get("icon"): return 0
        print(f"...... updating Icon for {scholar.name}")
        page["icon"]={"type": "external","external": {"url": scholar.picture}}
        return 1

    @staticmethod
    def evaluateCover(page, scholar):
        if page.get("cover"): return 0
        print(f"...... updating Cover for {scholar.name}")
        page["cover"]={"type": "external","external": {"url": scholar.picture}}
        return 1


    def updatePageOfScholar(self, page):
        pageProperties=page.get("properties")


        # ==============================
        # =           Filter    ########## TODO       =
        # ==============================
        FILTER = pageProperties.get("Citations")
        if FILTER:
            return 0
        # ======  End of Filter  =======

        URLproperty = pageProperties.get("Google Scholar")
        if URLproperty is None:
            return 0

        #-------------------------------
        scholar = Scholar.from_url(URLproperty['url'], verbose=False)
        #-------------------------------
        print(f"*** Comparing {scholar.name} / {scholar.organizationName} ***")
        status  =  [self.evaluatePropertyTitle(pageProperties, scholar),
                    self.evaluatePropertyInterests(pageProperties, scholar),
                    self.evaluatePropertyUniversity(pageProperties, scholar),
                    self.evaluatePropertyMetrics(pageProperties, scholar),
                    self.evaluatePropertyHomepage(pageProperties, scholar)]

        if any(status):
            self.updatePage(updateData={"properties":pageProperties}, pageId=page['id'])

        if self.evaluateIcon(page, scholar):
            self.updatePage(updateData={"icon": page["icon"]}, pageId=page['id'])

        if self.evaluateCover(page, scholar):
            self.updatePage(updateData={"cover": page["cover"]}, pageId=page['id'])

        iners = [
        {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{ "type": "text", "text": { "content": "Lacinato kale" } }]
            }
        },
        {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "type": "text",
                        "text": {
                            "content": "Lacinato kale is a variety of kale with a long tradition in Italian cuisine, especially that of Tuscany. It is also known as Tuscan kale, Italian kale, dinosaur kale, kale, flat back kale, palm tree kale, or black Tuscan palm.",
                            "link": { "url": "https://en.wikipedia.org/wiki/Lacinato_kale" }
                        }
                    }
                ]
            }
        }
    ]
        self.updatePage(updateData = {"children" : iners}, pageId=page['id'])


    def updatePageOfAllScholars(self):
        pages = self.scholarsData["results"]
        for page in pages:
            self.updatePageOfScholar(page)

        with open('./db_new.json', 'w', encoding='utf8') as f:
            json.dump(self.scholarsData, f, ensure_ascii=False)

    # def createPageWithName(self, name):
    #     #page create template
    #     template = {
    #                     "object": "page",
    #                     "parent":
    #                     {
    #                         "type": "database_id",
    #                         "database_id": databaseID
    #                     },
    #                     "properties":
    #                     {
    #                         "Name":{"title":[{"text":{"content": name}}]}
    #                     }
    #                 }
    #     self.createPage(template)




if __name__ == "__main__":
    # #main
    DATABASE_SCHOLAR_ID = '36ecfe52ed5e44cc98ab4f22a87eb4ea'
    DATABASE_UNIVERSITY_ID='f5a0ae0dc0bf4a33a6fcccdc6129bd28'

    # #practice
    # DATABASE_SCHOLAR_ID = '80b2fd2cf0b64759908018cf0da58f4d'
    # DATABASE_UNIVERSITY_ID='3b30954e568b4da788f20825279472d9'

    token = 'secret_wFBrBJ2HvixP9R8eZvo5WFzLqkiyQWzC46eFH9QWDp7'

    universitiesData = NotionUniversity(databaseID = DATABASE_UNIVERSITY_ID, token=token)

    scholarsData = NotionScholar(databaseID=DATABASE_SCHOLAR_ID, token=token)
    scholarsData.universityKeys = universitiesData.get_name_ID_pairs()
    scholarsData.createUniversityFromName = universitiesData.createUniversityFromName

    scholarsData.updatePageOfAllScholars()


    # universities.createPageWithName("rishabh shukla")
