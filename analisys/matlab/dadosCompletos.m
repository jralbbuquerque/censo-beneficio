close all; clc; clear;

table = load('renda-castanhal.csv');
renda = table(:, 1);
peso  = table(:, 2);

aux = 0;
k = 1;

for i = 1:length(renda)
    aux = peso(i);
    aux = round(aux);
    
    
    for j = 1:aux
        rendimento(k) = renda(i);
        k = k + 1;
    end
end

save('renda.mat', 'rendimento')