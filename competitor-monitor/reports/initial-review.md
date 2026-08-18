# Relatório de Revisão Inicial — Inteligência Competitiva Tripla

**Gerado em:** 2026-08-18  
**Método:** Coleta via Firecrawl MCP (map + scrape) + análise direta. Sem chamadas LLM externas.  
**Branch:** `claude/stoic-sagan-xfn808`

> ⚠️ **Status de todos os dados: `baseline_status = candidate`**  
> Nenhum dado é considerado aprovado até revisão humana explícita.  
> Os arquivos em `baseline/candidates/` devem ser revisados e movidos para `baseline/approved/` após validação.

---

## Resumo Executivo

| # | Concorrente | Tipo | Sobreposição TOTAL | Sobreposição PARCIAL | Clientes Identificados | Prioridade |
|---|---|---|---|---|---|---|
| 1 | **iT.eam** | Pure Cyber | 6 | 4 | 0 | 🔴 ALTA |
| 2 | **9net** | Pure Cyber | 5 | 5 | 0 | 🔴 ALTA |
| 3 | **TIVIT** | Tech/Cyber | 4 | 3 | 0 | 🔴 ALTA |
| 4 | **Tempest** | Pure Cyber | 2 | 3 | 0 | 🔴 ALTA |
| 5 | **BHS** | Microsoft/Cyber | 1 | 1 | 9 | 🟡 MÉDIA |
| 6 | **Shield Security** | Pure Cyber | 1 | 1 | 1 | 🟡 MÉDIA |
| 7 | **3CORP** | Infra/Telecom | 0 | 1 | 17 | 🟡 MÉDIA |
| 8 | **ISH** | Pure Cyber | 0 | 0 | 0 | 🟡 MÉDIA |
| 9 | **Actar** | Pure Cyber | 0 | 2 | 0 | 🟡 MÉDIA |
| 10 | **KPMG** | BIG4 | 0 | 2 | 0 | 🟢 BAIXA |
| 11 | **PwC** | BIG4 | 0 | 0 | 0 | 🟢 BAIXA |
| 12 | **Deloitte** | BIG4 | 0 | 0 | 0 | 🟢 BAIXA |
| 13 | **EY** | BIG4 | 0 | 0 | 1 | 🟢 BAIXA |
| 14 | **Solo Network** | Microsoft/Integrador | 0 | 0 | 1 | 🟢 BAIXA |
| 15 | **Tecno-IT** | Smart City | 0 | 0 | 2 | 🟢 BAIXA |

---

## Portfólio Tripla (Referência)

**Pilar CONFORMIDADE:** GRC/Compliance, LGPD, Privacy, Risk Assessment  
**Pilar DISPONIBILIDADE:** Backup, DR, Cloud Infrastructure, BCP  
**Pilar PROTEÇÃO:** SOC/MDR CyberWatch, EDR/Endpoint, Pentest, IAM/PAM, WAF, NGFW, SASE/ZTNA, DLP, NAC, Cloud Security, Vulnerability Management, Incident Response

---

## 1. iT.eam (`it-eam.com`)

**Tipo:** Pure Cybersecurity | **Sede:** Brasil (também PT e NL) | **Status:** Operacional

### Ofertas Identificadas

| Oferta | Sobreposição Tripla | Solução Tripla | Confidence |
|---|---|---|---|
| Next Generation SOC (IBM QRadar XDR/SIEM/UBA/SOAR/NDR) | **TOTAL** | SOC/MDR CyberWatch | 0.95 |
| Endpoint Security (HCL BigFix, IBM MaaS360, NGAV) | **TOTAL** | EDR / Endpoint | 0.90 |
| Data Security (IBM Guardium + DLP Forcepoint) | **TOTAL** | DLP | 0.90 |
| Threat Management & Incident Response (Blue/Red Team, Pentest) | **TOTAL** | Pentest / IR | 0.90 |
| Vulnerability Management & Patch (SANS) | **TOTAL** | Vulnerability Mgmt | 0.90 |
| MSS (Managed Security Services) | **TOTAL** | SOC/MDR CyberWatch | 0.85 |
| Application Security (Veracode, WAF, WAS) | **PARCIAL** | WAF / AppSec | 0.85 |
| Cloud Security (CSPM, CIEM, Cloud IAM) | **PARCIAL** | Cloud Security | 0.85 |
| Risk & Compliance / LGPD (framework 3 etapas) | **PARCIAL** | GRC/Compliance | 0.90 |
| Threat Intelligence / Brand & Executive Protection | **PARCIAL** | Threat Intelligence | 0.85 |
| EAM (Enterprise Asset Management) | FORA_DE_PORTFOLIO | — | 0.90 |

