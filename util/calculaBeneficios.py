# -*- coding: utf-8 -*-
"""
@author: Júnior Albuquerque
"""

# Preâmbulo
import pandas as pd
from util import bd
from util import amc

# Função que define um dicionário de variáveis relacionadas ao ano análisado 
def anoAnalisado(ano):
    global var_uf, var_cid, var_renda_domicilio, var_peso, var_renda_pessoa
    global var_cid_pessoas, var_renda_aposen, salario_min, tipo_aposen

    if ano == 2000:
        var_uf              = "v0102"
        var_cid             = "v0103"
        var_cid_pessoas     = "v1103" # caso especial do banco de dados
        var_renda_domicilio = "v7616"
        var_peso            = "p001"
        var_renda_pessoa    = "v4614"
        var_renda_aposen    = "v4573"
        salario_min         = 151
        
    elif ano == 2010:
        var_uf              = "v0001"
        var_cid             = "v0002"
        var_renda_domicilio = "v6529"
        var_peso            = "v0010"
        var_renda_pessoa    = "v6527"
        var_renda_aposen    = "v6591"
        tipo_aposen         = "v0656"
        salario_min         = 510

# Estabelece a conexão com o banco de dados
conn = bd.conn()

def beneficioEstados(estados, ano):
    """
        Calcula o índice de gini e renda média dos estados brasileiros.

    Parâmetros
    ----------
        estados: array com os estados brasileiros
                 ex: ["ac","pa", "ce", ...]
        ano: inteiro com o ano a ser analisado

    Retorno
    -------
        DataFrame com os resultados:
            - Código do Estado
            - Sigla da Unidade Federativa
            - Valor da renda total do estado
            - Valor da renda referente aos beneficios de apo e pensão
            - Percentual de participação desses beneficios
            - Percentual de participação dos beneficios até um salário min
            - Percentual de participação dos beneficios acima de um sálario min
    """  
    
    # Definição dos logs para controle da execução
    log_inicializacao = """
    =====================================================================
    = PARTICIPAÇÃO DAS APO. E PENSÕES ESTADOS BRASILEIROS - {}        =   
    """.format(ano)
    
    log_finalizacao = """
    = PROCESSO FINALIZADO                                                =
    ======================================================================
    """
    
    # Exibe log de inicialização
    print(log_inicializacao)
    
    # Importa o dicionário de variáveis
    anoAnalisado(ano)

    # Colunas do DataFrame de resultados
    colunas = """COD UF RENDA_TOTAL RENDA_BENEFICIOS PARTICIPACAO_TOTAL 
        PARTICIPACAO_ATE_1SAL PARTICIPACAO_ACIMA_1SAL""".split()
    
    # Cria o DataFrame de resultados
    results = pd.DataFrame(data = [], columns = colunas)

    # Para cada estado passado por parâmetros é realizado 
    # o cálculo das variáveis
    for k in estados:
        # Log de inicialização
        print('\r\tESTADO [{0}]...'.format(str.upper(k)), end="")

        # Query para o código dos estados
        sql = """
            SELECT {0} 
            FROM censo_{1}.domicilios_{2} 
            LIMIT 1
        """.format(var_uf, ano, k)
        
        # Atribui o código à variável cod_ufva
        cod_uf = pd.read_sql_query(sql, conn).loc[0][0]
        
        # Rendimento total do estado
        sql = """SELECT SUM({0} * {1})
            FROM censo_{2}.pessoas_{3}
            """.format(var_renda_pessoa, var_peso, ano, k)
        
        renda_total = pd.read_sql_query(sql, conn).loc[0][0]
        
        if ano == 2000:
            # Rendimento total dos beneficios do estado
            sql = """SELECT SUM({0} * {1}) 
                FROM censo_{2}.pessoas_{3}
                """.format(var_renda_aposen, var_peso, ano, k)
        else:
            # Rendimento total dos beneficios do estado
            sql = """SELECT SUM({0} * {1}) 
                FROM censo_{2}.pessoas_{3} 
                WHERE {4} = 1
                """.format(var_renda_aposen, var_peso, ano, k, tipo_aposen)
        
        renda_beneficios = pd.read_sql_query(sql, conn).loc[0][0]
        
        if ano == 2000:
            # Rendimento total dos beneficios acima de 1 salário minímo
            sql = """SELECT SUM({0} * {1}) 
                FROM censo_{2}.pessoas_{3} WHERE {0} > {4}
                """.format(var_renda_aposen, var_peso, ano, k, salario_min)
        else:
            # Rendimento total dos beneficios acima de 1 salário minímo
            sql = """SELECT SUM({0} * {1}) 
                FROM censo_{2}.pessoas_{3} WHERE {0} > {4} AND {5} = 1
                """.format(var_renda_aposen, var_peso, 
                    ano, k, salario_min, tipo_aposen)
            
        renda_beneficios_nsal = pd.read_sql_query(sql, conn).loc[0][0]
        
        if ano == 2000:
            # Rendimento total dos beneficios igual ou menor que 
            # 1 salário minímo
            sql = """SELECT SUM({0} * {1}) 
                FROM censo_{2}.pessoas_{3} WHERE {0} <= {4}
                """.format(var_renda_aposen, var_peso, ano, k, salario_min)
        else: 
            # Rendimento total dos beneficios acima de 1 salário minímo
            sql = """SELECT SUM({0} * {1}) 
                FROM censo_{2}.pessoas_{3} WHERE {0} <= {4} AND {5} = 1
                """.format(var_renda_aposen, var_peso, 
                ano, k, salario_min, tipo_aposen)
            
        renda_beneficios_1sal = pd.read_sql_query(sql, conn).loc[0][0]
        
        # Correções nos dados tais como nome dos estados, valores
        # deflacionados, dados repetidos e etc.
        if ano == 2000:
            # Corrige nome do estado Rio Grande do Norte
            if k == "rn1":
                k = "rn"
                
        elif ano == 2010:
            # Corrige o nome do estado de São Paulo
            if (k == "sp1") or (k == "sp2_rm"):
                k = "sp"    

        # cria o dicionário de resultados
        dict_results = {
            "COD": cod_uf,
            "UF": str.upper(k),
            "RENDA_TOTAL": renda_total,
            "RENDA_BENEFICIOS": renda_beneficios, 
            "PARTICIPACAO_TOTAL": renda_beneficios / renda_total,
            "PARTICIPACAO_ATE_1SAL": renda_beneficios_1sal / renda_total,
            "PARTICIPACAO_ACIMA_1SAL": renda_beneficios_nsal / renda_total
            }
        
        results = results.append(dict_results, ignore_index=True)
                
        # Log de finalização
        print('\r\t\t\t\tESTADO FINIALIZADO!'.format(str.upper(k)), end="")
    print('\r\t ** TODOS OS ESTADOS FORAM FINALIZADOS COM SUCESSO **',end="")
    print('\n' + log_finalizacao)
    return results

       
