import y2000
import y2010

# --------------------------- 2000 --------------------------- #
estados = [ "ac", "al", "am", "ap", "ba", "ce", "df", "es", "go", "ma", "mg", "ms", "mt",
          "pa", "pb", "pe", "pi", "pr", "rj", "rn1", "ro", "rr", "rs", "sc", "se", "sp", "to" ]    

uf = y2000.giniEstados( estados )
print('FINISH ESTADOS 2000. {} \n'.format(uf.shape))
uf.to_csv('gini-y2000-estados.csv', sep=',')

cid = y2000.giniCidades( estados )
print('FINISH CIDADES 2000. {} \n'.format(cid.shape))
cid.to_csv('gini-y2000-cidades.csv', sep=',')


# --------------------------- 2010 --------------------------- #
estados = [ "ac", "al" , "am", "ap", "ba", "ce", "df", "es", "go", "ma", "mg", "ms", "mt",
         "pa", "pb", "pe", "pi", "pr", "rj", "rn", "ro", "rr", "rs", "sc", "se", 
         "sp1", "sp2_rm", "to" ]

uf = y2010.giniEstados( estados )
print('FINISH ESTADOS 2010. {} \n'.format(uf.shape))
uf.to_csv('gini-y2010-estados.csv', sep=',')

cid = y2010.giniCidades( estados )
print('FINISH CIDADES 2010. {} \n'.format(cid.shape))
cid.to_csv('gini-y2010-cidades.csv', sep=',')