### Destaque
- **Primeiro no mundo a certificar SOC-CMM nível máximo** — diferencial competitivo forte
- Stack IBM: QRadar Suite (integra XDR, SIEM, UBA, SOAR, NDR), Guardium, MaaS360, SOAR
- Parceiros: Veracode, Forcepoint, HCL

### URLs para Monitoramento
- DIÁRIO: `https://it-eam.com/pt/security/soc`, `https://it-eam.com/pt/security/solutions`
- SEMANAL: `https://it-eam.com/pt/security/services`

---

## 2. 9net (`9net.com.br`)

**Tipo:** Pure Cybersecurity / MSS | **Sede:** São Paulo (Itaim Bibi) | **Status:** Operacional

### Ofertas Identificadas

| Oferta | Sobreposição Tripla | Solução Tripla | Confidence |
|---|---|---|---|
| MSS / SNOC 24x7 (Security Continuous Monitoring) | **TOTAL** | SOC/MDR CyberWatch | 0.90 |
| SOC (Security Operations Center) | **TOTAL** | SOC/MDR CyberWatch | 0.90 |
| Endpoint Security / EDR + DLP + Data Discovery | **TOTAL** | EDR / DLP | 0.90 |
| IAM (Identity & Access Management) | **TOTAL** | IAM/PAM | 0.90 |
| WAF (Web Application Firewall) | **TOTAL** | WAF | 0.90 |
| SSE / ZTNA / DLP (Security Service Edge) | **TOTAL** | SASE/ZTNA | 0.90 |
| SOAR (Orchestration, Automation & Response) | **PARCIAL** | SOC/MDR CyberWatch | 0.85 |
| Cloud Security | **PARCIAL** | Cloud Security | 0.85 |
| Security Rating Monitoring (outside-in) | **PARCIAL** | Vulnerability Mgmt | 0.80 |
| Assessment de Segurança / Vulnerability Assessment | **PARCIAL** | Pentest / VA | 0.85 |
| CISOaaS | **PARCIAL** | vCISO / Consultoria | 0.80 |
| GRC / LGPD Compliance | **PARCIAL** | GRC/Compliance | 0.85 |
| CDN | FORA_DE_PORTFOLIO | — | 0.85 |

### Destaque
- Parceiros: **Netskope, Palo Alto Networks, AlienVault (USM)**
- Portfólio de segurança muito completo para empresa de porte médio
- Blog ativo com artigos técnicos (EDR, SSE, Zero Trust, IA vs Ransomware)

### URLs para Monitoramento
- DIÁRIO: `https://9net.com.br/blog`
- SEMANAL: `https://9net.com.br/seguranca`, `https://9net.com.br/compliance`

---

## 3. TIVIT (`tivit.com`)

**Tipo:** Grande empresa de TI + Cibersegurança | **Status:** Operacional (pertence ao Grupo AlmavivA)

### Ofertas Identificadas

| Oferta | Sobreposição Tripla | Solução Tripla | Confidence |
|---|---|---|---|
| SOC (Security Operations Center) | **TOTAL** | SOC/MDR CyberWatch | 0.90 |
| MDR (Managed Detection & Response) | **TOTAL** | SOC/MDR CyberWatch | 0.90 |
| MSS (Managed Security Services) | **TOTAL** | SOC/MDR CyberWatch | 0.85 |
| IAM (Identity & Access Management) | **TOTAL** | IAM/PAM | 0.90 |
| Red Team Services | **TOTAL** | Pentest | 0.85 |
| GRC (Governance, Risk & Compliance) | **PARCIAL** | GRC/Compliance | 0.85 |
| TVM (Threat & Vulnerability Management) | **TOTAL** | Vulnerability Mgmt | 0.85 |
| Gerenciamento de Crises | **PARCIAL** | Incident Response | 0.75 |
| TIVIT Defense (produto proprietário) | INDETERMINADO | — | 0.65 |
| DevSecOps | FORA_DE_PORTFOLIO | — | 0.80 |

