#!/bin/bash
# scripts/security_audit.sh - Audit di sicurezza per Compliance Compass

set -e

# Colori per l'output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}===== Compliance Compass Security Audit =====${NC}"
echo "Data: $(date)"
echo "Ambiente: ${ENVIRONMENT:-development}"
echo

# Crea directory per report
REPORT_DIR="security_reports"
mkdir -p $REPORT_DIR
# Funzione per eseguire e verificare test
run_test() {
   name=$1
   command=$2
   echo -e "\n${YELLOW}Running $name...${NC}"
   
   if eval $command; then
       echo -e "${GREEN}$name completed successfully${NC}"
       return 0
   else
       echo -e "${RED}$name failed${NC}"
       return 1
   fi
}

# 1. Analisi statica del codice con Bandit
run_test "Bandit security scan" "bandit -r src/ -f json -o $REPORT_DIR/bandit-report.json"

# 2. Controllo dipendenze vulnerabili
run_test "Dependency check" "pip-audit -r requirements.txt -o $REPORT_DIR/dependencies-report.json -f json"

# 3. Controllo secrets hardcoded
run_test "Secret detection" "git-secrets --scan"

# 4. Controllo configurazioni CORS
echo -e "\n${YELLOW}Checking CORS configuration...${NC}"
if grep -r "CORS_ORIGINS" --include="*.py" ./src/ | grep -q "\\*"; then
   echo -e "${RED}WARNING: Wildcard CORS origin detected${NC}"
else
   echo -e "${GREEN}CORS configuration seems safe${NC}"
fi

# 5. Verifica JWT configuration
echo -e "\n${YELLOW}Checking JWT configuration...${NC}"
if grep -q "JWT_ALGORITHM.*HS256" src/config.py; then
   echo -e "${GREEN}JWT uses secure algorithm (HS256)${NC}"
else
   echo -e "${RED}WARNING: JWT may not be using HS256${NC}"
fi

# 6. Verifica password hashing
echo -e "\n${YELLOW}Checking password hashing...${NC}"
if grep -q "bcrypt" src/utils/password.py; then
   echo -e "${GREEN}Using secure password hashing (bcrypt)${NC}"
else
   echo -e "${RED}WARNING: bcrypt not detected for password hashing${NC}"
fi

# 7. Rate limiting check
echo -e "\n${YELLOW}Checking rate limiting...${NC}"
if grep -q "RateLimitMiddleware" src/main.py; then
   echo -e "${GREEN}Rate limiting middleware detected${NC}"
else
   echo -e "${RED}WARNING: Rate limiting may not be configured${NC}"
fi

# 8. Check for SQL injection prevention
echo -e "\n${YELLOW}Checking SQL injection prevention...${NC}"
if ! grep -r "execute(" --include="*.py" ./src/ | grep -q "f\""; then
   echo -e "${GREEN}No f-string SQL queries detected${NC}"
else
   echo -e "${RED}WARNING: Potential SQL injection risk detected${NC}"
fi

# 9. Input validation check
echo -e "\n${YELLOW}Checking input validation...${NC}"
schema_count=$(find ./src/schemas -name "*.py" | wc -l)
echo -e "${GREEN}Found $schema_count Pydantic schema files for input validation${NC}"

# 10. Generate summary
echo -e "\n${YELLOW}===== Security Audit Summary =====${NC}"
echo "Report files saved in $REPORT_DIR/"
echo "Please review the reports for detailed findings"
echo
echo "Key recommendations:"
echo "1. Regularly update dependencies"
echo "2. Implement content security policy (CSP)"
echo "3. Consider adding CSRF protection for non-GET endpoints"
echo "4. Add automated security scanning to CI/CD pipeline"

exit 0