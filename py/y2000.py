import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ds import bd
from ds import gini

## ------------------------- ÍNDICE DE GINI PARA ESTADOS ------------------------- ##
def giniEstados( estados ):
    results = pd.DataFrame( data = [], columns = "COD UF Gini_RD \
                        Gini_RP RendaMedia RendaMedia2010".split() )

    conn = bd.conn()

    for k in estados:
        print('[{}]: ÍNDICE DE GINI. Processando Estados...'.format(str.upper(k)), end='\n')

        # Código dos estados
        sql_UF = "SELECT v0102 AS UF FROM censo_2000.domicilios_{} limit 1".format(k)
        df_UF = pd.read_sql_query(sql_UF, conn)
        cod_uf = df_UF.loc[0, 'uf']

        # Renda média per capita
        sql_Renda = "SELECT \
                    ( SUM( v7616 * p001 ) / SUM( v7100 * p001 ) ) AS RP \
                    FROM censo_2000.domicilios_{}".format(k)
        df_Renda = pd.read_sql_query( sql_Renda, conn )
        renda = df_Renda.loc[ 0, 'rp' ]
        # Ajuste da renda per capita de julho de 2000 para valores em agosto de 2010
        # 99,19% de inflação no INCP
        renda2010 = renda + ( renda * 0.9919037 )   

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
                FROM censo_2000.pessoas_{} WHERE v4614 <> 0 \
                AND v4614 IS NOT NULL ORDER BY v4614 ASC".format(k)

        g_RP = gini.gini(sql_RP)
        # print('      Gini RP: {} '.format(round(g_RP[0], 4)), end='\n')

        results = results.append( {'COD': cod_uf,
                                    'UF': str.upper(k),
                                    'Gini_RD': g_RD[0],
                                    'Gini_RP': g_RP[0],
                                    'RendaMedia': round(renda, 2),
                                    'RendaMedia2010': round(renda2010, 2)}, ignore_index=True )
    return results
# --------------------------------------------------------------------------------------------------- #

## -------------------------------- ÍNDICE DE GINI PARA MUNICÍPIOS --------------------------------- ##
def giniCidades( estados ):
    results = pd.DataFrame( data = [], columns = "UF COD Gini_RD Gini_RP \
                                        RendaMedia RendaMedia2010".split() )
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


            results = results.append( {'COD': i,
                            'UF': str.upper(k),
                            'Gini_RD': g_RD[0],
                            'Gini_RP': g_RP[0],
                            'RendaMedia': round(renda, 2),
                            'RendaMedia2010': round(renda2010, 2)}, ignore_index=True )

    return results
# --------------------------------------------------------------------------------------------------- #

# ------------------------- PARTICIPAÇÕES DE BENEFICIOS NO BRASIL - ESTADOS ------------------------- #
def beneficioEstados( estados ):
    results = pd.DataFrame( data = [], columns = "UF Renda(Total) Renda(Beneficios) Total(%) Beneficio(>Sal) \
                                                    Beneficio(>Sal)(%) Beneficio(<=Sal) Beneficio(<=Sal)(%)".split() )
    conn = bd.conn()

    for k in estados:
        print('[{}]: PARTICIPAÇÃO DE BENEFÍCIOS. Processando Estados...'.format(str.upper(k)), end='\n')
        
        # Rendimento total do estado
        sql_RT = "SELECT SUM( v4614 * p001 ) AS RT \
                FROM censo_2000.pessoas_{}".format(k)

        # Rendimento total dos beneficios do estado
        sql_RB = "SELECT SUM( v4573 * p001 ) AS RB \
                FROM censo_2000.pessoas_{}".format(k)

        # Rendimento total dos beneficios acima de 1 salário minímo
        sql_RB_nSAL = "SELECT SUM( v4573 * p001 ) AS RB_nSAL \
                FROM censo_2000.pessoas_{} WHERE v4573 > 151".format(k)

        # Rendimento total dos beneficios igual ou menor que 1 salário minímo
        sql_RB_1SAL = "SELECT SUM( v4573 * p001 ) AS RB_1SAL \
                FROM censo_2000.pessoas_{} WHERE v4573 <= 151".format(k)

        df_RT = pd.read_sql_query( sql_RT, conn )
        df_RB = pd.read_sql_query( sql_RB, conn )
        df_RB_nSAL = pd.read_sql_query( sql_RB_nSAL, conn )
        df_RB_1SAL = pd.read_sql_query( sql_RB_1SAL, conn )

        RT = df_RT.loc[ 0, 'rt' ]
        RB = df_RB.loc[ 0, 'rb' ]
        RB_nSAL = df_RB_nSAL.loc[ 0, 'rb_nsal' ]
        RB_1SAL = df_RB_1SAL.loc[ 0, 'rb_1sal' ]

        results = results.append( {'UF': str.upper(k), 
                                  'Renda(Total)': RT,
                                  'Renda(Beneficios)': RB,
                                  'Total(%)': RB/RT,
                                  'Beneficio(>Sal)': RB_nSAL,
                                  'Beneficio(>Sal)(%)': RB_nSAL/RT,
                                  'Beneficio(<=Sal)': RB_1SAL,
                                  'Beneficio(<=Sal)(%)': RB_1SAL / RT}, ignore_index=True )
    return results
# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------- RESULTADOS DAS PARTICIPAÇÕES DE BENEFICIOS NO BRASIL - CIDADES ------------------------- #
def beneficioCidades( estados ):
    results = pd.DataFrame( data = [], columns = "UF COD Renda(Total) Renda(Beneficios) Total(%) Beneficio(>Sal) \
                                                    Beneficio(>Sal)(%) Beneficio(<=Sal) Beneficio(<=Sal)(%)".split() )
    conn = bd.conn()
    
    for k in estados: 
        print('[{}]: PARTICIPAÇÃO DE BENEFÍCIOS. Processando Cidades...'.format(str.upper(k)), end='\n')
        
        # Seleciona os estados e municpios
        sql = "SELECT DISTINCT( v1103 ) AS cidade FROM censo_2000.pessoas_{} WHERE v1103 <> 0".format(k)
        cidades = pd.read_sql_query( sql, conn )

        for i in cidades['cidade']:
            # Referenciando estado e cidade (k, i)

            # Rendimento total do estado
            sql_RT = "SELECT COALESCE( SUM( v4614 * p001 ), 0 ) AS RT \
                    FROM censo_2000.pessoas_{} WHERE v1103 = {}".format(k, i)

            # Rendimento total dos beneficios do estado
            sql_RB = "SELECT COALESCE( SUM( v4573 * p001 ), 0 ) AS RB \
                    FROM censo_2000.pessoas_{} WHERE v4573 <> 0 AND v1103 = {}".format(k, i)

            # Rendimento total dos beneficios acima de 1 salário minímo
            sql_RB_nSAL = "SELECT COALESCE( SUM( v4573 * p001 ), 0 ) AS RB_nSAL \
                    FROM censo_2000.pessoas_{} WHERE v4573 > 151 AND v4573 <> 0 AND v1103 = {}".format(k, i)

            # Rendimento total dos beneficios igual ou menor que 1 salário minímo
            sql_RB_1SAL = "SELECT COALESCE( SUM( v4573 * p001 ), 0 ) AS RB_1SAL \
                    FROM censo_2000.pessoas_{} WHERE v4573 <= 151 AND v4573 <> 0 AND v1103 = {}".format(k, i)

            df_RT = pd.read_sql_query( sql_RT, conn )
            df_RB = pd.read_sql_query( sql_RB, conn )
            df_RB_nSAL = pd.read_sql_query( sql_RB_nSAL, conn )
            df_RB_1SAL = pd.read_sql_query( sql_RB_1SAL, conn )

            RT = df_RT.loc[ 0, 'rt' ]
            RB = df_RB.loc[ 0, 'rb' ]
            RB_nSAL = df_RB_nSAL.loc[ 0, 'rb_nsal' ]
            RB_1SAL = df_RB_1SAL.loc[ 0, 'rb_1sal' ]
            
            results = results.append( {'UF': str.upper(k), 
                                      'COD': i,
                                      'Renda(Total)': RT,
                                      'Renda(Beneficios)': RB,
                                      'Total(%)': RB/RT,
                                      'Beneficio(>Sal)': RB_nSAL,
                                      'Beneficio(>Sal)(%)': RB_nSAL/RT,
                                      'Beneficio(<=Sal)': RB_1SAL,
                                      'Beneficio(<=Sal)(%)': RB_1SAL / RT}, ignore_index=True )

    return results
# ------------------------------------------------------------------------------------------ #