### Notas
- Dados obtidos apenas do menu de navegação (página de cybersecurity retornou 404)
- TIVIT é empresa de grande porte — também tem Cloud Solutions, Digital, Mainframe, Fintech
- Requer scrape direto de `https://tivit.com/cybersecurity/` para confirmação

### URLs para Monitoramento
- DIÁRIO: `https://tivit.com/cases/`
- SEMANAL: `https://tivit.com/cybersecurity/`, `https://tivit.com/tivit-defense/`

---

## 4. Tempest Security Intelligence (`tempest.com.br`)

**Tipo:** Pure Cybersecurity | **Sede:** Brasil | **Status:** Operacional

### Ofertas Identificadas

| Oferta | Sobreposição Tripla | Solução Tripla | Confidence |
|---|---|---|---|
| Pentest (Externo, Interno, Mobile, Web, API, IoT, Wi-Fi) | **TOTAL** | Pentest | 0.95 |
| Offensive Security / Red Team | **TOTAL** | Pentest | 0.85 |
| Cloud Security (Review, Assessment, Consulting, Secure IAC, Shadow IT) | **PARCIAL** | Cloud Security | 0.90 |
| Application Security | **PARCIAL** | Pentest / AppSec | 0.80 |
| Security Advisory / Gestão de Vulnerabilidades | **PARCIAL** | Vulnerability Mgmt | 0.80 |

### Destaque
- **50+ profissionais de Pentest** — maior time de pentest do Brasil (declaração própria)
- 20+ anos de experiência, 1000+ projetos, 4000+ vulnerabilidades identificadas
- **100+ clientes distintos** — não nomeados no site
- 80% do trabalho de Pentest é manual (diferencial)
- Blog técnico ativo: Sidechannel

### URLs para Monitoramento
- DIÁRIO: `https://sidechannel.tempest.com.br`
- SEMANAL: `https://www.tempest.com.br/consultoria/pentest`, `https://www.tempest.com.br/consultoria/cloud-security`

---

## 5. BHS (`bhs.com.br`)

**Tipo:** Microsoft Partner + Cybersecurity | **Status:** Operacional

### Clientes Identificados (9)

| Cliente | Case |
|---|---|
| FIEMG | Atendimento com IA via Microsoft Copilot Studio |
| Blossom Consult | Gestão Microsoft 365 e redução de custos |
| BS2 | Outsourcing de TI na corrida do PIX |
| Tegra | Migração ambiente SAP para Azure |
| RHI Magnesita | Gestão do espaço físico e retorno ao trabalho |
| Cemig | Agência virtual de autoatendimento (Cemig Atende) + Outsourcing TI (Cemig SIM) |
| Patrus | Maturidade de segurança Microsoft + Azure Virtual Desktop (70% redução de custos) |
| Grupo SADA | Reconhecimento na Cerimônia Anual |
| Monte Bravo | Segurança e conformidade na transição |

### Ofertas Identificadas

| Oferta | Sobreposição Tripla | Solução Tripla | Confidence |
|---|---|---|---|
| SOC 24x7 | **TOTAL** | SOC/MDR CyberWatch | 0.90 |
| Segurança Gerenciada (Microsoft M365/Azure) | **PARCIAL** | SOC/MDR CyberWatch | 0.85 |
| Microsoft 365 / Azure | FORA_DE_PORTFOLIO | — | 0.90 |

### Notas
- BHS é fortemente focada no ecossistema Microsoft
- SOC 24x7 é concorrência direta com CyberWatch Tripla
- Segmentos: energia, finanças, manufatura, logística, serviços financeiros

### URLs para Monitoramento
- DIÁRIO: `https://bhs.com.br/cases-e-resultados/`
- SEMANAL: `https://bhs.com.br/services/soc-24x7/`, `https://bhs.com.br/services/seguranca-gerenciada/`

---

## 6. Shield Security (`shieldsec.com.br`)

**Tipo:** Pure Cybersecurity | **Status:** Operacional

### Clientes Identificados (1)
| Cliente | Source |
|---|---|
| Drogaria Araújo | `/cases-drogaria-araujo` |

### Ofertas Identificadas

| Oferta | Sobreposição Tripla | Confidence |
|---|---|---|
| SOC/MDR | TOTAL (inferido) | 0.75 |
| Pentest / Segurança Ofensiva | TOTAL (inferido) | 0.75 |

