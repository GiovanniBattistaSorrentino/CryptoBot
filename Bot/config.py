#!/usr/bin/env python3
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import os

""" Bot Configuration """


class DefaultConfig:
    """ Bot Configuration """

    PORT = 3978
    APP_ID = os.environ.get("MicrosoftAppId", "")
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

    # Qna Maker
    QNA_KNOWLEDGEBASE_ID = os.environ.get("QnAKnowledgebaseId", "")
    QNA_ENDPOINT_KEY = os.environ.get("QnAEndpointKey", "")
    QNA_ENDPOINT_HOST = os.environ.get("QnAEndpointHostName", "")

    # Cosmos DB
    COSMOSDB_URI = os.environ.get("CosmobDBUri", '')
    COSMODB_KEY = os.environ.get("CosmosDBUri", '')
    COSMOSDB_DATABASE_NAME = os.environ.get("CosmosDBDatabaseNname", "")
    COSMOSDB_CONTAINER_NAME = os.environ.get("CosmosDBContainerName", "")

    # Search Bing
    BING_KEY = os.environ.get("BingKey", "")
    BING_SEARCH_URL = os.environ.get("BingSearchUrl", "")
    
    # Serverless Function
    SERVERLESS_FUNCTION_URI = os.environ.get("ServerlessFunctionUri", "")
    SERVERLESS_FUNCTION_KEY = os.environ.get("ServerlessFunctionkey", "")
