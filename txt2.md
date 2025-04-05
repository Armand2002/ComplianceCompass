# LVAA POSD System
Versione 1.0

## Realizzato da
Anselmi Armando 776919 Informatica e TPS  
a.anselmi4@studenti.uniba.it

Fuiano Luigi 754709 Informatica e TPS  
l.fuiano@studenti.uniba.it

Lorusso Vincenzo 764510 Informatica e TPS  
v.lorusso62@studenti.uniba.it 

![SERLAB Logo](serlab_logo.png)

# Indice

1. [PRODUCT BACKLOG](#product-backlog)
   1. [Introduzione](#introduzione)
   2. [Contesto di business](#contesto-di-business)
   3. [Stakeholder](#stakeholder)
   4. [Item funzionali](#item-funzionali)
      1. [IF-N1](#if-n1)
      2. [IF-N2](#if-n2)
      3. [IF-N3](#if-n3)
      4. [IF-N4](#if-n4)
      5. [IF-N5](#if-n5)
      6. [IF-N6](#if-n6)
      7. [IF-N7](#if-n7)
      8. [IF-N8](#if-n8)
      9. [IF-N9](#if-n9)
      10. [IF-N10](#if-n10)
      11. [IF-N11](#if-n11)
      12. [IF-N12](#if-n12)
      13. [IF-N13](#if-n13)
      14. [IF-N14](#if-n14)
      15. [IF-N15](#if-n15)
      16. [IF-N16](#if-n16)
      17. [IF-N17](#if-n17)
   5. [Item non funzionali](#item-non-funzionali)
      1. [Item Informativi](#item-informativi)
      2. [Item di interfaccia](#item-di-interfaccia)
      3. [Item Qualitativi](#item-qualitativi)
2. [SPRINT REPORT](#sprint-report)
   1. [Sprint Backlog](#sprint-backlog)
   2. [Product Requirement Specification](#product-requirement-specification)
      1. [Diagramma dei Casi d'uso](#diagramma-dei-casi-duso)
      2. [Specifiche dei Casi d'uso](#specifiche-dei-casi-duso)
   3. [System Architecture](#system-architecture)
      1. [Diagramma delle Componenti](#diagramma-delle-componenti)
      2. [Specifica delle componenti](#specifica-delle-componenti)
      3. [Specifica delle interfacce](#specifica-delle-interfacce)
      4. [Diagramma di Deployment](#diagramma-di-deployment)
   4. [Detailed Product Design](#detailed-product-design)
      1. [Diagramma delle Classi](#diagramma-delle-classi)
      2. [Specifiche delle Classi](#specifiche-delle-classi)
      3. [Diagrammi di Sequenza](#diagrammi-di-sequenza)
   5. [Data Modeling and Design](#data-modeling-and-design)
      1. [Modello logico del Database](#modello-logico-del-database)
      2. [Struttura fisica del Database](#struttura-fisica-del-database)
3. [GLOSSARIO](#glossario)
   1. [Acronimi](#acronimi)
   2. [Definizioni](#definizioni)

# PRODUCT BACKLOG

## Introduzione 

POSD System è un sistema software progettato per supportare i team di sviluppo nell'identificazione e integrazione di elementi di privacy e sicurezza nei sistemi software in tutte le fasi di sviluppo. La piattaforma implementa una Knowledge Base di pattern di privacy e conformità normativa.

## Contesto di business

POSD System si offre come una piattaforma web che supporta sviluppatori e organizzazioni nell'implementazione della Privacy by Design e nella conformità con il GDPR. Oltre a fungere da strumento per professionisti, serve anche come piattaforma educativa per utenti comuni interessati alla privacy e alla protezione dei dati.

## Stakeholder

- **Utenti sviluppatori**: Professionisti IT che necessitano di integrare requisiti di privacy e sicurezza nei loro progetti.
- **Utenti comuni**: Persone interessate a informarsi su tematiche di privacy e conformità.
- **Amministratori del sistema**: Responsabili della gestione, manutenzione ed evoluzione della piattaforma.
- **Enti Regolari**: Organizzazioni come l'Unione Europea che definiscono normative sulla privacy

## Item funzionali

### IF-N1

COME Utente  
DEVO POTER consultare l'elenco di Privacy Patterns  
Il Sistema fornisce un catalogo completo di Privacy Patterns.

### IF-N2

COME Utente  
DEVO POTER cercare specifici Privacy Patterns  
Il Sistema fornisce funzionalità di ricerca per trovare pattern specifici.

### IF-N3

COME Utente  
DEVO POTER effettuare ricerche avanzate all'interno della Knowledge Base  
PER TROVARE con precisione i pattern necessari  
Il Sistema fornisce ricerca con filtri, parole chiave e categorie.

### IF-N4

COME Utente  
DEVO POTER visualizzare gli articoli del GDPR  
PER COMPRENDERE meglio la conformità normativa  
Il Sistema fornisce accesso e riferimenti al regolamento GDPR.

### IF-N5

COME Utente  
DEVO POTER visualizzare descrizioni dettagliate  
PER COMPRENDERE a fondo i Privacy Pattern  
Il Sistema fornisce spiegazioni complete di ogni pattern.

### IF-N6

COME Utente  
DEVO POTER comprendere il contesto di applicazione  
PER VALUTARE l'implementazione dei pattern  
Il Sistema fornisce informazioni sul contesto d'uso di ogni pattern.

### IF-N7

COME Utente  
DEVO POTER conoscere i principi della PbD associati per pattern  
PER ALLINEARE l'implementazione con gli obiettivi di privacy  
Il Sistema classifica i pattern secondo strategie di privacy.

### IF-N8

COME Utente  
DEVO POTER conoscere l'architettura applicativa  
PER FACILITARE l'integrazione nel mio sistema  
Il Sistema indica il posizionamento MVC di ciascun pattern.

### IF-N9

COME Utente  
DEVO POTER associare i pattern alle fasi di design  
PER INTEGRARE privacy sin dalle prime fasi di sviluppo  
Il Sistema mappa i pattern alle fasi dello standard ISO 9241-210.

### IF-N10

COME Utente  
DEVO POTER verificare la conformità al GDPR  
PER GARANTIRE l'adeguamento normativo  
Il Sistema indica gli articoli GDPR soddisfatti da ciascun pattern.

### IF-N11

COME Utente  
DEVO POTER conoscere i principi Privacy by Design implementati  
PER SEGUIRE le best practice di settore  
Il Sistema mostra i principi PbD associati a ciascun pattern.

### IF-N12

COME Utente  
DEVO POTER valutare i rischi e le vulnerabilità  
PER IMPLEMENTARE misure preventive adeguate  
Il Sistema fornisce informazioni su vulnerabilità secondo classificazione CWE.

### IF-N13

COME Utente  
DEVO POTER conoscere le best practice di sicurezza  
PER MIGLIORARE la protezione dei dati  
Il Sistema fornisce raccomandazioni OWASP per ogni pattern.

### IF-N14

COME Utente  
DEVO POTER visualizzare esempi di implementazione  
PER FACILITATORE l'adozione dei pattern  
Il Sistema fornisce casi d'uso ed esempi pratici.

### IF-N15

COME Utente  
DEVO POTER ricevere aggiornamenti  
PER RIMANERE informato sulle novità  
Il Sistema fornisce una sezione dedicata agli aggiornamenti.

### IF-N16

COME Utente  
DEVO POTER ricevere notifiche  
PER RESTARE aggiornato senza dover visitare il sito  
Il Sistema fornisce un servizio di newsletter via email.

### IF-N17

COME Utente  
DEVO POTER interagire con un assistente virtuale  
PER RICEVERE supporto nella navigazione  
Il Sistema fornisce una chatbot per assistenza.

## Item non funzionali

### Item Informativi

Contiene l'elenco e la specifica di tutti gli eventuali requisiti non funzionali di tipo informativo.

#### IIN-1

Ogni Privacy Pattern contiene le seguenti informazioni strutturate:
- Titolo e Strategia;
- Descrizione e Collocazione MVC;
- Riferimenti GDPR e ISO 9241-210;
- Principio Privacy by Design;
- Contesto di Applicazione;
- Vulnerabilità (CWE) e Contromisure (OWSAP);
- Esempi di implementazione.

### Item di interfaccia

Contiene gli eventuali requisiti di interfaccia espressi tramite disegni (Sketch) e mockup.

#### IUI-1 Pagina Principale

![Pagina Principale](ui1_pagina_principale.png)

#### IUI-2 Pattern Cercato

![Pattern Cercato](ui2_pattern_cercato.png)

#### IUI-3 Ricerca Avanzata

![Ricerca Avanzata](ui3_ricerca_avanzata.png)

#### IUI-4 Ricevi Notifiche

![Ricevi Notifiche](ui4_ricevi_notifiche.png)

### Item Qualitativi

Contiene l'elenco e la specifica di tutti gli eventuali requisiti non funzionali di tipo qualitativo.

# SPRINT REPORT

## Sprint Backlog

| Codice Item | Numero Sprint | Note |
|-------------|---------------|------|
| IF-N1 | Sprint 1 | Riguarda l'implementazione elenco Privacy Patterns |
| IF-N2 | Sprint 1 | Riguarda la funzionalità di ricerca base |
| IF-N3 | Sprint 1 | Riguarda la ricerca avanzata con i filtri |
| IF-N4 | Sprint 1 | Riguarda il collegamento al GDPR |
| IF-N5 | Sprint 2 | Riguarda la visualizzazione delle descrizioni dei pattern |
| IF-N6 | Sprint 2 | Riguarda la visualizzazione contesto di applicazione |
| IF-N7 | Sprint 2 | Riguarda la categorizzazione per strategia |
| IF-N8 | Sprint 2 | Riguarda informazioni su architettura MVC |
| IF-N9 | Sprint 2 | Riguarda la mappatura a ISO 9241-210 |
| IF-N10 | Sprint 2 | Riguarda i collegamenti agli articoli GDPR |
| IF-N11 | Sprint 2 | Riguarda i principi Privacy by Design |
| IF-N12 | Sprint 2 | Riguarda le informazioni su vulnerabilità |
| IF-N13 | Sprint 2 | Riguarda le raccomandazioni sicurezza OWASP |
| IF-N14 | Sprint 3 | Riguarda inserimento esempi di implementazione |
| IF-N15 | Sprint 3 | Riguarda implementazione sezione aggiornamenti |
| IF-N16 | Sprint 3 | Riguarda implementazione di newsletter |
| IF-N17 | Sprint 3 | Riguarda implementazione chatbot |

## Product Requirement Specification 

### Diagramma dei Casi d'uso

![Diagramma dei Casi d'uso](use_case_diagram.png)

Nel diagramma sono esplicitati graficamente i casi d'uso utilizzabili da un singolo attore. L'attore Utente non viene fatta nessuna distinzione, l'Utente è anche un visitatore del nostro Sistema. Si mostra in modo specifico ogni singolo caso d'uso per l'attore:

I. Visualizza GDPR: permette all'utente di inviarlo al regolamento ufficiale GDPR.
II. Visualizza Privacy Patterns: permette all'utente di visualizzare l'elenco di tutti i privacy patterns.
III. Ricerca: è la funzione che permette all'utente di ricercare uno specifico pattern.
IV. Ricerca Avanzata: è la funzione che permette all'utente di cercare in modo preciso un privacy pattern.
V. ChatBot: è un software che permette all'utente di ricevere assistenza.
VI. Newsletter: è la funzione che permette all'utente di ricevere notifiche in caso di cambiamenti relativi al Sistema.
VII. Visualizza Aggiornamenti: è la funzione che permette all'utente di verificare gli aggiornamenti relativi al Sistema.

### Specifiche dei Casi d'uso

#### Regolamento GDPR

| ID | N2 |
|----|----|
| Descrizione | Vista del sito contenente il regolamento GDPR |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Utente seleziona "GDPR"<br>2. Sistema apre una nuova scheda contenente il GDPR |
| Postcondizioni | Sistema apre una nuova scheda con il sito ufficiale del GDPR |
| Sequenza alternativa degli eventi | - |

#### Elenco Privacy Patterns

| ID | N1 |
|----|----|
| Descrizione | Vista elenco Privacy Patterns |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Utente seleziona "Elenco Privacy Patterns"<br>2. Sistema mostra l'elenco dei Privacy Patterns |
| Postcondizioni | Sistema mostra elenco dei Privacy Patterns |
| Sequenza alternativa degli eventi | - |

#### Iscrizione Newsletter

| ID | N4 |
|----|----|
| Descrizione | Iscrizione Newsletter dell'utente |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Utente seleziona "Ricevi Notifiche"<br>2. Utente inserisce e-mail nel form |
| Postcondizioni | Utente visualizza schermata iscrizione riuscita |
| Sequenza alternativa degli eventi | -CodiceSbagliato -EmailIscrittaPrima<br>-Cancella iscrizione |

##### Iscrizione Newsletter sbagliata

| ID | N4.1 |
|----|----|
| Descrizione | Iscrizione Newsletter dell'utente con codice sbagliato |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Utente seleziona "Ricevi Notifiche"<br>2. Utente inserisce e-mail nel form<br>3. Sistema verifica la correttezza dell'email mandando un codice<br>4. Utente inserisce codice nel form<br>5. Sistema avvisa l'utente del codice sbagliato |
| Postcondizioni | Utente visualizza la schermata newsletter con rinvio codice |
| Sequenza alternativa degli eventi | - |

##### Email Newsletter già in uso

| ID | N4.2 |
|----|----|
| Descrizione | Iscrizione Newsletter dell'utente con email già in uso |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Utente seleziona "Ricevi Notifiche"<br>2. Utente inserisce e-mail nel form<br>3. Sistema verifica la correttezza dell'email mandando un codice<br>4. Utente inserisce codice nel form<br>5. Sistema avvisa dell'email già in uso |
| Postcondizioni | Utente visualizza schermata Newsletter ma con un messaggio di avviso dal Sistema di e-mail in uso |
| Sequenza alternativa degli eventi | - |

##### Cancella iscrizione Newsletter

| ID | N4.3 |
|----|----|
| Descrizione | Utente cancella iscrizione alla newsletter |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Utente seleziona "Ricevi Notifiche"<br>2. Utente inserisce e-mail nel form<br>3. Sistema verifica la correttezza dell'email mandando un codice<br>4. Utente inserisce codice nel form<br>5. Sistema avvisa dell'email già in uso |
| Postcondizioni | Utente visualizza messaggio dal Sistema di richiesta di cancellare iscrizione |
| Sequenza alternativa degli eventi | - |

#### Ricerca di un Privacy Pattern

| ID | N5 |
|----|----|
| Descrizione | Utente ricerca un determinato Privacy Pattern |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Utente scrive nella barra di ricerca<br>2. Sistema mostra il risultato cercato |
| Postcondizioni | Utente visualizza il risultato |
| Sequenza alternativa degli eventi | -RicercaNonAdatta |

##### Ricerca non andata a buon fine

| ID | N5.1 |
|----|----|
| Descrizione | Utente usa la barra di ricerca in modo errato |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Utente scrive nella barra di ricerca qualcosa di non inerente<br>2. Sistema avvisa dell'errore di ricerca |
| Postcondizioni | Sistema mostra una pagina di errore relativo alla ricerca |
| Sequenza alternativa degli eventi | - |

#### Aggiornamenti del Sistema

| ID | N3 |
|----|----|
| Descrizione | Utente visualizza gli ultimi aggiornamenti |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Utente visualizza schermata aggiornamenti nella home |
| Postcondizioni | Sistema mostra elenco aggiornamenti |
| Sequenza alternativa degli eventi | - |

#### Ricerca Avanzata

| ID | N6 |
|----|----|
| Descrizione | Utente utilizza filtro per una ricerca precisa |
| Precondizioni | - |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Sistema mostra lista dei tags |
| Postcondizioni | Sistema mostra elenco tags a cui l'utente può usufruire per trovare il pattern inerente |
| Sequenza alternativa degli eventi | - |

#### Privacy by Design del Privacy Pattern cercato

| ID | N7 |
|----|----|
| Descrizione | Utente visualizza Privacy by Design per pattern |
| Precondizioni | L'Utente ha cercato un privacy pattern |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Sistema mostra il principio della PbD del pattern cercato |
| Postcondizioni | Utente visualizza il principio della PbD del pattern |
| Sequenza alternativa degli eventi | - |

#### Componente MVC del Privacy Pattern cercato

| ID | N9 |
|----|----|
| Descrizione | Utente visualizza quale componente del MVC per pattern |
| Precondizioni | L'Utente ha cercato un privacy pattern |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Sistema mostra quale componente del MVC appartiene il pattern cercato |
| Postcondizioni | Utente visualizza la componente MVC del pattern |
| Sequenza alternativa degli eventi | - |

#### GPDR e ISO 9241-210 del Privacy Pattern cercato

| ID | N10 |
|----|----|
| Descrizione | Utente visualizza articoli GDPR e fasi dell'ISO 9241-210 per pattern |
| Precondizioni | L'Utente ha cercato un privacy pattern |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Sistema mostra articoli GDPR e fasi dell'ISO 9241-210 per il pattern cercato |
| Postcondizioni | Utente visualizza articoli GDPR e fasi dell'ISO 9241-210 del pattern |
| Sequenza alternativa degli eventi | - |

#### OWASP e CWE del Privacy Pattern cercato

| ID | N11 |
|----|----|
| Descrizione | Utente visualizza debolezze e vulnerabilità per il pattern cercato |
| Precondizioni | L'Utente ha cercato un privacy pattern |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Sistema mostra vulnerabilità dichiarate da OWASP e CWE per il pattern cercato |
| Postcondizioni | Utente visualizza vulnerabilità dichiarate da OWASP e CWE del pattern |
| Sequenza alternativa degli eventi | - |

#### Esempio del Privacy Pattern cercato

| ID | N12 |
|----|----|
| Descrizione | Utente visualizza esempio per il pattern cercato |
| Precondizioni | L'Utente ha cercato un privacy pattern |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Sistema mostra esempio per il pattern cercato |
| Postcondizioni | Utente visualizza esempi del pattern |
| Sequenza alternativa degli eventi | - |

#### Descrizione del Privacy Pattern cercato

| ID | N8 |
|----|----|
| Descrizione | Utente visualizza descrizione per il pattern cercato |
| Precondizioni | L'Utente ha cercato un privacy pattern |
| Attori Primari | Utente |
| Attori Secondari | - |
| Sequenza principale degli eventi | 1. Sistema mostra descrizione per il pattern cercato |
| Postcondizioni | Utente visualizza descrizione del pattern |
| Sequenza alternativa degli eventi | - |

## System Architecture

### Diagramma delle Componenti

![Diagramma delle Componenti](component_diagram.png)

### Specifica delle componenti

L'architettura delle componenti segue il pattern MVC (Model-View-Controller):

1. VIEW
   - **Utente**: rappresenta l'area di riferimento ed interazione riservata al visitatore, il quale non dovrà effettuare nessuna registrazione o login per sbloccare altre funzioni. Il visitatore potrà solo iscriversi alla newsletter per ricevere notifiche tramite e-mail del sistema. L'utente avrà la possibilità di visualizzare elenco dei Privacy Patterns, il GDPR, aggiornamenti del sistema, il ChatBot e visualizzare la ricerca.

2. CONTROLLER 
   - **PatternController**: si occupa della gestione dei pattern da mostrare
   - **SearchController**: si occupa della gestione di ricerca
   - **NewsletterController**: si occupa della gestione di iscrizioni da parte dell'utente per aggiornamenti
   - **ChatbotController**: si occupa della gestione di un bot che risponda a domande inerenti da parte dell'utente.

3. MODEL 
   - **PatternModel**: costituisce la rappresentazione nel sistema degli elementi che ogni pattern ne costituito
   - **UserModel**: costituisce la rappresentazione nel sistema la lista degli utenti registrati
   - **NotificationModel**: costituisce la rappresentazione nel sistema della lista degli aggiornamenti.

### Specifica delle interfacce

I. **Iscrizione**: è l'interfaccia esposta dalla view che permette all'utente di iscriversi alla newsletter del sistema;
II. **Ricerca**: è l'interfaccia esposta dalla view che permette all'utente di ricercare argomenti relativi ai pattern;
III. **Richiesta**: è l'interfaccia esposta dal controller che permette di modificare i dati della newsletter; 
IV. **Aggiornamento**: è l'interfaccia esposta dal model per la visualizzazione dei dati;
V. **Interrogazione**: è l'interfaccia esposta sul DBMS e permette al model di eseguire operazioni CRUD sulla memoria persistente.

### Diagramma di Deployment

![Diagramma di Deployment](deployment_diagram.png)

Il diagramma di deployment descrive graficamente come sono organizzate tra loro le periferiche e gli ambienti esecutivi. Nello specifico, è presente la comunicazione tra client e server che comunicano. Il client è costituito da un qualsiasi Browser Web che permette agli utilizzatori di accedere alle funzionalità della Web Application, eseguita su un server che ne garantisce il funzionamento.

## Detailed Product Design

### Diagramma delle Classi

![Diagramma delle Classi](class_diagram.png)

### Specifiche delle Classi

Sono definite le seguenti classi:

Si è creata un'unica classe per l'utente che ha controllo su tutte le azioni messe disponibile dal Sistema. La vista, rappresentata dal modulo Utente, si occupa di mostrare le interfacce di elenco privacy patterns, ricerca, ricerca avanzata, aggiornamenti, newsletter e di far visualizzare il sito GDPR. La maggior parte utilizzano funzioni relative alla gestione dei dati PKB rappresentati e divisi nei Patterns dalle loro istanze. Il modulo Aggiornamenti_Controller utilizza solo funzioni di stampa di Aggiornamenti, il quale costituisce la rappresentazione nel sistema le informazioni delle nuove versioni. Inoltre, il Newsletter_Controller gestisce le funzionalità di iscrizione e salvataggio delle e-mails.

### Diagrammi di Sequenza

#### Visita sito GDPR

![Visita sito GDPR](sequence_gdpr.png)

#### Iscrizione alla newsletter 

![Iscrizione alla newsletter](sequence_newsletter.png)

#### Ricerca 

![Ricerca](sequence_search.png)

#### Ricerca Avanzata

![Ricerca Avanzata](sequence_advanced_search.png)

#### Vista Aggiornamenti Sistema

![Vista Aggiornamenti Sistema](sequence_updates.png)

#### Visione Lista Privacy Patterns

![Visione Lista Privacy Patterns](sequence_patterns_list.png)

#### Visione descrizione pattern

![Visione descrizione pattern](sequence_pattern_description.png)

#### Visione esempi pattern 

![Visione esempi pattern](sequence_pattern_examples.png)

#### Visione debolezze e vulnerabilità pattern

![Visione debolezze e vulnerabilità pattern](sequence_pattern_vulnerabilities.png)

#### Visione collocazione MVC pattern

![Visione collocazione MVC pattern](sequence_pattern_mvc.png)

#### Visione Privacy by Design pattern

![Visione Privacy by Design pattern](sequence_pattern_pbd.png)

#### Visione Articolo GDPR e Fase ISO pattern

![Visione Articolo GDPR e Fase ISO pattern](sequence_pattern_gdpr_iso.png)

#### Visione elenco privacy patterns

![Visione elenco privacy patterns](sequence_patterns_list_view.png)

## Data modeling and design

Il modello del database è stato gestito tramite l'utilizzo del cms Strapi, il quale si connette ad un DBMS. Tra i vari disponibili, si è preferito utilizzare SQLite.

### Modello logico del Database

**Pattern**
| pattern_id (PK) | title | description | context | strategy |
|-----------------|-------|-------------|---------|----------|
| mvc_component | created_at | updated_at | | |

**PatternDetail**
| detail_id (PK) | pattern_id (FK) | gdpr_reference | pbd_principle | iso_phase |
|----------------|-----------------|----------------|---------------|-----------|
| vulnerability | owasp_category | example | | |

**User**
| user_id (PK) | email | subscribed | created_at | |
|--------------|-------|------------|------------|---|

**Newsletter**
| newsletter_id (PK) | title | content | sent_at | |
|-------------------|-------|---------|---------|---|

### Struttura fisica del Database

![Struttura fisica del Database](db_structure.png)

# GLOSSARIO

## Acronimi

GDPR: General Data Protection Regulation  
PbD: Privacy by Design  
PKB: Privacy Knowledge Base  
OWASP: Open Web Application Security Project  
CWE: Common Weakness Enumeration  
MVC: Model-View-Controller  
API: Application Programming Interface  
CRUD: Create Read Update Delete  
DBMS: Database Management System  

## Definizioni

**Soggetti**: Persone, GDPR, team di sviluppo.  
**Visitatore**: Utente.  
**Newsletter**: è un aggiornamento informativo periodico che il Sistema invia agli utenti iscritti aggiornamenti sulle proprie attività e versioni.  
**Privacy Pattern**: Soluzione riutilizzabile a problemi ricorrenti di privacy  
**Privacy by Design**: Approccio che integra la privacy in tutto il ciclo di sviluppo  
**Knowledge Base**: Repository centralizzato di informazioni strutturate  
**Chatbot**: Assistente virtuale basato su tecnologie di elaborazione del linguaggio naturale