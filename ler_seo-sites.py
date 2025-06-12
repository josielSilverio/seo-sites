import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# 1. Defina o escopo de acesso
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# 2. Substitua pelo nome do seu arquivo de credenciais
creds = ServiceAccountCredentials.from_json_keyfile_name('credentials.json', scope)

# 3. Autorize o cliente
client = gspread.authorize(creds)

# 4. Abra a planilha pelo link
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1Hq2Q0AsYByswfVq4nZiq63F8370YgjK2vajbajVJt6w/edit?usp=sharing'
sheet = client.open_by_url(spreadsheet_url)

# Diagnóstico: liste todas as abas
worksheets = sheet.worksheets()
print("Abas disponíveis na planilha:")
for ws in worksheets:
    print(ws.title)

# 5. Selecione a primeira aba (worksheet)
worksheet = sheet.worksheet('SEO SITES')

# 6. Leia todos os valores da planilha
data = worksheet.get_all_values()

# Procura a linha do mês 'mar-25' e verifica se está vazia
for row in data:
    if len(row) > 1 and 'mar-25' == row[1].strip():
        print(f"Linha de mar-25: {row}")
        # Verifica se todas as outras colunas (exceto a coluna de mês) estão vazias
        if all(cell.strip() == '' for cell in row[2:]):
            print("ATENÇÃO: Os dados de 'mar-25' estão vazios!")
        else:
            print("Dados de 'mar-25' encontrados.")
        break
else:
    print("Mês 'mar-25' não encontrado na planilha.")

# 7. Exiba os dados
# for row in data:
#     print(row)

# 1. Leia os dados da aba sheets113
sheet_sheets113 = sheet.worksheet('Sheet113')
data_sheets113 = sheet_sheets113.get_all_values()

# 2. Leia os dados da aba SEO SITES
sheet_seo = sheet.worksheet('SEO SITES')
data_seo = sheet_seo.get_all_values()

# 3. Mapeie as colunas da sheets113
header = data_sheets113[0]
if 'Landing page' in header:
    col_landing = header.index('Landing page')
elif 'GA4 property' in header:
    col_landing = header.index('GA4 property')
else:
    raise Exception("Cabeçalho de domínio não encontrado!")

# Função para normalizar URLs/domínios
def normalize_url(url):
    if not url:
        return ''
    url = url.lower().strip()
    url = url.replace('https://', '').replace('http://', '')
    if url.endswith('/'):
        url = url[:-1]
    return url

# Função para sanitizar métricas
def sanitize_metric(value):
    v = str(value).strip().lower()
    if v in ('', 'nenhum', 'none', 'nan', 'null', '-'):
        return '0'
    try:
        num = float(v.replace(',', '.'))
        if num.is_integer():
            return str(int(num))
        else:
            return f'{num:.2f}'.replace('.', ',')
    except ValueError:
        return '0'

# Dicionário para converter número do mês para nome em português
meses_pt = {
    '1': 'jan', '2': 'fev', '3': 'mar', '4': 'abr', '5': 'mai', '6': 'jun',
    '7': 'jul', '8': 'ago', '9': 'set', '10': 'out', '11': 'nov', '12': 'dez'
}

# Dicionário inverso para converter nome para número
meses_num = {v: k for k, v in meses_pt.items()}

def obter_meses_disponiveis_sheet113():
    """Obtém os meses disponíveis na Sheet113"""
    sheet_sheets113 = sheet.worksheet('Sheet113')
    data_sheets113 = sheet_sheets113.get_all_values()
    header = data_sheets113[0]
    
    meses_gsc = []
    meses_ga4 = []
    
    # Meses do GSC (Search Console)
    for col in header:
        match = re.match(r'(\d{4})\|(\d{2}) \(Impressions\)', col)
        if match:
            ano, mes = match.groups()
            mes_label = f"{meses_pt[str(int(mes))]}-{ano[2:]}"
            meses_gsc.append(mes_label)
    
    # Meses do GA4 (a partir da coluna H)
    header_sessoes = data_sheets113[0][7:]
    for mes_num in header_sessoes:
        mes_num = str(mes_num).strip()
        if mes_num.isdigit() and mes_num in meses_pt:
            mes_label = f"{meses_pt[mes_num]}-25"
            meses_ga4.append(mes_label)
    
    return meses_gsc, meses_ga4, data_sheets113, header

