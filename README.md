# A evolução dos gastos com transferências e o desempenho no Brasileirão

**Autor:** Pedro Vinicius Cardim

## Pergunta Norteadora
O aumento do valor gasto com contratações nos grandes clubes brasileiros garante melhor desempenho e posições mais altas na tabela do Campeonato Brasileiro?

## Fontes de dados
| Fonte | Formato | Acesso | Extraído | Link |
|---|---|---|---|---|
| Transfermarkt | CSV | token | (10/09/2026) | https://www.kaggle.com/datasets/davidcariboo/player-scores |
| Brasileirão | CSV | token | (17/09/2026) | https://www.kaggle.com/datasets/adaoduque/campeonato-brasileiro-de-futebol |

## Defeitos conhecidos das fontes

### Transfermarkt

* Coluna 'transfer_fee' possui 35,1% de valores ausentes e 54,9% iguais a zero.
* Coluna 'market_value_in_eur' possui 38,9% de valores ausentes.
* O calendario registrado em 'transfer_season' reflete a temporada europeia, incompatível com o calendário do futebol brasileiro.

### Brasileirão

* A coluna arrecadacao é inutilizável na prática, com quase 96% de dados ausentes.
* Faltam informações sobre formacao_mandante, formacao_visitante, tecnico_mandante e tecnico_visitante em mais de 50% dos jogos.
* Redundância de informações e excesso de colunas de contexto pontual (como horário e arena) que não agregam para a análise anual.

## Decisões de tratamento (Camada Prata)

### Transfermarkt

* A coluna transfer_season (temporada europeia) foi eliminada por ser redundante e incompatível com o calendário brasileiro. A rastreabilidade foi garantida através da manutenção da coluna original transfer_date.
* A coluna transfer_date foi formatada para o tipo datetime e, a partir dela, foi extraída a nova coluna transfer_year (ano civil da transação).
* As datas foram formatadas para o tipo correto (datetime) e foi criada a coluna transfer_year em substituição da transfer_season.
* As linhas cujo ano de transferência é inferior a 2018 foram apagadas.
* Foram criadas as colunas to_club_name_padrao e from_club_name_padrao. Foi utilizado um script de limpeza genérico para converter os nomes para minúsculas, remover acentos e espaços. A função aplicar_mapa foi aplicada para trocar sinônimos usando o dicionário MAPA_CLUBES_TM.
* As colunas originais com maiúsculas e acentos foram mantidas intactas, utilizando as versões padronizadas apenas como chave de cruzamento.
* Foram criadas duas colunas numéricas, transfer_fee_num e market_value_in_eur_num, que guardam os dados financeiros tratados. Textos indicando ausência de custo direto (como "free transfer" e "loan") foram convertidos para 0.0. Valores financeiros completamente ausentes foram mantidos como NaN para evitar a exclusão indevida das linhas de jogadores na base.
* Foi implementada uma validação de domínio para remoção exclusiva de erros financeiros físicos (valores negativos ou superiores a 300 milhões de Euros).

### Brasileirao 

* Foram eliminadas colunas consideradas inúteis para o objetivo da análise. Excluíram-se dados financeiros (arrecadacao), táticos (formacao_mandante, formacao_visitante, tecnico_mandante, tecnico_visitante) e de contexto pontual (hora, arena) e as redundâncias geográficas (mandante_Estado e visitante_Estado)..
* As datas foram tratadas para o formato datetime.
* Foi criada a nova coluna ano_campeonato (no formato Int64), que guarda o ano civil em que a partida foi realizada.
* Foram criadas as colunas mandante_padrao e visitante_padrao, com os nomes dos times tratados (retirados os espaços e acentos, caracteres convertidos para minúsculas e sinônimos uniformizados pelo dicionário MAPA_CLUBES_BR).
* Os placares (mandante_Placar e visitante_Placar) foram tipados para o numérico inteiro do pandas (Int64). Esse tipo foi escolhido por suportar valores ausentes (NaN) nativamente, sem forçar a conversão de gols para números decimais.
* Foi aplicada uma regra estrita de validação de domínio para os placares, removendo sumariamente linhas com valores negativos ou absurdamente altos (superiores a 15 gols). Isso assegura a exclusão de erros de digitação da fonte original.

## Atributos derivados

### transfer_year

* Ano civil extraído da data exata da transferência. Serve para alinhar o momento do gasto do clube com o ano em que o respectivo campeonato foi disputado, substituindo o dado da temporada europeia.

### ano_campeonato

* Ano civil extraído da data da partida. Serve como chave temporal para permitir o cruzamento dos jogos do campeonato com os investimentos feitos no mesmo período.