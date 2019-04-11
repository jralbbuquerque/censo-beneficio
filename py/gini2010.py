import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from ds import bd
from ds import gini

estados = [ "ac", "al" ]#, "am", "ap", "ba", "ce", "df", "es", "go", "ma", "mg", "ms", "mt",
         # "pa", "pb", "pe", "pi", "pr", "rj", "rn", "ro", "rr", "rs", "sc", "se", 
         # "sp1", "sp2_rm", "to" ]

results = pd.DataFrame( data = [], columns = "COD UF Gini_RD Gini_RP RendaMedia".split() )

conn = bd.conn()

for k in estados:
    
    print('[{}]: ÍNDICE DE GINI. Processando...'.format(str.upper(k)), end='\n')
    
    # Código dos estados
    sql_UF = "SELECT v0001 as UF FROM censo_2010.domicilios_%s limit 1 " %( k )
    df_UF = pd.read_sql_query(sql_UF, conn)
    cod_uf = df_UF.loc[0, 'uf']
    print('      Cod UF: {} '.format(cod_uf), end='\n')
    
    # Renda média per capita
    sql_Renda = "SELECT \
                ( SUM( v6529 * v0010 ) / SUM( v0401 * v0010 ) ) AS RP \
                FROM censo_2010.domicilios_%s" %( k )
    df_Renda = pd.read_sql_query( sql_Renda, conn )
    renda = df_Renda.loc[ 0, 'rp' ]
    # Ajuste da renda per capita de julho de 2000 para valores em agosto de 2010
    # 99,19% de inflação no INCP
    print('      Renda: {} '.format('R$' + str(round(renda, 2))), end='\n')
    
    # Índice de gini renda domiciliar      
    sql_RD = "SELECT \
            COALESCE( v6529 , 0 ) AS renda, COALESCE( ROUND( v0010 ), 0 ) AS peso \
            FROM censo_2010.domicilios_%s" %( k )
    
    g_RD = gini.gini(sql_RD)
    print('      Gini RD: {} '.format(round(g_RD[0], 4)), end='\n')
    
    
    # Índice de gini renda per capita
    # Considerando apenas pessoas com renda e acima de 10 anos (métrica do IBGE)
    sql_RP = "SELECT \
            COALESCE( v6527, 0 ) AS renda, COALESCE( ROUND( v0010 ) , 0 ) AS peso \
            FROM censo_2010.pessoas_%s WHERE v6527 <> 0 and v6527 IS NOT NULL ORDER BY v6527 ASC" %( k )
    
    g_RP = gini.gini(sql_RP)
    print('      Gini RP: {} '.format(round(g_RP[0], 4)), end='\n')
    
    results = results.append( {'COD': cod_uf,
                                'UF': k,
                                'Gini_RD': g_RD[0],
                                'Gini_RP': g_RP[0],
                                'RendaMedia': round(renda, 2)}, ignore_index=True )
    
    print('ADICIONADO COM SUCESSO! \n')

#results.to_csv('./dataset/gini2000.csv', sep = ',') 
#results.to_csv('gini2000.csv', sep = ',') 
print('FINISH! {}'.format(results.shape))
