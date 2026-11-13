# Vetores e percursos

Um vetor reúne vários valores em uma sequência. Em Python, listas são usadas
para representar essa estrutura. Os índices começam em zero: em uma lista com
cinco itens, os índices válidos vão de zero a quatro.

Para encontrar o maior elemento, pode-se iniciar uma variável com o primeiro
valor e percorrer os demais. Sempre que o elemento atual for maior que o maior
conhecido, a variável é atualizada. Inicializar o maior com zero é incorreto
quando todos os valores podem ser negativos.

# Busca linear

A busca linear percorre uma sequência do início ao fim, comparando cada elemento
com o valor procurado. Ao encontrar o valor, o algoritmo pode retornar o índice.
Se terminar o percurso sem encontrá-lo, retorna um marcador, como `-1`.

No melhor caso, o valor está na primeira posição e apenas uma comparação é
necessária. No pior caso, o valor está no final ou não existe, exigindo até `n`
comparações. Por isso, sua complexidade de tempo no pior caso é O(n).

# Casos de teste e casos limite

Um caso de teste define entradas e o resultado esperado. Além do caso comum,
teste limites: lista vazia, um único elemento, números negativos, zero, valores
repetidos e o item procurado ausente. Esses testes revelam suposições escondidas
na solução.

