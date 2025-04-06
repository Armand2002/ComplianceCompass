# Roadmap per l'Implementazione della Newsletter in ComplianceCompass

Basandomi sull'analisi della codebase attuale, ecco una roadmap strutturata per implementare il servizio di newsletter completo in 1-2 giorni lavorativi:

## Giorno 1: Backend e Infrastruttura

### Fase 1: Modello dati (2 ore)
- **Modello Newsletter**
  ```python
  # src/models/newsletter.py
  from sqlalchemy import Column, Integer, String, Boolean, DateTime
  from datetime import datetime
  from src.models.base import Base

  class NewsletterSubscription(Base):
      __tablename__ = "newsletter_subscriptions"
      
      id = Column(Integer, primary_key=True, index=True)
      email = Column(String(255), unique=True, nullable=False, index=True)
      is_active = Column(Boolean, default=True)
      verification_token = Column(String(100), nullable=True)
      is_verified = Column(Boolean, default=False)
      subscribed_at = Column(DateTime, default=datetime.utcnow)
      last_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  ```

- **Migration script per il nuovo modello**
- **Schema Pydantic**
  ```python
  # src/schemas/newsletter.py
  from pydantic import BaseModel, EmailStr, Field
  from datetime import datetime
  from typing import Optional

  class NewsletterSubscriptionBase(BaseModel):
      email: EmailStr = Field(..., description="Email dell'utente iscritto")

  class NewsletterSubscriptionCreate(NewsletterSubscriptionBase):
      pass

  class NewsletterSubscriptionResponse(NewsletterSubscriptionBase):
      id: int
      is_active: bool
      is_verified: bool
      subscribed_at: datetime
      
      class Config:
          orm_mode = True
  ```

### Fase 2: Servizio Newsletter (3 ore)
- **Implementazione del servizio**
  ```python
  # src/services/newsletter_service.py
  from typing import List, Dict, Any, Optional
  from sqlalchemy.orm import Session
  from datetime import datetime
  import secrets

  from src.models.newsletter import NewsletterSubscription
  from src.services.email_service import EmailService

  class NewsletterService:
      def __init__(self):
          self.email_service = EmailService()
      
      def subscribe(self, db: Session, email: str) -> NewsletterSubscription:
          # Implementa logica iscrizione
      
      def unsubscribe(self, db: Session, email: str) -> bool:
          # Implementa logica cancellazione iscrizione
      
      def verify_subscription(self, db: Session, email: str, token: str) -> bool:
          # Implementa verifica token
      
      def send_verification_email(self, email: str, token: str) -> bool:
          # Invia email verifica
      
      def get_subscription_status(self, db: Session, email: str) -> Dict[str, Any]:
          # Ottieni status iscrizione
  ```

- **Integrazione con EmailService esistente**
  - Aggiungi metodo `send_newsletter_verification_email`
  - Aggiungi metodo `send_newsletter_welcome_email`
  - Aggiungi modelli email con Jinja2

### Fase 3: Controller e Routes (3 ore)
- **Implementazione Controller**
  ```python
  # src/controllers/newsletter_controller.py
  from typing import Dict, Any, Optional
  from sqlalchemy.orm import Session
  from fastapi import HTTPException, status

  from src.services.newsletter_service import NewsletterService
  from src.models.newsletter import NewsletterSubscription

  class NewsletterController:
      def __init__(self):
          self.newsletter_service = NewsletterService()
      
      def subscribe(self, db: Session, email: str) -> Dict[str, Any]:
          # Implementa subscribe
      
      def unsubscribe(self, db: Session, email: str) -> Dict[str, Any]:
          # Implementa unsubscribe
      
      def verify_subscription(self, db: Session, email: str, token: str) -> Dict[str, Any]:
          # Implementa verify
      
      def get_subscription_status(self, db: Session, email: str) -> Dict[str, Any]:
          # Implementa status
  ```

- **Definizione Routes API**
  ```python
  # src/routes/newsletter_routes.py
  from fastapi import APIRouter, Depends, Query, HTTPException, status
  from sqlalchemy.orm import Session
  from pydantic import EmailStr

  from src.db.session import get_db
  from src.controllers.newsletter_controller import NewsletterController
  from src.schemas.newsletter import NewsletterSubscriptionCreate, NewsletterSubscriptionResponse

  router = APIRouter(
      prefix="/newsletter",
      tags=["newsletter"],
      responses={400: {"description": "Bad Request"}}
  )

  newsletter_controller = NewsletterController()

  @router.post("/subscribe", status_code=status.HTTP_201_CREATED)
  async def subscribe_newsletter(subscription: NewsletterSubscriptionCreate, db: Session = Depends(get_db)):
      # Implementa subscribe endpoint
  
  @router.delete("/unsubscribe")
  async def unsubscribe_newsletter(email: EmailStr = Query(...), db: Session = Depends(get_db)):
      # Implementa unsubscribe endpoint
  
  @router.post("/verify")
  async def verify_newsletter_subscription(email: EmailStr = Query(...), token: str = Query(...), db: Session = Depends(get_db)):
      # Implementa verify endpoint
  
  @router.get("/status", response_model=Dict[str, Any])
  async def get_newsletter_status(email: EmailStr = Query(...), db: Session = Depends(get_db)):
      # Implementa status endpoint
  ```