### Notas
- Homepage retornou arquivo muito extenso (85k chars) — conteúdo não processado na íntegra
- Dados baseados principalmente no mapa de URLs e blog
- Requer revisita manual para confirmar ofertas

### URLs para Monitoramento
- DIÁRIO: `https://shieldsec.com.br/cases-drogaria-araujo`
- SEMANAL: `https://shieldsec.com.br`

---

## 7. 3CORP Technology (`3corp.com.br`)

**Tipo:** Integrador de Infraestrutura / Telecom | **Status:** Operacional

### Clientes Identificados (17)

**Cases publicados:** Grupo Casas Bahia, Paschoalotto, Banco do Nordeste (BNB), DETRAN-SP, ARTESP, Prefeitura de Itapevi, CREA-SP, TCE-RJ, Câmara Municipal de Porto Alegre

**Mencionados adicionalmente:** Correios, Via Varejo, CCR Via Sul, Entrevias, Rodovia Tamoios, NWI Telecom, Ministério Público RJ, PMDF, Sodexo, Vogel

### Ofertas Identificadas

| Oferta | Sobreposição Tripla | Confidence |
|---|---|---|
| Segurança de Rede - Firewall (Huawei) | PARCIAL — NGFW | 0.85 |
| Infraestrutura de TI / Servidores | FORA_DE_PORTFOLIO | 0.90 |
| WLAN / Networking / Telecom | FORA_DE_PORTFOLIO | 0.90 |
| Smart Cities | FORA_DE_PORTFOLIO | 0.85 |

### Notas
- 3CORP é principalmente integradora de infraestrutura e telecom Huawei
- Muitos clientes no setor público/governo
- Sobreposição com Tripla limitada a Firewall

---

## 8. ISH Tecnologia (`ish.com.br`)

**Tipo:** Pure Cybersecurity | **Status:** Operacional

### Situação da Coleta
Site apresentou possível conteúdo de template WordPress (nomes fictícios: Justin Novak, Norton Berry). Conteúdo real não coletado com segurança.

### Notas
- ISH é empresa conhecida no mercado brasileiro de cibersegurança
- **Ação requerida:** Visita manual ao site para verificar conteúdo real
- Confidence muito baixa — dados insuficientes para classificação

---

## 9. Actar (`actar.com.br`)

**Tipo:** Pure Cybersecurity | **Status:** Operacional

### Ofertas Identificadas (por URL, conteúdo não carregou)

| Oferta | Sobreposição Tripla | Confidence |
|---|---|---|
| Cyber Security (geral) | INDETERMINADO | 0.60 |
| Zero Trust | PARCIAL — SASE/ZTNA | 0.65 |
| Privacidade e Proteção de Dados | PARCIAL — DLP/LGPD | 0.65 |
| DevSecOps | FORA_DE_PORTFOLIO | 0.70 |
| Consultoria em Cibersegurança | INDETERMINADO | 0.60 |

### Notas
- Página de Cyber Security não renderizou conteúdo (Elementor JS-heavy)
- **Ação requerida:** Re-scrape com `waitFor` para aguardar renderização JS

---

## 10. KPMG Brasil (`kpmg.com/br`)

**Tipo:** BIG4 — Advisory | **Regra:** Não confundir advisory com produto de tecnologia

### Ofertas Identificadas

| Oferta | Classificação | Nota |
|---|---|---|
| Estratégia e Governança Cyber | FORA_DE_PORTFOLIO | Advisory BIG4 |
| Segurança da Transformação | FORA_DE_PORTFOLIO | Advisory BIG4 |
| Defesa Cibernética | INDETERMINADO | Nome sugere SOC mas é consultoria |
| Resposta Cibernética (IR) | PARCIAL | Advisory IR — não produto |
| Segurança em Nuvem | FORA_DE_PORTFOLIO | Advisory |
| **Cyber Managed Services** | **PARCIAL** | ⚠️ Merece investigação — pode incluir SOC operacional |

### Notas
- Reconhecida pelo IDC como líder em consultoria de cibersegurança e em Incident Response
- Cyber Managed Services: investigar se inclui SOC operacional ou é apenas advisory gerenciado

---

## 11. PwC Brasil (`pwc.com.br`)

**Tipo:** BIG4 — Advisory | **Status:** Operacional

