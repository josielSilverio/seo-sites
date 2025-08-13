import gspread
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import RunReportRequest, DateRange, Dimension, Metric
import datetime
import time
import re
from gspread.utils import rowcol_to_a1

# Configurações
SCOPES = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly"
]

# Importar configurações do config.py
try:
    from config import SPREADSHEET_URL, SEARCH_CONSOLE_SITE, GA4_PROPERTY_ID, ABA_DADOS_ORIGEM
    # Opcional: mapeamento por domínio
    try:
        from config import DOMAIN_CONFIGS  # {'dominio.com': {'ga4_property_id': '123', 'sc_site': 'https://dominio.com/'} }
    except Exception:
        DOMAIN_CONFIGS = {}
except ImportError:
    # Configurações padrão caso config.py não esteja disponível
    SPREADSHEET_URL = 'https://docs.google.com/spreadsheets/d/1Hq2Q0AsYByswfVq4nZiq63F8370YgjK2vajbajVJt6w/edit?usp=sharing'
    SEARCH_CONSOLE_SITE = 'sc-domain:fortunerabbit-brasil.com'
    GA4_PROPERTY_ID = '456043089'
    ABA_DADOS_ORIGEM = 'SEO SITES'

class SEODataExtractor:
    def __init__(self):
        # Configurar credenciais para Google Sheets (service account)
        self.creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', SCOPES)
        self.gspread_client = gspread.authorize(self.creds)
        
        # Configurar credenciais para Search Console (service account)
        self.search_console_creds = service_account.Credentials.from_service_account_file(
            'credentials.json', scopes=['https://www.googleapis.com/auth/webmasters.readonly'])
        
        # Configurar credenciais para GA4 (OAuth - será configurado depois)
        self.ga4_creds = None
        # Tentar preparar credenciais de service account para GA4 (fallback)
        try:
            self.ga4_service_creds = service_account.Credentials.from_service_account_file(
                'credentials.json', scopes=['https://www.googleapis.com/auth/analytics.readonly']
            )
        except Exception:
            self.ga4_service_creds = None
        
        # Abrir planilha
        self.sheet = self.gspread_client.open_by_url(SPREADSHEET_URL)
        
        print("✅ Conexões estabelecidas com sucesso!")
        print("⚠️  GA4 usará autenticação OAuth (será solicitada na primeira execução)")
        
        # Cache de site do Search Console detectado pela planilha
        self._sc_site_url_cache = None
    
    def extrair_dados_search_console(self, start_date, end_date, domain_override: str | None = None):
        """Extrai dados do Google Search Console"""
        try:
            print(f"📊 Extraindo dados do Search Console ({start_date} a {end_date})...")
            
            service = build('searchconsole', 'v1', credentials=self.search_console_creds)

            # Resolver siteUrl a partir da planilha (A1) ou do config, com fallback
            candidate_sites = []
            domain = domain_override or self._detect_domain_from_sheet113()
            if domain:
                candidate_sites.extend([f"sc-domain:{domain}", f"https://{domain}/"])
                # Override específico do config, se existir
                cfg = DOMAIN_CONFIGS.get(domain)
                if cfg and cfg.get('sc_site'):
                    candidate_sites.insert(0, cfg['sc_site'])
            candidate_sites.append(SEARCH_CONSOLE_SITE)

            last_error = None
            for site in candidate_sites:
                try:
                    request = {
                        'startDate': start_date,
                        'endDate': end_date,
                        'dimensions': ['page', 'query'],
                        'rowLimit': 25000,
                        'startRow': 0
                    }
                    response = service.searchanalytics().query(siteUrl=site, body=request).execute()
                    dados = response.get('rows', [])
                    self._sc_site_url_cache = site
                    print(f"   ✅ {len(dados)} registros extraídos do Search Console (site: {site})")
                    return dados
                except Exception as e:
                    last_error = e
                    continue

            if last_error:
                raise last_error
            return []
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair dados do Search Console: {e}")
            return []
    
    def configurar_oauth_ga4(self):
        """Configura autenticação OAuth para GA4"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            import os
            
            SCOPES_GA4 = ['https://www.googleapis.com/auth/analytics.readonly']
            
            creds = None
            # Verificar se já existe token salvo
            if os.path.exists('token_ga4.json'):
                creds = Credentials.from_authorized_user_file('token_ga4.json', SCOPES_GA4)
            
            # Se não há credenciais válidas, fazer login
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    # Criar arquivo de credenciais OAuth se não existir
                    if not os.path.exists('oauth_credentials.json'):
                        print("❌ Arquivo oauth_credentials.json não encontrado!")
                        print("💡 Para configurar OAuth para GA4:")
                        print("   1. Acesse: https://console.cloud.google.com/")
                        print("   2. Vá em APIs e Serviços > Credenciais")
                        print("   3. Crie credenciais OAuth 2.0")
                        print("   4. Baixe o arquivo JSON e renomeie para 'oauth_credentials.json'")
                        return None
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        'oauth_credentials.json', SCOPES_GA4)
                    creds = flow.run_local_server(port=0)
                
                # Salvar credenciais para próxima execução
                with open('token_ga4.json', 'w') as token:
                    token.write(creds.to_json())
            
            self.ga4_creds = creds
            print("✅ Autenticação OAuth para GA4 configurada")
            return creds
            
        except Exception as e:
            print(f"❌ Erro ao configurar OAuth GA4: {e}")
            return None
    
    def extrair_dados_ga4(self, start_date, end_date, property_id: str | None = None):
        """Extrai dados do Google Analytics 4"""
        try:
            print(f"📈 Extraindo dados do GA4 ({start_date} a {end_date})...")
            
            # Selecionar método de autenticação: OAuth (se disponível) ou Service Account (fallback)
            if not self.ga4_creds:
                import os
                use_oauth = os.path.exists('oauth_credentials.json')
                creds = None
                if use_oauth:
                    creds = self.configurar_oauth_ga4()
                if not creds and self.ga4_service_creds is not None:
                    print("⚠️  Usando Service Account para GA4 (sem tela de consentimento)")
                    creds = self.ga4_service_creds
                if not creds:
                    print("❌ Não foi possível obter credenciais para GA4 (OAuth ou Service Account)")
                    return []
                self.ga4_creds = creds
            
            client = BetaAnalyticsDataClient(credentials=self.ga4_creds)
            
            request = RunReportRequest(
                property=f"properties/{(property_id or GA4_PROPERTY_ID)}",
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                dimensions=[Dimension(name="pagePath")],
                metrics=[
                    Metric(name="sessions")
                ]
            )
            
            response = client.run_report(request=request)
            
            dados = []
            for row in response.rows:
                dados.append({
                    'page_path': row.dimension_values[0].value,
                    'sessions': row.metric_values[0].value
                })
            
            print(f"   ✅ {len(dados)} registros extraídos do GA4")
            return dados
            
        except Exception as e:
            print(f"   ❌ Erro ao extrair dados do GA4: {e}")
            return []
    
    def processar_dados_search_console(self, dados_gsc, mes_ano):
        """Processa dados do Search Console para formato da planilha"""
        dados_processados = {}
        
        for row in dados_gsc:
            page = row['keys'][0] if len(row['keys']) > 0 else ''
            query = row['keys'][1] if len(row['keys']) > 1 else ''
            
            # Normalizar URL da página
            page_clean = self.normalize_url(page)
            
            if page_clean not in dados_processados:
                dados_processados[page_clean] = {
                    'impressions': 0,
                    'clicks': 0,
                    'ctr': 0,
                    'position': 0,
                    'queries': []
                }
            
            # Agregar métricas por página
            dados_processados[page_clean]['impressions'] += int(row.get('impressions', 0))
            dados_processados[page_clean]['clicks'] += int(row.get('clicks', 0))
            dados_processados[page_clean]['queries'].append(query)
        
        # Calcular CTR e posição média
        for page, metrics in dados_processados.items():
            if metrics['impressions'] > 0:
                metrics['ctr'] = (metrics['clicks'] / metrics['impressions']) * 100
            
        return dados_processados
    
    def processar_dados_ga4(self, dados_ga4):
        """Processa dados do GA4 para formato da planilha"""
        dados_processados = {}
        
        for row in dados_ga4:
            page_path = row['page_path']
            page_clean = self.normalize_url(page_path)
            
            dados_processados[page_clean] = {
                'sessions': int(row['sessions']),
                'users': int(row['users']),
                'pageviews': int(row['pageviews'])
            }
        
        return dados_processados
    
    def normalize_url(self, url):
        """Normaliza URLs para comparação"""
        if not url:
            return ''
        url = url.lower().strip()
        url = url.replace('https://', '').replace('http://', '')
        if url.endswith('/'):
            url = url[:-1]
        return url
    
    def atualizar_sheet113(self, dados_gsc, dados_ga4, mes_ano):
        """Atualiza a aba Sheet113 com os dados extraídos"""
        try:
            print("📝 Atualizando Sheet113...")
            
            sheet_113 = self.sheet.worksheet(ABA_DADOS_ORIGEM)
            
            # Obter dados atuais
            data_atual = sheet_113.get_all_values()

            # Detecção de layout vertical (meses nas linhas, métricas nas colunas)
            if data_atual and len(data_atual) >= 2:
                structure = self._locate_table_structure(data_atual)
                if structure is not None:
                    return self.atualizar_sheet113_vertical(dados_gsc, dados_ga4, mes_ano, structure)
            
            if not data_atual:
                print("   ⚠️ Sheet113 está vazia. Criando cabeçalhos...")
                # Criar cabeçalhos se a planilha estiver vazia
                headers = ['Landing page', 'GA4 property'] + \
                         [f'2025|{i:02d} (Impressions)' for i in range(1, 13)] + \
                         [f'2025|{i:02d} (Clicks)' for i in range(1, 13)] + \
                         [f'2025|{i:02d} (CTR)' for i in range(1, 13)] + \
                         [f'2025|{i:02d} (Average position)' for i in range(1, 13)] + \
                         [str(i) for i in range(1, 13)]  # Meses para GA4
                
                sheet_113.append_row(headers)
                data_atual = [headers]
            
            # Processar atualizações
            updates = []
            
            # Combinar dados por URL
            todas_urls = set(dados_gsc.keys()) | set(dados_ga4.keys())
            
            for url in todas_urls:
                # Procurar linha existente ou criar nova
                linha_encontrada = None
                for i, row in enumerate(data_atual[1:], 2):  # Começar da linha 2
                    if len(row) > 0 and self.normalize_url(row[0]) == url:
                        linha_encontrada = i
                        break
                
                if linha_encontrada is None:
                    # Adicionar nova linha
                    nova_linha = [url, url] + [''] * (len(data_atual[0]) - 2)
                    sheet_113.append_row(nova_linha)
                    linha_encontrada = len(data_atual) + 1
                    data_atual.append(nova_linha)
                
                # Atualizar dados do Search Console
                if url in dados_gsc:
                    gsc_data = dados_gsc[url]
                    mes_num = int(mes_ano.split('-')[0])  # Extrair número do mês
                    
                    # Colunas para impressões, clicks, CTR, posição (baseado no mês)
                    col_impressions = 2 + mes_num  # Ajustar conforme layout real
                    col_clicks = col_impressions + 12
                    col_ctr = col_clicks + 12
                    col_position = col_ctr + 12
                    
                    updates.extend([
                        {'range': f'{chr(65 + col_impressions)}{linha_encontrada}', 
                         'values': [[gsc_data['impressions']]]},
                        {'range': f'{chr(65 + col_clicks)}{linha_encontrada}', 
                         'values': [[gsc_data['clicks']]]},
                        {'range': f'{chr(65 + col_ctr)}{linha_encontrada}', 
                         'values': [[f"{gsc_data['ctr']:.2f}"]]}
                    ])
                
                # Atualizar dados do GA4
                if url in dados_ga4:
                    ga4_data = dados_ga4[url]
                    mes_num = int(mes_ano.split('-')[0])
                    
                    # Coluna para sessões (baseado no mês)
                    col_sessions = 50 + mes_num  # Ajustar conforme layout real
                    
                    updates.append({
                        'range': f'{chr(65 + col_sessions)}{linha_encontrada}',
                        'values': [[ga4_data['sessions']]]
                    })
            
            # Executar atualizações em lote
            if updates:
                sheet_113.batch_update([{'range': u['range'], 'values': u['values']} for u in updates])
                print(f"   ✅ {len(updates)} células atualizadas na Sheet113")
            else:
                print("   ⚠️ Nenhuma atualização necessária")
                
        except Exception as e:
            print(f"   ❌ Erro ao atualizar Sheet113: {e}")

    def atualizar_sheet113_vertical(self, dados_gsc_raw, dados_ga4_raw, mes_ano, structure=None):
        """Atualiza a aba Sheet113 quando o layout é vertical (meses nas linhas).
        Permite receber uma estrutura pré-localizada para maior robustez.
        """
        try:
            print("📝 Atualizando Sheet113 (layout vertical)...")
            sheet_113 = self.sheet.worksheet(ABA_DADOS_ORIGEM)
            data = sheet_113.get_all_values()

            if not data:
                print("   ❌ A aba Sheet113 está vazia. Adicione cabeçalhos primeiro.")
                return

            if structure is None:
                structure = self._locate_table_structure(data)
            if structure is None:
                print("   ❌ Não foi possível localizar cabeçalhos da tabela.")
                return

            header_row = structure['header_row']
            first_data_row = structure['first_data_row']
            last_data_row = structure.get('last_data_row', len(data) - 1)
            col_mes = structure['col_mes']
            col_impr = structure['col_impr']
            col_clicks = structure['col_clicks']
            col_ctr = structure['col_ctr']
            col_pos = structure['col_pos']
            col_sessions = structure['col_sessions']

            # Localizar linha do mês (ex: mar-25)
            alvo = mes_ao.strip().lower() if False else mes_ano.strip().lower()
            row_idx = None
            for i in range(first_data_row, last_data_row + 1):
                cel = data[i][col_mes].strip().lower() if len(data[i]) > col_mes else ''
                if cel == alvo:
                    row_idx = i + 1  # 1-based
                    break

            if row_idx is None:
                # Criar nova linha ao final
                row_idx = len(data) + 1
                num_cols = max(len(data[header_row]), 7)
                nova = [''] * num_cols
                nova[col_mes] = mes_ano
                sheet_113.append_row(nova)

            # Agregar GSC
            total_impr = 0
            total_clicks = 0
            pos_weighted_sum = 0.0
            for r in dados_gsc_raw:
                try:
                    impr = int(r.get('impressions', 0))
                except Exception:
                    impr = 0
                try:
                    clk = int(r.get('clicks', 0))
                except Exception:
                    clk = 0
                try:
                    pos = float(r.get('position', 0) or 0)
                except Exception:
                    pos = 0.0
                total_impr += impr
                total_clicks += clk
                pos_weighted_sum += pos * max(impr, 0)

            ctr_total = (total_clicks / total_impr * 100) if total_impr > 0 else 0.0
            pos_media = (pos_weighted_sum / total_impr) if total_impr > 0 else 0.0

            # Agregar GA4
            total_sessoes = 0
            for r in dados_ga4_raw:
                try:
                    total_sessoes += int(r.get('sessions', 0))
                except Exception:
                    pass

            # Atualiza APENAS células vazias
            updates = []
            # Garantir que tenhamos a linha atual para checar vazios
            current_line = []
            if row_idx - 1 < len(data):
                current_line = data[row_idx - 1]

            def cell_empty(col_index_zero_based):
                return (len(current_line) <= col_index_zero_based) or (current_line[col_index_zero_based].strip() == '')

            if col_impr is not None and cell_empty(col_impr):
                updates.append({'range': rowcol_to_a1(row_idx, col_impr + 1), 'values': [[int(total_impr)]]})
            if col_clicks is not None and cell_empty(col_clicks):
                updates.append({'range': rowcol_to_a1(row_idx, col_clicks + 1), 'values': [[int(total_clicks)]]})
            if col_ctr is not None and cell_empty(col_ctr):
                updates.append({'range': rowcol_to_a1(row_idx, col_ctr + 1), 'values': [[round(ctr_total, 2)]]})
            if col_pos is not None and cell_empty(col_pos):
                updates.append({'range': rowcol_to_a1(row_idx, col_pos + 1), 'values': [[round(pos_media, 2)]]})
            if col_sessions is not None and cell_empty(col_sessions):
                updates.append({'range': rowcol_to_a1(row_idx, col_sessions + 1), 'values': [[int(total_sessoes)]]})

            if updates:
                sheet_113.batch_update(updates, value_input_option='USER_ENTERED')
                print(f"   ✅ Linha '{mes_ano}' atualizada na Sheet113")
            else:
                print("   ⚠️ Nada para atualizar (layout vertical)")

        except Exception as e:
            print(f"   ❌ Erro ao atualizar Sheet113 (vertical): {e}")

    def _find_domain_row_index(self, data):
        """Localiza a linha (0-based) onde está o domínio na coluna A (primeiras 10 linhas)."""
        max_scan = min(10, len(data))
        for i in range(max_scan):
            try:
                val = (data[i][0] or '').strip()
            except Exception:
                val = ''
            if not val:
                continue
            v = val.replace('https://', '').replace('http://', '').split('/')[0].replace('www.', '')
            if re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', v):
                return i
        return None

    def _locate_table_structure(self, data, domain_row: int | None = None):
        """Encontra cabeçalho e índices de colunas conforme layout informado:
        A1: domínio; duas linhas abaixo: cabeçalho com colunas
        [Sessões] [Impressões] [Cliques] [CTR] [Posição] [Sessões] [FTD]
        """
        if not data:
            return None
        # Se não for informado, localizar o domínio a partir do topo
        if domain_row is None:
            domain_row = self._find_domain_row_index(data)
        if domain_row is None:
            return None
        header_row = domain_row + 2
        if header_row >= len(data):
            return None
        header = [h.strip() for h in data[header_row]]
        header_lower = [h.lower() for h in header]

        # Mapear colunas
        def find_exact(label, start_index=0):
            label_lower = label.lower()
            for i in range(start_index, len(header_lower)):
                if header_lower[i] == label_lower:
                    return i
            return None

        # Mês fica na primeira coluna da tabela (A)
        col_mes = 0
        col_impr = find_exact('Impressões')
        col_clicks = find_exact('Cliques')
        col_ctr = find_exact('CTR')
        col_pos = find_exact('Posição') or find_exact('Posicao')
        # A segunda ocorrência de "Sessões" é a coluna de sessões (primeira é título da primeira coluna)
        col_sessions = None
        sess_idx_first = find_exact('Sessões') or find_exact('Sessoes')
        if sess_idx_first is not None:
            # procurar próxima "Sessões" depois da primeira
            for i in range(sess_idx_first + 1, len(header_lower)):
                if header_lower[i] in ('sessões', 'sessoes'):
                    col_sessions = i
                    break
        if col_sessions is None:
            # Se não houver repetição, tente qualquer "sess"
            for i, h in enumerate(header_lower):
                if i == col_mes:
                    continue
                if 'sess' in h:
                    col_sessions = i
                    break

        if any(v is None for v in [col_impr, col_clicks, col_ctr, col_pos, col_sessions]):
            return None

        return {
            'header_row': header_row,
            'first_data_row': header_row + 1,
            'col_mes': col_mes,
            'col_impr': col_impr,
            'col_clicks': col_clicks,
            'col_ctr': col_ctr,
            'col_pos': col_pos,
            'col_sessions': col_sessions,
            'domain': (data[domain_row][0].replace('https://','').replace('http://','').split('/')[0].replace('www.','').strip()) if len(data[domain_row])>0 else None
        }

    def _locate_all_table_structures(self, data):
        """Varre a planilha para múltiplos blocos domínio+tabela, retornando uma lista de estruturas.
        Cada estrutura contém um intervalo de linhas [first_data_row, last_data_row] exclusivo por domínio.
        """
        structures = []
        i = 0
        n = len(data)
        while i < n:
            # Tenta localizar um domínio na janela a partir da linha i
            sub = data[i:min(i+10, n)]
            local_domain_row = self._find_domain_row_index(sub)
            if local_domain_row is None:
                i += 1
                continue

            domain_row = i + local_domain_row
            header_row = domain_row + 2
            if header_row >= n:
                break

            # Estrutura a partir deste domínio
            st = self._locate_table_structure(data, domain_row=domain_row)
            if not st:
                i = header_row + 1
                continue

            # Determinar o fim deste bloco (até próxima linha que contenha domínio)
            scan_start = header_row + 1
            next_domain_global = n
            idx = scan_start
            while idx < n:
                maybe_sub = data[idx:min(idx+10, n)]
                local_next = self._find_domain_row_index(maybe_sub)
                if local_next is not None:
                    next_domain_global = idx + local_next
                    break
                idx += 1

            st['last_data_row'] = next_domain_global - 1
            structures.append(st)
            i = next_domain_global

        return structures

    def _detect_domain_from_sheet113(self):
        """Tenta obter o domínio a partir da célula A1 da aba Sheet113 (texto ou link)."""
        try:
            sheet_113 = self.sheet.worksheet(ABA_DADOS_ORIGEM)
            val = sheet_113.acell('A1').value or ''
            val = val.strip()
            if not val:
                return None
            # Remover protocolo e caminhos
            val = val.replace('https://', '').replace('http://', '')
            val = val.split('/')[0]
            # Remover possíveis rótulos
            val = val.replace('www.', '')
            # Validar domínio simples
            if re.match(r'^[a-z0-9.-]+\.[a-z]{2,}$', val):
                return val
            return None
        except Exception:
            return None

    def preencher_meses_pendentes_vertical(self):
        """Percorre a aba Sheet113 (layout vertical) e preenche meses pendentes.
        - Considera pendente quando pelo menos uma métrica (Impressões, Cliques, CTR, Posição, Sessões)
          está vazia na linha do mês.
        - Só processa meses cujo período já terminou (mês completamente encerrado).
        - Sempre extrai GSC e GA4 para o mês e atualiza apenas as células vazias.
        """
        try:
            sheet_113 = self.sheet.worksheet(ABA_DADOS_ORIGEM)
            data = sheet_113.get_all_values()
            if not data or len(data) < 2:
                print("❌ A aba Sheet113 não possui dados/cabeçalho suficiente.")
                return { 'processed_months': 0 }

            # Encontrar múltiplos blocos (um por domínio)
            structures = self._locate_all_table_structures(data)
            if not structures:
                print("❌ Não foi possível identificar as colunas de métricas (Impressões, Cliques, CTR, Posição, Sessões).")
                return { 'processed_months': 0 }

            total_processados = 0
            meses_map = {
                'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
                'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
            }

            for structure in structures:
                domain = structure['domain']
                header_row = structure['header_row']
                first_data_row = structure['first_data_row']
                col_mes = structure['col_mes']
                col_impr = structure['col_impr']
                col_clicks = structure['col_clicks']
                col_ctr = structure['col_ctr']
                col_pos = structure['col_pos']
                col_sessions = structure['col_sessions']

                hoje = datetime.date.today()
                processados = 0

                for i in range(first_data_row, structure.get('last_data_row', len(data) - 1) + 1):
                    linha = data[i]
                    if len(linha) == 0:
                        continue
                    rotulo = linha[col_mes].strip().lower() if len(linha) > col_mes else ''
                    if not re.match(r'^[a-z]{3}-\d{2}$', rotulo):
                        continue

                    mes_str, ano_curto = rotulo.split('-')
                    if mes_str not in meses_map:
                        continue
                    ano = int('20' + ano_curto)
                    mes_num = meses_map[mes_str]

                    # Fim do mês
                    if mes_num == 12:
                        next_month = datetime.date(ano + 1, 1, 1)
                    else:
                        next_month = datetime.date(ano, mes_num + 1, 1)
                    fim_mes = next_month - datetime.timedelta(days=1)

                    # Só processa se mês já terminou
                    if fim_mes >= hoje:
                        continue

                    # Verificar se há campos vazios
                    def vazio(idx):
                        return (len(linha) <= idx) or (linha[idx].strip() == '')

                    precisa = vazio(col_impr) or vazio(col_clicks) or vazio(col_ctr) or vazio(col_pos) or vazio(col_sessions)
                    if not precisa:
                        continue

                    # Extrair para este domínio
                    inicio = datetime.date(ano, mes_num, 1)
                    periodo_inicio = inicio.strftime('%Y-%m-%d')
                    periodo_fim = fim_mes.strftime('%Y-%m-%d')
                    print(f"\n🚀 Processando {rotulo} ({periodo_inicio} a {periodo_fim}) para {domain}...")

                    # Resolver GA4 property por domínio (se configurado)
                    ga4_property_override = None
                    cfg = DOMAIN_CONFIGS.get(domain)
                    if cfg and cfg.get('ga4_property_id'):
                        ga4_property_override = cfg['ga4_property_id']

                    dados_gsc = self.extrair_dados_search_console(periodo_inicio, periodo_fim, domain_override=domain)
                    dados_ga4 = self.extrair_dados_ga4(periodo_inicio, periodo_fim, property_id=ga4_property_override)

                    # Atualiza só a linha do mês (com estrutura previamente localizada)
                    self.atualizar_sheet113_vertical(dados_gsc, dados_ga4, rotulo, structure)
                    processados += 1

                total_processados += processados

            print(f"\n✅ Meses processados: {total_processados}")
            return { 'processed_months': total_processados }

        except Exception as e:
            print(f"❌ Erro ao preencher meses pendentes: {e}")
            return { 'processed_months': 0 }
    
    def executar_extracao_completa(self, mes_ano='mar-25'):
        """Executa extração completa de dados"""
        print(f"🚀 Iniciando extração completa para {mes_ano}...")
        
        # Calcular datas baseado no mês
        ano = 2025
        mes = {'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
               'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12}[mes_ano.split('-')[0]]
        
        start_date = f"{ano}-{mes:02d}-01"
        
        # Último dia do mês
        if mes == 12:
            next_month = datetime.date(ano + 1, 1, 1)
        else:
            next_month = datetime.date(ano, mes + 1, 1)
        
        last_day = (next_month - datetime.timedelta(days=1)).day
        end_date = f"{ano}-{mes:02d}-{last_day:02d}"
        
        print(f"📅 Período: {start_date} a {end_date}")
        
        # Extrair dados
        dados_gsc = self.extrair_dados_search_console(start_date, end_date)
        dados_ga4 = self.extrair_dados_ga4(start_date, end_date)
        
        # Processar dados
        dados_gsc_processados = self.processar_dados_search_console(dados_gsc, mes_ano)
        dados_ga4_processados = self.processar_dados_ga4(dados_ga4)
        
        # Atualizar planilha conforme layout detectado
        try:
            sheet_113 = self.sheet.worksheet(ABA_DADOS_ORIGEM)
            dados_existentes = sheet_113.get_all_values()
            vertical = False
            if dados_existentes and len(dados_existentes) >= 2:
                header_lower = [h.strip().lower() for h in dados_existentes[0]]
                primeira = (dados_existentes[1][0].strip().lower() if len(dados_existentes[1]) > 0 else '')
                vertical = any('impress' in h for h in header_lower) and re.match(r'^[a-z]{3}-\d{2}$', primeira) is not None
            if vertical:
                self.atualizar_sheet113_vertical(dados_gsc, dados_ga4, mes_ano)
            else:
                self.atualizar_sheet113(dados_gsc_processados, dados_ga4_processados, mes_ano)
        except Exception:
            # Se detecção falhar, usar o método antigo
            self.atualizar_sheet113(dados_gsc_processados, dados_ga4_processados, mes_ano)
        
        print("🎉 Extração completa finalizada!")
        
        return {
            'gsc_records': len(dados_gsc),
            'ga4_records': len(dados_ga4),
            'processed_urls': len(set(dados_gsc_processados.keys()) | set(dados_ga4_processados.keys()))
        }

def main():
    """Função principal"""
    try:
        extractor = SEODataExtractor()
        
        # Menu interativo
        print("\n" + "="*60)
        print("🔧 EXTRATOR DE DADOS SEO - APIs Google")
        print("="*60)
        print("1 - Extrair dados para mês específico")
        print("2 - Extrair dados para múltiplos meses")
        print("3 - Testar conexões")
        
        opcao = input("\nEscolha uma opção (1/2/3): ").strip()
        
        if opcao == '1':
            mes = input("Digite o mês (ex: mar-25): ").strip()
            resultado = extractor.executar_extracao_completa(mes)
            print(f"\n📊 Resumo: {resultado['gsc_records']} registros GSC, {resultado['ga4_records']} registros GA4")
            
        elif opcao == '2':
            meses = input("Digite os meses separados por vírgula (ex: jan-25,fev-25,mar-25): ").strip().split(',')
            for mes in meses:
                mes = mes.strip()
                print(f"\n🔄 Processando {mes}...")
                resultado = extractor.executar_extracao_completa(mes)
                print(f"   📊 {resultado['processed_urls']} URLs processadas")
                time.sleep(2)  # Pausa entre requisições
                
        elif opcao == '3':
            print("\n🧪 Testando conexões...")
            # Teste básico
            dados_teste_gsc = extractor.extrair_dados_search_console('2025-03-01', '2025-03-07')
            dados_teste_ga4 = extractor.extrair_dados_ga4('2025-03-01', '2025-03-07')
            print(f"   ✅ Teste concluído: {len(dados_teste_gsc)} registros GSC, {len(dados_teste_ga4)} registros GA4")
        
        else:
            print("❌ Opção inválida!")
            
    except Exception as e:
        print(f"❌ Erro geral: {e}")
        print("\n💡 Verifique:")
        print("   - Se o arquivo credentials.json existe")
        print("   - Se as APIs estão habilitadas")
        print("   - Se a service account tem permissões adequadas")
        print("   - Se os IDs da propriedade GA4 e site Search Console estão corretos")

if __name__ == "__main__":
    main()