def preencher_mes_interativo():
    """Função interativa para preencher um mês específico"""
    while True:
        print("\n" + "="*50)
        print("🔄 PREENCHIMENTO INTERATIVO DE DADOS SEO")
        print("="*50)
        
        # Obter dados atuais da Sheet113
        meses_gsc, meses_ga4, data_sheets113, header = obter_meses_disponiveis_sheet113()
        
        print("\n📊 Meses disponíveis na Sheet113:")
        print(f"   GSC (Search Console): {', '.join(meses_gsc) if meses_gsc else 'Nenhum'}")
        print(f"   GA4 (Analytics): {', '.join(meses_ga4) if meses_ga4 else 'Nenhum'}")
        
        # Perguntar qual mês preencher
        print("\n❓ Qual mês você deseja preencher?")
        print("   Formato: mes-ano (ex: mar-25, jan-24)")
        mes_desejado = input("   Digite o mês: ").strip().lower()
        
        if not mes_desejado:
            print("❌ Mês não pode estar vazio!")
            continue
            
        # Verificar se o formato está correto
        if not re.match(r'^[a-z]{3}-\d{2}$', mes_desejado):
            print("❌ Formato inválido! Use: mes-ano (ex: mar-25)")
            continue
        
        # Verificar disponibilidade
        tem_gsc = mes_desejado in meses_gsc
        tem_ga4 = mes_desejado in meses_ga4
        
        print(f"\n🔍 Verificando disponibilidade do mês '{mes_desejado}':")
        print(f"   GSC: {'✅ Disponível' if tem_gsc else '❌ Não encontrado'}")
        print(f"   GA4: {'✅ Disponível' if tem_ga4 else '❌ Não encontrado'}")
        
        if not tem_gsc and not tem_ga4:
            print(f"\n⚠️  O mês '{mes_desejado}' não foi encontrado na Sheet113!")
            print("   Opções:")
            print("   1 - Revisar dados na Sheet113 e tentar novamente")
            print("   2 - Escolher outro mês") 
            print("   3 - Sair")
            
            opcao = input("   Escolha (1/2/3): ").strip()
            
            if opcao == '1':
                input("\n⏳ Revise a Sheet113 e pressione ENTER para continuar...")
                continue
            elif opcao == '2':
                continue
            else:
                print("👋 Saindo...")
                return
        
        # Se chegou aqui, pelo menos um tipo de dados está disponível
        print(f"\n✅ Dados encontrados para '{mes_desejado}'!")
        
        if tem_gsc and tem_ga4:
            print("   📈 Preenchendo dados do GSC (Search Console) e GA4 (Analytics)")
            tipo_dados = 'ambos'
        elif tem_gsc:
            print("   📈 Preenchendo apenas dados do GSC (Search Console)")
            tipo_dados = 'gsc'
        else:
            print("   📊 Preenchendo apenas dados do GA4 (Analytics)")
            tipo_dados = 'ga4'
        
        confirmar = input(f"\n❓ Confirmar preenchimento para '{mes_desejado}'? (s/n): ").strip().lower()
        
        if confirmar in ['s', 'sim', 'y', 'yes']:
            executar_preenchimento(mes_desejado, tipo_dados, data_sheets113, header)
            break
        else:
            print("❌ Operação cancelada.")
            continue

