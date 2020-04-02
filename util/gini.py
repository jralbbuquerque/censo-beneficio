# -*- coding: utf-8 -*-
"""
@author: Francisco Júnior
"""

# Preâmbulo
import numpy as np
import pandas as pd

def gini(df, sort):
    """
        Calcula o índice de gini a partir de um DataFrame contendo
    os dados equivalentes a renda da população em destaque.

    Parâmetros
    ----------
        df: Pandas DataFrame
        sort: Inteiro que indica se a base precisa ser ordenada ou não. 
              Se sort = 1 a base será ordenada, se for = 0 não será.

    Retorno
    -------
        Índice de Gini
    """  
    
    # Renomeia as colunas para padronizar
    df.rename(columns = 
          {df.columns[0]: "renda", df.columns[1]: "peso"}, inplace=True)
    
    if sort == 1:
        # Ordena os valores de renda (crescente)
        df = df.sort_values('renda', kind = 'mergesorted')
    
    # Expressão lógica para expandir a base de dados através
    # da variável peso
    df = df.reindex(df.index.repeat(
            pd.to_numeric(df['peso'], downcast='integer')))
    
    # Cálcula a população acumulada
    df['pop_cum'] = np.ones(len(df))
    df['pop_cum'] = df['pop_cum'].cumsum() / df['pop_cum'].size
    
    # Cálcula a renda acumulada
    df['renda_cum'] = df['renda'].cumsum() / df['renda'].sum()
    
    # Índice de Gini
    gini = 2 * (0.5 - np.trapz(df['renda_cum'], df['pop_cum']))
    
    return gini