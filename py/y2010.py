import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ds import bd
from ds import gini
from ds import amc

## ------------------------- ÍNDICE DE GINI PARA ESTADOS ------------------------- ##
def giniEstados(estados):   
    results = pd.DataFrame(data = [], columns = "COD UF Gini_RD Gini_RP RendaMedia".split())

    conn = bd.conn()

    for k in estados:
        print('[{}]: ÍNDICE DE GINI. Processando Estados...'.format(str.upper(k)), end='\n')

        # Código dos estados
        sql_UF = "SELECT v0001 as UF FROM censo_2010.domicilios_{} limit 1 ".format(k)
        df_UF = pd.read_sql_query(sql_UF, conn)
        cod_uf = df_UF.loc[0, 'uf']

        # Renda média per capita
        sql_Renda = "SELECT \
                    (SUM(v6529 * v0010) / SUM(v0401 * v0010)) AS RP \
                    FROM censo_2010.domicilios_{}".format(k)
        df_Renda = pd.read_sql_query(sql_Renda, conn)
        renda = df_Renda.loc[0, 'rp']

        # Índice de gini renda domiciliar      
        sql_RD = "SELECT \
                COALESCE(v6529 , 0) AS renda, COALESCE(ROUND(v0010), 0) AS peso \
                FROM censo_2010.domicilios_{}".format(k)

        g_RD = gini.gini(sql_RD)

        # Índice de gini renda per capita
        # Considerando apenas pessoas com renda e acima de 10 anos (métrica do IBGE)
        sql_RP = "SELECT \
                COALESCE(v6527, 0) AS renda, COALESCE(ROUND(v0010) , 0) AS peso \
                FROM censo_2010.pessoas_{} WHERE v6527 <> 0 and v6527 IS NOT NULL ORDER BY v6527 ASC".format(k)

        g_RP = gini.gini(sql_RP)
        
        # Corrige o nome do estado de São Paulo
        if (k == "sp1") or (k == "sp2_rm"):
            k = "sp"
        
        results = results.append({'COD': cod_uf, 'UF': str.upper(k), 'Gini_RD': g_RD[0],
                                  'Gini_RP': g_RP[0], 'RendaMedia': round(renda, 2)}, ignore_index=True)
    return results
# --------------------------------------------------------------------------------------------------- #

## -------------------------------- ÍNDICE DE GINI PARA MUNICÍPIOS --------------------------------- ##
def giniCidades(estados):
    results = pd.DataFrame(data = [], columns = "UF Cod2010 Cod2000 Gini_RD Gini_RP RendaMedia".split())
    conn = bd.conn()
    
    for k in estados:
        print('[{}]: ÍNDICE DE GINI. Processando Cidades...'.format(str.upper(k)), end='\n')
        
        # Seleciona os estados e municpios
        sql = "SELECT DISTINCT(v0002) AS cidade FROM censo_2010.domicilios_{}".format(k)
        cidades = pd.read_sql_query(sql, conn)    

        # print('PROCESSANDO Índice de Gini para as cidades...')
        for i in cidades['cidade']:

            # Renda média per capita
            sql_Renda = "SELECT \
                    (SUM(v6529 * v0010) / SUM(v0401 * v0010)) AS RP \
                    FROM censo_2010.domicilios_{} \
                    WHERE v0002 = '{}'".format(k, i)
            
            df_Renda = pd.read_sql_query(sql_Renda, conn)
            renda = df_Renda.loc[0, 'rp']

            # Índice de gini renda domiciliar      
            sql_RD = "SELECT \
                    COALESCE(v6529 , 0) AS renda, COALESCE(ROUND(v0010), 0) AS peso \
                    FROM censo_2010.domicilios_{}\
                    WHERE v0002 = '{}'".format(k, i)
        
            g_RD = gini.gini(sql_RD)

            # Índice de gini renda per capita
            # Considerando apenas pessoas com renda e acima de 10 anos (métrica do IBGE)
            sql_RP = "SELECT \
                    COALESCE(v6527, 0) AS renda, COALESCE(ROUND(v0010) , 0) AS peso \
                    FROM censo_2010.pessoas_{} WHERE v0002 = '{}' AND\
                    v6527 <> 0 and v6527 IS NOT NULL ORDER BY v6527 ASC".format(k, i)

            
            g_RP = gini.gini(sql_RP)
            
            # SQL - Unidade Federativa
            sql_UF = "SELECT v0001 as UF FROM censo_2010.domicilios_{} limit 1 ".format(k)
            df_UF = pd.read_sql_query(sql_UF, conn)
            
            # AMC do município em 2000
            cod2000 = df_UF.loc[0, 'uf'] + i
            cod2000 = int(cod2000)
            cod = amc.AMC(cod2000, 2000) 
            
            # Corrige o nome do estado de São Paulo
            if (k == "sp1") or (k == "sp2_rm"):
                uf = "sp"
            else:
                uf = k
                
            results = results.append( {'UF': str.upper(uf), 'Cod2010': df_UF.loc[0, 'uf'] + i, 'Cod2000': cod[0],
                                       'Gini_RD': g_RD[0], 'Gini_RP': g_RP[0],
                                       'RendaMedia': round(renda, 2)}, ignore_index=True )

    af = {'Cod2010': lambda x: x.tolist(), 'Cod2000':'first', 
          'Gini_RD':'mean', 'Gini_RP':'mean', 'RendaMedia':'mean'}

    results = results.groupby('Cod2000').aggregate(af)
    results.drop('Cod2000', axis = 1, inplace = True)
    
    return results
