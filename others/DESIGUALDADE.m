%GINI NA BASE DE MICRODADOS
%carrega a base
%M = load('estudo8_microdados_belem_MATLAB.csv');
%M = [load('estudo8_microdados_capitais_MATLAB_p1.csv');load('estudo8_microdados_capitais_MATLAB_p2.csv')];

%COLUNAS: CD_UF; CD_MUN; CD107; PESO; RURAL; RENDA; PESOAS

M = [
    load('estudo8_microdados_2000_AC.csv') 
    load('estudo8_microdados_2000_AL.csv')
    load('estudo8_microdados_2000_AM.csv')
    load('estudo8_microdados_2000_AP.csv')
    load('estudo8_microdados_2000_BA.csv')
    load('estudo8_microdados_2000_CE.csv')
    load('estudo8_microdados_2000_DF.csv')
    load('estudo8_microdados_2000_ES.csv')
    load('estudo8_microdados_2000_GO.csv')
    load('estudo8_microdados_2000_MA.csv')
    load('estudo8_microdados_2000_MG.csv')
    
    load('estudo8_microdados_2000_MS.csv')
    load('estudo8_microdados_2000_MT.csv')
    load('estudo8_microdados_2000_PA.csv')
    load('estudo8_microdados_2000_PB.csv')
    load('estudo8_microdados_2000_PE.csv')
    load('estudo8_microdados_2000_PI.csv')
    load('estudo8_microdados_2000_PR.csv')
    load('estudo8_microdados_2000_RJ.csv')
    load('estudo8_microdados_2000_RN.csv')
    
    load('estudo8_microdados_2000_RO.csv')
    load('estudo8_microdados_2000_RR.csv')
    load('estudo8_microdados_2000_RS.csv')
    load('estudo8_microdados_2000_SC.csv')
    load('estudo8_microdados_2000_SE.csv')
    load('estudo8_microdados_2000_TO.csv')
    load('estudo8_microdados_2000_SP.csv')
    ];


n = 0;
peso = 0;

M_RES = [];

while ~isempty(M),
    %pega o primeiro indice que indica o primeiro municipio
    m = M(1,2);

    %municipio sendo usado para o calculo
    fprintf('\n\tMUNICIPIO %d ',m);
    
    %acha as linhas daquele municipio
    i = find(M(:,2)==m);
    
    %carrega no T as linhas daquele municipio
    T = M(i,:);
    
    Pessoas = [];
    RTotal = [];    
    Domicilios = [];    
    RPercapita = [];
    RURAL = [];
    
    %RPTotal = [];
    %APOTotal = [ ];
    
    L_RES = [];
    %L_RES = [m, gini, gini_IBGE, theil_t];
    
    
    while ~isempty(T),
        
        t = T(1,3);
    
        %acha as linhas daquele CD107
        i = find(T(:,3)==t);
    
        %carrega no V as linhas daquele CD107
        V = T(i,:);
        
        while ~isempty(V),

            %pega o peso v
            v = V(1,4);

            %acha as linhas daquele peso
            i = find(V(:,4)==v);

            %carrega no K as linhas daquele peso (domicilios)
            K = V(i,:);

%             [n, c] = size(K);
%             
             Pessoas = [Pessoas v*K(1,7)];
             RTotal = [RTotal v*K(1,6)];
             RPercapita = [RPercapita K(1,6)/K(1,7)];
             Domicilios = [Domicilios v];
             RURAL = [RURAL K(1,5)];         