## Giorno 2: Frontend e Testing

### Fase 4: Frontend - Componenti UI (4 ore)
- **Componente Iscrizione Newsletter**
  ```jsx
  // frontend/src/components/newsletter/NewsletterSubscription.jsx
  import React, { useState } from 'react';
  import { useForm } from 'react-hook-form';
  
  const NewsletterSubscription = () => {
    const [status, setStatus] = useState('idle'); // idle, loading, success, error
    const [message, setMessage] = useState('');
    const { register, handleSubmit, formState: { errors } } = useForm();
    
    const onSubmit = async (data) => {
      // Implementa logica iscrizione
    };
    
    return (
      <div className="newsletter-container">
        <h3>Resta aggiornato</h3>
        <p>Iscriviti alla newsletter per ricevere aggiornamenti sui privacy pattern e nuove funzionalità.</p>
        
        {/* Form con gestione stato */}
      </div>
    );
  };
  
  export default NewsletterSubscription;
  ```

- **Componente Verifica Iscrizione**
  ```jsx
  // frontend/src/components/newsletter/NewsletterVerification.jsx
  import React, { useState, useEffect } from 'react';
  import { useLocation } from 'react-router-dom';
  
  const NewsletterVerification = () => {
    // Implementa logica verifica
  };
  
  export default NewsletterVerification;
  ```

- **Componente Gestione Iscrizione**
  ```jsx
  // frontend/src/components/newsletter/ManageSubscription.jsx
  import React, { useState } from 'react';
  import { useForm } from 'react-hook-form';
  
  const ManageSubscription = () => {
    // Implementa logica gestione
  };
  
  export default ManageSubscription;
  ```

- **CSS e Stili**
  ```scss
  // frontend/src/styles/components/newsletter.scss
  .newsletter-container {
    // Stili
  }
  
  .newsletter-form {
    // Stili
  }
  
  .newsletter-message {
    // Stili
  }
  ```

### Fase 5: Integrazioni e Routing (2 ore)
- **Aggiungi route nel router React**
  ```jsx
  // Aggiungi in frontend/src/App.jsx o nel router
  <Route path="/newsletter/verify" element={<NewsletterVerification />} />
  <Route path="/newsletter/manage" element={<ManageSubscription />} />
  ```

- **Integra componente in HomePage o Footer**
  ```jsx
  // Aggiungi componente in posizione appropriata
  <NewsletterSubscription />
  ```

- **Crea servizio API Frontend**
  ```jsx
  // frontend/src/services/newsletterService.js
  const subscribeNewsletter = async (email) => {
    // Implementa API call
  };
  
  const unsubscribeNewsletter = async (email) => {
    // Implementa API call
  };
  
  // ... altri metodi
  
  export { subscribeNewsletter, unsubscribeNewsletter /* ... */ };
  ```

### Fase 6: Testing e Ottimizzazione (3 ore)
- **Test Unitari Backend**
  ```python
  # tests/services/test_newsletter_service.py
  def test_subscribe_new_email():
    # Test subscribe con email nuova
  
  def test_subscribe_existing_email():
    # Test subscribe con email esistente
  ```

- **Test E2E**
  ```python
  # tests/e2e/test_newsletter_flows.py
  def test_newsletter_subscription_complete_flow():
    # Test flusso completo iscrizione
  ```

- **Verifica compatibilità dispositivi mobili**
- **Revisione del codice e ottimizzazione query**
- **Documentazione API e componenti**

## Fase 7: Lancio e Monitoraggio (1 ora)
- **Creazione template newsletter standard**
- **Script di admin per invio newsletter**
- **Setup monitoraggio errori**
- **Piano di rollback in caso di problemi**

## Note di integrazione

Sfrutta le classi esistenti:
- Utilizza `EmailService` esistente per gestire l'invio delle email
- Segui lo stesso pattern controller-service-model utilizzato per le notifiche
- Integra con `NotificationService` per notificare gli admin delle nuove iscrizioni

La maggior parte dell'infrastruttura necessaria è già presente nella codebase, incluso il sistema di invio email, template Jinja2, e gestione utenti, quindi il focus può essere principalmente sull'implementazione specifica della funzionalità newsletter.