# Material de Apoio 03 - Estrutura Sequencial em Portugol

Fonte didática: Material de Apoio 03 da disciplina Algoritmos e Programação I.

Um programa sequencial organiza comandos de entrada, processamento e saída. A
entrada reúne os dados fornecidos ao programa, o processamento realiza cálculos
ou operações e a saída apresenta o resultado.

# Entrada com leia

O comando `leia()` aguarda um dado do usuário e o armazena na variável indicada.
É importante solicitar claramente a informação antes da leitura:

```text
escreva("Digite sua idade: ")
leia(idade)
```

# Saída com escreva

O comando `escreva()` apresenta textos, valores de variáveis ou uma combinação
dos dois. Um texto entre aspas é mostrado literalmente. Um nome de variável sem
aspas é substituído pelo valor armazenado:

```text
escreva("Ola!")
escreva(idade)
escreva("Sua idade e: ", idade)
```

# Estrutura sequencial

Na estrutura sequencial, cada comando é executado uma vez, do primeiro ao último,
na ordem escrita. O processamento só deve usar uma variável depois que ela tiver
recebido um valor.

```text
algoritmo "idade_futura"

var
    idade, idade_futura: inteiro

inicio
    escreva("Digite sua idade: ")
    leia(idade)
    idade_futura <- idade + 10
    escreva("Daqui a 10 anos voce tera ", idade_futura, " anos.")
fimalgoritmo
```

# Exemplo de cálculo do troco

Para calcular um troco, o programa recebe `preco` e `pagamento`, calcula
`troco <- pagamento - preco` e apresenta o resultado. As três variáveis são do
tipo `real`, pois valores monetários podem possuir casas decimais.

# Checklist de um algoritmo sequencial

Antes de concluir, verifique: todas as variáveis necessárias foram declaradas; os
tipos são adequados; as mensagens de entrada são claras; a expressão de
processamento está correta; o resultado foi apresentado; e os comandos estão na
ordem correta.