%             APOTotal = [APOTotal K(1,4)*K(1,8)];
%             RPTotal = [RPTotal K(1,4)*K(1,7)];
             
            %acha o proximo conjunto de pesos que ainda nao foram usados
            i = find(V(:,4)~=v);

            %descarta o que já foi usado
            V = V(i,:);
        end
        
        
        %acha o proximo conjunto de CD107 que ainda nao foram usados
        i = find(T(:,3)~=t);
    
        %descarta o que já foi usado
        T = T(i,:);
    end
    
    %GINI da renda vs domicilio
    X = Domicilios;
    Y = RTotal;
    
    [s, is] = sort (Y./X);
    
    X = X(is);
    Y = Y(is);
    
    aX = cumsum(X/sum(X));
    aY = cumsum(Y/sum(Y));
    
    giniRD = 2*(0.5 - trapz([0 aX],[0 aY]));
    
    %fprintf('Gini da renda domiciliar %f\n', gini);
    fprintf(' gini(Renda vs Domicilios) %f', giniRD);
    %FIM GINI 
    
    
%     %GINI da renda PER CAPITA vs Pessoas 
%     X = Pessoas;
%     Y = RPercapita;
%     
%     [s, is] = sort (Y./X);
%     
%     X = X(is);
%     Y = Y(is);
%     
%     aX = cumsum(X/sum(X));
%     aY = cumsum(Y/sum(Y));
%     
%     giniPCP = 2*(0.5 - trapz([0 aX],[0 aY]));
%     
%     %fprintf('Gini da renda domiciliar %f\n', gini);
%     fprintf(' gini(Per Capita vs Pessoas) %f', giniPCP);
%     %FIM GINI da renda do domicilio
%     
      
    %GINI da renda total vs pessoas
    X = Pessoas;
    Y = RTotal;
    
    [s, is] = sort (Y./X);
    
    X = X(is);
    Y = Y(is);
    
    aX = cumsum(X/sum(X));
    aY = cumsum(Y/sum(Y));
    
    giniRP = 2*(0.5 - trapz([0 aX],[0 aY]));
    
    %fprintf('Gini da renda domiciliar %f\n', gini);
    fprintf(' gini(Renda vs Pessoas) %f', giniRP);
    %FIM GINI da renda do domicilio
    
    
    
%     %GINI da renda do trabalho principal do responsavel do domicilio
%     X = Domicilios;
%     Y = RPTotal;
%     
%     [s, is] = sort (Y./X);
%     
%     X = X(is);
%     Y = Y(is);
%     
%     aX = cumsum(X/sum(X));
%     aY = cumsum(Y/sum(Y));
%     
%     gini_IBGE = 2*(0.5 - trapz([0 aX],[0 aY]));
%     
%     %fprintf('Gini da renda domiciliar %f\n', gini);
%     fprintf(' gini(IBGE) %f', gini_IBGE);
%     %FIM GINI da renda trabalho principal do responsavel do domicilio
%     
    
    %THEIL-T
    Y = RPercapita./sum(RTotal);
    N = sum(Pessoas);
    
    LNY = log(N*Y);
    
    i = find(Y==0);
    LNY(i) = 0;
    
    theil_t = sum( Pessoas.*Y.*LNY );
    fprintf(' theil_t %f', theil_t);
    %FIM THEIL-T
    
    
    %AVALIANDO A POBREZA
    %RTotal2010 = RTotal / ((1000^2)*2.75) * 26303.4237875;
    
    i_p = find(RPercapita < 255);
    i_extp = find(RPercapita < 127.5);
    
    
    %salvando resultados
    L_RES = [m, giniRD, giniRP, theil_t, sum(Pessoas(i_p))/sum(Pessoas)*100,  sum(Pessoas(i_extp))/sum(Pessoas)*100, sum(Domicilios(i_p))/sum(Domicilios)*100,  sum(Domicilios(i_extp))/sum(Domicilios)*100];
    M_RES = [M_RES; L_RES];
    
    %acha o proximo conjunto de municipios que ainda nao foram usados
    i = find(M(:,2)~=m);
    
    %descarta o que já foi usado
    M = M(i,:);
    
end

fprintf('\n');
%save  'RESULTADOS.txt' 'M_RES'  -ascii
save  'RESULTADOS_01062018.txt' 'M_RES'  -ascii

