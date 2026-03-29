#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir acentuacao nos arquivos HTML do blog do atendente24h.
Aplica substituicoes APENAS em texto (nao em tags HTML, atributos, URLs, CSS, JS).
"""

import re
import os
import glob

# Dicionario de substituicoes
replacements = {
    # Palavras comuns
    r'\bnao\b': 'não', r'\bNao\b': 'Não',
    r'\bsao\b': 'são', r'\bSao\b': 'São',
    r'\bvoce\b': 'você', r'\bVoce\b': 'Você',
    r'\bja\b': 'já', r'\bJa\b': 'Já',
    r'\bso\b': 'só', r'\bSo\b': 'Só',
    r'\bate\b': 'até', r'\bAte\b': 'Até',
    r'\bapos\b': 'após', r'\bApos\b': 'Após',
    r'\btambem\b': 'também', r'\bTambem\b': 'Também',
    r'\balem\b': 'além', r'\bAlem\b': 'Além',
    r'\bentao\b': 'então', r'\bEntao\b': 'Então',
    r'\bporem\b': 'porém', r'\bPorem\b': 'Porém',
    r'\batras\b': 'atrás', r'\bAtras\b': 'Atrás',
    r'\bproprio\b': 'próprio', r'\bProprio\b': 'Próprio',
    r'\bpropria\b': 'própria', r'\bPropria\b': 'Própria',
    r'\bproprios\b': 'próprios', r'\bProprios\b': 'Próprios',
    r'\bproprias\b': 'próprias', r'\bProprias\b': 'Próprias',
    r'\brapido\b': 'rápido', r'\bRapido\b': 'Rápido',
    r'\brapida\b': 'rápida', r'\bRapida\b': 'Rápida',
    r'\brapidos\b': 'rápidos', r'\bRapidos\b': 'Rápidos',
    r'\bfacil\b': 'fácil', r'\bFacil\b': 'Fácil',
    r'\bfaceis\b': 'fáceis', r'\bFaceis\b': 'Fáceis',
    r'\botimo\b': 'ótimo', r'\bOtimo\b': 'Ótimo',
    r'\botima\b': 'ótima', r'\bOtima\b': 'Ótima',
    r'\bunico\b': 'único', r'\bUnico\b': 'Único',
    r'\bunica\b': 'única', r'\bUnica\b': 'Única',
    r'\bunicas\b': 'únicas', r'\bUnicos\b': 'Únicos',
    r'\bnumero\b': 'número', r'\bNumero\b': 'Número',
    r'\bnumeros\b': 'números', r'\bNumeros\b': 'Números',
    r'\bpublico\b': 'público', r'\bPublico\b': 'Público',
    r'\bpublicos\b': 'públicos',
    r'\bbasico\b': 'básico', r'\bBasico\b': 'Básico',
    r'\bbasica\b': 'básica', r'\bBasica\b': 'Básica',
    r'\bbasicos\b': 'básicos', r'\bBasicos\b': 'Básicos',
    r'\btecnico\b': 'técnico', r'\bTecnico\b': 'Técnico',
    r'\btecnica\b': 'técnica', r'\bTecnica\b': 'Técnica',
    r'\btecnicos\b': 'técnicos', r'\bTecnicos\b': 'Técnicos',
    r'\bmedico\b': 'médico', r'\bMedico\b': 'Médico',
    r'\bmedica\b': 'médica', r'\bMedica\b': 'Médica',
    r'\bmedicos\b': 'médicos', r'\bMedicos\b': 'Médicos',
    r'\bjuridico\b': 'jurídico', r'\bJuridico\b': 'Jurídico',
    r'\bjuridica\b': 'jurídica',
    r'\bhorario\b': 'horário', r'\bHorario\b': 'Horário',
    r'\bhorarios\b': 'horários', r'\bHorarios\b': 'Horários',
    r'\bsalario\b': 'salário', r'\bSalario\b': 'Salário',
    r'\bhistorico\b': 'histórico', r'\bHistorico\b': 'Histórico',
    r'\bperiodo\b': 'período', r'\bPeriodo\b': 'Período',
    r'\bperiodos\b': 'períodos',
    r'\bproximo\b': 'próximo', r'\bProximo\b': 'Próximo',
    r'\bpróximos\b': 'próximos',
    r'\binicio\b': 'início', r'\bInicio\b': 'Início',
    r'\bindice\b': 'índice', r'\bIndice\b': 'Índice',
    r'\bmaximo\b': 'máximo', r'\bMaximo\b': 'Máximo',
    r'\bminimo\b': 'mínimo', r'\bMinimo\b': 'Mínimo',
    r'\bagencia\b': 'agência', r'\bAgencia\b': 'Agência',
    r'\bagencias\b': 'agências',
    r'\bsequencia\b': 'sequência', r'\bSequencia\b': 'Sequência',
    r'\btendencia\b': 'tendência', r'\bTendencia\b': 'Tendência',
    r'\beficiencia\b': 'eficiência', r'\bEficiencia\b': 'Eficiência',
    r'\bconsistencia\b': 'consistência',
    r'\bpresenca\b': 'presença', r'\bPresenca\b': 'Presença',
    r'\bservico\b': 'serviço', r'\bServico\b': 'Serviço',
    r'\bservicos\b': 'serviços', r'\bServicos\b': 'Serviços',
    r'\bespaco\b': 'espaço', r'\bEspaco\b': 'Espaço',
    r'\blancamento\b': 'lançamento', r'\bLancamento\b': 'Lançamento',
    r'\blancamentos\b': 'lançamentos',
    r'\bcomeco\b': 'começo', r'\bComeco\b': 'Começo',
    r'\bcomecou\b': 'começou',
    r'\bavanco\b': 'avanço', r'\bAvanco\b': 'Avanço',
    r'\bforca\b': 'força', r'\bForca\b': 'Força',
    r'\balcanca\b': 'alcança',
    r'\bexito\b': 'êxito',
    r'\bcrianca\b': 'criança', r'\bCrianca\b': 'Criança',
    r'\bcriancas\b': 'crianças',
    r'\bfuncao\b': 'função', r'\bFuncao\b': 'Função',
    r'\bfuncoes\b': 'funções',
    r'\bgestao\b': 'gestão', r'\bGestao\b': 'Gestão',
    # Palavras terminadas em -ao
    r'\bsolucao\b': 'solução', r'\bSolucao\b': 'Solução',
    r'\bsolucoes\b': 'soluções',
    r'\bautomacao\b': 'automação', r'\bAutomacao\b': 'Automação',
    r'\bautomacoes\b': 'automações',
    r'\bconfiguracao\b': 'configuração', r'\bConfiguracao\b': 'Configuração',
    r'\bconfiguracoes\b': 'configurações',
    r'\bcomunicacao\b': 'comunicação', r'\bComunicacao\b': 'Comunicação',
    r'\bcomunicacoes\b': 'comunicações',
    r'\binformacao\b': 'informação', r'\bInformacao\b': 'Informação',
    r'\binformacoes\b': 'informações',
    r'\bintegracao\b': 'integração', r'\bIntegracao\b': 'Integração',
    r'\bintegracoes\b': 'integrações',
    r'\batualizacao\b': 'atualização', r'\bAtualizacao\b': 'Atualização',
    r'\batualizacoes\b': 'atualizações',
    r'\bapresentacao\b': 'apresentação', r'\bApresentacao\b': 'Apresentação',
    r'\batencao\b': 'atenção', r'\bAtencao\b': 'Atenção',
    r'\bopcao\b': 'opção', r'\bOpcao\b': 'Opção',
    r'\bopcoes\b': 'opções', r'\bOpcoes\b': 'Opções',
    r'\bsituacao\b': 'situação', r'\bSituacao\b': 'Situação',
    r'\bsituacoes\b': 'situações',
    r'\bimplementacao\b': 'implementação', r'\bImplementacao\b': 'Implementação',
    r'\bcontratacao\b': 'contratação', r'\bContratacao\b': 'Contratação',
    r'\bselecao\b': 'seleção', r'\bSelecao\b': 'Seleção',
    r'\bproducao\b': 'produção', r'\bProducao\b': 'Produção',
    r'\breducao\b': 'redução', r'\bReducao\b': 'Redução',
    r'\bprotecao\b': 'proteção', r'\bProtecao\b': 'Proteção',
    r'\blegislacao\b': 'legislação', r'\bLegislacao\b': 'Legislação',
    r'\baplicacao\b': 'aplicação', r'\bAplicacao\b': 'Aplicação',
    r'\baplicacoes\b': 'aplicações',
    r'\brevisao\b': 'revisão', r'\bRevisao\b': 'Revisão',
    r'\brestricao\b': 'restrição', r'\bRestricao\b': 'Restrição',
    r'\brestricoes\b': 'restrições',
    r'\bmanutencao\b': 'manutenção', r'\bManutencao\b': 'Manutenção',
    r'\bdefinicao\b': 'definição', r'\bDefinicao\b': 'Definição',
    r'\bdefinicoes\b': 'definições',
    r'\bavaliacao\b': 'avaliação', r'\bAvaliacao\b': 'Avaliação',
    r'\bavaliacoes\b': 'avaliações',
    r'\bformacao\b': 'formação', r'\bFormacao\b': 'Formação',
    r'\bgeneralizacao\b': 'generalização',
    r'\bpersonalizacao\b': 'personalização', r'\bPersonalizacao\b': 'Personalização',
    r'\bnotificacao\b': 'notificação', r'\bNotificacao\b': 'Notificação',
    r'\bnotificacoes\b': 'notificações',
    r'\baprovacao\b': 'aprovação', r'\bAprovacao\b': 'Aprovação',
    r'\bautorizacao\b': 'autorização', r'\bAutorizacao\b': 'Autorização',
    r'\bverificacao\b': 'verificação', r'\bVerificacao\b': 'Verificação',
    r'\bgravacao\b': 'gravação',
    r'\blimitacao\b': 'limitação', r'\bLimitacao\b': 'Limitação',
    r'\blimitacoes\b': 'limitações',
    r'\bsolicitacao\b': 'solicitação', r'\bSolicitacao\b': 'Solicitação',
    r'\bsolicitacoes\b': 'solicitações',
    r'\bevolucao\b': 'evolução', r'\bEvolucao\b': 'Evolução',
    r'\beducacao\b': 'educação', r'\bEducacao\b': 'Educação',
    r'\bnegocio\b': 'negócio', r'\bNegocio\b': 'Negócio',
    r'\bnegocios\b': 'negócios', r'\bNegocios\b': 'Negócios',
    r'\bfuncionarios\b': 'funcionários', r'\bFuncionarios\b': 'Funcionários',
    r'\bfuncionario\b': 'funcionário', r'\bFuncionario\b': 'Funcionário',
    r'\busuarios\b': 'usuários', r'\bUsuarios\b': 'Usuários',
    r'\busuario\b': 'usuário', r'\bUsuario\b': 'Usuário',
    r'\bduvida\b': 'dúvida', r'\bDuvida\b': 'Dúvida',
    r'\bduvidas\b': 'dúvidas', r'\bDuvidas\b': 'Dúvidas',
    r'\bpagina\b': 'página', r'\bPagina\b': 'Página',
    r'\bpaginas\b': 'páginas', r'\bPaginas\b': 'Páginas',
    r'\bmusica\b': 'música', r'\bMusica\b': 'Música',
    r'\bveiculo\b': 'veículo', r'\bVeiculo\b': 'Veículo',
    r'\bveiculos\b': 'veículos', r'\bVeiculos\b': 'Veículos',
    r'\bexperiencia\b': 'experiência', r'\bExperiencia\b': 'Experiência',
    r'\bexperiencias\b': 'experiências',
    r'\bpratica\b': 'prática', r'\bPratica\b': 'Prática',
    r'\bpraticas\b': 'práticas', r'\bPraticas\b': 'Práticas',
    r'\bgratis\b': 'grátis', r'\bGratis\b': 'Grátis',
    r'\bautomatico\b': 'automático', r'\bAutomatico\b': 'Automático',
    r'\bautomatica\b': 'automática', r'\bAutomatica\b': 'Automática',
    r'\bautomaticos\b': 'automáticos',
    r'\bautomaticas\b': 'automáticas',
    r'\bespecifico\b': 'específico', r'\bEspecifico\b': 'Específico',
    r'\bespecifica\b': 'específica', r'\bEspecifica\b': 'Específica',
    r'\bespecificos\b': 'específicos',
    r'\bmedia\b': 'média', r'\bMedia\b': 'Média',
    r'\bmedias\b': 'médias', r'\bMedias\b': 'Médias',
    r'\brecepcao\b': 'recepção', r'\bRecepcao\b': 'Recepção',
    # Palavras adicionais comuns
    r'\bpossivel\b': 'possível', r'\bPossivel\b': 'Possível',
    r'\bpossiveis\b': 'possíveis', r'\bPossiveis\b': 'Possíveis',
    r'\bdificil\b': 'difícil', r'\bDificil\b': 'Difícil',
    r'\bdificeis\b': 'difíceis',
    r'\buteis\b': 'úteis',
    r'\butil\b': 'útil', r'\bUtil\b': 'Útil',
    r'\bfisico\b': 'físico', r'\bFisico\b': 'Físico',
    r'\bfisica\b': 'física', r'\bFisica\b': 'Física',
    r'\bprazo\b': 'prazo',  # correct
    r'\banalise\b': 'análise', r'\bAnalise\b': 'Análise',
    r'\banalises\b': 'análises',
    r'\bsintese\b': 'síntese',
    r'\bhipotese\b': 'hipótese',
    r'\bcategoria\b': 'categoria',  # correct
    r'\benergia\b': 'energia',  # correct
    r'\bstrategia\b': 'estratégia',
    r'\bestrategia\b': 'estratégia', r'\bEstrategia\b': 'Estratégia',
    r'\bestrategias\b': 'estratégias',
    r'\bcenario\b': 'cenário', r'\bCenario\b': 'Cenário',
    r'\bcenarios\b': 'cenários',
    r'\bcalculo\b': 'cálculo', r'\bCalculo\b': 'Cálculo',
    r'\bcalculos\b': 'cálculos',
    r'\bmidia\b': 'mídia', r'\bMidia\b': 'Mídia',
    r'\bmidias\b': 'mídias',
    r'\bcodifico\b': 'codífico',
    r'\bcodigo\b': 'código', r'\bCodigo\b': 'Código',
    r'\bcodigos\b': 'códigos',
    r'\bclinica\b': 'clínica', r'\bClinica\b': 'Clínica',
    r'\bclinicas\b': 'clínicas',
    r'\borganico\b': 'orgânico', r'\bOrganico\b': 'Orgânico',
    r'\borganica\b': 'orgânica',
    r'\btipico\b': 'típico', r'\bTipico\b': 'Típico',
    r'\btipica\b': 'típica',
    r'\bimplicacao\b': 'implicação',
    r'\brelacao\b': 'relação', r'\bRelacao\b': 'Relação',
    r'\brelacoes\b': 'relações',
    r'\bconversao\b': 'conversão', r'\bConversao\b': 'Conversão',
    r'\bexpansao\b': 'expansão', r'\bExpansao\b': 'Expansão',
    r'\bcomparacao\b': 'comparação', r'\bComparacao\b': 'Comparação',
    r'\bdedicacao\b': 'dedicação', r'\bDedicacao\b': 'Dedicação',
    r'\bpreparacao\b': 'preparação', r'\bPreparacao\b': 'Preparação',
    r'\bplataforma\b': 'plataforma',  # correct
    r'\bhabilidade\b': 'habilidade',  # correct
    r'\bprofissional\b': 'profissional',  # correct
    r'\bqualidade\b': 'qualidade',  # correct
    r'\bresponsavel\b': 'responsável', r'\bResponsavel\b': 'Responsável',
    r'\bresponsaveis\b': 'responsáveis',
    r'\bdisponivel\b': 'disponível', r'\bDisponivel\b': 'Disponível',
    r'\bdisponiveis\b': 'disponíveis',
    r'\bconfiavel\b': 'confiável', r'\bConfiavel\b': 'Confiável',
    r'\bcontratuais\b': 'contratuais',  # correct
    r'\bflexivel\b': 'flexível', r'\bFlexivel\b': 'Flexível',
    r'\bflexiveis\b': 'flexíveis',
    r'\bacessivel\b': 'acessível', r'\bAcessivel\b': 'Acessível',
    r'\bacessiveis\b': 'acessíveis',
    r'\bnivel\b': 'nível', r'\bNivel\b': 'Nível',
    r'\bniveis\b': 'níveis',
    r'\bmóvel\b': 'móvel',  # already correct
    r'\bmovel\b': 'móvel', r'\bMovel\b': 'Móvel',
    r'\bmoveis\b': 'móveis',
    r'\bfuncionou\b': 'funcionou',  # correct
    r'\bsessao\b': 'sessão', r'\bSessao\b': 'Sessão',
    r'\bsessoes\b': 'sessões',
    r'\bativacao\b': 'ativação', r'\bAtivacao\b': 'Ativação',
    r'\btransacao\b': 'transação', r'\bTransacao\b': 'Transação',
    r'\btransacoes\b': 'transações',
    r'\bfrequencia\b': 'frequência', r'\bFrequencia\b': 'Frequência',
    r'\bpotencial\b': 'potencial',  # correct
    r'\bexcecao\b': 'exceção', r'\bExcecao\b': 'Exceção',
    r'\bexcecoes\b': 'exceções',
    r'\bpratico\b': 'prático', r'\bPratico\b': 'Prático',
    r'\bpraticos\b': 'práticos',
}


def fix_accents_in_text_only(html_content, replacements):
    """Aplica as substituicoes apenas no conteudo de texto, nao em tags HTML."""
    # Divide pelo conteudo de tags HTML (mantendo as tags intactas)
    parts = re.split(r'(<[^>]+>)', html_content)
    result = []
    for part in parts:
        if part.startswith('<'):
            # E uma tag HTML - nao modifica
            result.append(part)
        else:
            # E conteudo de texto - aplica substituicoes
            for pattern, replacement in replacements.items():
                part = re.sub(pattern, replacement, part)
            result.append(part)
    return ''.join(result)


def process_file(filepath, replacements):
    """Le, corrige e salva um arquivo HTML."""
    with open(filepath, 'r', encoding='utf-8') as f:
        original = f.read()

    fixed = fix_accents_in_text_only(original, replacements)

    if fixed != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed)
        return True
    return False


def main():
    blog_dir = '/Users/eduardoarantes/agentes/atendimento24h/blog'
    html_files = glob.glob(os.path.join(blog_dir, '*.html'))

    total = len(html_files)
    changed = 0
    unchanged = 0

    print(f"Processando {total} arquivos HTML em {blog_dir}/")
    print("-" * 60)

    for filepath in sorted(html_files):
        filename = os.path.basename(filepath)
        was_changed = process_file(filepath, replacements)
        if was_changed:
            changed += 1
            print(f"  [OK] {filename}")
        else:
            unchanged += 1

    print("-" * 60)
    print(f"Total: {total} arquivos")
    print(f"Modificados: {changed}")
    print(f"Sem alteracoes: {unchanged}")


if __name__ == '__main__':
    main()
