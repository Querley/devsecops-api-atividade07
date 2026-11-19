# DevSecOps Secure API — Esteira CI/CD de Segurança (Atividade 07)

Projeto de demonstração prática de uma esteira **DevSecOps ponta a ponta** com **Security Gates** automatizados no GitHub Actions, cobrindo da análise de código e dependências até contêineres, IaC e testes dinâmicos (DAST).

## Arquitetura do Projeto

```text
devsecops-api/
├── .github/workflows/devsecops.yml   # Pipeline CI/CD DevSecOps completa
├── app/
│   ├── __init__.py
│   └── main.py                       # API REST FastAPI com headers de segurança e validação Pydantic
├── infra/
│   └── main.tf                       # IaC Terraform (S3 com KMS + Public Access Block + SG restritivo)
├── tests/
│   └── test_api.py                   # Testes automatizados (Pytest)
├── Dockerfile                        # Imagem Python 3.12-slim endurecida (non-root, healthcheck)
├── docker-compose.yml                # Compose endurecido (read_only, cap_drop ALL, no-new-privileges)
└── requirements.txt                  # Dependências com versões fixadas
```

## Etapas e Security Gates da Pipeline

| Etapa | Controle | Ferramenta(s) | Critério de Bloqueio (Security Gate) |
| :--- | :--- | :--- | :--- |
| 0 | Testes Unitários | Pytest | Falha em testes funcionais ou de headers HTTP |
| 1 | Secret Scanning | Gitleaks | Qualquer segredo/token/chave detectado (`--exit-code 1`) |
| 2 | SAST | Semgrep | Falhas de segurança no código Python/OWASP (`--error`) |
| 3 | SCA & SBOM | Trivy FS | CVEs `HIGH` ou `CRITICAL` (`exit-code: 1`) + SBOM CycloneDX & SPDX |
| 4 | IaC & Dockerfile | Hadolint, Trivy Config, Checkov | Erros de Dockerfile ou más configurações `HIGH`/`CRITICAL` em Terraform/Compose |
| 5 | Container Scan | Trivy Image | CVEs `HIGH`/`CRITICAL` corrigíveis na imagem Docker + SBOM da imagem |
| 6 | DAST | OWASP ZAP + `curl` | Falhas graves em runtime ou ausência de headers de segurança HTTP |
| 7 | Deploy Gate | GitHub Actions (`needs`) | Só libera se **todas** as etapas anteriores forem aprovadas |

## Execução Local

```bash
pip install -r requirements.txt
pytest -v
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Ou via Docker Compose:

```bash
docker compose up --build
```
