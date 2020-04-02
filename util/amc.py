# -*- coding: utf-8 -*-
"""
@author: Francisco Júnior
"""

# Preâmbulo
import pandas as pd
import numpy as np

# Realiza a união de municpios que tiveram divisão territorial através do 
# seu código e ano de divisão 
def AMC(codMunicipio, anoAMC):
    """
        Avalia se um munipio teve divisão territorial a partir de
    um ano especifico. Caso sim, o mesmo retornara o código oringinal
    do municipio analisado.

    Parâmetros
    ----------
        codMunicipio: int
            Código do município a ser avaliado
        anoAMC: int
            Ano de avaliação

    Retorno
    -------
        Código do município e ano de modificação
    """
    
    # Lê arquivo com todas as divisões territoriais ocorridas desde 1939
    amc = pd.read_csv('./datasrc/AMC.csv')

    # Verifica se o municipio teve divisão territorial
    if(amc['newcod'] == codMunicipio).any() == False:
        return print('Codigo {} não está na base'.format(codMunicipio))
        
    else:
        # Transforma dataframe em array para facilitar acesso aos dados
        mun = np.array(amc[amc['newcod'] == codMunicipio])
        
        # Atribui o código à variável codOriginal para faciliar a
        # interpretação nas comparações lógicas
        codOriginal = codMunicipio
        
        # Seta variáveis para comparação
        codConvertido = 0
        anoInstalacao = 0
        
        # Transforma array bi-dimencional em uni-dimencional
        mun = mun[0]
        
        while(codOriginal != codConvertido):
            # Compara se o ano em que ocorreu a divisão
            # territorial é maior que o ano analisado
            if(mun[1] < anoAMC):
                # se o ano análisado for maior que o ano 
                # em que houve a divisão territorial, então
                # o anoInstalção receberá o ano em que houve
                # a divisão territorial e o código receberá 
                # seu antigo código
                anoInstalacao = mun[1]
                codConvertido = codOriginal

            else:
                # se não...
                anoInstalacao = mun[1]
                codConvertido = mun[2]

                result = AMC(codConvertido, anoAMC)
                codOriginal   = result[0]
                anoInstalacao = result[1]
                codCovertid   = result[2]
                

        return codOriginal, anoInstalacao, codConvertido