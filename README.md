## **Introdução** ##
Análise da situação dos benefícios de aposentadoria e pensão no Brasil, de acordo com os censos de 2000 e 2010

## **Origem dos Dados** ##
Dados públicos disponibilizados no site do IBGE (Fevereiro de 2019): ftp://ftp.ibge.gov.br/Censos/
Realizar o download das bases referentes aos censos de 2000 e 2010

## **Configuração do Ambiente** ##
Foi realizado um restore dos *datasets* para uma base [PostgreSQL](https://www.postgresql.org/)
Foi utilizado um container [Docker](https://www.docker.com/why-docker) contendo o serviço PostgreSQL e [Pgadmin4](https://www.pgadmin.org/). Tutorial de instalação disponível em: https://hub.docker.com/r/dpage/pgadmin4/

### **Requisitos** ### 
Distribuição Linux com os seguintes requisitos:
* GIT
* Docker 
* Docker Compose
* Unzip
* Jupyter Notebook

### **Clone do Repositório** ###
```bash
$ git clone https://github.com/jralbbuquerque/censo-beneficios.git
```

### **Servidor PostgreSQL** ### 
```bash
$ cd ../compose/
$ docker-compose up -d
```

### **Jupyter Notebook** ###
Configuração do ambiente de desenvolvimento Jupyter Lab
Tutorial de instalação: https://github.com/andrespp/docker-jupyterlab

### **Utilização do Dataset** ###
Restore da base:
* `pg_restore --no-owner --if-exists -1 -c -U your user -d censo -h localhost datasrc/censo_demografico_2010.custom`
* `pg_restore --no-owner --if-exists -1 -c -U your user -d censo -h localhost datasrc/censo_demografico_2000`

Acesse o pgAdmin através do seu navegador: `http://localhost`. login: `user`, senha:`pass`

Adicione o servidor da base: `servers => create a server...`. Name: `localhost`, host: `censodb`, port `5432`, username: `censo`, password: `censopassword`

Selecione a base de dados `censodb` e abra a ferramenta de consultas sql: `Tools => Query Toll`
