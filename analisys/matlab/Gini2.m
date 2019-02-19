% Cálculo do Índice de Gini
clear; clc; close;

% Rendimento bruto
renda = load( 'renda.mat' ); 
% renda = table(:, 1) .* table(:, 2);
renda=[ 950 950 980 1000 1200 1300 1300 3500 5000 8000];
rendimento = renda;
% rendimento = renda.rendimento;
n = length( rendimento );

%Renda média
m = sum( rendimento ) / n;
aux = 0;
gini_parcial = (rendimento(1)/(n*m)) * 0.1;
k = 0;

for i = 1:n
    % Proporção acumulada da população
    p( i ) = i / n;
    
    % Proporção acumulada de renda
    r( i ) = sum( rendimento( 1 : i ) ) / ( n * m );
end

for i = 1:n-1
    aux = (p( i + 1 ) - p( i )) * (r( i + 1 ) + r( i ));
    gini_parcial = gini_parcial + aux;
end

g = 1 - gini_parcial