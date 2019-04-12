import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ds import bd
from ds import gini

def giniEstados( estados ):
    ## ---------------- ESTADOS ---------------- ##
    results = pd.DataFrame( data = [], columns = "COD UF Gini_RD Gini_RP RendaMedia RendaMedia2010".split() )

    conn = bd.conn()

    for k in estados:
        print('[{}]: ÍNDICE DE GINI. Processando Estados...'.format(str.upper(k)), end='\n')

        # Código dos estados
        sql_UF = "SELECT v0102 AS UF FROM censo_2000.domicilios_{} limit 1".format( k )
        df_UF = pd.read_sql_query(sql_UF, conn)
        cod_uf = df_UF.loc[0, 'uf']
        # print('      Cod UF: {} '.format(cod_uf), end='\n')

        # Renda média per capita
        sql_Renda = "SELECT \
                    ( SUM( v7616 * p001 ) / SUM( v7100 * p001 ) ) AS RP \
                    FROM censo_2000.domicilios_{}".format(k)
        df_Renda = pd.read_sql_query( sql_Renda, conn )
        renda = df_Renda.loc[ 0, 'rp' ]
        # Ajuste da renda per capita de julho de 2000 para valores em agosto de 2010
        # 99,19% de inflação no INCP
        renda2010 = renda + ( renda * 0.9919037 )    
        # print('      Renda: {} '.format('R$' + str(round(renda, 2))), end='\n')
        # print('      Renda 2010: {} '.format('R$' + str(round(renda2010, 2))), end='\n')

        # Índice de gini renda domiciliar      
        sql_RD = "SELECT \
                COALESCE( v7616 , 0 ) AS renda, COALESCE( ROUND( p001 ), 0 ) AS peso \
                FROM censo_2000.domicilios_{}".format(k)

        g_RD = gini.gini(sql_RD)
        # print('      Gini RD: {} '.format(round(g_RD[0], 4)), end='\n')


        # Índice de gini renda per capita
        # Considerando apenas pessoas com renda e acima de 10 anos (métrica do IBGE)
        sql_RP = "SELECT \
                COALESCE( v4614 , 0 ) AS renda, COALESCE( ROUND( p001 ) , 0 ) AS peso \
                FROM censo_2000.pessoas_{} WHERE v4614 <> 0 AND v4614 IS NOT NULL ORDER BY v4614 ASC".format(k)

        g_RP = gini.gini(sql_RP)
        # print('      Gini RP: {} '.format(round(g_RP[0], 4)), end='\n')

        results = results.append( {'COD': cod_uf,
                                    'UF': k,
                                    'Gini_RD': g_RD[0],
                                    'Gini_RP': g_RP[0],
                                    'RendaMedia': round(renda, 2),
                                    'RendaMedia2010': round(renda2010, 2)}, ignore_index=True )
    return results
    

def giniCidades( estados ):
    ## ---------------- MUNICÍPIOS ---------------- ##
    
    results = pd.DataFrame( data = [], columns = "UF COD Gini_RD Gini_RP RendaMedia RendaMedia2010".split() )
    conn = bd.conn()
    
    for k in estados:
        print('[{}]: ÍNDICE DE GINI. Processando Cidades...'.format(str.upper(k)), end='\n')
        
        # Seleciona os estados e municpios
        sql = "SELECT DISTINCT( v0103 ) AS cidade FROM censo_2000.domicilios_{}".format(k)
        cidades = pd.read_sql_query( sql, conn )    

        # print('PROCESSANDO Índice de Gini para as cidades...')
        for i in cidades['cidade']:

            # Renda média per capita
            sql_Renda = "SELECT \
                        ( SUM( v7616 * p001 ) / SUM( v7100 * p001 ) ) AS RP \
                        FROM censo_2000.domicilios_{} WHERE v0103 = {}".format(k, i)
            df_Renda = pd.read_sql_query( sql_Renda, conn )
            renda = df_Renda.loc[ 0, 'rp' ]
            # Ajuste da renda per capita de julho de 2000 para valores em agosto de 2010
            # 99,19% de inflação no INCP
            renda2010 = df_Renda.loc[ 0, 'rp' ] + ( df_Renda.loc[ 0, 'rp' ] * 0.9919037 )

            # Índice de gini renda domiciliar      
            sql_RD = "SELECT \
                    COALESCE( v7616 , 0 ) AS renda, COALESCE( ROUND( p001 ), 0 ) AS peso \
                    FROM censo_2000.domicilios_{} WHERE v0103 = {}".format(k, i)
            g_RD = gini.gini(sql_RD)

            # Índice de gini renda per capita
            # Considerando apenas pessoas com renda e acima de 10 anos (métrica do IBGE)
            sql_RP = "SELECT \
                    COALESCE( v4614 , 0 ) AS renda, COALESCE( ROUND( p001 ) , 0 ) AS peso \
                    FROM censo_2000.pessoas_{} WHERE v1103 = {} AND\
                    v4614 <> 0 AND v4614 IS NOT NULL ORDER BY v4614 ASC".format(k, i)
            g_RP = gini.gini(sql_RP)


            results = results_cid.append( {'COD': i,
                                'UF': k,
                                'Gini_RD': g_RD[0],
                                'Gini_RP': g_RP[0],
                                'RendaMedia': round(renda, 2),
                                'RendaMedia2010': round(renda2010, 2)}, ignore_index=True )

            return results