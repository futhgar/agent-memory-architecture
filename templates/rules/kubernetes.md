---
paths:
  - "kubernetes/**"
---

# Kubernetes Conventions

## GitOps Pattern

Every workload gets an ArgoCD Application. Naming: `<namespace>-<app>.yaml`.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: <app-name>
  namespace: argocd
  finalizers: [resources-finalizer.argocd.argoproj.io]
spec:
  project: default
  destination:
    server: https://kubernetes.default.svc
    namespace: <target-namespace>
  syncPolicy:
    automated: { prune: true, selfHeal: true }
    syncOptions: [CreateNamespace=true]
```

## Manifest Conventions

- Labels: `app: <name>` on all resources
- IngressRoutes: use `IngressRoute` CRD, `entryPoints: [websecure]`, hostname `<app>.example.com`
- TLS: cert-manager Certificate, secret `<app>-tls`
- Storage: your project's StorageClass names go here
- Deployments with RWO PVC: use `strategy.type: Recreate` (prevents multi-attach deadlock)
- Secrets: Use SealedSecrets or External Secrets Operator — never plaintext
- SecurityContext: run as non-root (`runAsUser: 1000, runAsGroup: 1000, fsGroup: 1000` typical)

## Namespaces

List your project's namespaces here (e.g., `ai-llm, orchestration, monitoring, media, dev`).
