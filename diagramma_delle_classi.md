@startuml ComplianceCompass Architecture

skinparam componentStyle rectangle
skinparam backgroundColor transparent
skinparam monochrome false
skinparam componentBackgroundColor #f5f5f5
skinparam componentBorderColor #2c3e50
skinparam packageBackgroundColor #ecf0f1
skinparam packageBorderColor #7f8c8d
skinparam arrowColor #34495e
skinparam stereotypeFontSize 11
skinparam stereotypeFontColor #2980b9
skinparam noteBorderColor #3498db
skinparam noteFontColor #2c3e50

package "Frontend (React)" {
  [React UI Components] as UI <<presentation>>
  [React Router v6] as Router <<routing>>
  [Context API / Redux] as State <<state management>>
  [Axios API Client] as APIClient <<data access>>
  [Formik + Yup] as FormValidation <<validation>>
  
  note right of UI
    Componenti Material UI
    con design system personalizzato
  end note
}

package "Backend (FastAPI)" {
  package "API Layer" {
    [FastAPI Routes] as Routes <<endpoints>>
    [Pydantic Schemas] as Schemas <<validation>>
    [JWT Authentication] as AuthDeps <<security>>
    [Request/Response Middleware] as APIMiddleware <<interceptors>>
    
    note right of Routes
      REST API con endpoints
      versionati e documentazione
      OpenAPI automatica
    end note
  }
  
  package "Application Layer" {
    [Controllers] as Controllers <<business logic>>
    [Services] as Services <<domain services>>
    [DTOs] as DTOs <<data transfer>>
  }
  
  package "Domain Layer" {
    [Domain Models] as Models <<domain entities>>
    [Domain Events] as Events <<domain events>>
    [Value Objects] as ValueObjects <<domain values>>
    
    note right of Models
      Entità domain-driven
      con logica di business
      incapsulata
    end note
  }
  
  package "Infrastructure Layer" {
    [SQLAlchemy Repositories] as Repos <<data access>>
    [SQLAlchemy ORM] as ORM <<orm>>
    [External Integrations] as ExtServices <<integration>>
    [JWT + Password Hashing] as Security <<authentication>>
    [Python Logging] as Logging <<cross-cutting>>
    [Environment Config] as Config <<configuration>>
    
    note right of Repos
      Pattern Repository implementato
      con SQLAlchemy per isolamento
      dalla persistenza
    end note
  }
}

package "External Systems" {
  database "PostgreSQL" as PostgreSQL
  [SMTP Provider] as Email
  [S3-compatible Storage] as Storage
  
  note right of PostgreSQL
    Database relazionale
    con schema ottimizzato
    per pattern e relazioni
  end note
}

' Frontend internal connections
UI --> Router : routes through
UI --> State : reads/updates
UI --> FormValidation : validates inputs
State --> APIClient : triggers requests
APIClient -[#3498db,thickness=2]-> Routes : HTTP requests

' Backend connections - API Layer
Routes -[#3498db]-> Schemas : validates with
Routes -[#3498db]-> AuthDeps : secures with
Routes -[#3498db,thickness=2]-> Controllers : delegates to
APIMiddleware -[#e74c3c,dashed]-^ Routes : intercepts

' Backend connections - Application Layer
Controllers -[#3498db,thickness=2]-> Services : uses
Controllers -[#3498db]-> DTOs : transforms to/from
Services -[#3498db,thickness=2]-> Repos : persists via
Services -[#27ae60]-> ExtServices : integrates with
Services -[#e74c3c,dashed]-> Events : publishes

' Backend connections - Domain Layer
Models <-[#3498db]- Repos : mapped to/from
Models ..[#e74c3c,dashed]> Events : generates
Models ..[#3498db]> ValueObjects : composed of

' Infrastructure connections
Repos -[#3498db,thickness=2]-> ORM : uses
ORM -[#3498db,thickness=2]-> PostgreSQL : connects to
ExtServices -[#27ae60]-> Email : sends via
ExtServices -[#27ae60]-> Storage : stores in
Security -[#e74c3c,thickness=2,dashed]-> AuthDeps : provides
Logging -[#e74c3c,dashed]-^ Controllers : monitors
Logging -[#e74c3c,dashed]-^ Services : monitors
Config -[#e74c3c,dashed]-^ Services : configures

legend right
  **Tipi di connessioni**
  --[#3498db]-- Flusso dati sincrono
  --[#27ae60]-- Integrazione esterna 
  --[#e74c3c,dashed]-- Operazione asincrona/evento
  =[thickness=2]= Chiamata critica per performance
endlegend

@enduml