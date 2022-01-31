from azure.cosmos import CosmosClient
from config import DefaultConfig
from data_models import UserProfile
import json

# Dati di configurazione per l'utilizzo di Cosmos-DB
CONFIG = DefaultConfig()
uri = CONFIG.COSMOSDB_URI
key = CONFIG.COSMODB_KEY
database_name = CONFIG.COSMOSDB_DATABASE_NAME
container_name = CONFIG.COSMOSDB_CONTAINER_NAME

class DatabaseManager:

    @staticmethod
    def insertUser(id, nome_utente):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        dizionario = {}
        dizionario["id"] = id
        dizionario["nome_utente"] = nome_utente
        dizionario["cripto_tracciate"] = ''
        container.upsert_item(dizionario)

    @staticmethod
    def getUser(id):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        query1 = 'SELECT * FROM ContainerProva u WHERE u.id = \'' + str(id) + '\''
        lista_utenti = container.query_items(query = query1, enable_cross_partition_query=True)
        for item in iter(lista_utenti):
            user_profile = UserProfile(
                id=item["id"],
                nome_utente=item["nome_utente"],
                cripto_tracciate=item["cripto_tracciate"])
            return user_profile
        return None

    # Serve solo per debug
    @staticmethod
    def getUsers():
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        query1 = 'SELECT * FROM ContainerProva c'
        lista_utenti = container.query_items(query = query1, enable_cross_partition_query=True)
        users_profile = []
        i=0
        for item in iter(lista_utenti):
            if (i!=0):
                user = UserProfile(item["id"],
                                    item["nome_utente"],
                                    item["cripto_tracciate"])
                users_profile.append(user)
            i=1

        return users_profile

    @staticmethod
    def user_is_registered(id: str):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        query1 = 'SELECT * FROM ContainerProva c'
        lista_utenti = container.query_items(query=query1, enable_cross_partition_query=True)
        for item in iter(lista_utenti):
            user = UserProfile(id=item["id"],
                               nome_utente=item["nome_utente"],
                               cripto_tracciate=item["cripto_tracciate"])
            if (id == user.getId()):
                return user

        return False

    @staticmethod
    def aggiungi_cripto_utente(id, symbol_cripto_tracciata, valore_da_tracciare, maggiore: bool):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        query1 = 'SELECT * FROM ContainerProva u WHERE u.id = \'' + str(id) + '\''
        lista_utenti = container.query_items(query=query1, enable_cross_partition_query=True)
        for item in lista_utenti:
            nuovo_item = item.copy()
            if (maggiore):
                maggiore_minore = ">"
            else:
                maggiore_minore = "<"

            nuovo_item["cripto_tracciate"] = item["cripto_tracciate"] + str(symbol_cripto_tracciata) + ':' + str(
                valore_da_tracciare) + ':' + maggiore_minore + ', '
            container.replace_item(item, nuovo_item, populate_query_metrics=None, pre_trigger_include=None,
                                   post_trigger_include=None)

    @staticmethod
    def elimina_cripto_utente(id, symbol_cripto_tracciata):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        query1 = 'SELECT * FROM ContainerProva u WHERE u.id = \'' + str(id) + '\''
        lista_utenti = container.query_items(query=query1, enable_cross_partition_query=True)
        for item in lista_utenti:
            nuovo_item = item.copy()
            lista_cripto_tracciate = nuovo_item["cripto_tracciate"].split(', ')
            indice_elemento_da_rimuovere = None
            for i in range(len(lista_cripto_tracciate)):
                if (lista_cripto_tracciate[i].startswith(symbol_cripto_tracciata)):
                    indice_elemento_da_rimuovere = i
                    break
            if (indice_elemento_da_rimuovere is None):
                # print(str(nome_cripto_tracciata) + ' non presente')
                return
            lista_cripto_tracciate.pop(indice_elemento_da_rimuovere)
            nuova_stringa_cripto_tracciate = ''
            for cripto_tracciata in lista_cripto_tracciate:
                if (cripto_tracciata != ''):
                    nuova_stringa_cripto_tracciate = nuova_stringa_cripto_tracciate + cripto_tracciata + ', '
            nuovo_item["cripto_tracciate"] = nuova_stringa_cripto_tracciate
            container.replace_item(item, nuovo_item, populate_query_metrics=None, pre_trigger_include=None,
                                   post_trigger_include=None)

    @staticmethod
    def get_lista_cripto_tracciate(id_utente):
        client = CosmosClient(uri, credential=key, consistency_level='Session')
        database = client.get_database_client(database_name)
        container = database.get_container_client(container_name)

        query1 = 'SELECT * FROM ContainerProva u WHERE u.id = \'' + str(id_utente) + '\''
        lista_utenti = container.query_items(query = query1, enable_cross_partition_query=True)
        for item in lista_utenti:
            le = len(item["cripto_tracciate"])
            if(len == 0):
                return ''
            else:
                return item["cripto_tracciate"][0:le-2]

if __name__ == "__main__":
    users_profile = DatabaseManager.getUsers()
    for user in users_profile:
        print(user)
