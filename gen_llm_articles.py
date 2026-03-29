#!/usr/bin/env python3
"""
gen_llm_articles.py — Gera posts SEO com Ollama local (zero custo de API)
Uso: python3 gen_llm_articles.py [--limit 50] [--model llama3.2]
Resumavel: pula arquivos ja existentes automaticamente
"""

import os, json, time, argparse, requests, unicodedata, re
from datetime import datetime

BLOG_DIR = "/Users/eduardoarantes/agentes/atendimento24h/blog"
OLLAMA_URL = "http://localhost:11434/api/generate"
SITE_URL = "https://atendente24h.com"
import random as _random
from datetime import date as _date, timedelta as _timedelta

def _random_date():
    """Data aleatoria nos ultimos 6 meses ate hoje."""
    today = _date(2026, 3, 29)
    delta = _random.randint(0, 180)
    d = today - _timedelta(days=delta)
    meses = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    return f"{d.day} {meses[d.month-1]} {d.year}"

# ─── SEGMENTOS ────────────────────────────────────────────────────────────────
SEGMENTS = [
    # slug, nome_display, setor
    ("restaurante",           "Restaurante",               "Alimentacao"),
    ("delivery",              "Delivery",                  "Alimentacao"),
    ("pizzaria",              "Pizzaria",                  "Alimentacao"),
    ("hamburgueria",          "Hamburgueria",              "Alimentacao"),
    ("lanchonete",            "Lanchonete",                "Alimentacao"),
    ("sushi",                 "Restaurante de Sushi",      "Alimentacao"),
    ("cafeteria",             "Cafeteria",                 "Alimentacao"),
    ("doceria",               "Doceria",                   "Alimentacao"),
    ("confeitaria",           "Confeitaria",               "Alimentacao"),
    ("marmitaria",            "Marmitaria",                "Alimentacao"),
    ("ifood",                 "Loja no iFood",             "Delivery Apps"),
    ("uber-eats",             "Loja no Uber Eats",         "Delivery Apps"),
    ("rappi",                 "Loja no Rappi",             "Delivery Apps"),
    ("clinica-medica",        "Clinica Medica",            "Saude"),
    ("consultorio-medico",    "Consultorio Medico",        "Saude"),
    ("dentista",              "Clinica Odontologica",      "Saude"),
    ("psicologo",             "Psicologo",                 "Saude Mental"),
    ("psiquiatra",            "Clinica de Psiquiatria",    "Saude Mental"),
    ("fisioterapeuta",        "Clinica de Fisioterapia",   "Saude"),
    ("nutricionista",         "Consultorio de Nutricao",   "Saude"),
    ("dermatologista",        "Clinica de Dermatologia",   "Saude"),
    ("ortopedista",           "Clinica de Ortopedia",      "Saude"),
    ("laboratorio",           "Laboratorio de Exames",     "Saude"),
    ("veterinaria",           "Clinica Veterinaria",       "Pet"),
    ("pet-shop",              "Pet Shop",                  "Pet"),
    ("banho-tosa",            "Studio de Banho e Tosa",    "Pet"),
    ("salao-beleza",          "Salao de Beleza",           "Beleza"),
    ("barbearia",             "Barbearia",                 "Beleza"),
    ("manicure",              "Estudio de Manicure",       "Beleza"),
    ("clinica-estetica",      "Clinica Estetica",          "Beleza"),
    ("studio-maquiagem",      "Studio de Maquiagem",       "Beleza"),
    ("micropigmentacao",      "Studio de Micropigmentacao","Beleza"),
    ("tatuagem",              "Studio de Tatuagem",        "Beleza"),
    ("clinica-capilar",       "Clinica Capilar",           "Beleza"),
    ("spa",                   "Spa e Centro de Bem-Estar", "Beleza"),
    ("academia",              "Academia",                  "Fitness"),
    ("personal-trainer",      "Personal Trainer",          "Fitness"),
    ("studio-pilates",        "Studio de Pilates",         "Fitness"),
    ("crossfit",              "Box de CrossFit",           "Fitness"),
    ("yoga",                  "Studio de Yoga",            "Fitness"),
    ("natacao",               "Escola de Natacao",         "Fitness"),
    ("danca",                 "Escola de Danca",           "Fitness"),
    ("zumba",                 "Aulas de Zumba",            "Fitness"),
    ("imobiliaria",           "Imobiliaria",               "Imoveis"),
    ("corretor-imoveis",      "Corretor de Imoveis",       "Imoveis"),
    ("construtora",           "Construtora",               "Imoveis"),
    ("administradora-imoveis","Administradora de Imoveis", "Imoveis"),
    ("advogado",              "Escritorio de Advocacia",   "Juridico"),
    ("contador",              "Escritorio Contabil",       "Financeiro"),
    ("consultor-financeiro",  "Consultoria Financeira",    "Financeiro"),
    ("corretora-seguros",     "Corretora de Seguros",      "Financeiro"),
    ("escola",                "Escola",                    "Educacao"),
    ("curso-online",          "Plataforma de Curso Online","Educacao"),
    ("escola-idiomas",        "Escola de Idiomas",         "Educacao"),
    ("faculdade",             "Faculdade e Instituto",     "Educacao"),
    ("autoescola",            "Autoescola",                "Educacao"),
    ("farmacia",              "Farmacia",                  "Varejo"),
    ("drogaria",              "Drogaria",                  "Varejo"),
    ("loja-roupas",           "Loja de Roupas",            "Varejo"),
    ("loja-calcados",         "Loja de Calcados",          "Varejo"),
    ("loja-moveis",           "Loja de Moveis",            "Varejo"),
    ("loja-presentes",        "Loja de Presentes",         "Varejo"),
    ("papelaria",             "Papelaria",                 "Varejo"),
    ("ecommerce",             "Loja Virtual",              "E-commerce"),
    ("dropshipping",          "Loja Dropshipping",         "E-commerce"),
    ("marketplace",           "Vendedor em Marketplace",   "E-commerce"),
    ("oficina-mecanica",      "Oficina Mecanica",          "Automotivo"),
    ("concessionaria",        "Concessionaria",            "Automotivo"),
    ("lava-rapido",           "Lava-Rapido",               "Automotivo"),
    ("hotel",                 "Hotel",                     "Turismo"),
    ("pousada",               "Pousada",                   "Turismo"),
    ("agencia-viagem",        "Agencia de Viagem",         "Turismo"),
    ("airbnb",                "Anfitrao de Airbnb",        "Turismo"),
    ("buffet-eventos",        "Buffet e Eventos",          "Eventos"),
    ("fotografo",             "Fotografo e Videomaker",    "Servicos"),
    ("arquiteto",             "Arquiteto",                 "Servicos"),
    ("coach",                 "Coach e Mentor",            "Servicos"),
    ("consultoria-rh",        "Consultoria de RH",         "Servicos"),
    ("agencia-marketing",     "Agencia de Marketing",      "Servicos"),
    ("sindico",               "Sindico e Adm Condominio",  "Servicos"),
    ("energia-solar",         "Instalador de Energia Solar","Servicos"),
    ("reforma-residencial",   "Reformas e Construcao",     "Servicos"),
    ("jardinagem",            "Jardinagem e Paisagismo",   "Servicos"),
    ("transporte",            "Empresa de Transporte",     "Logistica"),
]

