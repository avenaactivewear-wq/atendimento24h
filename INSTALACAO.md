# Atendente24h - Guia de Instalacao e Operacao

Data: 28/Mar/2026
Versao: 1.0 - Operacao Manual com Automacao Parcial

---

## ESTADO ATUAL DO PRODUTO

**O que funciona hoje:**
- Landing page publicada em atendente24h.com/landing/
- 3 planos ativos no Kiwify com checkout funcionando
- Webhook Kiwify -> n8n ativa/suspende cliente na DataTable automaticamente
- Onboarding coletando todos os dados necessarios do cliente
- Admin com interface visual (dados mock, sem backend real ainda)

**O que e manual por enquanto (Eduardo faz):**
- Receber os dados do onboarding
- Criar instancia no Evolution API
- Configurar workflow n8n do cliente
- Avisar cliente que esta ativo

**O que falta para automacao total:**
- VPS em producao (n8n + Evolution API)
- Webhook de onboarding processando dados automaticamente
- Workflow n8n generalizando o bot Amanda por tenant

---

## FLUXO A: AUTOMATICO (ja funciona)

### Kiwify -> n8n -> DataTable

Quando um cliente compra qualquer plano no Kiwify:

1. Kiwify dispara webhook POST para:
   `https://crista-oleographic-frightfully.ngrok-free.dev/webhook/atendente24h-kiwify`

2. Workflow n8n ID `cULrEMc5mB2wACeb` processa e:
   - **purchase_approved** -> cria linha na DataTable com status=ativo
   - **subscription_canceled** -> atualiza status=cancelado
   - **charge_failed** -> atualiza status=suspenso
   - **subscription_reactivated** -> atualiza status=ativo

3. DataTable ID `sApbmIJ2qeEXWOq0` recebe os dados:
   - email, nome, whatsapp (vazio ate onboarding), plano
   - limite_mensagens (500/2500/15000 conforme plano)
   - mensagens_usadas=0, status, subscription_id, produto_id, data_ativacao

4. Cliente recebe email automatico de confirmacao do Kiwify

**ATENCAO:** A URL do webhook via ngrok e TEMPORARIA. Quando subir VPS, atualizar no Kiwify.

---

## FLUXO B: MANUAL EDUARDO (para cada novo cliente)

### Checklist pos-compra

Assim que um cliente comprar, Eduardo recebe notificacao do Kiwify. Execute nesta ordem:

**B1. Conferir DataTable**
- Abrir n8n -> DataTable `sApbmIJ2qeEXWOq0`
- Verificar se o registro foi criado com status=ativo
- Se nao criou: verificar ngrok ativo, reprocessar webhook manualmente

**B2. Aguardar dados do onboarding**
- Cliente e direcionado para atendente24h.com/onboarding/ pelo email Kiwify
- Onboarding envia os dados para o webhook `atendente24h-onboarding` no n8n
- Dados coletados: email, whatsapp (numero sem DDD), nome_atendente, nome_empresa, segmento, tom_de_voz, horario, contexto

**B3. Criar instancia no Evolution API**

```
POST https://[URL-EVOLUTION-API]/instance/create
Headers: apikey: [API_KEY]

Body:
{
  "instanceName": "cliente_[whatsapp]",
  "token": "[gerar token unico]",
  "number": "[numero_whatsapp_com_55]",
  "qrcode": true,
  "integration": "WHATSAPP-BAILEYS"
}
```

- Copiar o QR code gerado
- Enviar QR code para o cliente por email com instrucoes para escanear
- Aguardar confirmacao de conexao

**B4. Configurar workflow n8n do cliente**

Duplicar o workflow base do bot Amanda e configurar:
- Variavel `INSTANCE_NAME` = instanceName criado acima
- Variavel `SYSTEM_PROMPT` = contexto preenchido no onboarding
- Variavel `TOM_DE_VOZ` = tom selecionado pelo cliente
- Variavel `NOME_EMPRESA` = nome da empresa
- Variavel `HORARIO_HUMANO` = horario de atendimento humano
- Variavel `LIMITE_MSGS` = limite conforme plano (500/2500/15000)
- Variavel `EMAIL_CLIENTE` = email para alertas de limite
- Ativar o workflow

**B5. Atualizar DataTable com dados do onboarding**