# --------------------------------------------------------------------------------------------------- #

# ------------------------- PARTICIPAÇÕES DE BENEFICIOS NO BRASIL - ESTADOS ------------------------- #
def beneficioEstados(estados):
    results = pd.DataFrame(data = [], columns = "UF Renda(Total) Renda(Beneficios) Total(%) Beneficio(>Sal) \
                                                    Beneficio(>Sal)(%) Beneficio(<=Sal) Beneficio(<=Sal)(%)".split())
    conn = bd.conn()

    for k in estados:
        print('[{}]: PARTICIPAÇÃO DE BENEFÍCIOS. Processando Estados...'.format(str.upper(k)), end='\n')

        # Rendimento total do estado
        sql_RT = "SELECT SUM(v6527 * v0010) AS RT \
                FROM censo_2010.pessoas_{}".format(k)

        # Rendimento total dos beneficios do estado
        sql_RB = "SELECT SUM(v6591 * v0010) AS RB \
                FROM censo_2010.pessoas_{} WHERE v0656 = 1".format(k)

        # Rendimento total dos beneficios acima de 1 salário minímo
        sql_RB_nSAL = "SELECT SUM(v6591 * v0010) AS RB_nSAL \
                FROM censo_2010.pessoas_{} WHERE v6591 > 510 AND v0656 = 1".format(k)

        # Rendimento total dos beneficios igual ou menor que 1 salário minímo
        sql_RB_1SAL = "SELECT SUM(v6591 * v0010) AS RB_1SAL \
                FROM censo_2010.pessoas_{} WHERE v6591 <= 510 AND v0656 = 1".format(k)

        df_RT = pd.read_sql_query(sql_RT, conn)
        df_RB = pd.read_sql_query(sql_RB, conn)
        df_RB_nSAL = pd.read_sql_query(sql_RB_nSAL, conn)
        df_RB_1SAL = pd.read_sql_query(sql_RB_1SAL, conn)

        RT = df_RT.loc[0, 'rt']
        RB = df_RB.loc[0, 'rb']
        RB_nSAL = df_RB_nSAL.loc[0, 'rb_nsal']
        RB_1SAL = df_RB_1SAL.loc[0, 'rb_1sal']
        
        # Corrige o nome do estado de São Paulo
        if (k == "sp1") or (k == "sp2_rm"):
            k = "sp"
            
        results = results.append({'UF': str.upper(k), 'Renda(Total)': RT, 'Renda(Beneficios)': RB,
                                  'Total(%)': RB/RT, 'Beneficio(>Sal)': RB_nSAL,
                                  'Beneficio(>Sal)(%)': RB_nSAL/RT, 'Beneficio(<=Sal)': RB_1SAL,
                                  'Beneficio(<=Sal)(%)': RB_1SAL / RT}, ignore_index=True)
    return results