# ─── INTENCOES DE BUSCA ───────────────────────────────────────────────────────
# Cada intent gera um artigo diferente por segmento
# (slug_prefix, title_template, focus_kw_template, description_template)
INTENTS = [
    (
        "chatbot-whatsapp-para",
        "Chatbot WhatsApp para {nome}: Guia Completo 2026",
        "chatbot whatsapp para {nome_lower}",
        "Como usar chatbot no WhatsApp para {nome_lower}: configuracao, beneficios e resultados reais.",
    ),
    (
        "automacao-whatsapp-para",
        "Automacao de WhatsApp para {nome}: Como Funciona na Pratica",
        "automacao whatsapp {nome_lower}",
        "Passo a passo para automatizar o atendimento pelo WhatsApp no seu {nome_lower} e atender clientes 24h.",
    ),
    (
        "ia-atendimento-para",
        "IA de Atendimento para {nome}: Vale a Pena em 2026?",
        "ia atendimento {nome_lower} whatsapp",
        "Analise completa sobre usar inteligencia artificial no atendimento de {nome_lower}: custos, retorno e como comecar.",
    ),
    (
        "atendente-virtual-para",
        "Atendente Virtual para {nome}: Tudo que Voce Precisa Saber",
        "atendente virtual {nome_lower}",
        "Como um atendente virtual pode transformar o atendimento do seu {nome_lower} e aumentar conversoes.",
    ),
    (
        "como-automatizar-atendimento",
        "Como Automatizar o Atendimento do seu {nome} pelo WhatsApp",
        "como automatizar atendimento {nome_lower}",
        "Guia pratico para donos de {nome_lower} que querem automatizar respostas no WhatsApp sem complicacao.",
    ),
    (
        "whatsapp-ia-para",
        "WhatsApp com IA para {nome}: Do Zero ao Primeiro Atendimento Automatico",
        "whatsapp ia {nome_lower}",
        "Como configurar WhatsApp com inteligencia artificial no seu {nome_lower} em menos de um dia.",
    ),
    (
        "quanto-custa-chatbot-para",
        "Quanto Custa um Chatbot de WhatsApp para {nome}?",
        "quanto custa chatbot whatsapp {nome_lower}",
        "Comparativo de custos de chatbot WhatsApp para {nome_lower}: opcoes gratuitas, baratas e profissionais.",
    ),
    (
        "melhor-chatbot-para",
        "Melhor Chatbot de WhatsApp para {nome} em 2026",
        "melhor chatbot whatsapp {nome_lower} 2026",
        "Comparamos as principais ferramentas de chatbot para {nome_lower} e escolhemos a melhor custo-beneficio.",
    ),
    (
        "bot-agendamento-para",
        "Bot de Agendamento pelo WhatsApp para {nome}: Como Configurar",
        "bot agendamento whatsapp {nome_lower}",
        "Configure um bot de agendamento automatico no WhatsApp para seu {nome_lower} e reduza faltas e no-shows.",
    ),
    (
        "aumentar-vendas-whatsapp",
        "Como {nome} Aumenta as Vendas Usando IA no WhatsApp",
        "aumentar vendas whatsapp {nome_lower} ia",
        "Estrategias comprovadas para {nome_lower} usar inteligencia artificial no WhatsApp e vender mais.",
    ),
    (
        "responder-clientes-24h",
        "{nome}: Como Responder Clientes 24 Horas por Dia sem Contratar",
        "atender clientes 24h {nome_lower} sem contratar",
        "Como {nome_lower} pode atender clientes 24 horas por dia usando IA, sem custo de funcionario extra.",
    ),
    (
        "perdendo-clientes-por-demora",
        "{nome}: Voce Esta Perdendo Clientes por Demora na Resposta?",
        "perder clientes demora resposta whatsapp {nome_lower}",
        "Como a lentidao no atendimento custa clientes e dinheiro para {nome_lower}, e como resolver com IA.",
    ),
    (
        "substituir-atendente-ia",
        "IA Substitui Atendente Humano no {nome}? A Verdade",
        "ia substitui atendente humano {nome_lower}",
        "Analise honesta sobre o que a IA faz e nao faz no atendimento de {nome_lower}: quando usar e quando nao usar.",
    ),
    (
        "resultados-reais-ia",
        "{nome} com IA no WhatsApp: Resultados Reais de Quem Ja Usa",
        "resultados ia whatsapp {nome_lower}",
        "Dados e casos reais de {nome_lower} que implementaram IA no WhatsApp: aumento de conversoes e reducao de custo.",
    ),
    (
        "erros-ao-automatizar",
        "5 Erros que {nome} Comete ao Automatizar o WhatsApp",
        "erros automatizar whatsapp {nome_lower}",
        "Evite os erros mais comuns que donos de {nome_lower} cometem ao implementar automacao no WhatsApp.",
    ),
    (
        "script-atendimento-whatsapp",
        "Script de Atendimento WhatsApp para {nome}: Exemplos Prontos",
        "script atendimento whatsapp {nome_lower}",
        "Modelos de mensagens e scripts de atendimento prontos para {nome_lower} usar no WhatsApp com ou sem IA.",
    ),
    (
        "ia-segura-para",
        "IA no WhatsApp e Segura para {nome}? Privacidade e LGPD",
        "ia whatsapp seguro {nome_lower} lgpd",
        "Tudo sobre seguranca, privacidade e conformidade com a LGPD ao usar IA no WhatsApp no seu {nome_lower}.",
    ),
    (
        "tempo-de-resposta-whatsapp",
        "Tempo de Resposta no WhatsApp: Como {nome} Pode Responder Mais Rapido",
        "tempo resposta whatsapp {nome_lower}",
        "Por que o tempo de resposta no WhatsApp afeta diretamente as vendas do seu {nome_lower} e como melhorar.",
    ),
    (
        "whatsapp-business-ou-chatbot",
        "WhatsApp Business ou Chatbot IA: Qual Usar no seu {nome}?",
        "whatsapp business vs chatbot ia {nome_lower}",
        "Comparativo entre WhatsApp Business nativo e chatbot com IA para {nome_lower}: diferencas e qual escolher.",
    ),
    (
        "como-funciona-atendente-ia",
        "Como Funciona um Atendente IA no WhatsApp para {nome}",
        "como funciona atendente ia whatsapp {nome_lower}",
        "Explicacao simples de como funciona a inteligencia artificial no atendimento via WhatsApp para {nome_lower}.",
    ),
    (
        "whatsapp-automatico-fim-de-semana",
        "{nome}: Como Atender Clientes no Fim de Semana sem Estar Disponivel",
        "atendimento whatsapp fim de semana {nome_lower} automatico",
        "Como {nome_lower} pode atender clientes no sabado, domingo e feriados de forma automatica com IA.",
    ),
    (
        "reduzir-custo-atendimento",
        "Como {nome} Reduz o Custo de Atendimento com IA no WhatsApp",
        "reduzir custo atendimento {nome_lower} ia",
        "Calcule quanto seu {nome_lower} pode economizar substituindo parte do atendimento humano por IA.",
    ),
    (
        "converter-mais-leads-whatsapp",
        "Como {nome} Converte Mais Leads pelo WhatsApp com IA",
        "converter leads whatsapp {nome_lower}",
        "Tecnicas para aumentar a taxa de conversao de leads no WhatsApp do seu {nome_lower} usando automacao e IA.",
    ),
    (
        "fidelizar-clientes-whatsapp-ia",
        "Como {nome} Fideliza Clientes com Automacao no WhatsApp",
        "fidelizar clientes whatsapp {nome_lower} ia",
        "Estrategias de retencao e fidelizacao de clientes para {nome_lower} usando mensagens automaticas inteligentes.",
    ),
    (
        "configurar-chatbot-em-1-dia",
        "Como Configurar Chatbot no WhatsApp para {nome} em 1 Dia",
        "configurar chatbot whatsapp {nome_lower} rapido",
        "Guia rapido para {nome_lower} ter um chatbot funcionando no WhatsApp hoje, sem precisar de tecnico.",
    ),
    (
        "nao-perder-mensagem-whatsapp",
        "{nome}: Como Nunca Mais Perder uma Mensagem no WhatsApp",
        "nao perder mensagem whatsapp {nome_lower}",
        "Como {nome_lower} pode garantir que nenhuma mensagem de cliente fique sem resposta no WhatsApp.",
    ),
    (
        "whatsapp-ia-para-pequenas-empresas",
        "IA no WhatsApp para Pequenos {nome}s: Por Onde Comecar",
        "ia whatsapp pequeno {nome_lower}",
        "Como pequenos {nome_lower} sem equipe de TI podem implementar IA no WhatsApp de forma simples e barata.",
    ),
    (
        "diferencial-competitivo-ia",
        "Como {nome} Usa IA no WhatsApp como Diferencial Competitivo",
        "diferencial competitivo ia whatsapp {nome_lower}",
        "Por que implementar IA no WhatsApp coloca seu {nome_lower} a frente da concorrencia que ainda usa atendimento manual.",
    ),
    (
        "ganhar-mais-com-whatsapp-ia",
        "Como {nome} Fatura Mais com IA no WhatsApp",
        "faturar mais whatsapp ia {nome_lower}",
        "Como {nome_lower} usa inteligencia artificial no WhatsApp para aumentar ticket medio, recuperar vendas perdidas e crescer.",
    ),
    (
        "casos-de-uso-ia-whatsapp",
        "10 Usos de IA no WhatsApp que Todo {nome} Deveria Conhecer",
        "usos ia whatsapp {nome_lower}",
        "Lista dos principais casos de uso de inteligencia artificial no WhatsApp aplicados a {nome_lower}: do agendamento ao pos-venda.",
    ),
]

