import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ds import bd
from ds import gini
from ds import amc

def giniEstados( estados ):
    ## ---------------- ESTADOS ---------------- ##    
    results = pd.DataFrame( data = [], columns = "COD UF Gini_RD Gini_RP RendaMedia".split() )

    conn = bd.conn()

    for k in estados:
        print('[{}]: ÍNDICE DE GINI. Processando Estados...'.format(str.upper(k)), end='\n')

        # Código dos estados
        sql_UF = "SELECT v0001 as UF FROM censo_2010.domicilios_{} limit 1 ".format(k)
        df_UF = pd.read_sql_query(sql_UF, conn)
        cod_uf = df_UF.loc[0, 'uf']
        # print('      Cod UF: {} '.format(cod_uf), end='\n')

        # Renda média per capita
        sql_Renda = "SELECT \
                    ( SUM( v6529 * v0010 ) / SUM( v0401 * v0010 ) ) AS RP \
                    FROM censo_2010.domicilios_{}".format(k)
        df_Renda = pd.read_sql_query( sql_Renda, conn )
        renda = df_Renda.loc[ 0, 'rp' ]

        # print('      Renda: {} '.format('R$' + str(round(renda, 2))), end='\n')

        # Índice de gini renda domiciliar      
        sql_RD = "SELECT \
                COALESCE( v6529 , 0 ) AS renda, COALESCE( ROUND( v0010 ), 0 ) AS peso \
                FROM censo_2010.domicilios_{}".format(k)

        g_RD = gini.gini(sql_RD)
        # print('      Gini RD: {} '.format(round(g_RD[0], 4)), end='\n')


        # Índice de gini renda per capita
        # Considerando apenas pessoas com renda e acima de 10 anos (métrica do IBGE)
        sql_RP = "SELECT \
                COALESCE( v6527, 0 ) AS renda, COALESCE( ROUND( v0010 ) , 0 ) AS peso \
                FROM censo_2010.pessoas_{} WHERE v6527 <> 0 and v6527 IS NOT NULL ORDER BY v6527 ASC".format(k)

        g_RP = gini.gini(sql_RP)
        # print('      Gini RP: {} '.format(round(g_RP[0], 4)), end='\n')
        
        if (k == "sp1") or (k == "sp2_rm"):
            k = "sp"
        
        results = results.append( {'COD': cod_uf,
                                    'UF': k,
                                    'Gini_RD': g_RD[0],
                                    'Gini_RP': g_RP[0],
                                    'RendaMedia': round(renda, 2)}, ignore_index=True )
    return results


def giniCidades( estados ):
    ## ---------------- MUNICÍPIOS ---------------- ##
    
    results = pd.DataFrame( data = [], columns = "Cod2010 Cod2000 Gini_RD Gini_RP RendaMedia".split() )
    conn = bd.conn()
    
    for k in estados:
        print('[{}]: ÍNDICE DE GINI. Processando Cidades...'.format(str.upper(k)), end='\n')
        
        # Seleciona os estados e municpios
        sql = "SELECT DISTINCT( v0002 ) AS cidade FROM censo_2010.domicilios_{}".format(k)
        cidades = pd.read_sql_query( sql, conn )    

        # print('PROCESSANDO Índice de Gini para as cidades...')
        for i in cidades['cidade']:

            # Renda média per capita
            sql_Renda = "SELECT \
                    ( SUM( v6529 * v0010 ) / SUM( v0401 * v0010 ) ) AS RP \
                    FROM censo_2010.domicilios_%s \
                    WHERE v0002 = '%s'" %(k, i)
            
            df_Renda = pd.read_sql_query( sql_Renda, conn )
            renda = df_Renda.loc[ 0, 'rp' ]

            # Índice de gini renda domiciliar      
            sql_RD = "SELECT \
                    COALESCE( v6529 , 0 ) AS renda, COALESCE( ROUND( v0010 ), 0 ) AS peso \
                    FROM censo_2010.domicilios_%s\
                    WHERE v0002 = '%s'" %(k, i)
        
            g_RD = gini.gini(sql_RD)

            # Índice de gini renda per capita
            # Considerando apenas pessoas com renda e acima de 10 anos (métrica do IBGE)
            sql_RP = "SELECT \
                    COALESCE( v6527, 0 ) AS renda, COALESCE( ROUND( v0010 ) , 0 ) AS peso \
                    FROM censo_2010.pessoas_%s WHERE v0002 = '%s' AND\
                    v6527 <> 0 and v6527 IS NOT NULL ORDER BY v6527 ASC" %(k, i)

            
            g_RP = gini.gini(sql_RP)
            
            # SQL - Unidade Federativa
            sql_UF = "SELECT v0001 as UF FROM censo_2010.domicilios_%s limit 1 " %( k )
            df_UF = pd.read_sql_query( sql_UF, conn )
            
            # AMC do município em 2000
            cod2000 = df_UF.loc[ 0, 'uf' ] + i
            cod2000 = int( cod2000 )
            cod = amc.AMC( cod2000, 2000 ) 

            results = results.append( {'Cod2010': df_UF.loc[ 0, 'uf' ] + i,
                                       'Cod2000': cod[0],
                                       'Gini_RD': g_RD[0],
                                       'Gini_RP': g_RP[0],
                                       'RendaMedia': round(renda, 2)}, ignore_index=True )

    af = { 'Cod2010': lambda x: x.tolist(), 
    'Cod2000':'first', 
    'Gini_RD':'mean', 
    'Gini_RP':'mean', 
    'RendaMedia':'mean'}

    results = results.groupby( 'Cod2000' ).aggregate( af )
    results.drop( 'Cod2000', axis = 1, inplace = True )
    
    return results