% Cálculo do Índice de Gini
clear; clc; close;

% Rendimento bruto
renda = load( 'renda.mat' ); 
% renda = table(:, 1) .* table(:, 2);
% renda=[950 950 980 1000 1200 1300 1300 3500 5000 8000];
rendimento = renda.rendimento;
n = length( rendimento );

%Renda média
m = sum( rendimento ) / n;

% Variável auxiliar
aux = 0;

for i = 1:n
    % Proporção acumulada da população
    p( i ) = i / n;
    
    % Proporção acumulada de renda
    r( i ) = sum( rendimento( 1 : i ) ) / ( n * m );
    
    % Área da curva de Lorenz
    area( i ) = ( ( aux + r ( i ) ) / 2 ) * min( p ); 
    aux = r ( i );
end

% Cálculo Índice de Gini
B = sum( area );
A = 0.5 - B;
G = A / ( A + B )

% Plot
plot(p, r, 'r'); 
hold on;
plot([0,1],[0,1],'--k');
axis tight; axis square; grid on
title(['\bfÍndice de Gini = ',num2str(G)]);
xlabel('Proporção de população');
ylabel('Proporção de renda');