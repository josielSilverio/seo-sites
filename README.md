# SEO Sites - Automatizador de Dados SEO

## 📋 Descrição

Este projeto é uma ferramenta de automação em Python que integra dados de SEO entre diferentes planilhas do Google Sheets. O sistema lê dados de uma planilha principal ("Sheet113") e atualiza automaticamente uma planilha de relatórios SEO ("SEO SITES") com métricas como impressões, cliques, CTR, posição média e sessões do GA4.

## 🎯 Objetivo

Automatizar o processo de transferência e atualização de dados de SEO entre planilhas do Google Sheets, eliminando a necessidade de cópia manual e reduzindo erros humanos no processo de relatórios.

## ⚡ Funcionalidades

- **Integração Google Sheets**: Conecta-se automaticamente às planilhas via API do Google
- **Normalização de URLs**: Padroniza URLs para comparação eficiente
- **Mapeamento de Meses**: Converte datas numéricas para formato brasileiro (jan-25, fev-25, etc.)
- **Atualização em Lote**: Utiliza batch updates para otimizar performance
- **Sanitização de Dados**: Trata valores nulos, vazios e formata números corretamente
- **Logs Detalhados**: Exibe informações sobre todas as operações realizadas

### Métricas Processadas:
- 📈 **Impressões** - Número de vezes que o site apareceu nos resultados de busca
- 🖱️ **Cliques** - Número de cliques recebidos
- 📊 **CTR (Click-Through Rate)** - Taxa de cliques
- 📍 **Posição Média** - Posição média nos resultados de busca
- 👥 **Sessões GA4** - Dados de sessões do Google Analytics 4

## 🛠️ Tecnologias Utilizadas

- **Python 3.x**
- **gspread** - Biblioteca para integração com Google Sheets
- **oauth2client** - Autenticação OAuth2 para Google APIs
- **re** (regex) - Para processamento de strings e datas

## 📦 Pré-requisitos

1. **Python 3.6+** instalado no sistema
2. **Conta Google** com acesso às planilhas
3. **Projeto Google Cloud** configurado
4. **Credenciais de Serviço** do Google Cloud

## 🚀 Instalação

### Passo 1: Clone ou baixe o projeto
```bash
git clone [URL_DO_REPOSITORIO]
cd seo-sites
```

### Passo 2: Instale as dependências
```bash
pip install gspread oauth2client
```

### Passo 3: Configure as credenciais do Google

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative as APIs necessárias:
   - Google Sheets API
   - Google Drive API
4. Crie credenciais de conta de serviço:
   - Vá para "APIs e Serviços" > "Credenciais"
   - Clique em "Criar credenciais" > "Conta de serviço"
   - Baixe o arquivo JSON das credenciais
5. Renomeie o arquivo para `credentials.json` e coloque na pasta do projeto
6. Compartilhe suas planilhas com o email da conta de serviço

### Passo 4: Configure a planilha

Certifique-se de que sua planilha Google Sheets possui:
- Uma aba chamada **"Sheet113"** com os dados de origem
- Uma aba chamada **"SEO SITES"** para os dados de destino
- O formato correto de colunas conforme esperado pelo script

## ▶️ Como Usar

### Execução
```bash
python ler_seo-sites.py
```

O script apresenta um menu com duas opções:

### **1. 🚀 Preenchimento Automático Completo**
- Processa todos os meses disponíveis automaticamente
- Atualiza todas as métricas de uma só vez
- Modo original do script

### **2. 🎯 Preenchimento Interativo por Mês**
- **Nova funcionalidade!** 
- Permite escolher um mês específico para preencher
- Verifica se os dados estão disponíveis na Sheet113
- Oferece opção de revisar dados se houver incompatibilidade

### Fluxo do Modo Interativo:

1. **📋 Lista meses disponíveis** na Sheet113
2. **❓ Pergunta qual mês** você quer preencher
3. **🔍 Verifica disponibilidade** dos dados
4. **⚠️ Se não encontrar** → oferece opções:
   - Revisar Sheet113 e tentar novamente
   - Escolher outro mês
   - Sair
