@startuml ComplianceCompass Deployment Diagram

' Impostazioni di stile per massima leggibilità
skinparam backgroundColor white
skinparam shadowing false
skinparam defaultFontName "Arial"
skinparam defaultFontSize 12
skinparam linetype ortho
skinparam nodesep 80
skinparam ranksep 100

' Stile dei componenti
skinparam node {
  BackgroundColor #f5f5f5
  BorderColor #2c3e50
  FontColor #2c3e50
}

skinparam database {
  BackgroundColor #ecf0f1
  BorderColor #3498db
}

skinparam component {
  BackgroundColor #f8f9fa
  BorderColor #7f8c8d
}

' Client
node "Client" as client {
  [Web Browser] as browser
}

' Ambiente Docker
rectangle "Docker Environment" {
  node "Frontend Container\n(compliance-compass-frontend)" as frontendContainer {
    [React Application] as reactApp
    
    note bottom of frontendContainer
      **Volumi**:
      - ./frontend:/app
      - /app/node_modules
      **Porta**: 3000
    end note
  }
  
  node "API Container\n(compliance-compass-api)" as apiContainer {
    [FastAPI Application] as fastApi
    
    note bottom of apiContainer
      **Volumi**:
      - ./src:/app/src
      - ./alembic:/app/alembic
      - ./alembic.ini:/app/alembic.ini
      - ./scripts:/app/scripts
      - ./docker:/app/docker
      **Porta**: 8000
    end note
  }
  
  node "Database Container\n(compliance-compass-db)" as dbContainer {
    database "PostgreSQL 14" as postgres {
      [compliance_compass DB] as db
    }
    
    note bottom of dbContainer
      **Ambiente**:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=compliance_compass
      **Porta**: 5432
    end note
  }
  
  ' Volume persistente
  storage "postgres_data" as pgVolume {
    [DB Data] as dbData
  }
}

' Connessioni principali
client --> frontendContainer : HTTP (3000)
frontendContainer --> apiContainer : HTTP/REST (8000)
apiContainer --> dbContainer : SQL (5432)
dbContainer --> pgVolume : persists data

' Dipendenze
frontendContainer ..> apiContainer : depends on
apiContainer ..> dbContainer : depends on

' Rete di comunicazione
cloud "compliance_compass_network\n(bridge)" as network {
}

' Collegamenti alla rete
frontendContainer -- network : connected to
apiContainer -- network : connected to
dbContainer -- network : connected to

legend right
  <b>Legenda</b>
  --- Comunicazione HTTP/SQL
  ... Dipendenza per l'avvio
  --- Connessione alla rete
end legend

@enduml