def executar_preenchimento(mes_desejado, tipo_dados, data_sheets113, header):
    """Executa o preenchimento para o mês específico"""
    print(f"\n🚀 Iniciando preenchimento para {mes_desejado}...")
    
    # Lê dados da aba SEO SITES
    sheet_seo = sheet.worksheet('SEO SITES')
    data_seo = sheet_seo.get_all_values()
    
    updates = []
    
    # Mapear colunas da sheets113
    if 'Landing page' in header:
        col_landing = header.index('Landing page')
    elif 'GA4 property' in header:
        col_landing = header.index('GA4 property')
    else:
        print("❌ Erro: Cabeçalho de domínio não encontrado!")
        return
    
    # Processar dados GSC se disponível
    if tipo_dados in ['gsc', 'ambos']:
        print("📊 Processando dados do Search Console...")
        
        # Extrair ano e mês do mes_desejado (ex: mar-25 -> 2025, 03)
        mes_nome, ano_curto = mes_desejado.split('-')
        mes_numero = meses_num[mes_nome]
        ano_completo = f"20{ano_curto}"
        
        # Buscar colunas correspondentes
        padrao_impressoes = f"{ano_completo}|{mes_numero.zfill(2)} (Impressions)"
        
        try:
            col_impr = header.index(padrao_impressoes)
            col_ctr = header.index(f"{ano_completo}|{mes_numero.zfill(2)} (CTR)")
            col_pos = header.index(f"{ano_completo}|{mes_numero.zfill(2)} (Average position)")
            col_clicks = header.index(f"{ano_completo}|{mes_numero.zfill(2)} (Clicks)")
            
            for row in data_sheets113[1:]:
                url = normalize_url(row[col_landing])
                if not url:
                    continue
                    
                # Buscar na aba SEO SITES
                for i, seo_row in enumerate(data_seo):
                    seo_url = normalize_url(''.join(seo_row))
                    if url == seo_url:
                        # Procurar linha do mês específico
                        for j in range(i+1, min(i+20, len(data_seo))):
                            if len(data_seo[j]) > 1 and data_seo[j][1].strip() == mes_desejado:
                                val_impr = sanitize_metric(row[col_impr])
                                val_clicks = sanitize_metric(row[col_clicks])
                                val_ctr = sanitize_metric(row[col_ctr])
                                val_pos = sanitize_metric(row[col_pos])
                                
                                print(f"   📈 {url} → Impr: {val_impr}, Clicks: {val_clicks}, CTR: {val_ctr}, Pos: {val_pos}")
                                
                                # Adicionar atualizações
                                if len(data_seo[j]) <= 2 or data_seo[j][2].strip() in ['', '0']:
                                    updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 3), 'values': [[val_impr]]})
                                if len(data_seo[j]) <= 3 or data_seo[j][3].strip() in ['', '0']:
                                    updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 4), 'values': [[val_clicks]]})
                                if len(data_seo[j]) <= 4 or data_seo[j][4].strip() in ['', '0']:
                                    updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 5), 'values': [[val_ctr]]})
                                if len(data_seo[j]) <= 5 or data_seo[j][5].strip() in ['', '0']:
                                    updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 6), 'values': [[val_pos]]})
                                break
                        break
                        
        except ValueError as e:
            print(f"❌ Erro ao encontrar colunas GSC para {mes_desejado}: {e}")
    
    # Processar dados GA4 se disponível
    if tipo_dados in ['ga4', 'ambos']:
        print("📊 Processando dados do Google Analytics...")
        
        mes_nome, ano_curto = mes_desejado.split('-')
        mes_numero = meses_num[mes_nome]
        
        # Buscar coluna do GA4
        header_sessoes = data_sheets113[0][7:]
        try:
            col_idx = header_sessoes.index(mes_numero)
            col_ga4 = 7 + col_idx
            
            for row in data_sheets113[1:]:
                if len(row) <= col_ga4 or not row[7].strip():
                    continue
                    
                dominio = normalize_url(row[7])
                sessoes = sanitize_metric(row[col_ga4])
                
                # Buscar na aba SEO SITES
                for i, seo_row in enumerate(data_seo):
                    seo_url = normalize_url(''.join(seo_row))
                    if dominio == seo_url:
                        for j in range(i+1, min(i+20, len(data_seo))):
                            if len(data_seo[j]) > 1 and data_seo[j][1].strip() == mes_desejado:
                                print(f"   📊 {dominio} → Sessões: {sessoes}")
                                
                                valor_atual = data_seo[j][6] if len(data_seo[j]) > 6 else ''
                                if valor_atual.strip() in ['', '0']:
                                    updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 7), 'values': [[sessoes]]})
                                break
                        break
                        
        except ValueError:
            print(f"❌ Coluna GA4 não encontrada para o mês {mes_numero}")
    
    # Executar atualizações
    if updates:
        sheet_seo.batch_update([{'range': u['range'], 'values': u['values']} for u in updates])
        print(f"\n✅ {len(updates)} células atualizadas com sucesso!")
    else:
        print("\n⚠️  Nenhuma célula precisou ser atualizada (dados já preenchidos ou não encontrados).")

