@startuml ComplianceCompass Database Model

' Stile generale
skinparam backgroundColor white
skinparam defaultFontName "Arial"
skinparam defaultFontSize 12
skinparam linetype ortho

' Stile entità
skinparam class {
  BackgroundColor #f5f5f5
  BorderColor #2c3e50
  ArrowColor #3498db
}

' Enum
enum "UserRole" as UserRole {
  ADMIN
  EDITOR
  VIEWER
}

enum "SeverityLevel" as SeverityLevel {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

enum "NotificationType" as NotificationType {
  SYSTEM
  INFO
  WARNING
  SUCCESS
  PRIVACY_PATTERN
  COMMENT
  NEWSLETTER
}

' Entità principali
entity "users" as users {
  *id : integer <<PK>>
  --
  email : varchar(255) <<UQ, IX>>
  username : varchar(50) <<UQ, IX>>
  hashed_password : varchar(255)
  full_name : varchar(100)
  role : UserRole
  is_active : boolean
  bio : text
  avatar_url : varchar(255)
  created_at : timestamp
  updated_at : timestamp
  last_login : timestamp
}

entity "privacy_patterns" as patterns {
  *id : integer <<PK>>
  --
  title : varchar(255) <<UQ, IX>>
  description : text
  context : text
  problem : text
  solution : text
  consequences : text
  strategy : varchar(100) <<IX>>
  mvc_component : varchar(50) <<IX>>
  view_count : integer
  created_at : timestamp
  updated_at : timestamp
  *created_by_id : integer <<FK>>
}

entity "implementation_examples" as examples {
  *id : integer <<PK>>
  --
  title : varchar(255)
  description : text
  code : text
  language : varchar(50)
  diagram_url : varchar(255)
  created_at : timestamp
  updated_at : timestamp
  *created_by_id : integer <<FK>>
  *pattern_id : integer <<FK>>
}

entity "gdpr_articles" as gdpr {
  *id : integer <<PK>>
  --
  number : varchar(20) <<UQ, IX>>
  title : varchar(255)
  content : text
  summary : text
  category : varchar(100) <<IX>>
  chapter : varchar(100) <<IX>>
  is_key_article : boolean <<IX>>
  created_at : timestamp
  updated_at : timestamp
}

entity "pbd_principles" as pbd {
  *id : integer <<PK>>
  --
  name : varchar(100) <<UQ, IX>>
  description : text
}

entity "iso_phases" as iso {
  *id : integer <<PK>>
  --
  name : varchar(100) <<UQ, IX>>
  standard : varchar(50)
  description : text
  order : integer
}

entity "vulnerabilities" as vuln {
  *id : integer <<PK>>
  --
  code : varchar(50) <<UQ, IX>>
  name : varchar(255)
  description : text
  severity : SeverityLevel
}

entity "notifications" as notifications {
  *id : integer <<PK>>
  --
  *user_id : integer <<FK>>
  message : text
  link : varchar(255)
  is_read : boolean
  type : NotificationType
  created_at : timestamp
  updated_at : timestamp
}

' Sistema Newsletter
entity "newsletter_subscribers" as subscribers {
  *id : uuid <<PK>>
  --
  email : varchar(255) <<UQ, IX>>
  first_name : varchar(100)
  last_name : varchar(100)
  is_active : boolean
  confirmation_token : varchar(255) <<UQ>>
  is_confirmed : boolean
  preferences : jsonb
  created_at : timestamp
  updated_at : timestamp
}

entity "newsletter_campaigns" as campaigns {
  *id : uuid <<PK>>
  --
  title : varchar(255)
  subject : varchar(255)
  content : text
  content_html : text
  status : varchar(50)
  scheduled_at : timestamp
  sent_at : timestamp
  target_segment : jsonb
  created_at : timestamp
  updated_at : timestamp
  *created_by_id : integer <<FK>>
}

entity "newsletter_deliveries" as deliveries {
  *id : uuid <<PK>>
  --
  *campaign_id : uuid <<FK>>
  *subscriber_id : uuid <<FK>>
  status : varchar(50)
  sent_at : timestamp
  delivered_at : timestamp
  opened_at : timestamp
  clicked_at : timestamp
  error : text
  created_at : timestamp
  updated_at : timestamp
}

' Tabelle di associazione per relazioni many-to-many
entity "pattern_gdpr_articles" as pattern_gdpr {
  *pattern_id : integer <<PK, FK>>
  *gdpr_article_id : integer <<PK, FK>>
}

entity "pattern_pbd_principles" as pattern_pbd {
  *pattern_id : integer <<PK, FK>>
  *pbd_principle_id : integer <<PK, FK>>
}

entity "pattern_iso_phases" as pattern_iso {
  *pattern_id : integer <<PK, FK>>
  *iso_phase_id : integer <<PK, FK>>
}

entity "pattern_vulnerabilities" as pattern_vuln {
  *pattern_id : integer <<PK, FK>>
  *vulnerability_id : integer <<PK, FK>>
}

' Relazioni one-to-many
users ||--o{ patterns : creates
users ||--o{ examples : creates
users ||--o{ notifications : receives
users ||--o{ campaigns : creates

patterns ||--o{ examples : has

' Relazioni many-to-many
patterns }o--o{ gdpr : references
pattern_gdpr }|--|| patterns
pattern_gdpr ||--|{ gdpr

patterns }o--o{ pbd : implements
pattern_pbd }|--|| patterns
pattern_pbd ||--|{ pbd

patterns }o--o{ iso : applies_to
pattern_iso }|--|| patterns
pattern_iso ||--|{ iso

patterns }o--o{ vuln : addresses
pattern_vuln }|--|| patterns
pattern_vuln ||--|{ vuln

' Relazioni newsletter
campaigns ||--o{ deliveries : results_in
subscribers ||--o{ deliveries : receives

@enduml