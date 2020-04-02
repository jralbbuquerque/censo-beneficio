# -*- coding: utf-8 -*-
"""
@author: Júnior Albuquerque
"""

# Preâmbulo
import pandas as pd
from util import bd
from util import amc
from util import gini

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

def progressividadeEstados(estados, ano):
    """
        Calcula o índice a progressividade da parcela de aposentadorias e
        pensões dos estados brasileiros.

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
            - Índice de Gini
            - Valor da participação da parcela analisada
            - Progressividade da parcela analisada
            - Progressividade da parcela analisada até um salário min
            - Progressividade da parcela analisada acima de um sálario min
    """  
    
    # Definição dos logs para controle da execução
    log_inicializacao = """
    =====================================================================
    = PROGRESSIVIDADE DAS APO. E PENSÕES ESTADOS BRASILEIROS - {}     =   
    """.format(ano)
    
    log_finalizacao = """
    = PROCESSO FINALIZADO                                                =
    ======================================================================
    """
    
    # Exibe log de inicialização
    print(log_inicializacao)
    
    # Importa o dicionário de variáveis
    anoAnalisado(ano)
    
    colunas = """COD UF GINI PARCELA_CH PROG_TOTAL 
        PROG_ATE_1SAL PROG_ACIMA_1SAL""".split()
    results = pd.DataFrame(data = [], columns = colunas)

    for k in estados:
        # Log de inicialização
        print('\r\tESTADO [{0}]...'.format(str.upper(k)), end="")
        
        # Query para o código dos estados
        sql = """
            SELECT {0} 
            FROM censo_{1}.domicilios_{2} 
            LIMIT 1
        """.format(var_uf, ano, k)
        
        # Atribui o código à variável cod_uf
        cod_uf = pd.read_sql_query(sql, conn).loc[0][0]
        # Como cada ano possui um conjunto de regras diferentes, foram 
        # dividas as análises em duas condições
        if ano == 2000:
            # Query para selecionar valores de renda subdividindo-os em total,
            # até um salário mínimo e acima de um salário mínimo
            sql = """SELECT
                        COALESCE({0}, 0) AS renda,
                        COALESCE(ROUND({1}), 0) AS peso,
                        COALESCE({2}, 0) AS ben_tot,
                        COALESCE(CASE WHEN {2} <= {5} 
                            THEN {2} ELSE 0 END, 0) AS ben_1sal,
                        COALESCE(CASE WHEN {2} > {5} 
                            THEN {2} ELSE 0 END, 0) AS ben_nsal
                    FROM censo_{3}.pessoas_{4}
                    WHERE {0} <> 0
                        AND {0} IS NOT NULL
                    ORDER BY {0} ASC
            """.format(var_renda_pessoa, var_peso, var_renda_aposen, ano, k, salario_min)
            
            # Corrige nome do estado Rio Grande do Norte
            if k == "rn1":
                k = "rn"
        
        elif ano == 2010:
            # Query para selecionar valores de renda subdividindo-os em total,
            # até um salário mínimo e acima de um salário mínimo
            sql = """SELECT
                        COALESCE({0}, 0) AS renda,
                        COALESCE(ROUND({1}), 0) AS peso,
                        COALESCE(CASE WHEN {2} = 1 
                            THEN {3} ELSE 0 END, 0) AS ben_tot,
                        COALESCE(CASE WHEN {3} > {4} 
                            THEN 0 WHEN {3} <= {4} AND {2} = 1 
                            THEN {3} END, 0) AS ben_1sal,
                        COALESCE(CASE WHEN {3} <= {4} 
                            THEN 0 WHEN {3} > {4} AND {2} = 1 
                            THEN {3} END, 0) AS ben_nsal
                    FROM censo_{5}.pessoas_{6}
                    WHERE {0} <> 0
                        AND {0} IS NOT NULL
                    ORDER BY {0} ASC
            """.format(var_renda_pessoa, var_peso, tipo_aposen, 
                var_renda_aposen, salario_min, ano, k)
            # Corrige o nome do estado de São Paulo
            if (k == "sp1") or (k == "sp2_rm"):
                k = "sp"

        # Ordena os dados
        df = pd.read_sql_query(sql, conn)
        df = df.sort_values('renda', kind = 'mergesorted')
        
        # Cálcula o Índice de Gini
        df_aux = df[['renda', 'peso']]
        gini_estado = gini.gini(df_aux, sort=0)
        
        # Cálcula a participação da parcela analisada
        df_aux = df[['ben_tot', 'peso']]
        parcela_total = gini.gini(df_aux, sort=0)
        # Cálcula a progressividade da parcela analisada
        progressividade_total = gini_estado - parcela_total
        
        # Cálcula a participação da parcela analisada até um salário min
        df_aux = df[['ben_1sal', 'peso']]
        parcela_ate_1sal = gini.gini(df_aux, sort=0)
        # Cálcula a progressividade da parcela analisada até um salário min
        progressividade_ate_1sal = gini_estado - parcela_ate_1sal
        
        # Cálcula a participação da parcela analisada acima de um salário min
        df_aux = df[['ben_nsal', 'peso']]
        parcela_acima_1sal = gini.gini(df_aux, sort=0)
        # Cálcula a progressividade da parcela analisada acima de um salário min
        progressividade_acima_1sal = gini_estado - parcela_acima_1sal
            
        # cria o dicionário de resultados
        dict_results = {
            "COD": cod_uf,
            "UF": str.upper(k),
            "GINI": gini_estado,
            "PARCELA_CH": parcela_total,
            "PROG_TOTAL": progressividade_total, 
            "PROG_ATE_1SAL": progressividade_ate_1sal,
            "PROG_ACIMA_1SAL": progressividade_acima_1sal
            }
        
        results = results.append(dict_results, ignore_index=True)
        
        # Log de finalização
        print('\r\t\t\t\tESTADO FINIALIZADO!'.format(str.upper(k)), end="")
    print('\r\t ** TODOS OS ESTADOS FORAM FINALIZADOS COM SUCESSO **',end="")
    print('\n' + log_finalizacao)
    return results


