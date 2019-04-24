import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ds import bd

conn = bd.conn()

# ---------- CALCULO DO ÍNDICE DE GINI ---------- #

def gini( sql ):
    df = pd.read_sql_query( sql, conn )     
    df = df.sort_values( 'renda', kind = 'mergesorted')
    
    # Expandir a base através dos pesos
    df = df.reindex( df.index.repeat( pd.to_numeric( df['peso'], downcast='integer') ) )
    
    #df_tot[ 'pop_cum' ] = np.arange( len( df_tot ) )
    #df_tot[ 'pop_cum' ] = df_tot.pop_cum.cumsum() / df_tot.pop_cum.sum()
    # População acumulada
    df['pop_cum'] = np.ones( len( df ) )
    df['pop_cum'] = df['pop_cum'].cumsum() / df['pop_cum'].size
    # Renda acumulada
    df['renda_cum'] = df['renda'].cumsum() / df['renda'].sum()
    
    # Índice de Gini
    g = 2 * ( 0.5 - np.trapz( df['renda_cum'], df['pop_cum'] ) )
    
    return g, df['pop_cum'], df['renda_cum']


# ---------- PLOT DA CURVA DE LORENZ---------- #

def plotagem( pessoas, renda ):
    plt.plot( pessoas, renda, 'k' )
    plt.plot( [ 0, 1 ], 'r' )
    plt.ylim( 0, 1 ), plt.xlim( 0, 1 )
    plt.fill_between( pessoas, renda, facecolor = 'y' )

    plt.xlabel( 'Proporção de população' )
    plt.ylabel( 'Proporção de renda' )
    plt.title( 'Curva de Lorenz' )
    plt.show()