# ------------------------------------------------------------------------------------------------------------------ #

# ------------------------- RESULTADOS DAS PARTICIPAÇÕES DE BENEFICIOS NO BRASIL - CIDADES ------------------------- #
def beneficioCidades(estados):
    results = pd.DataFrame(data = [], columns = "UF COD Renda(Total) Renda(Beneficios) Total(%) Beneficio(>Sal) \
                                                    Beneficio(>Sal)(%) Beneficio(<=Sal) Beneficio(<=Sal)(%)".split())
    conn = bd.conn()
    
    for k in estados: 
        print('[{}]: PARTICIPAÇÃO DE BENEFÍCIOS. Processando Cidades...'.format(str.upper(k)), end='\n')
        
        # Seleciona os estados e municpios
        sql = "SELECT DISTINCT(v0002) AS cidade FROM censo_2010.domicilios_{}".format(k)
        cidades = pd.read_sql_query(sql, conn)

        for i in cidades['cidade']:
            # Referenciando estado e cidade (k, i)
            # Rendimento total da cidade
            sql_RT = "SELECT COALESCE(SUM(v6527 * v0010), 0) AS RT \
                    FROM censo_2010.pessoas_{} WHERE v0002 = '{}'".format(k, i)

            # Rendimento total dos beneficios da cidade
            sql_RB = "SELECT COALESCE(SUM(v6527 * v0010), 0) AS RB \
                    FROM censo_2010.pessoas_{} WHERE v6591 <> 0 AND v0656 = 1 AND v0002 = '{}'".format(k, i)

            # Rendimento total dos beneficios acima de 1 salário minímo
            sql_RB_nSAL = "SELECT COALESCE(SUM(v6527 * v0010), 0) AS RB_NSAL \
                    FROM censo_2010.pessoas_{} WHERE v6591 <> 0 AND v6591 > 510 AND v0656 = 1 AND v0002 = '{}'".format(k, i)

            # Rendimento total dos beneficios igual ou menor que 1 salário minímo
            sql_RB_1SAL = "SELECT COALESCE(SUM(v6527 * v0010), 0) AS RB_1SAL \
                    FROM censo_2010.pessoas_{} WHERE v6591 <> 0 AND v6591 <= 510 AND v0656 = 1 AND v0002 = '{}'".format(k, i)

            # SQL - Unidade Federativa
            sql_UF = "SELECT v0001 as UF FROM censo_2010.domicilios_{} limit 1 ".format(k)
            df_UF = pd.read_sql_query(sql_UF, conn)
            
            # AMC do município em 2000
            cod2000 = df_UF.loc[0, 'uf'] + i
            cod2000 = int(cod2000)
            cod = amc.AMC(cod2000, 2000) 
            
            df_RT = pd.read_sql_query(sql_RT, conn)
            df_RB = pd.read_sql_query(sql_RB, conn)
            df_RB_nSAL = pd.read_sql_query(sql_RB_nSAL, conn)
            df_RB_1SAL = pd.read_sql_query(sql_RB_1SAL, conn)

            RT = df_RT.loc[0, 'rt']
            RB = df_RB.loc[0, 'rb']
            RB_nSAL = df_RB_nSAL.loc[0, 'rb_nsal']
            RB_1SAL = df_RB_1SAL.loc[0, 'rb_1sal']

            
            # Corrige o nome do estado de São Paulo
            if (k == "sp1") or (k == "sp2_rm"):
                uf = "sp"
            else:
                uf = k
                
            results = results.append( {'UF': str.upper(uf), 'Cod2010': df_UF.loc[ 0, 'uf' ] + i,
                                      'Cod2000': cod[0], 'Renda(Total)': RT, 'Renda(Beneficios)': RB,
                                      'Total(%)': RB/RT, 'Beneficio(>Sal)': RB_nSAL, 'Beneficio(>Sal)(%)': RB_nSAL/RT,
                                      'Beneficio(<=Sal)': RB_1SAL, 'Beneficio(<=Sal)(%)': RB_1SAL / RT}, ignore_index=True )
    
    af = {'UF': 'first', 'Cod2010': lambda x: x.tolist(), 'Cod2000':'first', 
          'Renda(Total)':'sum', 'Renda(Beneficios)':'sum', 'Total(%)': 'sum',
          'Beneficio(>Sal)': 'sum', 'Beneficio(>Sal)(%)': 'sum', 'Beneficio(<=Sal)': 'sum',
          'Beneficio(<=Sal)(%)':'sum'}

    results = results.groupby('Cod2000').aggregate(af)
    results['Total(%)'] = results[ 'Renda(Beneficios)' ] / results['Renda(Total)']
    results['Beneficio(>Sal)(%)'] = results['Beneficio(>Sal)'] / results['Renda(Total)']
    results['Beneficio(<=Sal)(%)'] = results['Beneficio(<=Sal)'] / results['Renda(Total)']
    results.drop( 'Cod2000', axis = 1, inplace = True )
    
    return results
