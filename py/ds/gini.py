import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ds import bd

conn = bd.conn()
# ---------- CALCULO DO ÍNDICE DE GINI ---------- #

def gini( sql ):
    df = pd.read_sql_query( sql, conn )
    df = df.sort_values()
    # Separa valores em renda e população
    renda = df[ 'renda' ]
    pessoas = df[ 'peso' ]
    
    # Transforma as listas em arrays
    pessoas = np.array( pessoas )
    renda = np.array( renda )

    # Organiza os dados
    aux = np.argsort( [ renda/pessoas for renda, pessoas in zip( renda, pessoas ) ], kind = "stable")
    
    renda = [ j for _, j in zip( aux, renda[ aux ] )]
    pessoas = [ i for _, i in zip(aux, pessoas[ aux ] )]

    # Soma acumulada de renda e pessoas 
    renda = np.cumsum( renda / sum( renda ) )
    pessoas = np.cumsum( pessoas / sum( pessoas ) )
    
    # Fŕomula do indíce de gini [ Gini = 1 - CurvaLorenz]
    g = 2 * ( 0.5 - np.trapz( renda, pessoas ) )
    
    return g, pessoas, renda


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