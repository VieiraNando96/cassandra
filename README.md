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

## 3. Arquitetura da solução

A arquitetura do projeto foi construída utilizando contêineres Docker para isolar e orquestrar os principais componentes da solução: banco de dados NoSQL (Cassandra), ambiente de análise distribuída (Spark) e interface interativa (Jupyter Notebook).

### 3.1 Visão geral
A solução é composta por três serviços principais:

- cassandra-seed: nó principal do cluster Cassandra (seed node), responsável por inicializar o cluster e servir como ponto de descoberta para outros nós.

- cassandra-node1: segundo nó do cluster Cassandra, formando um cluster distribuído de banco de dados.

- jupyter-pyspark: ambiente de análise que combina:
    
        Jupyter Notebook

        Apache Spark (modo local) com conector para Cassandra

        Ferramentas de ETL (pandas, numpy) e visualização (matplotlib, seaborn)

        DSBulk (DataStax Bulk Loader) para carga em massa de dados no Cassandra

Os serviços se comunicam por meio de uma rede Docker bridge (cassandra-network), permitindo que o Spark se conecte ao Cassandra utilizando os nomes dos contêineres (ex.: cassandra-seed) como host.

## 4. Tabelas principais

#### 4.1 Tabela customers

Armazena os dados dos clientes, permitindo análises por região (estado/cidade).

- Partition key: customer_id
- Uso principal:
    - Join com orders_by_customer para análises de vendas e receita por estado/região.
    - Base para contagem de clientes distintos.

#### 4.2 Tabela sellers

Dados dos vendedores da plataforma.

- Partition key: seller_id
- Uso principal:
    - Análises futuras por região do vendedor.
    - Possibilidade de estudar desempenho por seller.

#### 4.3 Tabela products

Catálogo de produtos com informações de categoria e atributos físicos.

- Partition key: product_id
- Uso principal:
    - Join com items_by_order para:
    - calcular receita por categoria de produto;
    - analisar relação entre atributos (peso, dimensões) e vendas;
    - cruzar categorias com avaliações (reviews_by_order).

#### 4.4 Tabela orders_by_customer

Tabela que combina informações de pedidos com o cliente (1 pedido por linha), preparada para consultas por cliente e por tempo.

 - Partition key: customer_id
 - Clustering column: order_id
 - Uso principal:
     - vendas e receita por estado
     - tempo médio de entrega

#### 4.5 Tabela items_by_order

Tabela de itens agregada por pedido, preparada para análise de receita e quantidade.

 - Partition key: order_id
 - Clustering column: order_item_id.
 - Uso Principal:
     - receita por categoria
     - valor total de pedidos
     - construção do ticket médio

#### 4.6 Tabela payments_by_order

Tabela com informações de pagamento agrupadas por pedido.
 - Partition key: order_id
 - Clustering column: payment_sequential
 - Uso principal:
     - métodos de pagamento mais utilizados
     - comportamento de pagamentos em pedidos de alto valor

#### 4.7 Tabela reviews_by_order

Tabela com avaliações de clientes associadas ao pedido.
 - Partition key: order_id
 - Clustering column: review_id
 - Uso Principal:
     - análise de satisfação por categoria de produto
     - estudos de relação entre tempo de entrega e nota de avaliação

### 5. Visão geral do fluxo

#### 5.1 Extração
 - Download dos arquivos CSV originais do dataset da Olist (via Kaggle).
 - Organização dos arquivos em diretórios específicos dentro do projeto.

#### 5.2 Transformação
 - Tratamento dos dados com Python (pandas), incluindo:
    * conversão de tipos;
    * limpeza e padronização;
    * criação de tabelas derivadas orientadas a queries;
    * geração de arquivos CSV tratados prontos para carga no cassandra

#### 5.3 Carga
 - Utilização do DataStax Bulk Loader (DSBulk), instalado no contêiner jupyter-pyspark, para carregar os CSV tratados diretamente nas tabelas do keyspace olist_keyspace no Cassandra.

 #### 5.4 Consumo
  - Leitura das tabelas Cassandra pelo Spark, criando DataFrames PySpark que são usados nas análises de negócio.

## 6. Como executar o projeto

Esta seção descreve, passo a passo, como reproduzir o ambiente do projeto localmente, desde o download dos dados até a execução das análises em Jupyter Notebook com Spark e Cassandra.

Pré-requisito geral: sistema com Docker e Docker Compose instalados.

#### 6.1 Clonar repositorio

    git clone https://github.com/VieiraNando96/cassandra.git
    cd <seu-repo>

