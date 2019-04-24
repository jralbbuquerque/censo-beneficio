import psycopg2

def conn():
    # ---------- CONEXÃO COM O BANCO DE DADOS ---------- #
    # Parâmetros da Conexão
    host    = 'lincpo.com.br'
    port    = '2035'
    dbname  = 'censo'
    dbtable = 'censo_2000'
    user    = 'prevdb_user'
    pwd     = 'pr3v'

    # Conexão com o Banco de Dados
    conn = psycopg2.connect("host='{}' port={} dbname='{}'user={} password={}"
             .format(host, port, dbname, user, pwd))

    if conn == -1:
        print("Não foi possível conectar a Base de Dados")
    else:
        return conn