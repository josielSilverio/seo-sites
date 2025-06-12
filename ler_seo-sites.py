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

# --- Otimização: Atualização em lote (batch_update) para todas as colunas ---
def sanitize_metric(value):
    v = str(value).strip().lower()
    if v in ('', 'nenhum', 'none', 'nan', 'null', '-'):
        return '0'
    try:
        num = float(v.replace(',', '.'))
        # Sempre retorna com vírgula como separador decimal, sem aspas extras
        if num.is_integer():
            return str(int(num))
        else:
            # Formata para sempre usar vírgula e nunca aspas simples
            return f'{num:.2f}'.replace('.', ',')
    except ValueError:
        return '0'

updates = []

# Dicionário para converter número do mês para nome em português
meses_pt = {
    '1': 'jan', '2': 'fev', '3': 'mar', '4': 'abr', '5': 'mai', '6': 'jun',
    '7': 'jul', '8': 'ago', '9': 'set', '10': 'out', '11': 'nov', '12': 'dez'
}

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