Abrir registro do cliente na DataTable e preencher:
- whatsapp = numero coletado no onboarding
- nome = nome da empresa
- workflow_id = ID do workflow criado no passo B4

**B6. Testar**

- Enviar mensagem de teste para o numero do cliente via outro celular
- Verificar que o bot responde de forma coerente com o contexto
- Verificar que o n8n esta incrementando mensagens_usadas

**B7. Avisar cliente**

Enviar WhatsApp ou email para o cliente:
> "Seu atendente [nome] esta ativo! Faca um teste agora enviando uma mensagem para [numero]."

---

## FLUXO C: EXPERIENCIA DO CLIENTE

1. Cliente acessa atendente24h.com e escolhe um plano
2. Paga no Kiwify (cartao ou PIX)
3. Recebe email do Kiwify com confirmacao e link para atendente24h.com/onboarding/
4. No onboarding, preenche 4 passos:
   - Passo 1: email da conta + numero do WhatsApp que sera atendido
   - Passo 2: nome do atendente, tom de voz, nome empresa, segmento, horario
   - Passo 3: contexto do negocio + documentos de referencia (opcional)
   - Passo 4: revisao e envio
5. Eduardo recebe notificacao e executa o fluxo B acima
6. Em ate 24h o cliente recebe QR code por email para conectar o WhatsApp
7. Apos escanear, o bot esta ativo

**SLA atual:** 24h para ativacao apos onboarding concluido.

---

## FLUXO D: GESTAO DE LIMITES DE MENSAGENS

O workflow n8n do cliente deve verificar a DataTable antes de cada resposta:

```javascript
// Pseudocodigo do check de limite no n8n
const cliente = await buscarCliente(email_ou_whatsapp)
const pct = cliente.mensagens_usadas / cliente.limite_mensagens

if (pct >= 1.0) {
  // Bot para de responder
  return "Ola! Seu plano atingiu o limite de mensagens deste mes. Para continuar sendo atendido, faca upgrade em: [link_upgrade]"
}

if (pct >= 0.8 && !cliente.alerta_80_enviado) {
  // Enviar email de alerta para o cliente
  enviarEmail(cliente.email, "Voce usou 80% do seu limite mensal")
  marcarAlertaEnviado(cliente.id)
}

// Processar mensagem normalmente
incrementarContador(cliente.id)
```

**Links de upgrade por plano:**
- Basico -> Recomendado: https://pay.kiwify.com.br/NoT2pJ2
- Recomendado -> Pro: https://pay.kiwify.com.br/ZHeaXQC

**Reset mensal:** n8n deve zerar mensagens_usadas no dia do aniversario da assinatura (usar campo data_ativacao para calcular).

---

## FLUXO E: CANCELAMENTO E INADIMPLENCIA

**Totalmente automatico via webhook Kiwify:**

- `subscription_canceled` -> status=cancelado -> bot para de responder imediatamente
- `charge_failed` (atraso) -> status=suspenso -> bot para de responder
- `subscription_reactivated` -> status=ativo -> bot volta a responder

**O workflow n8n valida o status antes de cada resposta.** Se status != "ativo", retorna mensagem padrao:

> "Oi! Identificamos uma pendencia na sua assinatura do Atendente24h. Para regularizar, acesse: atendente24h.com ou entre em contato com suporte."

**Para reativar manualmente** (caso cliente resolva direto com Eduardo):
- Atualizar status na DataTable para "ativo"
- N8n ja passa a responder na proxima mensagem

---

## FLUXO F: DEPLOY EM VPS (PENDENTE)

Quando subir o servidor de producao, executar nesta ordem:

**F1. Provisionar VPS**
- Hetzner CX21 (2vCPU, 4GB RAM) ou DigitalOcean Basic $12/mes
- Ubuntu 22.04 LTS
- Abrir portas: 80, 443, 5678 (n8n), 8080 (Evolution API)

**F2. Instalar dependencias**
```bash
# Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**F3. Subir n8n**
```yaml
# docker-compose.yml
version: '3.8'
services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=n8n.atendente24h.com
      - N8N_PORT=5678
      - N8N_PROTOCOL=https
      - WEBHOOK_URL=https://n8n.atendente24h.com
      - N8N_ENCRYPTION_KEY=[gerar chave aleatoria]
    volumes:
      - ~/.n8n:/home/node/.n8n