- Consultoria de cybersecurity (Digital Trust) — URL 404, requer localização correta
- Foco: auditoria, consultoria tributária e de negócios
- Sobreposição com Tripla: **mínima**
- Monitorar cases de sucesso para identificar clientes em comum: `https://www.pwc.com.br/pt/consultoria/cases-sucesso.html`

---

## 12. Deloitte Brasil (`deloitte.com`)

**Tipo:** BIG4 — Advisory | **Status:** Operacional

- Site bloqueia crawler (apenas 1 URL retornada no mapa)
- Sobreposição com Tripla: **mínima** (advisory, não produto)
- **Ação requerida:** Visita manual ou busca específica por páginas de cybersecurity Brasil

---

## 13. EY Brasil (`ey.com/pt_br`)

**Tipo:** BIG4 — Advisory | **Status:** Operacional

### Cliente Identificado (1)
| Cliente | Case |
|---|---|
| Banco do Brasil | Governança de IA com IBM e EY |

### Notas
- Cybersecurity URL retornou 404 — EY tem consultoria de cyber mas página BR não encontrada
- Forte foco em IA (AI Sentiment Survey 2026, Agentes de IA)
- Aliança com Microsoft e IBM para IA
- Sobreposição com Tripla: **mínima**

---

## 14. Solo Network (`solo-network.com.br`)

**Tipo:** Microsoft Partner / Integrador | **Status:** Operacional

### Cliente Identificado (1)
| Cliente | Case |
|---|---|
| Copel | Migração Microsoft 365 |

### Notas
- Microsoft Partner of the Year 2020
- Foco: licenciamento e implementação Microsoft — não cibersegurança pura
- Sobreposição com Tripla: **baixa**

---

## 15. Tecno-IT (`tecnoit.com.br`)

**Tipo:** Smart City / TI Municipal | **Status:** ⚠️ Em recuperação judicial

### Clientes Identificados (2)
- Prefeitura de Boa Vista (RR)
- Prefeitura de Aparecida de Goiânia (GO)

### Notas
- Foco em smart cities — fora do portfólio Tripla
- Situação financeira comprometida (recuperação judicial)
- **Prioridade de monitoramento: BAIXA**

---

## Recomendações de Ação

### ⚡ Ações imediatas (antes de aprovar baseline)

1. **ISH**: Visitar site manualmente — conteúdo coletado parece ser template demo
2. **Actar**: Re-scrape com renderização JS (`waitFor: 3000`) — página não carregou
3. **Tempest**: Coletar lista de clientes/parceiros de `/parceiros`
4. **TIVIT**: Scrape direto de `https://tivit.com/cybersecurity/` — URL correta diferente da mapeada
5. **Shield Security**: Processar conteúdo completo da homepage (85k chars)
6. **KPMG**: Investigar `https://kpmg.com/br/pt/services/advisory/risk-consulting/cyber-security/cyber-managed-services.html`

### 📊 Concorrentes mais relevantes para Tripla

**Alta ameaça (portfólio diretamente competitivo):**
- **iT.eam** — SOC, EDR, DLP, Pentest, Compliance com certificação mundial
- **9net** — SOC/MSS, EDR, IAM, WAF, ZTNA/SSE — portfólio muito completo
- **TIVIT** — SOC, MDR, IAM, GRC, Red Team em empresa de grande porte

**Ameaça média:**
- **Tempest** — líder em Pentest no Brasil
- **BHS** — SOC 24x7 focado Microsoft com clientes enterprise verificados

**Monitoramento básico (baixa ameaça direta):**
- 3CORP, ISH, Actar, Shield Security
- BIG4 (KPMG, PwC, Deloitte, EY) — monitorar clientes em comum
- Solo Network, Tecno-IT

---

## Próximos Passos

1. **Revisar** este relatório e os JSONs em `baseline/candidates/`
2. **Aprovar** ou **rejeitar** cada entrada — mover aprovadas para `baseline/approved/`
3. **Ativar monitoramento** (via `monitor.py`) somente após aprovação do baseline
4. **NÃO ativar** alertas por email — `ALERT_EMAIL_ENABLED=false` permanece até aprovação

---

*Gerado por Claude Code (claude-sonnet-4-6) em 2026-08-18*  
*Método: Firecrawl MCP (map + scrape) + análise direta — zero chamadas LLM para tarefas determinísticas*
