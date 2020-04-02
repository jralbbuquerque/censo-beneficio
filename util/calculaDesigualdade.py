# -*- coding: utf-8 -*-
"""
@author: Júnior Albuquerque
"""

# Preâmbulo
import pandas as pd
import os
from util import bd
from util import gini
from util import amc

# Função que define um dicionário de variáveis relacionadas ao ano análisado 
def anoAnalisado(ano):
    global var_uf, var_cid, var_renda_domicilio, var_peso, var_renda_pessoa
    global var_cid_pessoas

    if ano == 2000:
        var_uf              = "v0102"
        var_cid             = "v0103"
        var_cid_pessoas     = "v1103" # caso especial do banco de dados
        var_renda_domicilio = "v7616"
        var_peso            = "p001"
        var_renda_pessoa    = "v4614"
    elif ano == 2010:
        var_uf              = "v0001"
        var_cid             = "v0002"
        var_renda_domicilio = "v6529"
        var_peso            = "v0010"
        var_renda_pessoa    = "v6527"

# Estabelece a conexão com o banco de dados
conn = bd.conn()

def giniEstados(estados, ano):
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
            - Gini da Renda Domiciliar
            - Gini da Renda Per Capita
            - Renda Média em 2000
            - Renda Média em 2010 (valores deflacionados)
    """  
    
    # Definição dos logs para controle da execução
    log_inicializacao = """
    =====================================================================
    = ÍNDICE DE GINI DOS ESTADOS BRASILEIROS - {}                     =   
    """.format(ano)
    
    log_finalização = """
    = PROCESSO FINALIZADO                                                =
    ======================================================================
    """
    
    # Exibe log de inicialização
    print(log_inicializacao)
    
    # Importa o dicionário de variáveis
    anoAnalisado(ano)
    
    # Colunas do DataFrame de resultados
    colunas = "COD UF GINI_RD GINI_RP RENDA_MEDIA RENDA_MEDIA_2010".split()
    
    # Cria o DataFrame de resultados
    results = pd.DataFrame(data = [], columns = colunas)

    # Para cada estado passado por parâmetros é realizado 
    # o cálculo das variáveis
    for k in estados:
        
        # Log de inicialização
        print('\r\t - ESTADO [{0}]...'.format(str.upper(k)), end="")

        # Query para o código dos estados
        sql = """
            SELECT {0} 
            FROM censo_{1}.domicilios_{2} 
            LIMIT 1
        """.format(var_uf, ano, k)
        
        # Atribui o código à variável cod_uf
        cod_uf = pd.read_sql_query(sql, conn).loc[0][0]

        # Query para a renda média
        sql = """
            SELECT (SUM({0} * {1}) / SUM({1})) 
            FROM censo_{2}.domicilios_{3}
        """.format(var_renda_domicilio, var_peso, ano, k)
        
        # Atribui a renda a variável renda
        renda = pd.read_sql_query(sql, conn).loc[0][0]   

        # Query para cálcular o ìndice de Gini domicililar
        # A query retorna a renda domiciliar
        sql = """
            SELECT COALESCE({0} , 0) AS RENDA, COALESCE(ROUND({1}), 0) AS PESO
            FROM censo_{2}.domicilios_{3}
            """.format(var_renda_domicilio, var_peso, ano, k)
        
        # Cria um DataFrame para parametrizar a função gini
        df = pd.read_sql_query(sql, conn)
        gini_RD = gini.gini(df, sort=1)


        # Query para cálcular o índice de gini renda per capita
        # Considerando apenas pessoas com renda e acima de 
        # 10 anos (métrica do IBGE)
        sql = """
            SELECT COALESCE({0} , 0) AS RENDA, COALESCE(ROUND({1}) , 0) AS PESO
            FROM censo_{2}.pessoas_{3} 
            WHERE {0} <> 0 
                AND {0} IS NOT NULL
            """.format(var_renda_pessoa, var_peso, ano, k)
        
        # Cria um DataFrame para parametrizar a função gini
        df = pd.read_sql_query(sql, conn)
        gini_RP = gini.gini(df, sort=1)
        
        # Correções nos dados tais como nome dos estados, valores
        # deflacionados, dados repetidos e etc.
        if ano == 2000:
            # Corrige nome do estado Rio Grande do Norte
            if k == "rn1":
                k = "rn"
            # Ajuste da renda per capita de julho de 2000 para valores 
            # em agosto de 2010 - 99,19% de inflação no INCP
            renda2010 = renda + (renda * 0.9919037)    
        elif ano == 2010:
            # Corrige o nome do estado de São Paulo
            if (k == "sp1") or (k == "sp2_rm"):
                k = "sp"    
            # Não há ajuste de valores no ano de 2010
            renda2010 = renda  
        
        # cria o dicionário de resultados
        dict_results = {
            "COD": cod_uf,
            "UF": str.upper(k),
            "GINI_RD": gini_RD,
            "GINI_RP": gini_RP, 
            "RENDA_MEDIA": renda,
            "RENDA_MEDIA_2010": renda2010
            }
        
        # Adiciona os resultados no DataFrame de results a cada interação
        results = results.append(dict_results, ignore_index=True)
        
        # Log de finalização
        print('\r\t\t\t\tESTADO FINIALIZADO!'.format(str.upper(k)), end="")
    print('\r\t ** TODOS OS ESTADOS FORAM FINALIZADOS COM SUCESSO **',end="")
    print('\n' + log_finalização)
    return results

def giniCidades(estados, ano):
    """
        Calcula o índice de gini e renda média das cidades brasileiras.

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
            - Código da Cidade em 2000
            - Código da Cidade em 2010
            - Gini da Renda Domiciliar
            - Gini da Renda Per Capita
            - Renda Média em 2000
            - Renda Média em 2010 (valores deflacionados)
    """  
    
    # Definição dos logs para controle da execução
    log_inicializacao = """
    =====================================================================
    = ÍNDICE DE GINI DAS CIDADES BRASILEIROS - {}                     =   
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
    colunas = """COD_UF UF COD_CIDADE_2000 COD_CIDADE_2010 GINI_RD GINI_RP 
                RENDA_MEDIA RENDA_MEDIA_2010""".split()
    
    # Cria o DataFrame de resultados
    results = pd.DataFrame(data = [], columns = colunas)
    
    for k in estados:
        # Log de inicialização
        print('\r\t - ESTADO [{0}]...'.format(str.upper(k)), end="")

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
            
            sql = """
                SELECT (SUM({0} * {1}) / SUM({1})) 
                FROM censo_{2}.domicilios_{3}
                WHERE {4} = '{5}'
            """.format(var_renda_domicilio, var_peso, ano, k, var_cid, i)
            
            # Atribui a renda a variável renda
            renda = pd.read_sql_query(sql, conn).loc[0][0]   

            # Query para cálcular o ìndice de Gini domicililar
            # A query retorna a renda domiciliar
            sql = """
                SELECT COALESCE({0} , 0) AS RENDA, 
                    COALESCE(ROUND({1}), 0) AS PESO
                FROM censo_{2}.domicilios_{3}
                WHERE {4} = '{5}'
                """.format(var_renda_domicilio, var_peso, ano, k, var_cid, i)

            # Cria um DataFrame para parametrizar a função gini
            df = pd.read_sql_query(sql, conn)
            gini_RD = gini.gini(df, sort=1)
            
            # cria variável auxiliar para corrigir o problema da variável com o 
            # codigo da cidade mudar na base de dados do censo de 2000
            if ano == 2000:
                aux = var_cid_pessoas
            elif ano == 2010:
                aux = var_cid
            
            # Query para cálcular o índice de gini renda per capita
            # Considerando apenas pessoas com renda e acima de 
            # 10 anos (métrica do IBGE)
                
            sql = """
                SELECT COALESCE({0} , 0) AS RENDA, 
                    COALESCE(ROUND({1}) , 0) AS PESO
                FROM censo_{2}.pessoas_{3} 
                WHERE {0} <> 0 
                    AND {0} IS NOT NULL
                    AND {4} = '{5}'
                """.format(var_renda_pessoa, var_peso, ano, k, aux, i)

            # Cria um DataFrame para parametrizar a função gini
            df = pd.read_sql_query(sql, conn)
            gini_RP = gini.gini(df, sort=1)

            # Correções nos dados tais como nome dos estados, valores
            # deflacionados, dados repetidos e etc.
            if ano == 2000:
                # Corrige nome do estado Rio Grande do Norte
                if k == "rn1":
                    uf = "rn"
                else:
                    uf = k    
                # Ajuste da renda per capita de julho de 2000 para valores 
                # em agosto de 2010 - 99,19% de inflação no INCP
                renda2010 = renda + (renda * 0.9919037)  
                
                # AMC do município em 2000, agregando os municípios pelo seu 
                # código do ano de 2000
                codigo_amc = []
                codigo_amc.append(i)
                
                codigo_cidade = i
                
            elif ano == 2010:
                # Corrige o nome do estado de São Paulo
                if (k == "sp1") or (k == "sp2_rm"):
                    uf = "sp"  
                else:
                    uf = k    
                # Não há ajuste de valores no ano de 2010
                renda2010 = renda  
            
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
                "GINI_RD": gini_RD,
                "GINI_RP": gini_RP, 
                "RENDA_MEDIA": renda,
                "RENDA_MEDIA_2010": renda2010
                }

            # Adiciona os resultados no DataFrame de results a cada interação
            results = results.append(dict_results, ignore_index=True)
        # Log de finalização
        print('\r\t\t\t\tESTADO FINIALIZADO!'.format(str.upper(k)), end="")
    print('\r\t ** TODOS OS ESTADOS FORAM FINALIZADOS COM SUCESSO **',end="")
        
    if ano == 2010:
        results_agg = {'COD_UF': 'first',
                       'UF': 'first',
                       'COD_CIDADE_2000': 'first',
                       'COD_CIDADE_2010': lambda x: x.tolist(),
                       'GINI_RD': 'mean',
                       'GINI_RP': 'mean',
                       'RENDA_MEDIA': 'mean',
                       'RENDA_MEDIA_2010': 'mean'}

        results = results.groupby('COD_CIDADE_2000').aggregate(results_agg)
        results.drop('COD_CIDADE_2000', axis = 1, inplace = True)
    
    print('\n' + log_finalizacao)
    os.system('cls' if os.name=='nt' else 'clear')
    return results