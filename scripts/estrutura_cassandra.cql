--Criação do Keyspace

CREATE KEYSPACE IF NOT EXISTS olist_keyspace
WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 2};

-- ESTRUTURA DAS TABELAS

-- orders_by_customer (Contém informações principais de pedidos por cliente)

CREATE TABLE IF NOT EXISTS olist_keyspace.orders_by_customer (
    customer_id UUID,
    order_id UUID,
    order_status TEXT,
    order_purchase_timestamp TIMESTAMP,
    order_approved_at TIMESTAMP,
    order_delivered_carrier_date TIMESTAMP,
    order_delivered_customer_date TIMESTAMP,
    order_estimated_delivery_date TIMESTAMP,
    PRIMARY KEY (customer_id, order_id)
);

--   items_by_order (Relaciona cada pedido aos produtos comprado)
 
 CREATE TABLE IF NOT EXISTS olist_keyspace.items_by_order (
    order_id UUID,
    order_item_id INT,
    product_id UUID,
    seller_id UUID,
    price FLOAT,
    freight_value FLOAT,
    shipping_limit_date TIMESTAMP,
    PRIMARY KEY (order_id, order_item_id)
);

-- payments_by_order (Pagamentos relacionados a cada pedido)

CREATE TABLE IF NOT EXISTS olist_keyspace.payments_by_order (
    order_id UUID,
    payment_sequential INT,
    payment_type TEXT,
    payment_installments INT,
    payment_value FLOAT,
    PRIMARY KEY (order_id, payment_sequential)
);

-- products (Dados de cada produto)

CREATE TABLE IF NOT EXISTS olist_keyspace.products (
    product_id UUID,
    product_category_name TEXT,
    product_name_length INT,
    product_description_length INT,
    product_photos_qty INT,
    product_weight_g FLOAT,
    product_length_cm FLOAT,
    product_height_cm FLOAT,
    product_width_cm FLOAT,
    PRIMARY KEY (product_id)
);

-- customers (Localização e identificação do cliente)

CREATE TABLE IF NOT EXISTS olist_keyspace.customers (
    customer_id UUID,
    customer_unique_id UUID,
    customer_zip_code_prefix INT,
    customer_city TEXT,
    customer_state TEXT,
    PRIMARY KEY (customer_id)
);

-- sellers(Informações geográficas dos vendedores)

CREATE TABLE IF NOT EXISTS olist_keyspace.sellers (
    seller_id UUID,
    seller_zip_code_prefix INT,
    seller_city TEXT,
    seller_state TEXT,
    PRIMARY KEY (seller_id)
);

-- reviews_by_order (Avaliações dos clientes sobre os pedidos)

CREATE TABLE IF NOT EXISTS olist_keyspace.reviews_by_order (
    review_id UUID,
    order_id UUID,
    review_score INT,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TIMESTAMP,
    review_answer_timestamp TIMESTAMP,
    PRIMARY KEY (order_id, review_id)
);

