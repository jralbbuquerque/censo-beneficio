# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 21:03:24 2019

@author: Júnior Albuquerque
"""

import pandas as pd
import time
import datetime as dt
from util import calculaDesigualdade
from util import calculaBeneficios
from util import calculaProgressividade

log_inicializacao = """
    ======================================================================
    = Decomposição do Índice de Gini                                     =
    = Aposentadorias e Pensões Brasil 2000 e 2010 - Cidades e Estados    =
    =                                                                    =
    = Autor: Francisco Júnior                                            =
    = <jralbbuquerque@gmail.com>                                         =
    = https://github.com/jralbbuquerque/censo-beneficios                  =
    =                                                                    =
    = Laboratório de Pesquisa Operacional                                =
    = Universidade Federal do Pará                                       =
    ======================================================================
"""

print(log_inicializacao)

# Track execution time
print("Started at: {}\n".format(dt.datetime.now()))
start_time = time.time()

"""
estados_2000 = ["ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma", 
                "mg", "ms", "mt", "pa", "pb", "pe", "pi", "pr", "rj", "rn1", 
                "ro", "rr", "rs", "sc", "se", "sp", "to"]
"""

estados_2010 = ["ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma", 
                "mg", "ms", "mt", "pa", "pb", "pe", "pi", "pr", "rj", "rn", 
                "ro", "rr", "rs", "sc", "se", "sp1", "sp2_rm", "to"]

"""
gini_uf = calculaDesigualdade.giniEstados(estados_2000, 2000)
gini_cid = calculaDesigualdade.giniCidades(estados_2000, 2000)
beneficios_uf = calculaBeneficios.beneficioEstados(estados_2000, 2000)
beneficios_cid = calculaBeneficios.beneficioCidades(estados_2000, 2000)
progressividade_uf = calculaProgressividade.progressividadeEstados(estados_2000, 2000)
progressividade_cid = calculaProgressividade.progressividadeCidades(estados_2000, 2000)

with pd.ExcelWriter('dataset/ano_2000.xlsx') as writer:  
    gini_uf.to_excel(writer, sheet_name='Gini_Estados', index=False)
    gini_cid.to_excel(writer, sheet_name='Gini_Cidade', index=False)
    beneficios_uf.to_excel(writer, sheet_name='Beneficio_Estados', index=False)
    beneficios_cid.to_excel(writer, sheet_name='Beneficio_Cidades', index=False)
    progressividade_uf.to_excel(writer, sheet_name='Progressividade_Estados', index=False)
    progressividade_cid.to_excel(writer, sheet_name='Progressividade_Cidades', index=False)
"""
gini_uf = calculaDesigualdade.giniEstados(estados_2010, 2010)
gini_cid = calculaDesigualdade.giniCidades(estados_2010, 2010)
beneficios_uf = calculaBeneficios.beneficioEstados(estados_2010, 2010)
beneficios_cid = calculaBeneficios.beneficioCidades(estados_2010, 2010)
progressividade_uf = calculaProgressividade.progressividadeEstados(estados_2010, 2010)
progressividade_cid = calculaProgressividade.progressividadeCidades(estados_2010, 2010)

with pd.ExcelWriter('dataset/ano_2010.xlsx') as writer:  
    gini_uf.to_excel(writer, sheet_name='Gini_Estados', index=False)
    gini_cid.to_excel(writer, sheet_name='Gini_Cidade', index=False)
    beneficios_uf.to_excel(writer, sheet_name='Beneficio_Estados', index=False)
    beneficios_cid.to_excel(writer, sheet_name='Beneficio_Cidades', index=False)
    progressividade_uf.to_excel(writer, sheet_name='Progressividade_Estados', index=False)
    progressividade_cid.to_excel(writer, sheet_name='Progressividade_Cidades', index=False)
    
# Print out elapsed time
elapsed_time = (time.time() - start_time) / 60
print("\n\nFinished at: {}. ".format(dt.datetime.now()), end="")
print("Execution time: {0:0.4f} minutes.".format(elapsed_time))