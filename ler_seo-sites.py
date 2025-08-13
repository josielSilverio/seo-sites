#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from api_extractor import SEODataExtractor


def print_header():
    print("\n" + "=" * 60)
    print("🔧 SEO Sites - Menu Principal")
    print("=" * 60)


def opcao_1_sync_pendentes(extractor: SEODataExtractor):
    print("\n🚀 Sincronizando meses pendentes na aba SEO SITES...")
    resultado = extractor.preencher_meses_pendentes_vertical()
    print(f"\n✅ Concluído. Meses processados: {resultado.get('processed_months', 0)}")


def opcao_2_preencher_mes(extractor: SEODataExtractor):
    rotulo = input("Informe o mês (ex: mar-25): ").strip().lower()
    if not rotulo:
        print("❌ Mês não pode estar vazio.")
        return
    try:
        meses_map = {
            'jan': 1, 'fev': 2, 'mar': 3, 'abr': 4, 'mai': 5, 'jun': 6,
            'jul': 7, 'ago': 8, 'set': 9, 'out': 10, 'nov': 11, 'dez': 12
        }
        mes_str, ano_curto = rotulo.split('-')
        ano = int('20' + ano_curto)
        mes_num = meses_map[mes_str]
    except Exception:
        print("❌ Formato inválido. Use: mes-ano (ex: mar-25)")
        return

    import datetime
    if mes_num == 12:
        next_month = datetime.date(ano + 1, 1, 1)
    else:
        next_month = datetime.date(ano, mes_num + 1, 1)
    fim_mes = next_month - datetime.timedelta(days=1)
    inicio = datetime.date(ano, mes_num, 1)
    print(f"\n📅 Período: {inicio} a {fim_mes}")

    dados_gsc = extractor.extrair_dados_search_console(inicio.strftime('%Y-%m-%d'), fim_mes.strftime('%Y-%m-%d'))
    dados_ga4 = extractor.extrair_dados_ga4(inicio.strftime('%Y-%m-%d'), fim_mes.strftime('%Y-%m-%d'))
    extractor.atualizar_sheet113_vertical(dados_gsc, dados_ga4, rotulo)


def opcao_3_testar_conexoes(extractor: SEODataExtractor):
    print("\n🧪 Testando conexões...")
    try:
        # Jan 2025 semana 1 como quick check
        gsc = extractor.extrair_dados_search_console('2025-01-01', '2025-01-07')
        ga4 = extractor.extrair_dados_ga4('2025-01-01', '2025-01-07')
        print(f"   ✅ GSC OK ({len(gsc)} registros) | GA4 OK ({len(ga4)} registros)")
    except Exception as e:
        print(f"   ❌ Falha nos testes: {e}")


def main():
    extractor = SEODataExtractor()

    while True:
        print_header()
        print("1 - Sincronizar meses pendentes na SEO SITES")
        print("2 - Preencher um mês específico na SEO SITES")
        print("3 - Testar conexões (GSC + GA4)")
        print("4 - Sair")

        opcao = input("\nEscolha (1-4): ").strip()

        if opcao == '1':
            opcao_1_sync_pendentes(extractor)
        elif opcao == '2':
            opcao_2_preencher_mes(extractor)
        elif opcao == '3':
            opcao_3_testar_conexoes(extractor)
        elif opcao == '4':
            print("👋 Saindo...")
            break
        else:
            print("❌ Opção inválida. Escolha 1 a 4.")


if __name__ == "__main__":
    main()