#### 6.2 Baixar o dataset da Olist (Kaggle)

 - Acessar o dataset no Kaggle: Brazilian E-Commerce Public Dataset by Olist
 - Fazer o download do pacote .zip com os arquivos CSV.
 - Extrair os arquivos e organizá-los na seguinte estrutura dentro do projeto:
    
        data/
            olist_customers_dataset.csv
            olist_orders_dataset.csv
            olist_order_items_dataset.csv
            olist_order_payments_dataset.csv
            olist_order_reviews_dataset.csv
            olist_products_dataset.csv
            olist_sellers_dataset.csv

Observação: os nomes dos arquivos devem ser exatamente os originais do Kaggle.

#### 6.3 Subir o ambiente Docker (Cassandra + Jupyter + Spark)

Na raiz do projeto, execute:

    docker-compose up -d

Isso irá:

  - Criar e iniciar:
    * cassandra-seed (nó seed do Cassandra)
    * cassandra-node1 (segundo nó do cluster)
    * jupyter-pyspark-app (Jupyter + Spark + DSBulk)
 - Criar os volumes de dados do Cassandra
 - Criar a rede cassandra-network

 Para verificar se os serviços estão no ar:

    docker ps

#### 6.4 Criar o keyspace e tabelas no Cassandra

O esquema do banco (keyspace olist_keyspace e todas as tabelas) é criado a partir do script estrutura_cassandra.cql.

Com o cluster já em execução, rode:

    docker exec -i cassandra-seed cqlsh < scripts/estrutura_cassandra.cql

Para validar, você pode entrar no cqlsh e listar as tabelas:

    docker exec -it cassandra-seed cqlsh

    USE olist_keyspace;
    DESCRIBE TABLES;

#### 6.5 Preparar os dados (ETL → CSV tratados)

Execute o script/notebook de preparação dos dados, que lê os CSV brutos em data e gera os arquivos tratados em data/tratado.

Execute o script Python:

    python scripts/transformacao.py

Ao final, você deve ter algo como:

    data/
        tratado/
            customers.csv
            sellers.csv
            products.csv
            orders_by_customer.csv
            items_by_order.csv
            payments_by_order.csv
            reviews_by_order.csv

#### 6.6 Carregar dados no Cassandra com DSBulk

A carga é feita a partir do contêiner jupyter-pyspark-app, utilizando o DSBulk.

Execute o script carregando_para_cassandra.sh:

    chmod +x scripts/carregando_para_cassandra.sh
    ./scripts/carregando_para_cassandra.sh

Para validar a carga:

    docker exec -it cassandra-seed cqlsh

    USE olist_keyspace;
    SELECT COUNT(*) FROM customers;
    SELECT COUNT(*) FROM orders_by_customer;
    SELECT COUNT(*) FROM items_by_order;

#### 6.7 Acessar o Jupyter Notebook

Com o contêiner jupyter-pyspark-app rodando, o Jupyter Notebook estará disponível em:

URL: http://localhost:8888

Abra o navegador e acesse esse endereço.

Execute cada celula do analise.ipynb

## 7. Análises e resultados

Esta seção apresenta um resumo dos principais resultados obtidos a partir das consultas realizadas com PySpark sobre os dados armazenados no Cassandra. As análises foram construídas para responder diretamente às perguntas de negócio definidas na seção 2.

#### 7.1 Quais categorias de produtos geram mais receita?

 - As categorias “beleza_saude” e “relogios_presentes” se destacam como as que mais geram receita, superando a marca de R$ 1,2 milhão cada no período analisado.

 - Categorias como “cama_mesa_banho”, “esporte_lazer”, “informatica_acessorios” e “moveis_decoracao” também apresentam faturamento elevado, combinando alto volume de vendas com ticket médio competitivo.

 - A categoria “cool_stuff” chama a atenção por ter um ticket médio alto (≈ R$ 167) mesmo com um volume de vendas menor que outras categorias, indicando um perfil de produtos mais caros.

 - Categorias como “utilidades_domesticas”, “automotivo” e “ferramentas_jardim” aparecem com boa participação na receita, reforçando a relevância de itens para o dia a dia, manutenção e lazer doméstico.

#### 7.2 Quais estados brasileiros concentram mais vendas e receita?

 - O estado de São Paulo (SP) se destaca com larga vantagem em relação aos demais:
    * concentra 47.449 pedidos;
    * gera mais de R$ 5,2 milhões em receita;
    * apresenta um ticket médio em torno de R$ 110. Isso reflete o peso econômico e populacional do estado, além da forte penetração do e-commerce.

 - Estados do Sudeste (SP, RJ, MG e ES) aparecem todos no top 10 e, juntos, representam uma parcela muito significativa do faturamento, confirmando a região como o principal mercado da plataforma.

 - Estados do Sul (RS, PR, SC) também apresentam desempenho expressivo, com:
    * bom volume de pedidos;
    * ticket médio em torno de R$ 120–125, ou seja, ligeiramente acima do valor observado em SP.

 - Alguns estados, como BA, DF e GO, embora com volume de pedidos menor que SP e RJ, apresentam tickets médios mais elevados (em torno de R$ 125–135), indicando um perfil de compras proporcionalmente mais valioso por pedido.

