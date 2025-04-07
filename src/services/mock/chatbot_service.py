"""
Versione semplificata del ChatbotService per demo/esame
"""

class SimpleChatbotService:
    """
    Implementa risposte predefinite per dimostrare la funzionalità del chatbot
    senza richiedere modelli NLP pesanti
    """
    
    def __init__(self):
        self.responses = {
            "gdpr": "Il GDPR (General Data Protection Regulation) è il regolamento dell'UE sulla protezione dei dati personali. Principali articoli: Art.5 (Principi), Art.6 (Liceità), Art.7 (Consenso), Art.25 (Privacy by Design).",
            "privacy by design": "Privacy by Design significa integrare la protezione dei dati fin dalla progettazione. Principi chiave: proattività, privacy come impostazione predefinita, privacy incorporata nel design, funzionalità completa.",
            "pattern": "I Privacy Pattern sono soluzioni riutilizzabili per implementare la privacy nei sistemi informatici. Esempi: Minimizzazione dei dati, Consenso informato, Pseudonimizzazione, Separazione dei dati.",
            "minimizzazione": "La minimizzazione dei dati (Art.5 GDPR) richiede di raccogliere solo i dati personali necessari, adeguati e limitati alle finalità. Implementazioni comuni: campi opzionali, anonimizzazione, eliminazione automatica.",
            "default": "Sono una versione semplificata del chatbot per la demo. Prova a chiedere informazioni su 'GDPR', 'Privacy by Design', 'Pattern' o specifici concetti come 'minimizzazione'."
        }
    
    def generate_response(self, query: str) -> str:
        """Genera una risposta basata su parole chiave nella query"""
        query = query.lower()
        
        for key, response in self.responses.items():
            if key in query:
                return response
        
        return self.responses["default"]