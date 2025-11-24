# Análise de dados com Cassandra e Spark

## 0. Introdução

Este projeto tem como objetivo explorar e analisar dados reais de comércio eletrônico brasileiro utilizando uma arquitetura moderna baseada em Apache Cassandra e Apache Spark, orquestrada com Docker e acessada por meio de Jupyter Notebooks.

O resultado é um ambiente reproduzível e escalável, que demonstra na prática como integrar Cassandra e Spark para análise de dados de e-commerce, desde a ingestão até a extração de insights de negócio.

## 1. Base de dados

### Contexto

Este projeto utiliza o Olist Brazilian E-Commerce Public Dataset, um dataset público disponibilizado pela Olist Store no Kaggle. O dataset contém informações reais e anonimizadas de aproximadamente 100 mil pedidos realizados entre 2016 e 2018 em diversos marketplaces brasileiros conectados à plataforma Olist.

A Olist é uma plataforma que conecta pequenos e médios varejistas a grandes marketplaces brasileiros, permitindo que vendedores anunciem seus produtos em múltiplos canais através de um único contrato. Este dataset oferece uma visão abrangente do ecossistema de e-commerce brasileiro, incluindo dados de pedidos, produtos, clientes, vendedores, pagamentos e avaliações.

### Fonte de dados

Nome: Brazilian E-Commerce Public Dataset by Olist

Plataforma: Kaggle

Período: Setembro/2016 a Agosto/2018

Volume: ~100.000 pedidos

### Estrutura do Dataset


#### 1. **olist_customers_dataset.csv**
Informações sobre os clientes que realizaram pedidos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `customer_id` | String (UUID) | Identificador único do cliente |
| `customer_unique_id` | String (UUID) | Identificador único do cliente (pode ter múltiplos customer_id) |
| `customer_zip_code_prefix` | Integer | Prefixo do CEP do cliente |
| `customer_city` | String | Cidade do cliente |
| `customer_state` | String | Estado do cliente (UF) |


---

#### 2. **olist_sellers_dataset.csv**
Informações sobre os vendedores cadastrados na plataforma.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `seller_id` | String (UUID) | Identificador único do vendedor |
| `seller_zip_code_prefix` | Integer | Prefixo do CEP do vendedor |
| `seller_city` | String | Cidade do vendedor |
| `seller_state` | String | Estado do vendedor (UF) |


---

#### 3. **olist_products_dataset.csv**
Catálogo de produtos disponíveis para venda.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `product_id` | String (UUID) | Identificador único do produto |
| `product_category_name` | String | Categoria do produto (em português) |
| `product_name_length` | Integer | Comprimento do nome do produto (caracteres) |
| `product_description_length` | Integer | Comprimento da descrição do produto |
| `product_photos_qty` | Integer | Quantidade de fotos do produto |
| `product_weight_g` | Float | Peso do produto (gramas) |
| `product_length_cm` | Float | Comprimento do produto (cm) |
| `product_height_cm` | Float | Altura do produto (cm) |
| `product_width_cm` | Float | Largura do produto (cm) |


---

#### 4. **olist_orders_dataset.csv**
Informações principais sobre os pedidos realizados.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `order_id` | String (UUID) | Identificador único do pedido |
| `customer_id` | String (UUID) | Referência ao cliente |
| `order_status` | String | Status do pedido (delivered, shipped, canceled, etc.) |
| `order_purchase_timestamp` | Timestamp | Data/hora da compra |
| `order_approved_at` | Timestamp | Data/hora da aprovação do pagamento |
| `order_delivered_carrier_date` | Timestamp | Data/hora de envio para transportadora |
| `order_delivered_customer_date` | Timestamp | Data/hora de entrega ao cliente |
| `order_estimated_delivery_date` | Timestamp | Data estimada de entrega |


---

#### 5. **olist_order_items_dataset.csv**
Detalhes dos itens que compõem cada pedido.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `order_id` | String (UUID) | Referência ao pedido |
| `order_item_id` | Integer | Número sequencial do item no pedido |
| `product_id` | String (UUID) | Referência ao produto |
| `seller_id` | String (UUID) | Referência ao vendedor |
| `shipping_limit_date` | Timestamp | Data limite para envio |
| `price` | Float | Preço do item |
| `freight_value` | Float | Valor do frete |


---

#### 6. **olist_order_payments_dataset.csv**
Informações sobre os pagamentos dos pedidos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `order_id` | String (UUID) | Referência ao pedido |
| `payment_sequential` | Integer | Número sequencial do pagamento (pedidos podem ter múltiplos pagamentos) |
| `payment_type` | String | Tipo de pagamento (credit_card, boleto, voucher, debit_card) |
| `payment_installments` | Integer | Número de parcelas |
| `payment_value` | Float | Valor do pagamento |


---