#### 7.3 Qual a relação entre preço e quantidade vendida?

 - As faixas 0–50 e 50–100 concentram o maior volume de itens vendidos (mais de 72 mil vendas somadas), com preços médios relativamente baixos. Isso indica um forte peso de produtos de tíquete baixo e giro alto.

 - A faixa 100–200 apresenta:
    * quantidade de vendas ainda bastante alta (27 mil itens);
    * a maior receita total entre todas as faixas (≈ R$ 3,87 milhões). Essa faixa equilibra bem volume e valor, sendo um ponto importante da estratégia de pricing.

 - As faixas 200–500 e 500+ possuem volume de vendas menor, mas cada item vendido gera muito mais receita.

 #### 7.4 Qual o tempo médio de entrega por região?

 - Os maiores tempos médios de entrega são observados em estados das regiões Norte e partes do Nordeste:
    * Roraima (RR): ~29,3 dias em média;
    * Amapá (AP): ~27,2 dias;
    * Amazonas (AM): ~26,4 dias;
    * Pará (PA) e Maranhão (MA) também com tempos médios acima de 21 dias.

- Já estados como ES, GO e MS possuem tempos médios de entrega menores (em torno de 15–16 dias)

- Os valores de tempo máximo de entrega (por exemplo, pedidos que levam mais de 150–190 dias) sugerem a existência de outliers

 #### 7.5 Quais são os métodos de pagamento predominantes em compras de alto valor?

  - Em todos os pedidos, o cartão de crédito já é o método dominante, mas quando filtramos apenas pedidos acima de R$ 149,70, essa predominância fica ainda mais clara:
    * uma parte muito relevante dos pedidos de alto valor é paga com cartão de crédito parcelado.

 - O boleto continua em segundo lugar, tanto em número de pedidos quanto em valor total, indicando que ainda há um perfil importante de clientes que preferem pagamento à vista via boleto, mesmo em tickets mais altos.

 - Voucher e débito são métodos marginais no contexto de alto valor, indicando que:
    * vouchers tendem a ser usados em compras de menor ticket;
    * o débito não é o método preferido para valores mais elevados.

## 8. Conclusão

Este projeto demonstrou, de ponta a ponta, como integrar Apache Cassandra e Apache Spark em uma arquitetura baseada em Docker para analisar dados reais de e-commerce em larga escala, utilizando o dataset público da Olist.

A partir de um pipeline completo de ETL, os dados foram:

 - extraídos dos arquivos CSV originais do Kaggle;
 - transformados e organizados em tabelas derivadas orientadas a queries de negócio;
 - carregados em um keyspace dedicado no Cassandra;
 - consumidos pelo Spark via conector oficial, permitindo análises distribuídas com PySpark.

Com essa infraestrutura, foi possível responder às principais perguntas de negócio propostas:

 - Identificar as categorias de produtos que mais geram receita, evidenciando a concentração do faturamento em alguns segmentos específicos.
 - Mapear os estados brasileiros com maior volume de vendas e receita, destacando a força das regiões Sudeste e Sul e apontando oportunidades em outros mercados.
 - Entender a relação entre preço e quantidade vendida, mostrando o equilíbrio entre produtos de baixo valor e alto giro, faixas intermediárias muito relevantes para o faturamento e itens de alto valor unitário.
 - Avaliar o tempo médio de entrega por região, evidenciando os desafios logísticos em estados mais afastados dos grandes centros e o impacto potencial na experiência do cliente.
 - Analisar os métodos de pagamento em compras de alto valor, confirmando o papel central do cartão de crédito parcelado na viabilização de tickets mais altos.

Além dos resultados de negócio, o projeto reforça alguns pontos técnicos importantes:

 - A modelagem orientada a queries no Cassandra é fundamental para garantir leituras eficientes em cenários analíticos.
 - O uso do Spark sobre dados armazenados em Cassandra permite combinar escalabilidade com flexibilidade de análise (joins, agregações complexas, cálculo de métricas).
 - A adoção de Docker e Docker Compose torna o ambiente reprodutível, facilitando tanto o desenvolvimento quanto a avaliação do projeto por outras pessoas.

Em síntese, o projeto alcança o objetivo de mostrar, na prática, como utilizar um stack moderno de dados para transformar um grande volume de informações de e-commerce em insights acionáveis para o negócio.