```

**F4. Subir Evolution API**
```yaml
  evolution-api:
    image: atendai/evolution-api:latest
    restart: always
    ports:
      - "8080:8080"
    environment:
      - AUTHENTICATION_API_KEY=[api_key_forte]
      - DATABASE_PROVIDER=sqlite
    volumes:
      - evolution_data:/evolution/instances
```

**F5. Configurar SSL (Certbot)**
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d n8n.atendente24h.com -d api.atendente24h.com
```

**F6. Migrar workflows do n8n local**
- Exportar todos os workflows: n8n -> Settings -> Export
- Importar no n8n do VPS
- Recriar credenciais (nao sao exportadas por seguranca)

**F7. Atualizar URLs no Kiwify**
- Login em kiwify.com.br -> Produtos -> cada produto -> Webhooks
- Substituir URL ngrok por: `https://n8n.atendente24h.com/webhook/atendente24h-kiwify`
- Fazer compra de teste para validar

**F8. Desligar ngrok local**
- Nao desligar antes de validar tudo no VPS
- Testar pelo menos: compra aprovada, cancelamento, onboarding

---

## INFORMACOES DE REFERENCIA

### Produtos Kiwify
| Plano | Preco | Limite Msgs | Produto ID | Link Checkout |
|-------|-------|-------------|------------|---------------|
| Basico | R$197/mes | 500 | d1d17330-2ac3-11f1-bdcc-fbd262fdb101 | https://pay.kiwify.com.br/6ahByUz |
| Recomendado | R$397/mes | 2.500 | 233f8cc0-2ac4-11f1-885c-092676e2c6c6 | https://pay.kiwify.com.br/NoT2pJ2 |
| Pro | R$797/mes | 15.000 | 8c6f3150-2ac4-11f1-ad58-d73905e62c75 | https://pay.kiwify.com.br/ZHeaXQC |

### n8n Workflows
| ID | Nome | Status |
|----|------|--------|
| cULrEMc5mB2wACeb | Licencas Kiwify | ATIVO |
| sApbmIJ2qeEXWOq0 | DataTable Clientes | ATIVO |
| KTRA1gSjkACGAJJv | Onboarding Webhook | ATIVO |

PENDENCIA: no workflow KTRA1gSjkACGAJJv, node "Montar Alerta Eduardo", trocar o campo phone_eduardo (5511999999999) pelo numero real de Eduardo com DDI 55.

### URLs atuais (ngrok temporario)
- Webhook Kiwify: `https://crista-oleographic-frightfully.ngrok-free.dev/webhook/atendente24h-kiwify`
- Webhook Onboarding: `https://crista-oleographic-frightfully.ngrok-free.dev/webhook/atendente24h-onboarding`

### Plano x limite_mensagens na DataTable
```
produto_id d1d17330 -> limite_mensagens = 500    (Basico)
produto_id 233f8cc0 -> limite_mensagens = 2500   (Recomendado)
produto_id 8c6f3150 -> limite_mensagens = 15000  (Pro)
```

---

## CHECKLIST PARA COMECAR A VENDER HOJE

### Antes de aceitar o primeiro cliente:

- [ ] Confirmar ngrok rodando localmente (`ngrok http 5678`)
- [ ] Testar webhook Kiwify com compra de R$1 (criar produto teste)
- [ ] Verificar que DataTable recebe o registro corretamente
- [ ] Criar workflow n8n base do bot (baseado no bot Amanda) pronto para duplicar
- [ ] Criar template de email para enviar QR code ao cliente
- [ ] Definir numero de WhatsApp de suporte para enviar ao cliente apos ativacao
- [ ] Adicionar link do onboarding no email de confirmacao do Kiwify

### Limitacoes atuais que o cliente precisa saber (comunicar na LP ou pos-venda):
- Ativacao em ate 24h uteis (manual por enquanto)
- Bot responde automaticamente, transferencia humana por horario definido
- Sem painel self-service por enquanto (admin e uso interno de Eduardo)

---

## PROXIMOS PASSOS PARA ESCALAR

1. **Semana 1:** Criar workflow n8n de onboarding automatico (recebe webhook, cria instancia Evolution API, ativa bot) - elimina o fluxo manual B
2. **Semana 2:** Subir VPS, migrar tudo, encerrar ngrok
3. **Semana 3:** Conectar admin real com DataTable via API n8n
4. **Semana 4:** Self-service: cliente acessa painel, ve uso, faz upgrade sozinho