# ------------------------------------------------------------------------------------------ #

# ------------------------- PROGRESSIVIDADE DAS PARCELAS - ESTADOS ------------------------- #
def progressividadeEstados(estados):
    results = pd.DataFrame(data = [], columns = 'COD UF GINI(G) PARCELA(CH) P_TOTAL P_1SAL P_NSAL \
                                        MRENDA MBEN_TOT MBEN_1SAL MBEN_NSAL'.split())
    conn = bd.conn()

    for k in estados:
        print('[{}]: PROGRESSIVIDADE DAS PARC. DE APOSENTADORIA. Processando Estados...'.format(str.upper(k)), end='\n')
        
        sql = "SELECT \
                     COALESCE(v6527, 0) AS renda_tot, \
                     ROUND(v0010) AS peso_tot, \
                     COALESCE(CASE WHEN v0656 = 1 THEN v6591 ELSE 0 END, 0) AS ben_tot, \
                     COALESCE(CASE WHEN v6591 > 510 THEN 0 WHEN v6591 <= 510 AND v0656 = 1 THEN v6591 END, 0) AS ben_1sal, \
                     COALESCE(CASE WHEN v6591 <= 510 THEN 0 WHEN v6591 > 510 AND v0656 = 1 THEN v6591 END, 0) AS ben_nsal \
                   FROM censo_2010.pessoas_{} WHERE v6527 <> 0 and v6527 IS NOT NULL ORDER BY v6527 ASC".format(k)
    
        # Código dos estados
        sql_UF = "SELECT v0001 as UF FROM censo_2010.domicilios_{} limit 1 ".format(k)
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

        # Rendas médias
        mRendaTot = sum(df['renda_tot']) / len(df)
        mBenTot = sum(df['ben_tot']) / len(df)
        mBenNsal = sum(df['ben_nsal']) / len(df)
        mBen1Sal = sum(df['ben_1sal']) / len(df)

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

        # Corrige o nome do estado de São Paulo
        if (k == "sp1") or (k == "sp2_rm"):
            k = "sp"

        results = results.append({'COD': cod_uf, 'UF': str.upper(k), 'GINI(G)': g, 'PARCELA(CH)': ch1, 
                                  'P_TOTAL': p1, 'P_1SAL': p2, 'P_NSAL': p3, 'MRENDA': mRendaTot,
				  'MBEN_TOT': mBenTot, 'MBEN_1SAL': mBen1Sal, 'MBEN_NSAL': mBenNsal}, ignore_index = True)
    
    return results
# ------------------------------------------------------------------------------------------ #

