# Strategia di Testing Compliance Compass

## Obiettivi
- Garantire una copertura del codice >=90%
- Assicurare la corretta funzionalità di tutti i percorsi utente critici
- Ridurre i tempi di regressione automatizzando i test
- Fornire feedback rapido agli sviluppatori durante lo sviluppo

## Livelli di Test
1. **Test Unitari**: Verifica di componenti isolati
2. **Test di Integrazione**: Verifica dell'interazione tra componenti
3. **Test API End-to-End**: Verifica degli endpoint API completi
4. **Test di Performance**: Verifica delle prestazioni sotto carico
5. **Test di Sicurezza**: Verifica delle vulnerabilità di sicurezza

## Approccio per Componente
- **Controllers**: Test unitari con mock di servizi e DB
- **Services**: Test unitari con mock di dipendenze esterne
- **Models**: Test unitari delle relazioni e validazioni
- **Schemas**: Test di validazione dei dati
- **Middleware**: Test di integrazione con richieste simulate
- **Routes**: Test API end-to-end

## Convenzioni
- Ogni file di test corrisponde a un file di codice (`test_*.py`)
- Test unitari usano pytest fixtures per setup/teardown
- I mock si trovano in `tests/mocks/`
- I test parametrizzati usano `@pytest.mark.parametrize`
- Le classi di test iniziano con "Test" (es. `TestAuthController`)

## Metriche
- Copertura del codice tracciata con coverage.py
- Metriche di esecuzione dei test (tempo, pass/fail) in CI/CD
- Report di copertura generati in HTML e JSON

## Integrazione CI/CD
- Test unitari e di integrazione eseguiti su ogni commit
- Test E2E e di performance eseguiti su PR e nightly
- Soglie di qualità bloccanti per merge (>=90% copertura)