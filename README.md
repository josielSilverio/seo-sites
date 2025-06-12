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

### Execução Básica
```bash
python ler_seo-sites.py
```

### O que o script faz:

1. **🔍 Conexão**: Conecta-se à planilha Google Sheets usando as credenciais
2. **📊 Leitura**: Lê dados das abas "Sheet113" e "SEO SITES"
3. **🔄 Processamento**: Normaliza URLs e mapeia dados entre as planilhas
4. **✏️ Atualização**: Atualiza células vazias ou com valor "0" na planilha de destino
5. **📈 Relatório**: Exibe logs detalhados das operações realizadas

### Exemplo de Saída:
```
Abas disponíveis na planilha:
Sheet113
SEO SITES

Atualizando example.com (mar-25) na linha 15: Impr: 0 -> 1500, Cliques: 0 -> 45, CTR: 0 -> 3,00, Pos: 0 -> 12,50
Atualizando sessões de example.com (mar-25) na linha 15: 0 -> 890

125 células atualizadas em lote!
```

## 📁 Estrutura do Projeto

```
seo-sites/
│
├── ler_seo-sites.py     # Script principal
├── credentials.json     # Credenciais Google (não incluído no git)
└── README.md           # Este arquivo
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

**Versão Atual**: 1.0.0

### Changelog:
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