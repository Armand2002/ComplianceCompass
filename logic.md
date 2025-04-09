@startuml ComplianceCompass Logical Data Model

' Impostazioni di base
skinparam backgroundColor white
skinparam linetype ortho
skinparam defaultFontName "Arial"
skinparam defaultFontSize 12

' Entità principali con attributi essenziali
entity "User" {
  UserID
  --
  Email
  Username
  Role
}

entity "PrivacyPattern" {
  PatternID
  --
  Title
  Strategy
  MVC_Component
}

entity "ImplementationExample" {
  ExampleID
  --
  Title
  Language
}

entity "GDPRArticle" {
  ArticleID
  --
  Number
  Title
}

entity "PbDPrinciple" {
  PrincipleID
  --
  Name
}

entity "ISOPhase" {
  PhaseID
  --
  Name
  Standard
}

entity "Vulnerability" {
  VulnerabilityID
  --
  Name
  Severity
}

entity "Notification" {
  NotificationID
  --
  Type
  Message
}

entity "NewsletterSubscriber" {
  SubscriberID
  --
  Email
}

entity "NewsletterCampaign" {
  CampaignID
  --
  Title
  Subject
}

entity "NewsletterDelivery" {
  DeliveryID
  --
  Status
}

' Relazioni senza cardinalità dettagliate
User -- PrivacyPattern : creates
User -- ImplementationExample : creates
User -- Notification : receives
User -- NewsletterCampaign : creates

PrivacyPattern -- ImplementationExample : contains

PrivacyPattern -- GDPRArticle : references
PrivacyPattern -- PbDPrinciple : implements
PrivacyPattern -- ISOPhase : applies to
PrivacyPattern -- Vulnerability : addresses

NewsletterCampaign -- NewsletterDelivery : generates
NewsletterSubscriber -- NewsletterDelivery : receives

@enduml