# ------------------------- PROGRESSIVIDADE DAS PARCELAS - CIDADES ------------------------- #
def progressividadeCidades(estados):
    results = pd.DataFrame(data = [], columns = 'UF COD2010 COD2000 GINI(G) PARCELA(CH) P_TOTAL P_1SAL P_NSAL \
                                        MRENDA MBEN_TOT MBEN_1SAL MBEN_NSAL'.split())
    conn = bd.conn()
    
    for k in estados:
        print('[{}]: PROGRESSIVIDADE DAS PARC. DE APOSENTADORIA. Processando Cidades...'.format(str.upper(k)), end='\n')
        
        # Seleciona os estados e municpios
        sql = "SELECT DISTINCT( v0002 ) AS cidade FROM censo_2010.domicilios_{}".format(k)
        cidades = pd.read_sql_query(sql, conn)

        # SQL - Unidade Federativa
        sql_UF = "SELECT v0001 as UF FROM censo_2010.domicilios_{} limit 1".format(k)  
        df_UF = pd.read_sql_query(sql_UF, conn)
        uf = df_UF.loc[0, 'uf']
            
        for i in cidades['cidade']:
            sql = "SELECT \
                     COALESCE(v6527, 0) AS renda_tot, \
                     COALESCE(ROUND(v0010), 0) AS peso_tot, \
                     COALESCE(CASE WHEN v0656 = 1 THEN v6591 ELSE 0 END, 0 ) AS ben_tot, \
                     COALESCE(CASE WHEN v6591 > 510 THEN 0 WHEN v6591 <= 510 AND v0656 = 1 THEN v6591 END, 0) AS ben_1sal, \
                     COALESCE(CASE WHEN v6591 <= 510 THEN 0 WHEN v6591 > 510 AND v0656 = 1 THEN v6591 END, 0) AS ben_nsal \
                   FROM censo_2010.pessoas_{} WHERE v6527 <> 0 AND v0002 = {} AND v6527 IS NOT NULL ORDER BY v6527 ASC".format(k, i)
        
            # Ordena os dados
            df = pd.read_sql_query(sql, conn)     
            df = df.sort_values('renda_tot', kind = 'mergesorted')

            # Expande a base acerca dos pesos
            df = df.reindex(df.index.repeat(pd.to_numeric(df.peso_tot, downcast='integer')))

            # População e renda acumuladas
            df['pop_cum'] = np.ones(len(df))
            df['pop_cum'] = df.pop_cum.cumsum() / df.pop_cum.size
            df['renda_cum'] = df.renda_tot.cumsum() / df.renda_tot.sum()

            # Rendas médias
            mRendaTot = sum(df['renda_tot']) / len(df)
            mBenTot = sum(df['ben_tot']) / len(df)
            mBenNsal = sum(df['ben_nsal']) / len(df)
            mBen1Sal = sum(df['ben_1sal']) / len(df)

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
            
            Cod2000 = int(uf + i)
            cod = amc.AMC(Cod2000, 2000) 
            
            # Corrige o nome do estado de São Paulo
            if (k == "sp1") or (k == "sp2_rm"):
                uff = "sp"
            else:
                uff = k

            results = results.append({'UF': str.upper(uff), 'COD2010': (str(uf) + str(i)), 'COD2000': str(cod[0]),
                                      'GINI(G)': g, 'PARCELA(CH)': ch1, 'P_TOTAL': p1, 'P_1SAL': p2, 
                                      'P_NSAL': p3, 'MRENDA': mRendaTot, 'MBEN_TOT': mBenTot, 'MBEN_1SAL': mBen1Sal,
				      'MBEN_NSAL': mBenNsal}, ignore_index = True) 

    results = results.fillna(0)
    
    af = {'UF':'first', 'COD2010': lambda x: x.tolist(), 'COD2000':'first', 
          'GINI(G)':'mean', 'PARCELA(CH)':'mean', 'P_TOTAL':'mean', 'P_1SAL':'mean',
          'P_NSAL':'mean', 'MRENDA':'mean', 'MBEN_TOT':'mean', 'MBEN_1SAL':'mean', 'MBEN_NSAL':'mean' }
    
    results = results.groupby('COD2000').aggregate(af)
    results.drop('COD2000', axis = 1, inplace = True)
    
    return results
