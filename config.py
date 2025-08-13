# Configurações do Projeto SEO Sites
# Edite este arquivo para personalizar as configurações

# =============================================================================
# CONFIGURAÇÕES PRINCIPAIS
# =============================================================================

# URL da planilha Google Sheets
SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1Hq2Q0AsYByswfVq4nZiq63F8370YgjK2vajbajVJt6w/edit?usp=sharing'

# Site do Google Search Console
# Formatos possíveis:
# - Para domínio: 'sc-domain:exemplo.com'
# - Para URL específica: 'https://exemplo.com/'
SEARCH_CONSOLE_SITE = 'https://fortunerabbit-brasil.com'

# ID da propriedade do Google Analytics 4
# COMO ENCONTRAR O ID:
# 1. Acesse Google Analytics 4
# 2. Vá em Admin (engrenagem no canto inferior esquerdo)
# 3. Na coluna "Propriedade", clique em "Detalhes da propriedade"
# 4. Copie o "ID da propriedade" (apenas números, ex: 123456789)
GA4_PROPERTY_ID = '456043089'  # ⚠️ SUBSTITUA pelo ID real da sua propriedade GA4
   
# EXEMPLO de onde encontrar:
# - URL do GA4: https://analytics.google.com/analytics/web/#/pXXXXXXXXX/
# - O ID é a sequência de números após o "p" (XXXXXXXXX)
# - OU vá em Admin > Detalhes da propriedade > "ID da propriedade"

# =============================================================================
# CONFIGURAÇÕES DE DATAS
# =============================================================================

# Meses disponíveis para extração
MESES_DISPONIVEIS = {
    'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
}

# Ano padrão para extração
ANO_PADRAO = 2025

# =============================================================================
# CONFIGURAÇÕES DE API
# =============================================================================

# Escopos necessários para as APIs
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly"
]

# Arquivo de credenciais da service account
CREDENTIALS_FILE = 'credentials.json'

# Limites de requisições
SEARCH_CONSOLE_ROW_LIMIT = 25000
GA4_ROW_LIMIT = 10000

# =============================================================================
# CONFIGURAÇÕES DA PLANILHA
# =============================================================================

# Nomes das abas
# A aba de análise/agregação agora é a 'SEO SITES'
ABA_DADOS_ORIGEM = 'SEO SITES'
ABA_DADOS_DESTINO = 'SEO SITES'

# Mapeamento de colunas na Sheet113 (ajuste conforme sua planilha)
COLUNAS_SHEET113 = {
    'landing_page': 0,  # Coluna A
    'ga4_property': 1,  # Coluna B
    'impressions_start': 2,  # Coluna C (início das colunas de impressões)
    'clicks_start': 14,  # Coluna O (início das colunas de clicks)
    'ctr_start': 26,  # Coluna AA (início das colunas de CTR)
    'position_start': 38,  # Coluna AM (início das colunas de posição)
    'sessions_start': 50  # Coluna AX (início das colunas de sessões GA4)
}

# =============================================================================
# CONFIGURAÇÕES DE PROCESSAMENTO
# =============================================================================

# Dimensões para extração do Search Console
SEARCH_CONSOLE_DIMENSIONS = ['page', 'query']

# Métricas para extração do GA4
GA4_DIMENSIONS = ['pagePath']
GA4_METRICS = ['sessions', 'users', 'pageviews']

# Configurações de normalização de URL
URL_NORMALIZATION = {
    'remove_protocols': True,  # Remove http:// e https://
    'remove_trailing_slash': True,  # Remove / no final
    'convert_to_lowercase': True  # Converte para minúsculas
}

# =============================================================================
# CONFIGURAÇÕES DE LOG
# =============================================================================

# Nível de detalhamento dos logs
LOG_LEVEL = 'INFO'  # DEBUG, INFO, WARNING, ERROR

# Mostrar progresso detalhado
SHOW_PROGRESS = True

# =============================================================================
# CONFIGURAÇÕES AVANÇADAS
# =============================================================================

# Tempo de espera entre requisições (segundos)
DELAY_BETWEEN_REQUESTS = 1

# Número máximo de tentativas em caso de erro
MAX_RETRIES = 3

# Timeout para requisições (segundos)
REQUEST_TIMEOUT = 30

# =============================================================================
# MAPEAMENTO POR DOMÍNIO (OPCIONAL)
# =============================================================================

# Configure domínios específicos com overrides para GA4 e Search Console.
# Exemplo:
# DOMAIN_CONFIGS = {
#     'fortunerabbit-brasil.com': {
#         'ga4_property_id': '456043089',
#         'sc_site': 'https://fortunerabbit-brasil.com/'
#     },
#     'tigrinho-brasil.com': {
#         'ga4_property_id': '123456789',
#         'sc_site': 'https://tigrinho-brasil.com/'
#     }
# }
DOMAIN_CONFIGS = {
    'fortunerabbit-brasil.com': {
        'ga4_property_id': '456043089',
        'sc_site': 'https://fortunerabbit-brasil.com/'
    },
   'tigrinho-brasil.com': {
        'ga4_property_id': '456039452',
        'sc_site': 'https://tigrinho-brasil.com/'
    },
   'aviator-brasil.com': {
        'ga4_property_id': '456031494',
        'sc_site': 'https://aviator-brasil.com/'
    },
   'gatesofolympus-br.com': {
        'ga4_property_id': '456031033',
        'sc_site': 'https://gatesofolympus-br.com/'
    },
   'roletasaovivo.com': {
        'ga4_property_id': '456037626',
        'sc_site': 'https://roletasaovivo.com/'
    },
   'bacbobrasil.com': {
        'ga4_property_id': '456040818',
        'sc_site': 'https://bacbobrasil.com/'
    },
   'ninjacrashbrasil.com': {
        'ga4_property_id': '456037477',
        'sc_site': 'https://ninjacrashbrasil.com/'
    },
   'sugar-rush-brasil.com': {
        'ga4_property_id': '459090372',
        'sc_site': 'https://sugar-rush-brasil.com/'
    },
   'fortuneox-brasil.com': {
        'ga4_property_id': '459067987',
        'sc_site': 'https://fortuneox-brasil.com/'
    },
   'jogar-cassinos.com': {
        'ga4_property_id': '473449989',
        'sc_site': 'https://jogar-cassinos.com/'
    }
}

# =============================================================================
# INSTRUÇÕES DE CONFIGURAÇÃO
# =============================================================================

"""
PARA CONFIGURAR ESTE PROJETO:

1. GOOGLE ANALYTICS 4:
   - Acesse GA4 > Admin > Detalhes da propriedade
   - Copie o "ID da propriedade" (número)
   - Cole em GA4_PROPERTY_ID acima

2. GOOGLE SEARCH CONSOLE:
   - Verifique o formato do seu site no Search Console
   - Se for domínio: use 'sc-domain:seudominio.com'
   - Se for URL: use 'https://seusite.com/'
   - Atualize SEARCH_CONSOLE_SITE acima

3. CREDENCIAIS:
   - Certifique-se de que o arquivo 'credentials.json' está na pasta do projeto
   - A service account deve ter permissões para:
     * Google Sheets API
     * Google Search Console API
     * Google Analytics Data API

4. PLANILHA:
   - Verifique se a URL da planilha está correta
   - Confirme se as abas 'Sheet113' e 'SEO SITES' existem
   - Ajuste o mapeamento de colunas se necessário

5. TESTE:
   - Execute: python api_extractor.py
   - Escolha opção 3 para testar conexões
   - Se houver erros, verifique as configurações acima
"""