#### 7. **olist_order_reviews_dataset.csv**
Avaliações e comentários dos clientes sobre os pedidos.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `review_id` | String (UUID) | Identificador único da avaliação |
| `order_id` | String (UUID) | Referência ao pedido |
| `review_score` | Integer | Nota da avaliação (1 a 5) |
| `review_comment_title` | String | Título do comentário |
| `review_comment_message` | String | Mensagem do comentário |
| `review_creation_date` | Timestamp | Data de criação da avaliação |
| `review_answer_timestamp` | Timestamp | Data de resposta à avaliação |


## 2. Pergunta de negócio

Este projeto busca responder questões estratégicas sobre o comportamento do e-commerce brasileiro, utilizando análise de dados distribuída com Apache Cassandra e PySpark.

#### 2.1 **Quais categorias de produtos geram mais receita?**

#### 2.2 **Quais estados brasileiros concentram mais vendas e receita?**

#### 2.3 **Qual a relação entre preço e quantidade vendida?**

#### 2.4 **Qual o tempo médio de entrega por região?**

#### 2.5 **Quais são os métodos de pagamento predominantes em compras de alto valor?**

## 4. Arquitetura da solução

A arquitetura do projeto foi construída utilizando contêineres Docker para isolar e orquestrar os principais componentes da solução: banco de dados NoSQL (Cassandra), ambiente de análise distribuída (Spark) e interface interativa (Jupyter Notebook).

### 4.1 Visão geral
A solução é composta por três serviços principais:

- cassandra-seed: nó principal do cluster Cassandra (seed node), responsável por inicializar o cluster e servir como ponto de descoberta para outros nós.

- cassandra-node1: segundo nó do cluster Cassandra, formando um cluster distribuído de banco de dados.

- jupyter-pyspark: ambiente de análise que combina:
    
        Jupyter Notebook

        Apache Spark (modo local) com conector para Cassandra

        Ferramentas de ETL (pandas, numpy) e visualização (matplotlib, seaborn)

        DSBulk (DataStax Bulk Loader) para carga em massa de dados no Cassandra

Os serviços se comunicam por meio de uma rede Docker bridge (cassandra-network), permitindo que o Spark se conecte ao Cassandra utilizando os nomes dos contêineres (ex.: cassandra-seed) como host.

## 5. Tabelas principais

#### 5.1 Tabela customers

Armazena os dados dos clientes, permitindo análises por região (estado/cidade).

- Partition key: customer_id
- Uso principal:
    - Join com orders_by_customer para análises de vendas e receita por estado/região.
    - Base para contagem de clientes distintos.

#### 5.2 Tabela sellers

Dados dos vendedores da plataforma.

- Partition key: seller_id
- Uso principal:
    - Análises futuras por região do vendedor.
    - Possibilidade de estudar desempenho por seller.

#### 5.3 Tabela products

Catálogo de produtos com informações de categoria e atributos físicos.

- Partition key: product_id
- Uso principal:
    - Join com items_by_order para:
    - calcular receita por categoria de produto;
    - analisar relação entre atributos (peso, dimensões) e vendas;
    - cruzar categorias com avaliações (reviews_by_order).

#### 5.4 Tabela orders_by_customer

Tabela que combina informações de pedidos com o cliente (1 pedido por linha), preparada para consultas por cliente e por tempo.

 - Partition key: customer_id
 - Clustering column: order_id
 - Uso principal:
     - vendas e receita por estado
     - tempo médio de entrega

#### 5.5 Tabela items_by_order

Tabela de itens agregada por pedido, preparada para análise de receita e quantidade.

 - Partition key: order_id
 - Clustering column: order_item_id.
 - Uso Principal:
     - receita por categoria
     - valor total de pedidos
     - construção do ticket médio

#### 5.6 Tabela payments_by_order

Tabela com informações de pagamento agrupadas por pedido.
 - Partition key: order_id
 - Clustering column: payment_sequential
 - Uso principal:
     - métodos de pagamento mais utilizados
     - comportamento de pagamentos em pedidos de alto valor

#### 5.7 Tabela reviews_by_order

Tabela com avaliações de clientes associadas ao pedido.
 - Partition key: order_id
 - Clustering column: review_id
 - Uso Principal:
     - análise de satisfação por categoria de produto
     - estudos de relação entre tempo de entrega e nota de avaliação

### 6.1 Visão geral do fluxo

#### 6.1.1 Extração
 - Download dos arquivos CSV originais do dataset da Olist (via Kaggle).
 - Organização dos arquivos em diretórios específicos dentro do projeto.

#### 6.1.2 Transformação
 - Tratamento dos dados com Python (pandas), incluindo:
    * conversão de tipos;
    * limpeza e padronização;
    * criação de tabelas derivadas orientadas a queries;
    * geração de arquivos CSV tratados prontos para carga no cassandra

#### 6.1.3 Carga
 - Utilização do DataStax Bulk Loader (DSBulk), instalado no contêiner jupyter-pyspark, para carregar os CSV tratados diretamente nas tabelas do keyspace olist_keyspace no Cassandra.

 #### 6.1.4 Consumo
  - Leitura das tabelas Cassandra pelo Spark, criando DataFrames PySpark que são usados nas análises de negócio.