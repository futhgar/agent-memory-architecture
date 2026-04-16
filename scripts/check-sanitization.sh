#!/usr/bin/env bash
# Pre-publish sanitization check — scan for leaked personal data and secrets.
# Run before flipping the repo from private to public.
set -uo pipefail

FAIL=0
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== Sanitization Check ==="
echo "Repo: $ROOT"
echo ""

# 1. Check for common secret patterns
echo "[1/5] Scanning for credential patterns..."
PATTERNS=(
    'sk-[A-Za-z0-9]{32,}'                    # OpenAI-style
    'ghp_[A-Za-z0-9]{36}'                    # GitHub PAT
    'github_pat_[A-Za-z0-9_]{82}'            # Fine-grained GitHub PAT
    'AKIA[A-Z0-9]{16}'                       # AWS access key
    'eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{10,}'  # JWT
    'Bearer\s+[A-Za-z0-9._-]{30,}'           # Bearer tokens
    'xox[pbar]-[A-Za-z0-9-]{10,}'            # Slack tokens
    'ya29\.[A-Za-z0-9_-]{50,}'               # Google OAuth
    'syt_[A-Za-z0-9_]{20,}'                  # Matrix/Synapse tokens
)

for pattern in "${PATTERNS[@]}"; do
    HITS=$(grep -rE "$pattern" "$ROOT" \
        --exclude-dir=.git \
        --exclude-dir=node_modules \
        --exclude="check-sanitization.sh" \
        2>/dev/null || true)
    if [[ -n "$HITS" ]]; then
        echo "  FAIL: found potential credential matching $pattern"
        echo "$HITS" | head -3
        FAIL=1
    fi
done
[[ $FAIL -eq 0 ]] && echo "  PASS: no credential patterns found"

# 2. Check for personal domains/emails
echo ""
echo "[2/5] Scanning for personal domains and emails..."
BAD_PATTERNS=(
    '[a-z0-9._%+-]+@[a-z0-9.-]+\.(com|org|net|dev|io)'     # emails (excluding examples)
)
# Whitelist: expected example patterns
WHITELIST='example\.(com|org|lab|net)|your[_-]domain|<YOUR|\.example|user@example'

LEAKS=$(grep -rE '[a-z0-9._%+-]+@[a-z0-9.-]+\.(com|org|net|dev|io)' "$ROOT" \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    2>/dev/null | grep -vE "$WHITELIST" || true)

if [[ -n "$LEAKS" ]]; then
    echo "  WARN: possible email/domain leaks (review manually):"
    echo "$LEAKS" | head -5
    echo "  (not blocking — examples in docs may be flagged)"
fi

# 3. Check for IPs outside of example ranges
echo ""
echo "[3/5] Scanning for non-example IPs..."
# Allow: 10.0.0.x, 127.0.0.1, 0.0.0.0, 192.168.1.x, 172.16.x.x (common examples)
IP_LEAKS=$(grep -rEo '\b([0-9]{1,3}\.){3}[0-9]{1,3}\b' "$ROOT" \
    --exclude-dir=.git \
    --exclude-dir=node_modules \
    2>/dev/null | grep -vE '^[^:]+:(10\.0\.|127\.0\.0\.1|0\.0\.0\.0|192\.168\.1\.|172\.16\.|255\.255\.|169\.254\.)' | sort -u || true)

if [[ -n "$IP_LEAKS" ]]; then
    echo "  WARN: IPs found outside example ranges (review manually):"
    echo "$IP_LEAKS" | head -10
    echo "  (not blocking — check if these are your real infrastructure)"
fi

# 4. Check for known personal identifiers (customize this list for your setup)
echo ""
echo "[4/5] Scanning for personal identifiers..."
PERSONAL_PATTERNS=(
    # Add your personal patterns here before publishing:
    # 'your-real-name'
    # 'your-real-domain'
    # 'your-real-username'
)

if [[ ${#PERSONAL_PATTERNS[@]} -eq 0 ]]; then
    echo "  SKIP: no personal patterns configured (edit scripts/check-sanitization.sh to add yours)"
fi

for pattern in "${PERSONAL_PATTERNS[@]}"; do
    HITS=$(grep -rli "$pattern" "$ROOT" --exclude-dir=.git 2>/dev/null || true)
    if [[ -n "$HITS" ]]; then
        echo "  FAIL: found '$pattern' in:"
        echo "$HITS"
        FAIL=1
    fi
done

# 5. Check for tool-reported leaks
echo ""
echo "[5/5] Running external scanners if installed..."
if command -v gitleaks &>/dev/null; then
    gitleaks detect --no-git --source "$ROOT" --report-format=json --report-path=/dev/null 2>&1 | tail -5 || {
        echo "  FAIL: gitleaks reported findings"
        FAIL=1
    }
    echo "  PASS: gitleaks clean"
else
    echo "  SKIP: gitleaks not installed (brew install gitleaks)"
fi

if command -v trufflehog &>/dev/null; then
    trufflehog filesystem "$ROOT" --no-verification 2>&1 | tail -3 || true
    echo "  INFO: trufflehog ran — review output above"
else
    echo "  SKIP: trufflehog not installed (brew install trufflehog)"
fi

echo ""
if [[ $FAIL -eq 0 ]]; then
    echo "SANITIZATION: PASS"
    exit 0
else
    echo "SANITIZATION: FAIL — fix issues above before publishing"
    exit 1
fi