# ==========================================
# MENU PRINCIPAL
# ==========================================

def menu_principal():
    """Menu principal do script"""
    while True:
        print("\n" + "="*60)
        print("🔧 AUTOMATIZADOR DE DADOS SEO - MENU PRINCIPAL")
        print("="*60)
        print("1 - Preenchimento automático completo (modo original)")
        print("2 - Preenchimento interativo por mês")
        print("3 - Sair")
        
        opcao = input("\nEscolha uma opção (1/2/3): ").strip()
        
        if opcao == '1':
            executar_modo_original()
        elif opcao == '2':
            preencher_mes_interativo()
        elif opcao == '3':
            print("👋 Saindo do programa...")
            break
        else:
            print("❌ Opção inválida! Escolha 1, 2 ou 3.")

def executar_modo_original():
    """Executa o modo original do script (preenchimento completo)"""
    print("\n🔄 Executando preenchimento automático completo...")
    
    # 5. Selecione a primeira aba (worksheet)
    worksheet = sheet.worksheet('SEO SITES')

    # 6. Leia todos os valores da planilha
    data = worksheet.get_all_values()

    # Procura a linha do mês 'mar-25' e verifica se está vazia
    for row in data:
        if len(row) > 1 and 'mar-25' == row[1].strip():
            print(f"Linha de mar-25: {row}")
            # Verifica se todas as outras colunas (exceto a coluna de mês) estão vazias
            if all(cell.strip() == '' for cell in row[2:]):
                print("ATENÇÃO: Os dados de 'mar-25' estão vazios!")
            else:
                print("Dados de 'mar-25' encontrados.")
            break
    else:
        print("Mês 'mar-25' não encontrado na planilha.")

    # 1. Leia os dados da aba sheets113
    sheet_sheets113 = sheet.worksheet('Sheet113')
    data_sheets113 = sheet_sheets113.get_all_values()

    # 2. Leia os dados da aba SEO SITES
    sheet_seo = sheet.worksheet('SEO SITES')
    data_seo = sheet_seo.get_all_values()

    # 3. Mapeie as colunas da sheets113
    header = data_sheets113[0]
    if 'Landing page' in header:
        col_landing = header.index('Landing page')
    elif 'GA4 property' in header:
        col_landing = header.index('GA4 property')
    else:
        raise Exception("Cabeçalho de domínio não encontrado!")

    updates = []

    # Para cada coluna de mês no header (Sheet113)
    for idx, col in enumerate(header):
        match = re.match(r'(\d{4})\|(\d{2}) \(Impressions\)', col)
        if match:
            ano, mes = match.groups()
            mes_label = f"{meses_pt[str(int(mes))]}-{ano[2:]}"
            col_impr = idx
            col_ctr = header.index(f"{ano}|{mes} (CTR)")
            col_pos = header.index(f"{ano}|{mes} (Average position)")
            col_clicks = header.index(f"{ano}|{mes} (Clicks)")
            for row in data_sheets113[1:]:
                url = normalize_url(row[col_landing])
                encontrou = False
                for i, seo_row in enumerate(data_seo):
                    seo_url = normalize_url(''.join(seo_row))
                    if url == seo_url:
                        for j in range(i+1, min(i+20, len(data_seo))):
                            if len(data_seo[j]) > 1 and data_seo[j][1].strip() == mes_label:
                                encontrou = True
                                val_impr = sanitize_metric(row[col_impr])
                                val_clicks = sanitize_metric(row[col_clicks])
                                val_ctr = sanitize_metric(row[col_ctr])
                                val_pos = sanitize_metric(row[col_pos])
                                print(f"Atualizando {url} ({mes_label}) na linha {j+1}: Impr: {data_seo[j][2]} -> {val_impr}, Cliques: {data_seo[j][3]} -> {val_clicks}, CTR: {data_seo[j][4]} -> {val_ctr}, Pos: {data_seo[j][5]} -> {val_pos}")
                                if (len(data_seo[j]) <= 2 or data_seo[j][2].strip() == '' or data_seo[j][2].strip() == '0'):
                                    updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 3), 'values': [[val_impr]]})
                                if (len(data_seo[j]) <= 3 or data_seo[j][3].strip() == '' or data_seo[j][3].strip() == '0'):
                                    updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 4), 'values': [[val_clicks]]})
                                if (len(data_seo[j]) <= 4 or data_seo[j][4].strip() == '' or data_seo[j][4].strip() == '0'):
                                    updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 5), 'values': [[val_ctr]]})
                                if (len(data_seo[j]) <= 5 or data_seo[j][5].strip() == '' or data_seo[j][5].strip() == '0'):
                                    updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 6), 'values': [[val_pos]]})
                                break
                        break
                if not encontrou:
                    print(f"AVISO: Não encontrou {url} ({mes_label}) na tabela SEO-SITES!")

    # --- Atualize as sessões do GA4 para todos os meses ---
    # Supondo que o cabeçalho está na linha 1 (índice 0), coluna H (índice 7)
    header_sessoes = data_sheets113[0][7:]  # Pega só os meses (colunas I, J, K...)
    linha_inicio_sessoes = 1  # Dados começam na linha 2 (índice 1)

    for col_idx, mes_num in enumerate(header_sessoes):
        mes_num = str(mes_num).strip()
        if not mes_num.isdigit():
            continue
        mes_label = f"{meses_pt[str(int(mes_num))]}-25"
        for row in data_sheets113[linha_inicio_sessoes:]:
            if len(row) <= 7 + col_idx or not row[7].strip():
                continue
            dominio = normalize_url(row[7])
            sessoes = sanitize_metric(row[7 + col_idx])
            encontrou = False
            for i, seo_row in enumerate(data_seo):
                seo_url = normalize_url(''.join(seo_row))
                if dominio == seo_url:
                    for j in range(i+1, min(i+20, len(data_seo))):
                        if len(data_seo[j]) > 1 and data_seo[j][1].strip() == mes_label:
                            valor_atual = data_seo[j][6] if len(data_seo[j]) > 6 else ''
                            print(f"Atualizando sessões de {dominio} ({mes_label}) na linha {j+1}: {valor_atual} -> {sessoes}")
                            if valor_atual.strip() == '' or valor_atual.strip() == '0':
                                updates.append({'range': gspread.utils.rowcol_to_a1(j+1, 7), 'values': [[sessoes]]})
                            encontrou = True
                            break
                    break
            if not encontrou:
                print(f"AVISO: Não encontrou {dominio} ({mes_label}) na tabela SEO-SITES!")

    # --- Executa todas as atualizações em lote ---
    if updates:
        sheet_seo.batch_update([{'range': u['range'], 'values': u['values']} for u in updates])
        print(f"{len(updates)} células atualizadas em lote!")
    else:
        print("Nenhuma célula precisou ser atualizada.")

# Executar menu principal
if __name__ == "__main__":
    menu_principal()