# ------------------------- PROGRESSIVIDADE DAS PARCELAS - ESTADOS ------------------------- #
def progressividadeEstados(estados):
    results = pd.DataFrame( data = [], columns = 'COD UF GINI(G) PARCELA(CH) P_TOTAL P_1SAL P_NSAL'.split() )
    conn = bd.conn()

    for k in estados:
        print('[{}]: PROGRESSIVIDADE DAS PARC. DE APOSENTADORIA. \
            Processando Estados...'.format(str.upper(k)), end='\n')
        
        sql = "SELECT \
                COALESCE(v4614, 0) AS renda_tot, \
                COALESCE(ROUND(p001), 0) AS peso_tot, \
                COALESCE(v4573, 0 ) AS ben_tot, \
                COALESCE(CASE WHEN v4573 <= 151 THEN v4573 ELSE 0 END, 0) AS ben_1sal, \
                COALESCE(CASE WHEN v4573 > 151 THEN v4573 ELSE 0 END, 0) AS ben_nsal \
               FROM censo_2000.pessoas_{} WHERE v4614 <> 0 AND v4614 IS NOT NULL ORDER BY v4614 ASC".format(k)
    
        # Código dos estados
        sql_UF = "SELECT v0102 AS UF FROM censo_2000.domicilios_{} limit 1".format(k)
        df_UF = pd.read_sql_query(sql_UF, conn)
        cod_uf = df_UF.loc[0, 'uf']

        # Ordena os dados
        df = pd.read_sql_query(sql, conn)     
        df = df.sort_values('renda_tot', kind = 'mergesorted')

        # Expande a base acerca dos pesos
        df = df.reindex(df.index.repeat(pd.to_numeric(df.peso_tot, downcast='integer')))

        # População e renda acumuladas
        df['pop_cum'] = np.ones(len(df))
        df['pop_cum'] = df.pop_cum.cumsum() / df.pop_cum.size
        df['renda_cum'] = df.renda_tot.cumsum() / df.renda_tot.sum()

        # Índice de gini
        g = 2 * (0.5 - np.trapz(df.renda_cum, df.pop_cum))

        # Progressividade - benefícios de aposentadorias e pensões
        df['ben_cum'] = df.ben_tot.cumsum() / df.ben_tot.sum()
        ch1 = 2 * (0.5 - np.trapz(df.ben_cum, df.pop_cum))
        p1 = g - ch1

        # Progressividade - benefícios de aposentadorias e pensões até 1 salário
        df['ben_cum'] = df.ben_1sal.cumsum() / df.ben_1sal.sum()
        ch2 = 2 * (0.5 - np.trapz(df.ben_cum, df.pop_cum))
        p2 = g - ch2

        # Progressividade - benefícios de aposentadorias e pensões acima de 1 salário
        df['ben_cum'] = df.ben_nsal.cumsum() / df.ben_nsal.sum()
        ch3 = 2 * (0.5 - np.trapz(df.ben_cum, df.pop_cum))
        p3 = g - ch3

        results = results.append( {'COD': cod_uf, 'UF': k, 'GINI(G)': g, 'PARCELA(CH)': ch1, 
                                   'P_TOTAL': p1, 'P_1SAL': p2, 'P_NSAL': p3}, ignore_index = True)
    
    return results
# ------------------------------------------------------------------------------------------ #

# ------------------------- PROGRESSIVIDADE DAS PARCELAS - CIDADES ------------------------- #
def progressividadeCidades(estados):
    results = pd.DataFrame(data = [], columns = 'UF COD GINI(G) PARCELA(CH) P_TOTAL P_1SAL P_NSAL'.split())
    conn = bd.conn()
    
    for k in estados:
        print('[{}]: PROGRESSIVIDADE DAS PARC. DE APOSENTADORIA. Processando Cidades...'.format(str.upper(k)), end='\n')
        
        # Seleciona os estados e municpios
        sql = "SELECT DISTINCT(v1103) AS cidade FROM censo_2000.pessoas_{} WHERE v1103 <> 0".format(k)
        cidades = pd.read_sql_query( sql, conn )

        for i in cidades['cidade']:
            sql = "SELECT \
                    COALESCE( v4614, 0 ) AS renda_tot, \
                    COALESCE( ROUND( p001 ), 0 ) AS peso_tot, \
                    COALESCE( v4573, 0 ) AS ben_tot, \
                    COALESCE( CASE WHEN v4573 <= 151 THEN v4573 ELSE 0 END, 0) AS ben_1sal, \
                    COALESCE( CASE WHEN v4573 > 151 THEN v4573 ELSE 0 END, 0) AS ben_nsal \
                   FROM censo_2000.pessoas_{} WHERE v4614 <> 0 AND v4614 IS NOT NULL AND v1103 = {} ORDER BY v4614 ASC".format(k, i)

            # Ordena os dados
            df = pd.read_sql_query(sql, conn)     
            df = df.sort_values('renda_tot', kind = 'mergesorted')

            # Expande a base acerca dos pesos
            df = df.reindex(df.index.repeat(pd.to_numeric(df.peso_tot, downcast='integer')))

            # População e renda acumuladas
            df['pop_cum'] = np.ones(len(df))
            df['pop_cum'] = df.pop_cum.cumsum() / df.pop_cum.size
            df['renda_cum'] = df.renda_tot.cumsum() / df.renda_tot.sum()

            # Índice de gini
            g = 2 * (0.5 - np.trapz(df.renda_cum, df.pop_cum))

            # Progressividade - benefícios de aposentadorias e pensões
            df['ben_cum'] = df.ben_tot.cumsum() / df.ben_tot.sum()
            ch1 = 2 * (0.5 - np.trapz(df.ben_cum, df.pop_cum))
            p1 = g - ch1

            # Progressividade - benefícios de aposentadorias e pensões até 1 salário
            df['ben_cum'] = df.ben_1sal.cumsum() / df.ben_1sal.sum()
            ch2 = 2 * (0.5 - np.trapz(df.ben_cum, df.pop_cum))
            p2 = g - ch2

            # Progressividade - benefícios de aposentadorias e pensões acima de 1 salário
            df['ben_cum'] = df.ben_nsal.cumsum() / df.ben_nsal.sum()
            ch3 = 2 * (0.5 - np.trapz(df.ben_cum, df.pop_cum))
            p3 = g - ch3

            results = results.append( { 'UF': k, 'COD': i, 'GINI(G)': g, 'PARCELA(CH)': ch1, 
                                       'P_TOTAL': p1, 'P_1SAL': p2, 'P_NSAL': p3}, ignore_index = True)
            results = results.fillna(0)
        
    return results
