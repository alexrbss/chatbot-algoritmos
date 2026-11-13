# Material de Apoio 02 - Introdução ao Portugol

Fonte didática: Material de Apoio 02 da disciplina Algoritmos e Programação I.

Portugol é uma forma de representar algoritmos com comandos escritos de maneira
semelhante à língua portuguesa. Ele permite estudar fundamentos de programação
antes de lidar com todos os detalhes de linguagens como C.

# Estrutura de um algoritmo em Portugol

Todo algoritmo possui um nome, uma área para declarar variáveis e uma região na
qual os comandos são executados. A estrutura usada na disciplina é:

```text
algoritmo "exemplo"

var
    // declaracao das variaveis

inicio
    // comandos do programa

fimalgoritmo
```

`algoritmo` inicia e nomeia o algoritmo. `var` marca a área de declaração de
variáveis. `inicio` abre a sequência de comandos e `fimalgoritmo` encerra o
algoritmo. Comentários começam com `//` e não são executados.

# Variáveis e tipos de dados

Uma variável é um espaço reservado na memória do computador para armazenar um
valor durante a execução. O nome identifica a variável, o tipo determina a
espécie de informação permitida e o valor é o dado armazenado naquele momento.

Os tipos apresentados são: `inteiro` para números sem casas decimais, `real`
para números com casas decimais, `caractere` para um caractere, `literal` para
texto e `logico` para verdadeiro ou falso.

Os nomes devem começar por letra, não devem conter espaços, acentos ou símbolos
especiais e não podem usar palavras reservadas. Nomes como `idade_aluno` ajudam a
revelar o propósito do dado.

# Declaração e atribuição

Declarar uma variável reserva e identifica um espaço de memória. Atribuir coloca
um valor nesse espaço. Em Portugol, a atribuição usa `<-`:

```text
var
    idade: inteiro

inicio
    idade <- 18
```

Uma expressão é calculada antes de seu resultado ser armazenado. Em
`media <- (nota1 + nota2) / 2`, primeiro a soma e a divisão são realizadas;
depois o resultado é atribuído a `media`. O símbolo `<-` não é uma igualdade
matemática: ele indica o sentido do armazenamento.