5. **✅ Se encontrar** → confirma e executa o preenchimento

### Exemplo de Uso Interativo:
```
🔧 AUTOMATIZADOR DE DADOS SEO - MENU PRINCIPAL
1 - Preenchimento automático completo (modo original)
2 - Preenchimento interativo por mês
3 - Sair

Escolha uma opção (1/2/3): 2

🔄 PREENCHIMENTO INTERATIVO DE DADOS SEO

📊 Meses disponíveis na Sheet113:
   GSC (Search Console): mar-25, abr-25
   GA4 (Analytics): mar-25, abr-25

❓ Qual mês você deseja preencher?
   Formato: mes-ano (ex: mar-25, jan-24)
   Digite o mês: mar-25

🔍 Verificando disponibilidade do mês 'mar-25':
   GSC: ✅ Disponível
   GA4: ✅ Disponível

✅ Dados encontrados para 'mar-25'!
   📈 Preenchendo dados do GSC (Search Console) e GA4 (Analytics)

❓ Confirmar preenchimento para 'mar-25'? (s/n): s

🚀 Iniciando preenchimento para mar-25...
   📈 example.com → Impr: 1500, Clicks: 45, CTR: 3,00, Pos: 12,50
   📊 example.com → Sessões: 890

✅ 5 células atualizadas com sucesso!
```

### O que o script faz:

1. **🔍 Conexão**: Conecta-se à planilha Google Sheets usando as credenciais
2. **📊 Leitura**: Lê dados das abas "Sheet113" e "SEO SITES"
3. **🔄 Processamento**: Normaliza URLs e mapeia dados entre as planilhas
4. **✏️ Atualização**: Atualiza células vazias ou com valor "0" na planilha de destino
5. **📈 Relatório**: Exibe logs detalhados das operações realizadas

## 📁 Estrutura do Projeto

```
seo-sites/
│
├── ler_seo-sites.py           # Script principal com menu interativo
├── credentials.json           # Credenciais Google (não incluído no git)
├── credentials_example.json   # Exemplo da estrutura do arquivo de credenciais
├── .gitignore                 # Arquivos e pastas ignorados pelo Git
└── README.md                  # Este arquivo
```

## ⚙️ Configurações

### URL da Planilha
Para alterar a planilha alvo, modifique a variável `spreadsheet_url` no script:
```python
spreadsheet_url = 'SUA_URL_AQUI'
```

### Mapeamento de Meses
O script mapeia automaticamente meses numéricos para o formato português:
- 1 → jan, 2 → fev, 3 → mar, etc.

## 🔧 Solução de Problemas

### ❌ Erro de Autenticação
- Verifique se o arquivo `credentials.json` está na pasta correta
- Confirme se as planilhas foram compartilhadas com o email da conta de serviço

### ❌ Aba não encontrada
- Certifique-se de que as abas "Sheet113" e "SEO SITES" existem
- Verifique se os nomes estão escritos exatamente como esperado

### ❌ Dados não atualizados
- O script só atualiza células vazias ou com valor "0"
- Verifique se os URLs estão sendo normalizados corretamente

## 📈 Versão

**Versão Atual**: 2.0.0

### Changelog:
- **v2.0.0**: 
  - ✨ **Nova funcionalidade**: Preenchimento interativo por mês
  - 🎯 Menu principal com opções de modo automático ou interativo
  - 🔍 Verificação inteligente de disponibilidade de dados
  - ⚠️ Sistema de alerta para incompatibilidades de dados
  - 🔄 Opção de revisar e tentar novamente
  - 📊 Interface mais amigável com emojis e cores
- **v1.0.0**: Versão inicial com funcionalidades básicas de sincronização de dados SEO

## 🤝 Contribuição

Para contribuir com o projeto:
1. Faça um fork do repositório
2. Crie uma branch para sua feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença [MIT](LICENSE) - veja o arquivo LICENSE para mais detalhes.

## 📞 Suporte

Para dúvidas ou problemas:
- Abra uma issue no repositório
- Entre em contato com a equipe de desenvolvimento

---

**Desenvolvido com ❤️ para automação de dados SEO** 