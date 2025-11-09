# Análise de dados com Cassandra e Spark

## 1. Base de dados

### Contexto

Este projeto utiliza o Olist Brazilian E-Commerce Public Dataset, um dataset público disponibilizado pela Olist Store no Kaggle. O dataset contém informações reais e anonimizadas de aproximadamente 100 mil pedidos realizados entre 2016 e 2018 em diversos marketplaces brasileiros conectados à plataforma Olist.

A Olist é uma plataforma que conecta pequenos e médios varejistas a grandes marketplaces brasileiros, permitindo que vendedores anunciem seus produtos em múltiplos canais através de um único contrato. Este dataset oferece uma visão abrangente do ecossistema de e-commerce brasileiro, incluindo dados de pedidos, produtos, clientes, vendedores, pagamentos e avaliações.

### Fonte de dados

Nome: Brazilian E-Commerce Public Dataset by Olist
Plataforma: Kaggle
Licença: CC BY-NC-SA 4.0 (Creative Commons)
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

#### 2.1 **Quais categorias de produto geram maior receita total?**

**Métricas:**
- Receita total por categoria
- Quantidade de pedidos por categoria
- Ticket médio por categoria

**Análise esperada:**
- Ranking das top 10 categorias por faturamento
- Comparação entre volume de vendas e receita
- Identificação de categorias de alto valor agregado

**Visualizações:**
- Gráfico de barras: Receita por categoria
- Gráfico de pizza: Participação percentual no faturamento total
- Tabela: Top 10 categorias com métricas detalhadas

#### 2.2 **Quais estados brasileiros concentram mais vendas e faturamento?**

**Objetivo:** Mapear a distribuição geográfica das vendas para otimizar logística e campanhas regionais.

**Métricas:**
- Número de pedidos por estado
- Receita total por estado
- Ticket médio por estado
- Concentração de clientes por região

**Análise esperada:**
- Ranking dos estados por volume de vendas
- Identificação de mercados saturados vs. oportunidades de expansão
- Análise da relação entre população e volume de vendas

**Visualizações:**
- Mapa de calor: Distribuição de vendas por estado
- Gráfico de barras horizontais: Top 10 estados por faturamento
- Tabela comparativa: Vendas vs. população por estado

Qual é a relação entre preço e quantidade vendida (dispersão)?

Qual é o tempo médio de entrega por região?

Quais formas de pagamento predominam nas compras mais caras?