# Estruturas condicionais

Uma estrutura condicional escolhe qual bloco executar de acordo com uma
expressão lógica. Em Python, `if` representa a primeira condição, `elif` permite
testar alternativas e `else` trata o caso restante. A ordem das condições é
importante: quando uma condição verdadeira é encontrada, os blocos seguintes da
mesma estrutura não são executados.

Antes de escrever o código, identifique os casos do problema e transforme cada
regra em uma condição. Para classificar um número, por exemplo, os casos são:
maior que zero, menor que zero e igual a zero.

# Laço while

O laço `while` repete um bloco enquanto sua condição for verdadeira. Ele é útil
quando a quantidade de repetições depende de uma condição e não está pronta em
uma coleção. Um laço correto normalmente possui inicialização, condição e
atualização da variável de controle.

Se a atualização for esquecida, a condição pode permanecer verdadeira para
sempre, formando um laço infinito. Um teste de mesa registra, em cada iteração,
o valor da variável de controle, o resultado da condição e a saída produzida.

# Laço for

O laço `for` percorre itens de uma coleção ou uma sequência conhecida. Em
Python, `range(inicio, fim)` gera valores do início até um valor anterior ao fim.
Por isso, `range(1, 6)` produz 1, 2, 3, 4 e 5.

Quando a quantidade de repetições é conhecida, `for` costuma comunicar melhor a
intenção. Quando a repetição depende de uma condição dinâmica, `while` pode ser
mais adequado.

