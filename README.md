# SEO Sites – Coletor de SEO (Search Console + GA4) para Google Sheets

## Visão geral
Ferramenta em Python para preencher automaticamente relatórios de SEO em uma única aba do Google Sheets (`SEO SITES`).

Para cada domínio presente na aba, o script:
- Lê o domínio (A) e, duas linhas abaixo, identifica o cabeçalho: Sessões | Impressões | Cliques | CTR | Posição | Sessões | FTD
- Percorre as linhas de meses (jan-25, fev-25, …)
- Para meses já encerrados com qualquer célula vazia, extrai métricas do Google Search Console e do GA4 e preenche apenas as células vazias
- Nunca sobrescreve valores já preenchidos

Métricas preenchidas:
- Impressões, Cliques (GSC)
- CTR (calculada) e Posição média ponderada por Impressões (GSC)
- Sessões (GA4)
- FTD não é lido nem alterado

## Requisitos
- Python 3.8+
- `credentials.json` (service account) com acesso a: Google Sheets API, Search Console API e GA4 Data API
- GA4 via OAuth (opcional): `oauth_credentials.json` + login para gerar `token_ga4.json`; ou dar Viewer à service account no GA4

## Instalação
```bash
pip install -r requirements.txt
```

## Configuração
- Edite `config.py`:
  - `SPREADSHEET_URL`: URL da planilha
  - `ABA_DADOS_ORIGEM`: use `SEO SITES`
  - `DOMAIN_CONFIGS`: mapeie propriedades por domínio, se quiser ID de GA4/SC específicos
  - Exemplo:
    ```python
    DOMAIN_CONFIGS = {
      'fortunerabbit-brasil.com': {
        'ga4_property_id': '456043089',
        'sc_site': 'https://fortunerabbit-brasil.com/'
      }
    }
    ```

## Como usar
```bash
python ler_seo-sites.py
```
- 1: Sincronizar meses pendentes na SEO SITES (todos os domínios)
- 2: Preencher um mês específico
- 3: Testar conexões (GSC + GA4)

## Formatação dos dados
- Todos os valores são gravados como números (sem aspas, sem %):
  - CTR e Posição com 2 casas decimais (ex.: 5.94)
  - Impressões, Cliques e Sessões como inteiros (ex.: 103)

## Estrutura do projeto
```
SEO-sites/
├── api_extractor.py    # Lógica de extração e preenchimento por domínio/bloco
├── ler_seo-sites.py    # Menu simples de execução
├── config.py           # Configurações (planilha, aba, domínios)
├── requirements.txt    # Dependências
├── credentials.json    # Service account (não versionar)
└── README.md
```

## Dicas de solução de problemas
- Search Console 403: adicione o email da service account como usuário da propriedade (ou ajuste `sc_site` em `DOMAIN_CONFIGS`)
- GA4 sem login: conceda Viewer da propriedade ao email da service account ou configure OAuth desktop e gere `token_ga4.json`
- Cabeçalho não encontrado: confirme que a linha do domínio está na coluna A e que o cabeçalho está duas linhas abaixo com os títulos acima

## Versão
- v1.0.0
  - Primeira versão estável do coletor: fluxo único, multi-domínio, atualização apenas de células vazias na aba `SEO SITES`, números em formato numérico.

## Licença
MIT