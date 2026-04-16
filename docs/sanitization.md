# Sanitization Checklist

How to keep your public fork of this architecture safe from credential leaks, doxxing, and operational disclosure.

## The Rule

**Never fork the private repo. Always `git init` a fresh repo.** Copying is how secrets leak.

## Before First Commit

Run all three:
```bash
# Install if needed
brew install gitleaks detect-secrets
pip install trufflehog

# Scan your working directory
gitleaks detect --no-git
trufflehog filesystem .
detect-secrets scan --all-files .
```

Fix every finding before committing.

## What to Strip

| Category | What to look for | Replace with |
|----------|-----------------|--------------|
| IPs | `10.27.1.x`, specific private ranges | `10.0.0.x`, `192.168.1.x` (RFC 1918 examples) |
| Public IPs | Real Hetzner/AWS IPs | `<YOUR_VPS_IP>` |
| Domains | Real domain | `example.com`, `<YOUR_DOMAIN>` |
| Subdomains | `msam.guatulab.com` | `msam.example.com` |
| Usernames | Real usernames | `<YOUR_USER>`, `user` |
| Email addresses | Personal emails | `<YOUR_EMAIL>` |
| UUIDs | Paperclip/Linear/service UUIDs | `<YOUR_WORKSPACE_ID>` |
| API keys | `sk-...`, `ghp_...`, `eyJ...` | `<YOUR_API_KEY>` |
| Tokens | Bearer tokens, Matrix tokens | Remove entirely or `<YOUR_TOKEN>` |
| Bucket names | `tofu-state`, `backups-<company>` | `<YOUR_BUCKET>` |
| Node names | `bifrost`, `fenrir` | Generic (`node-01`) or keep if not sensitive |
| GPU specs | If specific to your hardware | Generic (`<YOUR_GPU>`) |
| Company names | References to your company | `<YOUR_COMPANY>` (unless self-promoting in README) |

## What to Keep

- Architecture patterns (naming conventions, layer structure)
- Script logic (with paths replaced by env vars)
- Mermaid diagrams (with labels anonymized)
- Best practice documentation
- Research and references

## Ongoing Sync from Private to Public

**Manual curation only. Never automate this.**

Bad: `git pull private && git push public` (will leak secrets eventually)
Good: for each update, review the diff, copy sanitized version to public repo, commit separately

Suggested workflow:
1. Make the change in your private repo
2. Verify it works
3. Manually create the equivalent change in the public repo directory
4. Run `gitleaks` and `trufflehog` on the public repo
5. Commit and push

## Emergency Response

If you accidentally commit a secret:

1. **Rotate the secret immediately** — do not assume the commit will save you
2. Use `git-filter-repo` to rewrite history:
   ```bash
   git filter-repo --path <leaked-file> --invert-paths
   git push --force origin main
   ```
3. Force-push (you're rewriting history — coordinate with any collaborators)
4. Check if GitHub caching surfaces the secret at `github.com/<user>/<repo>/blame/<commit-hash>/<file>` — if yes, contact GitHub Support
5. Scan GitHub/Google for the leaked value to see where else it's indexed

## Pre-Commit Hook

Drop this in `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Block commits containing common credential patterns
if git diff --cached | grep -E 'sk-[A-Za-z0-9]{32}|ghp_[A-Za-z0-9]{36}|AKIA[A-Z0-9]{16}|eyJ[A-Za-z0-9_-]{20}\.[A-Za-z0-9_-]{20}'; then
    echo "BLOCKED: Commit contains what looks like a credential"
    echo "If this is a false positive, use git commit --no-verify"
    exit 1
fi
```

Make it executable: `chmod +x .git/hooks/pre-commit`

## Verify Your Repo is Clean

Run `./scripts/check-sanitization.sh` (provided in this repo) before publishing.