def progressividadeCidades(estados, ano):
    """
        Calcula o índice a progressividade da parcela de aposentadorias e
        pensões das cidades brasileiras.

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
            - Índice de Gini
            - Valor da participação da parcela analisada
            - Progressividade da parcela analisada
            - Progressividade da parcela analisada até um salário min
            - Progressividade da parcela analisada acima de um sálario min
    """  
    
    # Definição dos logs para controle da execução
    log_inicializacao = """
    =====================================================================
    = PROGRESSIVIDADE DAS APO. E PENSÕES CIDADES BRASILEIRAS - {}     =   
    """.format(ano)
    
    log_finalizacao = """
    = PROCESSO FINALIZADO                                                =
    ======================================================================
    """
    
    # Exibe log de inicialização
    print(log_inicializacao)
    
    # Importa o dicionário de variáveis
    anoAnalisado(ano)
    
    colunas = """COD_UF UF COD_CIDADE_2000 COD_CIDADE_2010 
        GINI PARCELA_CH PROG_TOTAL PROG_ATE_1SAL PROG_ACIMA_1SAL""".split()
    results = pd.DataFrame(data = [], columns = colunas)

    for k in estados:
        # Log de inicialização
        print('\r\tESTADO [{0}]...'.format(str.upper(k)), end="")
        
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
                sql = """SELECT
                            COALESCE({0}, 0) AS renda,
                            COALESCE(ROUND({1}), 0) AS peso,
                            COALESCE({2}, 0) AS ben_tot,
                            COALESCE(CASE WHEN {2} <= {5} 
                                THEN {2} ELSE 0 END, 0) AS ben_1sal,
                            COALESCE(CASE WHEN {2} > {5} 
                                THEN {2} ELSE 0 END, 0) AS ben_nsal
                        FROM censo_{3}.pessoas_{4}
                        WHERE {0} <> 0
                            AND {0} IS NOT NULL
                            AND {6} = {7}
                        ORDER BY {0} ASC
                """.format(var_renda_pessoa, var_peso, 
                    var_renda_aposen, ano, k, salario_min, var_cid_pessoas, i)

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
                sql = """SELECT
                            COALESCE({0}, 0) AS renda,
                            COALESCE(ROUND({1}), 0) AS peso,
                            COALESCE(CASE WHEN {2} = 1 
                                THEN {3} ELSE 0 END, 0) AS ben_tot,
                            COALESCE(CASE WHEN {3} > {4} 
                                THEN 0 WHEN {3} <= {4} AND {2} = 1 
                                THEN {3} END, 0) AS ben_1sal,
                            COALESCE(CASE WHEN {3} <= {4} THEN 0 
                                WHEN {3} > {4} AND {2} = 1 
                                THEN {3} END, 0) AS ben_nsal
                        FROM censo_{5}.pessoas_{6}
                        WHERE {0} <> 0
                            AND {0} IS NOT NULL
                            AND {7} = {8}
                        ORDER BY {0} ASC
                """.format(var_renda_pessoa, var_peso, tipo_aposen, 
                    var_renda_aposen, salario_min, ano, k, var_cid, i)
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

            # Ordena os dados
            df = pd.read_sql_query(sql, conn)     
            df = df.sort_values('renda', kind = 'mergesorted')

            # Cálcula o Índice de Gini
            df_aux = df[['renda', 'peso']]
            gini_estado = gini.gini(df_aux, sort=0)

            # Cálcula a participação da parcela analisada
            df_aux = df[['ben_tot', 'peso']]
            parcela_total = gini.gini(df_aux, sort=0)
            # Cálcula a progressividade da parcela analisada
            progressividade_total = gini_estado - parcela_total

            # Cálcula a participação da parcela analisada até um salário min
            df_aux = df[['ben_1sal', 'peso']]
            parcela_ate_1sal = gini.gini(df_aux, sort=0)
            # Cálcula a progressividade da parcela analisada até um salário min
            progressividade_ate_1sal = gini_estado - parcela_ate_1sal

            # Cálcula a participação da parcela analisada acima de um salário min
            df_aux = df[['ben_nsal', 'peso']]
            parcela_acima_1sal = gini.gini(df_aux, sort=0)
            # Cálcula a progressividade da parcela analisada acima de um salário min
            progressividade_acima_1sal = gini_estado - parcela_acima_1sal

            # cria o dicionário de resultados
            dict_results = {
                "COD_UF": cod_uf,
                "UF": str.upper(uf),
                "COD_CIDADE_2000": codigo_amc[0],
                "COD_CIDADE_2010": codigo_cidade,
                "GINI": gini_estado,
                "PARCELA_CH": parcela_total,
                "PROG_TOTAL": progressividade_total, 
                "PROG_ATE_1SAL": progressividade_ate_1sal,
                "PROG_ACIMA_1SAL": progressividade_acima_1sal
                }

            results = results.append(dict_results, ignore_index=True)
        
        # Log de finalização
        print('\r\t\t\t\tESTADO FINIALIZADO!'.format(str.upper(k)), end="")
    print('\r\t ** TODOS OS ESTADOS FORAM FINALIZADOS COM SUCESSO **',end="")

    # Se o ano for de 2010 os dados são agrupados para as cidades que foram
    # divididas.
    if ano == 2010:
        results_agg = {'COD_UF': 'first',
                       'UF': 'first',
                       'COD_CIDADE_2000': 'first',
                       'COD_CIDADE_2010': lambda x: x.tolist(),
                       'GINI': 'mean',
                       'PARCELA_CH': 'mean',
                       'PROG_TOTAL': 'mean',
                       'PROG_ATE_1SAL': 'mean',
                       'PROG_ACIMA_1SAL': 'mean'}

        results = results.groupby('COD_CIDADE_2000').aggregate(results_agg)
        results.drop('COD_CIDADE_2000', axis = 1, inplace = True)        
        
    print('\n' + log_finalizacao)
    return results