# ─── TOPICOS STANDALONE (nao ligados a segmento especifico) ───────────────────
STANDALONE_TOPICS = [
    ("chatbot-e-seguro-para-empresas",
     "Chatbot e Seguro para Empresas? Privacidade e Riscos",
     "chatbot seguro empresas lgpd",
     "Analise sobre seguranca, privacidade e LGPD no uso de chatbots comerciais no WhatsApp."),
    ("ia-substitui-atendente-humano",
     "IA Substitui o Atendente Humano? A Verdade em 2026",
     "ia substitui atendente humano",
     "O que a inteligencia artificial pode e nao pode fazer no lugar de um atendente humano: limites e possibilidades."),
    ("como-funciona-chatbot-ia-whatsapp",
     "Como Funciona um Chatbot com IA no WhatsApp: Explicacao Simples",
     "como funciona chatbot ia whatsapp",
     "Explicacao didatica de como funciona um chatbot com inteligencia artificial no WhatsApp para leigos."),
    ("whatsapp-business-api-o-que-e",
     "WhatsApp Business API: O que E e Para Que Serve",
     "whatsapp business api o que e",
     "Entenda a diferenca entre WhatsApp comum, Business e API, e quando cada um faz sentido para seu negocio."),
    ("tempo-resposta-whatsapp-impacto-vendas",
     "Tempo de Resposta no WhatsApp: Como Impacta Suas Vendas",
     "tempo resposta whatsapp impacto vendas",
     "Dados sobre como a velocidade de resposta no WhatsApp afeta a taxa de conversao de clientes."),
    ("ia-no-atendimento-lgpd",
     "IA no Atendimento e a LGPD: O que sua Empresa Deve Saber",
     "ia atendimento lgpd conformidade",
     "Como garantir conformidade com a LGPD ao usar inteligencia artificial no atendimento ao cliente."),
    ("chatbot-aprende-com-o-tempo",
     "Chatbot Aprende com o Tempo? Como Funciona o Aprendizado",
     "chatbot aprende automaticamente",
     "Como os chatbots com IA evoluem e melhoram com o uso, e o que esperar ao comecar a usar."),
    ("custo-funcionario-atendimento-vs-ia",
     "Funcionario de Atendimento vs IA: Comparativo de Custo Real",
     "custo funcionario atendimento vs ia",
     "Quanto custa um funcionario dedicado ao atendimento versus uma IA no WhatsApp: comparativo detalhado."),
    ("como-treinar-chatbot-para-meu-negocio",
     "Como Treinar um Chatbot para Responder Sobre meu Negocio",
     "como treinar chatbot meu negocio",
     "Passo a passo para configurar e treinar um chatbot com as informacoes especificas do seu negocio."),
    ("atendimento-24h-sem-funcionario",
     "Atender 24h por Dia sem Funcionario: E Possivel com IA?",
     "atender 24h sem funcionario ia",
     "Como empresas de todos os tamanhos conseguem atender clientes 24 horas por dia usando inteligencia artificial."),
    ("erros-comuns-automacao-whatsapp",
     "7 Erros Comuns ao Automatizar o WhatsApp da sua Empresa",
     "erros automacao whatsapp empresas",
     "Evite os erros que mais atrapalham quem tenta automatizar o WhatsApp: da escolha da ferramenta ao tom das mensagens."),
    ("roi-chatbot-whatsapp-como-calcular",
     "Como Calcular o ROI de um Chatbot de WhatsApp",
     "roi chatbot whatsapp como calcular",
     "Metodologia simples para calcular o retorno sobre investimento de um chatbot de WhatsApp no seu negocio."),
    ("whatsapp-ia-madrugada-feriado",
     "Vender de Madrugada e em Feriados com WhatsApp IA",
     "vender madrugada feriado whatsapp ia",
     "Como empresas usam IA no WhatsApp para capturar vendas fora do horario comercial, quando a concorrencia dorme."),
    ("diferenca-chatbot-atendente-ia",
     "Diferenca entre Chatbot e Atendente IA: Qual Escolher?",
     "diferenca chatbot atendente ia",
     "Entenda a diferenca tecnica e pratica entre chatbot simples e atendente com IA real, e qual e melhor para seu negocio."),
    ("whatsapp-ia-para-solopreneur",
     "WhatsApp com IA para Solopreneur e Autonomo: Vale a Pena?",
     "whatsapp ia solopreneur autonomo",
     "Como profissionais autonomos e solopreneurs usam IA no WhatsApp para escalar o atendimento sem contratar."),
    ("metricas-atendimento-whatsapp",
     "Metricas de Atendimento no WhatsApp: O que Acompanhar",
     "metricas atendimento whatsapp",
     "Quais indicadores de atendimento no WhatsApp toda empresa deve monitorar e como melhorar cada um."),
    ("resposta-automatica-whatsapp-profissional",
     "Como Criar Respostas Automaticas Profissionais no WhatsApp",
     "resposta automatica whatsapp profissional",
     "Modelos e tecnicas para criar respostas automaticas que parecem humanas e convertem clientes no WhatsApp."),
    ("ia-atendimento-pequeno-negocio",
     "IA de Atendimento para Pequenos Negocios: Por Onde Comecar",
     "ia atendimento pequeno negocio whatsapp",
     "Guia para donos de pequenos negocios que querem comecar a usar IA no atendimento sem investimento alto."),
    ("whatsapp-business-recursos-gratuitos",
     "WhatsApp Business: Recursos Gratuitos que Poucos Usam",
     "whatsapp business recursos gratuitos",
     "Funcionalidades do WhatsApp Business que a maioria das empresas ignora mas que podem melhorar muito o atendimento."),
    ("como-escalar-atendimento-sem-contratar",
     "Como Escalar o Atendimento sem Contratar Mais Funcionarios",
     "escalar atendimento sem contratar funcionarios",
     "Estrategias para aumentar a capacidade de atendimento do seu negocio sem elevar os custos com pessoal."),
    ("chatbot-para-geração-de-leads",
     "Chatbot WhatsApp para Geracao de Leads: Como Funciona",
     "chatbot whatsapp geracao leads",
     "Como usar chatbot no WhatsApp para capturar, qualificar e nutrir leads automaticamente."),
    ("whatsapp-ia-cobrança-automatica",
     "Cobranca Automatica pelo WhatsApp com IA: Guia Completo",
     "cobranca automatica whatsapp ia",
     "Como automatizar a cobranca de clientes pelo WhatsApp de forma eficiente e sem constrangimentos."),
    ("pesquisa-satisfacao-whatsapp-automatica",
     "Pesquisa de Satisfacao Automatica pelo WhatsApp: Como Fazer",
     "pesquisa satisfacao whatsapp automatica",
     "Como enviar pesquisas de satisfacao automaticas pelo WhatsApp e usar os dados para melhorar o negocio."),
    ("integrar-chatbot-crm",
     "Como Integrar seu Chatbot WhatsApp com CRM",
     "integrar chatbot whatsapp crm",
     "Passo a passo para conectar seu chatbot de WhatsApp a um CRM e centralizar o historico dos clientes."),
    ("mensagem-ausente-whatsapp-profissional",
     "Mensagem de Ausencia Profissional no WhatsApp: Exemplos",
     "mensagem ausencia whatsapp profissional",
     "Exemplos de mensagens de ausencia para WhatsApp Business que informam e ainda convertem clientes."),
    ("chatbot-vs-humano-quando-usar-cada",
     "Chatbot vs Atendente Humano: Quando Usar Cada Um",
     "chatbot vs atendente humano quando usar",
     "Guia pratico para decidir quando usar chatbot e quando transferir para atendimento humano no seu negocio."),
    ("ia-whatsapp-aumentar-ticket-medio",
     "Como IA no WhatsApp Aumenta o Ticket Medio das Vendas",
     "ia whatsapp aumentar ticket medio",
     "Como inteligencia artificial pode sugerir produtos e servicos adicionais e aumentar o valor medio por cliente."),
    ("recuperar-clientes-inativos-whatsapp",
     "Como Recuperar Clientes Inativos pelo WhatsApp com IA",
     "recuperar clientes inativos whatsapp ia",
     "Estrategias para reativar clientes que pararam de comprar usando mensagens automaticas inteligentes no WhatsApp."),
    ("whatsapp-ia-pós-venda",
     "Pos-Venda Automatico no WhatsApp: Como Usar IA para Fidelizar",
     "pos-venda automatico whatsapp ia",
     "Como automatizar o acompanhamento pos-venda no WhatsApp para melhorar satisfacao e gerar indicacoes."),
    ("como-medir-resultado-chatbot",
     "Como Medir os Resultados do seu Chatbot de WhatsApp",
     "como medir resultados chatbot whatsapp",
     "Quais metricas usar para saber se seu chatbot de WhatsApp esta gerando retorno real para o negocio."),
    ("automacao-whatsapp-sem-perder-humanidade",
     "Automacao no WhatsApp sem Perder o Toque Humano",
     "automacao whatsapp sem perder toque humano",
     "Como automatizar o atendimento no WhatsApp mantendo uma comunicacao calorosa e personalizada."),
    ("transferir-ia-para-humano-whatsapp",
     "Como Configurar Transferencia de IA para Atendente Humano no WhatsApp",
     "transferir chatbot ia para humano whatsapp",
     "Boas praticas para configurar a transicao suave entre atendimento automatico e humano no WhatsApp."),
    ("whatsapp-ia-para-franquia",
     "WhatsApp com IA para Redes e Franquias: Como Padronizar o Atendimento",
     "whatsapp ia franquia padronizar atendimento",
     "Como redes de franquia e empresas multi-unidade usam IA para padronizar o atendimento no WhatsApp."),
    ("ia-atendimento-b2b",
     "IA de Atendimento para Empresas B2B no WhatsApp",
     "ia atendimento b2b whatsapp",
     "Como empresas que vendem para outras empresas usam IA no WhatsApp para qualificar leads e agilizar propostas."),
    ("atendente24h-como-funciona",
     "Como Funciona o Atendente24h: Plataforma Completa de IA para WhatsApp",
     "como funciona atendente24h",
     "Guia completo sobre a plataforma Atendente24h: funcionalidades, planos, integrações e como começar."),
    ("atendente24h-vs-contratar-atendente",
     "Atendente24h vs Contratar um Atendente: O que Compensa?",
     "atendente24h vs contratar atendente",
     "Comparativo financeiro e operacional entre usar o Atendente24h e contratar um atendente humano."),
    ("vale-a-pena-chatbot-pequeno-negocio",
     "Vale a Pena um Chatbot para Pequeno Negocio em 2026?",
     "vale a pena chatbot pequeno negocio 2026",
     "Analise honesta sobre quando vale investir em chatbot e quando pode esperar, para donos de pequenos negocios."),
    ("whatsapp-ia-para-mei",
     "WhatsApp com IA para MEI: Automatize o Atendimento sem Gastar Muito",
     "whatsapp ia mei microempreendedor",
     "Como microempreendedores individuais podem usar IA no WhatsApp para profissionalizar o atendimento com custo baixo."),
    ("ia-whatsapp-fora-horario-comercial",
     "Atender Clientes Fora do Horario Comercial com IA no WhatsApp",
     "atender fora horario comercial ia whatsapp",
     "Como capturar e converter clientes que entram em contato fora do expediente usando automacao inteligente."),
    ("nps-whatsapp-automatico",
     "NPS pelo WhatsApp: Como Coletar Feedback Automaticamente",
     "nps whatsapp automatico como fazer",
     "Como implementar coleta automatica de NPS e satisfacao de clientes pelo WhatsApp para melhorar o negocio."),
    ("chatbot-para-black-friday",
     "Chatbot WhatsApp para Black Friday: Como Preparar sua Empresa",
     "chatbot whatsapp black friday",
     "Como preparar seu atendimento via WhatsApp para suportar o volume alto de clientes na Black Friday com chatbot."),
    ("whatsapp-ia-para-lancamento",
     "Como Usar IA no WhatsApp para Lancar um Produto ou Servico",
     "whatsapp ia lancamento produto servico",
     "Estrategia para usar automacao inteligente no WhatsApp durante o lancamento de produtos, capturando e nutrindo leads."),
    ("perguntas-frequentes-chatbot-empresas",
     "Perguntas Frequentes sobre Chatbot de WhatsApp para Empresas",
     "perguntas frequentes chatbot whatsapp empresas",
     "Respondemos as principais duvidas de empresarios sobre chatbots de WhatsApp: seguranca, custo, configuracao e resultados."),
    ("chatbot-ia-tendencias-2026",
     "Tendencias de Chatbot e IA no Atendimento para 2026",
     "tendencias chatbot ia atendimento 2026",
     "O que esperar para chatbots e IA no atendimento ao cliente em 2026: novas funcionalidades e oportunidades."),
    ("como-escrever-mensagens-whatsapp-que-convertem",
     "Como Escrever Mensagens no WhatsApp que Convertem Clientes",
     "mensagens whatsapp que convertem clientes",
     "Tecnicas de copywriting para mensagens de WhatsApp que geram respostas, engajamento e conversoes."),
    ("ia-whatsapp-sem-precisar-de-ti",
     "Como Usar IA no WhatsApp sem Equipe de TI",
     "ia whatsapp sem equipe ti tecnico",
     "Ferramentas e plataformas que permitem implementar IA no WhatsApp sem precisar de conhecimento tecnico ou equipe de TI."),
    ("ganhos-rapidos-chatbot-whatsapp",
     "Ganhos Rapidos ao Implantar Chatbot no WhatsApp da sua Empresa",
     "ganhos rapidos chatbot whatsapp empresa",
     "Os primeiros resultados que voce percebe nos dias seguintes a implantacao de um chatbot no WhatsApp da empresa."),
    ("como-ia-ajuda-no-atendimento-pos-venda",
     "Como a IA Ajuda no Atendimento Pos-Venda pelo WhatsApp",
     "ia atendimento pos-venda whatsapp",
     "Como usar inteligencia artificial para melhorar o acompanhamento pos-venda e reduzir reclamacoes e cancelamentos."),
]

