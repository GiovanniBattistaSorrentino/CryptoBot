CryptoBot
===========
**Autori**:
- Marrazzo Vincenzo
- Sorrentino Giovanni Battista

**CryptoBot** è un bot per Telegram in grado di fornire supporto agli utenti che fanno parte del mondo delle criptovalute con esso sarà più facile ricevere informazioni e amministrare le proprie cripto.

Le funzionalità offerte dal bot sono:

-   possibilità di **tracciare** una o più criptovalute inviando un messaggio all'utente quando queste superano o raggiungono un valore più basso di un valore fissato in input;
-   ricevere le ultime **notizie riguardo** il mondo cripto (ultime 3 notizie);
-   ricevere una lista delle 10 cripto che hanno avuto un **maggiore incremento** di valore nelle ultime 24 ore;
-   servizio Question and Answer per rispondere a tutte le **domande** relative al mondo cripto;
-   restituire le criptovalute che hanno un **prezzo compreso** in un range di valori inserito dell'utente.

	
<p align="center"><img src="./images/architettura.jpg"/></p>

Il bot è stato sviluppato in Python ed è stato pubblicato ed utilizza come canale Telegram ed utilizza i seguenti servizi:

-   **AppService**: Per effettuare hosting dell'applicazione su cloud.
-   **BotService**: Per sviluppare, testare e pubblicare il bot in Azure.
-   **Cosmos DB**: Per conservare i dati persistenti relativi agli utenti
-   **Bing Search**: Per ricercare i le notizie riguardanti il mondo cripto.
-   **QnA Maker**: Per la gestione delle domande relative al mondo cripto
-   **FunctionApp con funzione trigger time**: Per controllare se le cripto tracciate dagli utenti hanno raggiunto un valore per cui gli utenti devono ricevere un alert 

Prerequisiti
------------

-   Una sottoscrizione ad Azure
-   Python 3.8
-   Azure CLI
-   Bot Framework Emulator
-   Ngrok
-   Visual Studio Code con le estensioni Azure Account e Azure functions

Creazone delle risorse
-------------
### Web App

1.  Aprire il prompt dei comandi per accedere al portale di Azure con il comando
```sh
az login
```

2.  Creare la registrazione dell’applicazione con il comando
```sh
az ad app create --display-name "CryptoBot_bot" –password "AtLeastSixteenCharacters\_0" --available-to-other-tenants
```
È necessario registrare i valori **appID** e **secret** dopo l’esecuzione del comando precedente e inserirli nel seguente comando.
```sh
az deployment sub create --template-file "deploymentTemplates\template-with-new-rg.json" --location westeurope --parameters appId="appId" appSecret="appSecret" botId="CryptoBot_bot" botSku=F0 newAppServicePlanName="NewAppServicePlanCryBot" newWebAppName="CryBotWebApp" groupName="GroupCryBot" groupLocation="West Europe" newAppServicePlanLocation="West Europe" --name "CryBot"
```

### Cosmos DB
Per creare la risorsa di cosmos recarsi nel portale di Azure e successivamente:

1. Creare una nuova risorsa utilizzando la barra di ricerca e cercare 'Cosmos DB'.
2. Specifare nel campo resource group "GroupCryBot"
3. Creare una nuova risorsa utilizzando la barra di ricerca e cercare 'Azure Cosmos DB'.
4. Specificare "serverless" per la voce "Capacity mode".
5. Settare "Core(SQL)" per la voce "API".
6. Confermare la creazione della risorsa.

### App per le funzioni
Per creare la risorsa relativa alla function app recarsi nel portale di Azure e successivamente:
    
1. Creare una nuova risorsa utilizzando la barra di ricerca e cercare 'app per le funzioni'.
2. Specifare nel campo resource group "GroupCryBot"
3. Specificare "Docker Container" per la voce "Publish".
4. Specificare "Linux" per la voce "operating system".
5. Specificare "App service plan" per la voce "plan type".

### QnA Maker
Per creare la risorsa relativa al QnA Maker seguire la seguente guida:
    https://docs.microsoft.com/it-it/azure/cognitive-services/qnamaker/quickstarts/create-publish-knowledge-base
    
### Bing search v7
1. Creare una nuova risorsa utilizzando la barra di ricerca e cercare 'Bing search v7'.
2. Specifare nel campo resource group "GroupCryBot"
3. Specificare "Standard S1" per la voce "Pricing Tier".

Deploy della funzione serverless
-------------
Per effettuare il deploy della funzione serverless è necessario avere installato Visual studio code, con le estensioni Azure Account e Azure functions. Tramite l'estensione Azure Account è possibile effettuare l'accesso con il proprio account di azure, una volta fatto ciò è necessaio:

1. andare in Azure functions e creare un nuovo progetto
2. selezionare come python come linguaggio e la relativa versione
3. seleziona "trigger time" come template
4. immettere con "0 0 * * * *" nel campo relativo alla espressione cron
5. inserire il codice della funzione serverless(spiegare qua dove sta) nel file init.py
6. andare in "deploy to function App"

Deploy del bot su Azure
-------------
Scaricare la cartella bot dal repository Github. Una volta scaricata creare un zip con i file presenti nella cartella ed eseguire il seguente comando nel CLI di Azure:
```sh
az webapp deployment source config-zip --resource-group "GroupCryBot" --name "CryBotWebApp" --src "bot.zip"
```
**Integrazione con telegram**
Per l'integrazione con telegram eseguire i seguenti passi:
1. andare nel botfather(accessibile tramite ricerca da telegram) ed eseguire il comando /newbot
2. inserire nome e username del bot e prendere il toker
3. andare nel portale azure relativo alla risorsa azure bot e andare in channels
4. selezionare telegram e inseire il token

Deploy del bot in locale
-------------

Il bot può essere testato in locale utilizzando Bot Framework Emulator e ngrok.

#### Testare il bot utilizzando Bot Framework Emulator
1. Avviare il debug su VS Code
2. Avviare Bot Framework Emulator e selezionare 'Open Bot'.
3. Inserire i campi richiesti:
    * Bot URL: `http://localhost:3978/api/messages`
    * Microsoft App ID: presente nel file config.py
    * Microsoft App password: presente nel file config.py

#### Testare il bot su Telegram usando ngrok
Creare un nuovo bot per Telegram e nella sezione Canali del servizio bot configurare il bot inserendo il token.
1. avviare ngrok
```sh
$ ./ngrok http -host-header=rewrite 3978
```
2. recurerare l'endpoint fornito da ngrok ed inserirlo come endpoint di messaggistica sul servizio azure bot presente sul portale Azure.
3. a questo punto è possibile testare il bot utilizzando Telegram o la web chat di Azure.








