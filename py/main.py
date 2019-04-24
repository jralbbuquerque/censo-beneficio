import y2000
import y2010

# --------------------------- 2000 --------------------------- #
estados = ["ac", "al", "am", "ap", "ba", "ce", "df", 
           "es", "go", "ma", "mg", "ms", "mt", "pa", 
           "pb", "pe", "pi", "pr", "rj", "rn1", "ro", 
           "rr", "rs", "sc", "se", "sp", "to"]    
'''
uf = y2000.giniEstados(estados)
print('FINISH ESTADOS 2000. {} \n'.format(uf.shape))
uf.to_csv('../dataset/y2000-uf-gini.csv', sep=',')

cid = y2000.giniCidades(estados)
print('FINISH CIDADES 2000. {} \n'.format(cid.shape))
cid.to_csv('../dataset/y2000-cid-gini.csv', sep=',')

uf = y2000.beneficioEstados(estados)
print('FINISH ESTADOS 2000. {} \n'.format(uf.shape))
uf.to_csv('../dataset/y2000-uf-beneficios.csv', sep=',')

cid = y2000.beneficioCidades(estados)
print('FINISH CIDADES 2000. {} \n'.format(cid.shape))
cid.to_csv('../dataset/y2000-cid-beneficios.csv', sep=',')
'''
uf = y2000.progressividadeEstados(estados)
print('FINISH ESTADOS 2000. {} \n'.format(uf.shape))
uf.to_csv('../dataset/y2000-uf-progressividade.csv', sep=',')

cid = y2000.progressividadeEstados(estados)
print('FINISH CIDADES 2000. {} \n'.format(cid.shape))
cid.to_csv('../dataset/y2000-cid-progressividade.csv', sep=',')

# --------------------------- 2010 --------------------------- #
estados = ["ac", "al" , "am", "ap", "ba", "ce", "df", 
           "es", "go", "ma", "mg", "ms", "mt", "pa", 
           "pb", "pe", "pi", "pr", "rj", "rn", "ro", 
           "rr", "rs", "sc", "se", "sp1", "sp2_rm", "to"]
'''
uf = y2010.giniEstados(estados)
print('FINISH GINI ESTADOS 2010. {} \n'.format(uf.shape))
uf.to_csv('../dataset/y2010-uf-gini.csv', sep=',')

cid = y2010.giniCidades(estados)
print('FINISH GINI CIDADES 2010. {} \n'.format(cid.shape))
cid.to_csv('../dataset/y2010-cid-gini.csv', sep=',')

uf = y2010.beneficioEstados(estados)
print('FINISH BENEFICIOS ESTADOS 2010. {} \n'.format(uf.shape))
uf.to_csv('../dataset/y2010-uf-beneficio.csv', sep=',')

cid = y2010.beneficioCidades(estados)
print('FINISH BENEFICIOS CIDADES 2010. {} \n'.format(cid.shape))
cid.to_csv('../dataset/y2010-cid-beneficio.csv', sep=',')
'''
uf = y2010.progressividadeEstados(estados)
print('FINISH PROGRESSIVIDADE ESTADOS 2010. {} \n'.format(uf.shape))
uf.to_csv('../dataset/y2010-uf-progressividade.csv', sep=',')

cid = y2010.progressividadeCidades(estados)
print('FINISH PROGRESSIVIDADE CIDADES 2010. {} \n'.format(cid.shape))
cid.to_csv('../dataset/y2010-cid-progressividade.csv', sep=',')
