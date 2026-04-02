#!/bin/bash
# Security Scan Script
# Checks for potential security risks and private tokens

echo "=========================================="
echo "SECURITY SCAN - v0.1.0-alpha"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

echo "1. Scanning for API Keys and Tokens..."
echo "   Pattern: api_key, apikey, token, secret, password"
PATTERN_FILES=$(grep -r -l -i "\(api_key\|apikey\|api-key\|secret_key\|secretkey\|secret-key\|private_key\|password\|passwd\|token\)" --include="*.py" --include="*.json" --include="*.md" --include="*.txt" --include="*.yml" --include="*.yaml" src/ tests/ docs/ demos/ benchmarks/ 2>/dev/null | grep -v ".pyc" | head -20)
if [ -n "$PATTERN_FILES" ]; then
    echo -e "   ${YELLOW}⚠️  Potential sensitive patterns found in:${NC}"
    echo "$PATTERN_FILES" | while read f; do echo "     - $f"; done
else
    echo -e "   ${GREEN}✓ No sensitive patterns found${NC}"
fi
echo ""

echo "2. Scanning for hardcoded credentials..."
PATTERN_FILES=$(grep -r -l -E "(password\s*=\s*['\"][^'\"]+['\"]|secret\s*=\s*['\"][^'\"]+['\"]|token\s*=\s*['\"][^'\"]+['\"])" --include="*.py" src/ tests/ demos/ 2>/dev/null)
if [ -n "$PATTERN_FILES" ]; then
    echo -e "   ${RED}🚨 Potential hardcoded credentials found in:${NC}"
    echo "$PATTERN_FILES" | while read f; do echo "     - $f"; done
else
    echo -e "   ${GREEN}✓ No hardcoded credentials found${NC}"
fi
echo ""

echo "3. Scanning for AWS/Azure/GCP keys..."
AWS_KEYS=$(grep -r -l "AKIA[0-9A-Z]\{16\}" --include="*.py" --include="*.json" --include="*.md" . 2>/dev/null)
AZURE_KEYS=$(grep -r -l "[0-9a-f]\{8\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{4\}-[0-9a-f]\{12\}" --include="*.py" --include="*.json" . 2>/dev/null | head -5)
GCP_KEYS=$(grep -r -l "AIza[0-9A-Za-z_-]\{35\}" --include="*.py" --include="*.json" . 2>/dev/null)

if [ -n "$AWS_KEYS" ] || [ -n "$AZURE_KEYS" ] || [ -n "$GCP_KEYS" ]; then
    echo -e "   ${RED}🚨 Cloud provider keys found!${NC}"
    [ -n "$AWS_KEYS" ] && echo "     AWS: $AWS_KEYS"
    [ -n "$AZURE_KEYS" ] && echo "     Azure: $AZURE_KEYS"
    [ -n "$GCP_KEYS" ] && echo "     GCP: $GCP_KEYS"
else
    echo -e "   ${GREEN}✓ No cloud provider keys found${NC}"
fi
echo ""

echo "4. Scanning for database connection strings..."
DB_PATTERNS=$(grep -r -l -E "(mongodb(\+srv)?://|postgres(ql)?://|mysql://|redis://|mongodb://)" --include="*.py" --include="*.json" --include="*.md" --include="*.txt" . 2>/dev/null)
if [ -n "$DB_PATTERNS" ]; then
    echo -e "   ${YELLOW}⚠️  Database connection strings found in:${NC}"
    echo "$DB_PATTERNS" | while read f; do echo "     - $f"; done
else
    echo -e "   ${GREEN}✓ No database connection strings found${NC}"
fi
echo ""

echo "5. Scanning for private keys (PEM, RSA, etc.)..."
KEY_FILES=$(find . -name "*.pem" -o -name "*.key" -o -name "*.p12" -o -name "*.pfx" -o -name "id_rsa" -o -name "id_dsa" 2>/dev/null | grep -v ".git")
if [ -n "$KEY_FILES" ]; then
    echo -e "   ${RED}🚨 Private key files found:${NC}"
    echo "$KEY_FILES" | while read f; do echo "     - $f"; done
else
    echo -e "   ${GREEN}✓ No private key files found${NC}"
fi
echo ""

echo "6. Scanning for .env files..."
ENV_FILES=$(find . -name ".env" -o -name ".env.local" -o -name ".env.production" -o -name ".env.development" 2>/dev/null | grep -v ".git")
if [ -n "$ENV_FILES" ]; then
    echo -e "   ${YELLOW}⚠️  Environment files found:${NC}"
    echo "$ENV_FILES" | while read f; do echo "     - $f"; done
    echo -e "   ${YELLOW}   Make sure these are in .gitignore!${NC}"
else
    echo -e "   ${GREEN}✓ No .env files found${NC}"
fi
echo ""

echo "7. Checking .gitignore..."
if [ -f ".gitignore" ]; then
    echo -e "   ${GREEN}✓ .gitignore exists${NC}"
    echo "   Checking for sensitive patterns..."
    IGNORE_CHECKS=(".env" ".key" ".pem" "__pycache__" ".pyc" ".DS_Store")
    for pattern in "${IGNORE_CHECKS[@]}"; do
        if grep -q "$pattern" .gitignore 2>/dev/null; then
            echo -e "     ${GREEN}✓ $pattern is ignored${NC}"
        else
            echo -e "     ${YELLOW}⚠️  $pattern NOT in .gitignore${NC}"
        fi
    done
else
    echo -e "   ${RED}🚨 .gitignore NOT FOUND!${NC}"
fi
echo ""

echo "8. Scanning for IP addresses..."
IP_ADDRS=$(grep -r -E "\b([0-9]{1,3}\.){3}[0-9]{1,3}\b" --include="*.py" --include="*.json" --include="*.md" src/ tests/ docs/ demos/ 2>/dev/null | grep -v "127.0.0.1\|0.0.0.0\|255.255.255" | head -10)
if [ -n "$IP_ADDRS" ]; then
    echo -e "   ${YELLOW}⚠️  IP addresses found:${NC}"
    echo "$IP_ADDRS" | head -5 | while read line; do echo "     $line"; done
else
    echo -e "   ${GREEN}✓ No external IP addresses found${NC}"
fi
echo ""

echo "9. Scanning for TODO comments that might contain sensitive info..."
TODO_SENSITIVE=$(grep -r -i "TODO.*\(password\|secret\|key\|token\|credential\)" --include="*.py" src/ tests/ 2>/dev/null)
if [ -n "$TODO_SENSITIVE" ]; then
    echo -e "   ${YELLOW}⚠️  TODOs mentioning sensitive terms:${NC}"
    echo "$TODO_SENSITIVE" | head -5 | while read line; do echo "     $line"; done
else
    echo -e "   ${GREEN}✓ No suspicious TODOs found${NC}"
fi
echo ""

echo "10. Scanning for executable scripts with potential risks..."
EXEC_PERMS=$(find . -type f -perm +111 -name "*.py" 2>/dev/null | grep -v ".git")
if [ -n "$EXEC_PERMS" ]; then
    echo -e "   ${YELLOW}⚠️  Executable Python files:${NC}"
    echo "$EXEC_PERMS" | while read f; do echo "     - $f"; done
else
    echo -e "   ${GREEN}✓ No executable Python files${NC}"
fi
echo ""

echo "=========================================="
echo "SCAN COMPLETE"
echo "=========================================="
echo ""
echo "If any RED 🚨 items were found, review them immediately."
echo "If any YELLOW ⚠️  items were found, review to ensure they are safe."
echo ""
