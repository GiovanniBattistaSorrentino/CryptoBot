# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.


class News:
    def __init__(self, name: str = None, url: str = None, description: str = None, data_published: str = None):
        self.name = name
        self.url = url
        self.description = description
        self.data_published = data_published

    # Getter
    def getName(self):
        return self.name

    def getUrl(self):
        return self.url

    def getDescription(self):
        return self.description

    def getData_published(self):
        return self.data_published

    # Setter
    def setName(self, name):
        self.name = name

    def setUrl(self, url):
        self.url = url

    def setDescription(self, description):
        self.description = description

    def setData_published(self, data_published):
        self.data_published = data_published

    # metodi sovrascritti
    def __str__(self):
        return f"name: {self.name}, " \
               f"url: {self.url}, " \
               f"description: {self.description}, " \
               f"data_published: {self.data_published}"

    # Metodi sovrascritti
    def __eq__(self, o: object) -> bool:
        if isinstance(o, News):
            return self.name == o.name and self.url == o.url and self.description == o.description and self.data_published == o.data_published
