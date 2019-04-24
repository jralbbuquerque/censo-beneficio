import pandas as pd
import numpy as np

# --------------- ACM --------------- #

def AMC( codMunicipio, anoAMC ):
    amc = pd.read_csv('ds/AMC.csv')

    if( amc.newcod == codMunicipio ).any() == False:
        return print( 'Codigo %s não está na base' %codMunicipio )
        
    else:
        mun = np.array( amc[ amc.newcod == codMunicipio ] )
        codOriginal = codMunicipio
        codConvertido = 0
        anoInstalacao = 0
        while( codOriginal != codConvertido ):
            if( mun[0][1] > anoAMC ):
                anoInstalacao = mun[0][1]
                codConvertido = mun[0][2]

                result = AMC( codConvertido, anoAMC )
                codOriginal = result[0]
                anoInstalacao = result[1]
                codCovertid = result[2]
            else:
                anoInstalacao = mun[0][1]
                codConvertido = codOriginal

        return codOriginal, anoInstalacao, codConvertido