# ─── TEMPLATE HTML ─────────────────────────────────────────────────────────────
def slug_to_url(slug):
    return f"{SITE_URL}/blog/{slug}"

def make_html(slug, title, focus_kw, description, setor, body_html, read_time="6 min", pub_date=None):
    if pub_date is None:
        today = _date(2026, 3, 29)
        d = today - _timedelta(days=_random.randint(0, 180))
        pub_date = d.strftime("%Y-%m-%d")
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} | Atendente24h</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{slug_to_url(slug)}">
<link rel="icon" type="image/svg+xml" href="/favicon.svg">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap">
<script data-goatcounter="https://atendente24h.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
<script type="application/ld+json">
{{"@context":"https://schema.org","@type":"Article","headline":"{title}","description":"{description}","url":"{slug_to_url(slug)}","datePublished":"{pub_date}","dateModified":"{pub_date}","author":{{"@type":"Organization","name":"Atendente24h","url":"{SITE_URL}"}},"publisher":{{"@type":"Organization","name":"Atendente24h","url":"{SITE_URL}","logo":{{"@type":"ImageObject","url":"{SITE_URL}/favicon.svg"}}}},"breadcrumb":{{"@type":"BreadcrumbList","itemListElement":[{{"@type":"ListItem","position":1,"name":"Inicio","item":"{SITE_URL}"}},{{"@type":"ListItem","position":2,"name":"Blog","item":"{SITE_URL}/blog"}},{{"@type":"ListItem","position":3,"name":"{title}","item":"{slug_to_url(slug)}"}}]}}}}
</script>
<style>
*,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
:root{{--green:#25D366;--bg:#080808;--surface:#0f0f0f;--card:#141414;--border:rgba(255,255,255,0.08);--border-green:rgba(37,211,102,0.25);--text:#fff;--text2:#a1a1aa;--text3:#52525b;--radius:12px}}
body{{background:var(--bg);color:var(--text);font-family:'Plus Jakarta Sans',system-ui,sans-serif;font-size:16px;line-height:1.7;-webkit-font-smoothing:antialiased}}
a{{color:var(--green);text-decoration:none}}a:hover{{text-decoration:underline}}
.nav-wrap{{border-bottom:1px solid var(--border);padding:0 24px}}
nav{{max-width:900px;margin:0 auto;display:flex;align-items:center;justify-content:space-between;height:60px}}
.logo{{font-weight:800;font-size:18px;color:#fff;text-decoration:none}}
.nav-cta{{background:var(--green);color:#000;padding:8px 18px;border-radius:8px;font-weight:700;font-size:14px;text-decoration:none}}
.nav-cta:hover{{text-decoration:none;opacity:.9}}
.container{{max-width:760px;margin:0 auto;padding:48px 24px 80px}}
.breadcrumb{{font-size:13px;color:var(--text3);margin-bottom:32px}}
.breadcrumb a{{color:var(--text3)}}
.tag{{background:rgba(37,211,102,.15);color:var(--green);font-size:12px;font-weight:700;padding:4px 12px;border-radius:20px;display:inline-block;margin-bottom:16px}}
h1{{font-size:clamp(26px,4vw,40px);font-weight:800;letter-spacing:-1px;line-height:1.2;margin-bottom:16px}}
.meta{{color:var(--text3);font-size:14px;margin-bottom:40px;padding-bottom:24px;border-bottom:1px solid var(--border)}}
.content h2{{font-size:22px;font-weight:700;margin:36px 0 12px;letter-spacing:-.5px}}
.content p{{color:#d4d4d8;margin-bottom:16px}}
.content ul,.content ol{{color:#d4d4d8;padding-left:24px;margin-bottom:16px}}
.content li{{margin-bottom:8px}}
.content strong{{color:#fff}}
.highlight-box{{background:rgba(37,211,102,.07);border:1px solid var(--border-green);border-radius:12px;padding:20px 24px;margin:24px 0}}
.highlight-box p{{color:#d4d4d8;margin:0}}
.cta-box{{background:var(--card);border:1px solid var(--border-green);border-radius:16px;padding:32px;text-align:center;margin:48px 0}}
.cta-box h3{{font-size:22px;font-weight:800;margin-bottom:8px}}
.cta-box p{{color:var(--text2);margin-bottom:24px}}
.btn-cta{{background:var(--green);color:#000;padding:14px 32px;border-radius:10px;font-weight:800;font-size:16px;display:inline-block;text-decoration:none}}
.btn-cta:hover{{opacity:.9;text-decoration:none}}
footer{{border-top:1px solid var(--border);padding:32px 24px;text-align:center;color:var(--text3);font-size:13px}}
footer a{{color:var(--text3)}}
@media(max-width:640px){{.container{{padding:32px 16px 64px}}h1{{font-size:26px}}}}
</style>
</head>
<body>
<div class="nav-wrap">
  <nav>
    <a href="{SITE_URL}" class="logo">Atendente24h</a>
    <a href="{SITE_URL}/#planos" class="nav-cta">Ver planos</a>
  </nav>
</div>
<div class="container">
  <div class="breadcrumb"><a href="{SITE_URL}">Inicio</a> &rsaquo; <a href="{SITE_URL}/blog">Blog</a> &rsaquo; {title}</div>
  <span class="tag">{setor}</span>
  <h1>{title}</h1>
  <div class="meta">{_random_date()} &middot; {read_time} de leitura</div>
  <div class="content">
{body_html}
  </div>
  <div class="cta-box">
    <h3>Pronto para automatizar seu atendimento?</h3>
    <p>Junte-se a centenas de empresas que ja usam o Atendente24h para atender clientes 24h pelo WhatsApp.</p>
    <a href="{SITE_URL}/#planos" class="btn-cta">Comecar agora &rarr;</a>
  </div>
</div>
<footer>
  <p>Atendente24h &copy; 2026 &mdash; Atendimento automatizado com IA para PMEs brasileiras</p>
  <p style="margin-top:8px"><a href="{SITE_URL}">{SITE_URL}</a></p>
</footer>
</body>
</html>"""

# ─── GERACAO DE TOPICOS ────────────────────────────────────────────────────────
def build_topic_list():
    topics = []
    seen_slugs = set()

    # Combinacoes segmento x intent
    for seg_slug, seg_nome, seg_setor in SEGMENTS:
        for intent_prefix, title_tpl, kw_tpl, desc_tpl in INTENTS:
            slug = f"{intent_prefix}-{seg_slug}"
            if slug in seen_slugs:
                continue
            seen_slugs.add(slug)
            title = title_tpl.format(nome=seg_nome, nome_lower=seg_nome.lower())
            kw = kw_tpl.format(nome=seg_nome, nome_lower=seg_nome.lower())
            desc = desc_tpl.format(nome=seg_nome, nome_lower=seg_nome.lower())
            topics.append((slug, title, kw, desc, seg_setor))

    # Topicos standalone
    for slug, title, kw, desc in STANDALONE_TOPICS:
        if slug not in seen_slugs:
            seen_slugs.add(slug)
            topics.append((slug, title, kw, desc, "Estrategia"))

    return topics

# ─── CHAMADA OLLAMA ────────────────────────────────────────────────────────────
def clean_body(html):
    """Converte markdown residual para HTML e remove artefatos."""
    import re
    # **texto** -> <strong>texto</strong>
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    # *texto* -> <em>texto</em>
    html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
    # Remove blocos de codigo ```
    html = re.sub(r'```[\s\S]*?```', '', html)
    # Remove linhas que comecam com # (headings markdown)
    html = re.sub(r'^#{1,6}\s+(.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    # Converte - item de lista solta para <li> se nao estiver dentro de <ul>
    html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    # Remove tags html/head/body se o modelo incluiu
    html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<html[^>]*>|</html>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<head[^>]*>[\s\S]*?</head>', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<body[^>]*>|</body>', '', html, flags=re.IGNORECASE)
    return html.strip()

def call_ollama(title, focus_kw, seg_nome, model, timeout=180):
    prompt = f"""Artigo de blog em portugues do Brasil. Apenas HTML, sem markdown.

TITULO: {title}
SEGMENTO: {seg_nome}

REGRAS:
- 3 subtitulos <h2>, paragrafos <p>, listas <ul><li>
- 1 bloco: <div class="highlight-box"><p><strong>Dado:</strong> texto</p></div>
- Mencione <a href="https://atendente24h.com">Atendente24h</a> 2 vezes
- Proibido: **, ##, tracos de lista, markdown
- Comece com <h2> ou <p> direto

HTML:"""

    resp = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.65,
                "num_predict": 1200,
                "top_p": 0.85,
            }
        },
        timeout=timeout
    )
    resp.raise_for_status()
    raw = resp.json().get("response", "").strip()
    return clean_body(raw)

# ─── MAIN ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=0, help="Maximo de artigos a gerar (0=todos)")
    parser.add_argument("--model", default="llama3.2", help="Modelo Ollama")
    parser.add_argument("--list", action="store_true", help="Apenas lista topicos sem gerar")
    parser.add_argument("--batch", type=int, default=20, help="Commitar a cada N artigos gerados")
    parser.add_argument("--skip", type=int, default=0, help="Pula os primeiros N topicos pendentes (para rodar multiplos workers)")
    parser.add_argument("--worker", type=int, default=0, help="ID do worker (0,1,2...) para particionar os topicos")
    args = parser.parse_args()

    topics = build_topic_list()
    print(f"Total de topicos na lista: {len(topics)}")

    if args.list:
        for i, (slug, title, kw, desc, setor) in enumerate(topics, 1):
            print(f"{i:4d}. [{setor}] {slug}")
        return

    # Filtra ja existentes
    pending = [(slug, title, kw, desc, setor)
               for slug, title, kw, desc, setor in topics
               if not os.path.exists(os.path.join(BLOG_DIR, f"{slug}.html"))]

    print(f"Ja existentes: {len(topics) - len(pending)} | Pendentes: {len(pending)}")

    # Particiona para workers paralelos (round-robin por indice)
    if args.worker or args.skip:
        n_workers = max(args.worker + 1, 1)
        pending = [t for i, t in enumerate(pending) if i % n_workers == args.worker]
        print(f"Worker {args.worker}: {len(pending)} topicos")

    if args.limit:
        pending = pending[:args.limit]
        print(f"Limitado a {args.limit} artigos")

    ok = 0
    erros = 0
    for i, (slug, title, kw, desc, setor) in enumerate(pending, 1):
        print(f"[{i}/{len(pending)}] {slug[:60]}...", end=" ", flush=True)
        try:
            body = call_ollama(title, kw, setor, args.model)
            if len(body) < 600:
                print(f"CURTO ({len(body)} chars), pulando")
                erros += 1
                continue
            html = make_html(slug, title, kw, desc, setor, body)
            path = os.path.join(BLOG_DIR, f"{slug}.html")
            with open(path, "w", encoding="utf-8") as f:
                f.write(html)
            print(f"OK ({len(body)} chars)")
            ok += 1

            # Commit a cada batch
            if ok % args.batch == 0:
                total_now = len([f for f in os.listdir(BLOG_DIR) if f.endswith(".html") and f != "index.html"])
                print(f"  → Commitando lote ({total_now} posts total)...")
                os.system(f'cd {BLOG_DIR}/.. && git add blog/ && git commit -m "blog: +{args.batch} posts SEO ({total_now} total)" && git push')

        except Exception as e:
            print(f"ERRO: {e}")
            erros += 1
            time.sleep(2)

    # Commit final com restante
    os.system(f'cd {BLOG_DIR}/.. && git add blog/ && git commit -m "blog: lote final SEO" && git push 2>/dev/null || true')
    total_posts = len([f for f in os.listdir(BLOG_DIR) if f.endswith(".html") and f != "index.html"])
    print(f"\nConcluido: {ok} gerados, {erros} erros | Total no blog: {total_posts}")

if __name__ == "__main__":
    main()