def beneficioCidades(estados, ano):
    """
        Calcula o índice de gini e renda média dos estados brasileiros.

    Parâmetros
    ----------
        estados: array com os estados brasileiros
                 ex: ["ac","pa", "ce", ...]
        ano: inteiro com o ano a ser analisado

    Retorno
    -------
        DataFrame com os resultados:
            - Código do Estado
            - Sigla da Unidade Federativa
            - Código da cidade no ano de 2000
            - Código da cidade no ano de 2010
            - Valor da renda total do estado
            - Valor da renda referente aos beneficios de apo e pensão
            - Percentual de participação desses beneficios
            - Percentual de participação dos beneficios até um salário min
            - Percentual de participação dos beneficios acima de um sálario min
    """
    # Definição dos logs para controle da execução
    log_inicializacao = """
    =====================================================================
    = PARTICIPAÇÃO DAS APO. E PENSÕES CIDADES BRASILEIRAS - {}        =   
    """.format(ano)
    
    log_finalizacao = """
    = PROCESSO FINALIZADO                                                =
    ======================================================================
    """
    
    # Exibe log de inicialização
    print(log_inicializacao)
    
    # Importa o dicionário de variáveis
    anoAnalisado(ano)

    # Colunas do DataFrame de resultados
    colunas = """COD_UF UF COD_CIDADE_2000 COD_CIDADE_2010 
                RENDA_TOTAL RENDA_BENEFICIOS RENDA_BENEFICIOS_ATE_1SAL 
                RENDA_BENEFICIOS_ACIMA_1SAL PARTICIPACAO_TOTAL 
                PARTICIPACAO_ATE_1SAL PARTICIPACAO_ACIMA_1SAL""".split()
    
    # Cria o DataFrame de resultados
    results = pd.DataFrame(data = [], columns = colunas)    

    for k in estados:
        # Log de inicialização
        print('\r\tESTADO [{0}]...'
              .format(str.upper(k)), end="")

        # Query para o código dos estados
        sql = """
            SELECT {0} 
            FROM censo_{1}.domicilios_{2} 
            LIMIT 1
        """.format(var_uf, ano, k)
        
        # Atribui o código à variável cod_uf
        cod_uf = pd.read_sql_query(sql, conn).loc[0][0]
        
        # Seleciona os estados e municpios
        sql = """
            SELECT DISTINCT({0}) 
            FROM censo_{1}.domicilios_{2}
        """.format(var_cid, ano, k)
        
        cod_cid = pd.read_sql_query(sql, conn) 
        
        for i in cod_cid.iloc[:,0]:  
            # Como cada ano possui um conjunto de regras diferentes, foram 
            # dividas as análises em duas condições
            if ano == 2000:
                # Rendimento total do estado
                sql = """SELECT COALESCE(SUM({0} * {1}), 0)
                    FROM censo_{2}.pessoas_{3}
                    WHERE {4} = {5}
                    """.format(var_renda_pessoa, var_peso, ano, k,
                        var_cid_pessoas, i)

                renda_total = pd.read_sql_query(sql, conn).loc[0][0]

                # Rendimento total dos beneficios do estado
                sql = """SELECT COALESCE(SUM({0} * {1}), 0) 
                    FROM censo_{2}.pessoas_{3}
                    WHERE {4} = {5}
                        AND {0} <> 0
                    """.format(var_renda_aposen, var_peso, ano, k, 
                        var_cid_pessoas, i)
                
                renda_beneficios = pd.read_sql_query(sql, conn).loc[0][0]
                
                # Rendimento total dos beneficios acima de 1 salário minímo
                sql = """SELECT COALESCE(SUM({0} * {1}), 0) 
                    FROM censo_{2}.pessoas_{3} 
                    WHERE {0} > {4} 
                        AND {5} = {6}
                        AND {0} <> 0
                    """.format(var_renda_aposen, var_peso, ano, k, 
                        salario_min, var_cid_pessoas, i)
                
                renda_beneficios_nsal = pd.read_sql_query(sql, conn).loc[0][0]
                
                # Rendimento total dos beneficios igual ou menor que 
                # 1 salário minímo
                sql = """SELECT COALESCE(SUM({0} * {1}), 0) 
                    FROM censo_{2}.pessoas_{3} 
                    WHERE {0} <= {4} 
                        AND {5} = {6}
                        AND {0} <> 0
                    """.format(var_renda_aposen, var_peso, ano, k, 
                        salario_min, var_cid_pessoas, i)
                
                renda_beneficios_1sal = pd.read_sql_query(sql, conn).loc[0][0]
                
                # Corrige nome do estado Rio Grande do Norte
                if k == "rn1":
                    uf = "rn"
                else:
                    uf = k    
                
                # AMC do município em 2000, agregando os municípios pelo seu 
                # código do ano de 2000
                codigo_amc = []
                codigo_amc.append(i)
                
                codigo_cidade = i
                
            elif ano == 2010:
                # Rendimento total da cidade
                sql = """SELECT SUM({0} * {1})
                    FROM censo_{2}.pessoas_{3}
                    WHERE {4} = {5} 
                    """.format(var_renda_pessoa, var_peso, ano, k, 
                        var_cid, i, tipo_aposen)

                renda_total = pd.read_sql_query(sql, conn).loc[0][0]

                # Rendimento total dos beneficios do estado
                sql = """SELECT SUM({0} * {1}) 
                    FROM censo_{2}.pessoas_{3}
                    WHERE {4} = {5} 
                        AND {6} = 1
                        AND {7} <> 0 
                    """.format(var_renda_pessoa, var_peso, ano, k, 
                        var_cid, i, tipo_aposen, var_renda_aposen)
                
                renda_beneficios = pd.read_sql_query(sql, conn).loc[0][0]
                
                # Rendimento total dos beneficios acima de 1 salário minímo
                sql = """SELECT SUM({0} * {1}) 
                    FROM censo_{2}.pessoas_{3} 
                    WHERE {4} > {5}
                        AND {6} = {7} 
                        AND {8} = 1
                        AND {4} <> 0
                    """.format(var_renda_pessoa, var_peso, ano, k, 
                        var_renda_aposen, salario_min, var_cid, i, tipo_aposen)
                
                renda_beneficios_nsal = pd.read_sql_query(sql, conn).loc[0][0]
                
                # Rendimento total dos beneficios igual ou menor que 
                # 1 salário minímo
                sql = """SELECT SUM({0} * {1}) 
                    FROM censo_{2}.pessoas_{3} 
                    WHERE {4} <= {5} 
                        AND {6} = {7} 
                        AND {8} = 1
                        AND {4} <> 0
                    """.format(var_renda_pessoa, var_peso, ano, k, 
                        var_renda_aposen, salario_min, var_cid, i, tipo_aposen)
                
                renda_beneficios_1sal = pd.read_sql_query(sql, conn).loc[0][0]
                
                # Corrige o nome do estado de São Paulo
                if (k == "sp1") or (k == "sp2_rm"):
                    uf = "sp"  
                else:
                    uf = k     
            
                # AMC do município em 2000, agregando os municípios pelo seu 
                # código do ano de 2000
                old_codigo = cod_uf + i
                old_codigo = int(old_codigo)
                codigo_amc = amc.AMC(old_codigo, 2000)
                
                codigo_cidade = 0
                codigo_cidade = cod_uf + i
        
            # cria o dicionário de resultados
            dict_results = {
                "COD_UF": cod_uf,
                "UF": str.upper(uf),
                "COD_CIDADE_2000": codigo_amc[0],
                "COD_CIDADE_2010": codigo_cidade,
                "RENDA_TOTAL": renda_total,
                "RENDA_BENEFICIOS": renda_beneficios, 
                "RENDA_BENEFICIOS_ATE_1SAL": renda_beneficios_1sal,
                "RENDA_BENEFICIOS_ACIMA_1SAL": renda_beneficios_nsal,
                "PARTICIPACAO_TOTAL": renda_beneficios / renda_total,
                "PARTICIPACAO_ATE_1SAL": renda_beneficios_1sal / renda_total,
                "PARTICIPACAO_ACIMA_1SAL": renda_beneficios_nsal / renda_total
                }

            results = results.append(dict_results, ignore_index=True)
    
        # Log de finalização
        print('\r\t\t\t\tESTADO FINIALIZADO!'.format(str.upper(k)), end="")
    print('\r\t ** TODOS OS ESTADOS FORAM FINALIZADOS COM SUCESSO **',end="")

    if ano == 2010:
        results_agg = {'COD_UF': 'first',
                       'UF': 'first',
                       'COD_CIDADE_2000': 'first',
                       'COD_CIDADE_2010': lambda x: x.tolist(),
                       'RENDA_TOTAL': 'sum',
                       'RENDA_BENEFICIOS': 'sum',
                       'RENDA_BENEFICIOS_ATE_1SAL': 'sum',
                       'RENDA_BENEFICIOS_ACIMA_1SAL': 'sum',
                       'PARTICIPACAO_TOTAL': 'mean',
                       'PARTICIPACAO_ATE_1SAL': 'mean',
                       'PARTICIPACAO_ACIMA_1SAL': 'mean'}

        results = results.groupby('COD_CIDADE_2000').aggregate(results_agg)
        
        results['PARTICIPACAO_TOTAL'] = \
            results['RENDA_BENEFICIOS'] / results['RENDA_TOTAL']
        
        results['PARTICIPACAO_ATE_1SAL'] = \
            results['RENDA_BENEFICIOS_ATE_1SAL'] / results['RENDA_TOTAL']
        
        results['PARTICIPACAO_ACIMA_1SAL'] = \
            results['RENDA_BENEFICIOS_ACIMA_1SAL'] / results['RENDA_TOTAL']
            
        results.drop('COD_CIDADE_2000', axis = 1, inplace = True)
    
    results.drop("""RENDA_BENEFICIOS_ATE_1SAL RENDA_BENEFICIOS_ACIMA_1SAL
                 """.split(), axis=1, inplace=True)
    
    print('\n' + log_finalizacao)
    return results