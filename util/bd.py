# -*- coding: utf-8 -*-
"""
@author: Francisco Júnior
"""
# Preâmbulo
import psycopg2

# Conexão com o Banco de Dados 
def conn():
    # Parâmetros da conexão
    #host    = '200.239.72.1'
    #port    = '2035'
    #dbname  = 'censo'
    #user    = 'prevdb_user'
    #pwd     = 'pr3v'

    # Parâmetros da conexão
    host    = 'localhost'
    port    = '5432'
    dbname  = 'censo'
    user    = 'postgres'
    pwd     = 'pr3v'

    # Estabelece conexão
    conn = psycopg2.connect("host='{}' port={} dbname='{}'user={} password={}"
             .format(host, port, dbname, user, pwd))

    if conn == -1:
        print("Não foi possível conectar a Base de Dados")
    else:
        return conn