import pandas as pd
import os
import uuid
from datetime import datetime

data_dir = './data'
trans_dir = './data/tratado'

#criando diretorio de saida
os.makedirs(trans_dir, exist_ok=True)

#Dicionario para mapear somente os arquivos que possui IDs a serem transformados em uuid
uuid_maps = {
    'customer': {},
    'order': {},
    'product': {},
    'seller': {},
    'review': {}
}

def get_or_create_uuid(original_id, map_type):
    #Converte ID original para UUID (mantém consistência)
    if pd.isna(original_id) or original_id == '':
        return str(uuid.uuid4())
    
    if original_id not in uuid_maps[map_type]:
        # Gerar UUID determinístico baseado no ID original
        # Isso garante que o mesmo ID sempre gere o mesmo UUID
        namespace = uuid.NAMESPACE_DNS
        uuid_maps[map_type][original_id] = str(uuid.uuid5(namespace, str(original_id)))
    
    return uuid_maps[map_type][original_id]

#Iniciando o processamento dos arquivos: 

# 1 - CUSTOMERS
print("Processando: customers...")

df_customers = pd.read_csv(f'{data_dir}/olist_customers_dataset.csv')

#removendo duplicatas
df_customers = df_customers.drop_duplicates(subset=['customer_id'])

# Converter IDs para UUID
df_customers['customer_id_uuid'] = df_customers['customer_id'].apply(
    lambda x: get_or_create_uuid(x, 'customer')
)

df_customers['customer_unique_id_uuid'] = df_customers['customer_unique_id'].apply(
    lambda x: get_or_create_uuid(x, 'customer')
)

# Tratar valores nulos
df_customers['customer_zip_code_prefix'] = df_customers['customer_zip_code_prefix'].fillna(0).astype(int)
df_customers['customer_city'] = df_customers['customer_city'].fillna('Unknown')
df_customers['customer_state'] = df_customers['customer_state'].fillna('Unknown')

# Preparar para Cassandra
df_customers_prepared = df_customers[[
    'customer_id_uuid',
    'customer_unique_id_uuid',
    'customer_zip_code_prefix',
    'customer_city',
    'customer_state'
]].rename(columns={
    'customer_id_uuid': 'customer_id',
    'customer_unique_id_uuid': 'customer_unique_id'
})

# Salvar
output_file = f'{trans_dir}/customers.csv'
df_customers_prepared.to_csv(output_file, index=False)
print(f"{len(df_customers_prepared)} registros → {output_file}")

# Guardar mapeamento original para usar em outras tabelas
customer_id_map = dict(zip(df_customers['customer_id'], df_customers['customer_id_uuid']))

# 2 - SELLERS
print("\nProcessando: sellers...")

df_sellers = pd.read_csv(f'{data_dir}/olist_sellers_dataset.csv')

# Remover duplicatas
df_sellers = df_sellers.drop_duplicates(subset=['seller_id'])

# Converter IDs para UUID
df_sellers['seller_id_uuid'] = df_sellers['seller_id'].apply(
    lambda x: get_or_create_uuid(x, 'seller')
)

# Tratar valores nulos
df_sellers['seller_zip_code_prefix'] = df_sellers['seller_zip_code_prefix'].fillna(0).astype(int)
df_sellers['seller_city'] = df_sellers['seller_city'].fillna('Unknown')
df_sellers['seller_state'] = df_sellers['seller_state'].fillna('Unknown')

# Preparar para Cassandra
df_sellers_prepared = df_sellers[[
    'seller_id_uuid',
    'seller_zip_code_prefix',
    'seller_city',
    'seller_state'
]].rename(columns={
    'seller_id_uuid': 'seller_id'
})

# Salvar
output_file = f'{trans_dir}/sellers.csv'
df_sellers_prepared.to_csv(output_file, index=False)
print(f"{len(df_sellers_prepared)} registros → {output_file}")

# Guardar mapeamento
seller_id_map = dict(zip(df_sellers['seller_id'], df_sellers['seller_id_uuid']))

# 3 - PRODUCTS

print("\nProcessando: products...")

df_products = pd.read_csv(f'{data_dir}/olist_products_dataset.csv')

# Remover duplicatas
df_products = df_products.drop_duplicates(subset=['product_id'])

# Converter IDs para UUID
df_products['product_id_uuid'] = df_products['product_id'].apply(
    lambda x: get_or_create_uuid(x, 'product')
)

# Tratar valores nulos
df_products['product_category_name'] = df_products['product_category_name'].fillna('unknown')
df_products['product_name_lenght'] = df_products['product_name_lenght'].fillna(0).astype(int)
df_products['product_description_lenght'] = df_products['product_description_lenght'].fillna(0).astype(int)
df_products['product_photos_qty'] = df_products['product_photos_qty'].fillna(0).astype(int)
df_products['product_weight_g'] = df_products['product_weight_g'].fillna(0)
df_products['product_length_cm'] = df_products['product_length_cm'].fillna(0)
df_products['product_height_cm'] = df_products['product_height_cm'].fillna(0)
df_products['product_width_cm'] = df_products['product_width_cm'].fillna(0)

# Preparar para Cassandra
df_products_prepared = df_products[[
    'product_id_uuid',
    'product_category_name',
    'product_name_lenght',
    'product_description_lenght',
    'product_photos_qty',
    'product_weight_g',
    'product_length_cm',
    'product_height_cm',
    'product_width_cm'
]].rename(columns={
    'product_id_uuid': 'product_id'
})

# Salvar
output_file = f'{trans_dir}/products.csv'
df_products_prepared.to_csv(output_file, index=False)
print(f"{len(df_products_prepared)} registros → {output_file}")

# Guardar mapeamento
product_id_map = dict(zip(df_products['product_id'], df_products['product_id_uuid']))

# 4 - ORDERS

print("\nProcessando: orders...")

df_orders = pd.read_csv(f'{data_dir}/olist_orders_dataset.csv')

# Remover duplicatas
df_orders = df_orders.drop_duplicates(subset=['order_id'])

# Converter IDs para UUID
df_orders['order_id_uuid'] = df_orders['order_id'].apply(
    lambda x: get_or_create_uuid(x, 'order')
)
df_orders['customer_id_uuid'] = df_orders['customer_id'].map(customer_id_map)

# Remover orders sem customer válido
df_orders = df_orders.dropna(subset=['customer_id_uuid'])

# Converter datas para formato ISO (Cassandra aceita)
date_columns = [
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]

for col in date_columns:
    df_orders[col] = pd.to_datetime(df_orders[col], errors='coerce')
    # Formato ISO: YYYY-MM-DD HH:MM:SS (sem timezone para simplificar)
    df_orders[col] = df_orders[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    # Substituir NaT por string vazia (DSBULK vai ignorar)
    df_orders[col] = df_orders[col].fillna('')

# Tratar valores nulos
df_orders['order_status'] = df_orders['order_status'].fillna('unknown')

# Preparar para Cassandra
df_orders_prepared = df_orders[[
    'customer_id_uuid',
    'order_id_uuid',
    'order_status',
    'order_purchase_timestamp',
    'order_approved_at',
    'order_delivered_carrier_date',
    'order_delivered_customer_date',
    'order_estimated_delivery_date'
]].rename(columns={
    'customer_id_uuid': 'customer_id',
    'order_id_uuid': 'order_id'
})

# Salvar
output_file = f'{trans_dir}/orders_by_customer.csv'
df_orders_prepared.to_csv(output_file, index=False)
print(f"{len(df_orders_prepared)} registros → {output_file}")

# Guardar mapeamento
order_id_map = dict(zip(df_orders['order_id'], df_orders['order_id_uuid']))

#5 - ORDER ITEMS

print("\nProcessando: order_items...")

df_items = pd.read_csv(f'{data_dir}/olist_order_items_dataset.csv')

# Converter IDs para UUID
df_items['order_id_uuid'] = df_items['order_id'].map(order_id_map)
df_items['product_id_uuid'] = df_items['product_id'].map(product_id_map)
df_items['seller_id_uuid'] = df_items['seller_id'].map(seller_id_map)

# Remover items sem IDs válidos
df_items = df_items.dropna(subset=['order_id_uuid', 'product_id_uuid', 'seller_id_uuid'])

# Converter data
df_items['shipping_limit_date'] = pd.to_datetime(df_items['shipping_limit_date'], errors='coerce')
df_items['shipping_limit_date'] = df_items['shipping_limit_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
df_items['shipping_limit_date'] = df_items['shipping_limit_date'].fillna('')

# Tratar valores nulos
df_items['price'] = df_items['price'].fillna(0)
df_items['freight_value'] = df_items['freight_value'].fillna(0)

# Preparar para Cassandra
df_items_prepared = df_items[[
    'order_id_uuid',
    'order_item_id',
    'product_id_uuid',
    'seller_id_uuid',
    'price',
    'freight_value',
    'shipping_limit_date'
]].rename(columns={
    'order_id_uuid': 'order_id',
    'product_id_uuid': 'product_id',
    'seller_id_uuid': 'seller_id'
})

# Salvar
output_file = f'{trans_dir}/items_by_order.csv'
df_items_prepared.to_csv(output_file, index=False)
print(f"{len(df_items_prepared)} registros → {output_file}")

#6 - PAYMENTS

print("\nProcessando: payments...")

df_payments = pd.read_csv(f'{data_dir}/olist_order_payments_dataset.csv')

# Converter IDs para UUID
df_payments['order_id_uuid'] = df_payments['order_id'].map(order_id_map)

# Remover payments sem order válido
df_payments = df_payments.dropna(subset=['order_id_uuid'])

# Tratar valores nulos
df_payments['payment_type'] = df_payments['payment_type'].fillna('unknown')
df_payments['payment_installments'] = df_payments['payment_installments'].fillna(1).astype(int)
df_payments['payment_value'] = df_payments['payment_value'].fillna(0)

# Preparar para Cassandra
df_payments_prepared = df_payments[[
    'order_id_uuid',
    'payment_sequential',
    'payment_type',
    'payment_installments',
    'payment_value'
]].rename(columns={
    'order_id_uuid': 'order_id'
})

# Salvar
output_file = f'{trans_dir}/payments_by_order.csv'
df_payments_prepared.to_csv(output_file, index=False)
print(f"{len(df_payments_prepared)} registros → {output_file}")

# 7. REVIEWS

print("\nProcessando: reviews...")

df_reviews = pd.read_csv(f'{data_dir}/olist_order_reviews_dataset.csv')

# Converter IDs para UUID
df_reviews['review_id_uuid'] = df_reviews['review_id'].apply(
    lambda x: get_or_create_uuid(x, 'review')
)
df_reviews['order_id_uuid'] = df_reviews['order_id'].map(order_id_map)

# Remover reviews sem order válido
df_reviews = df_reviews.dropna(subset=['order_id_uuid'])

# Converter datas
df_reviews['review_creation_date'] = pd.to_datetime(df_reviews['review_creation_date'], errors='coerce')
df_reviews['review_creation_date'] = df_reviews['review_creation_date'].dt.strftime('%Y-%m-%d %H:%M:%S')
df_reviews['review_creation_date'] = df_reviews['review_creation_date'].fillna('')

df_reviews['review_answer_timestamp'] = pd.to_datetime(df_reviews['review_answer_timestamp'], errors='coerce')
df_reviews['review_answer_timestamp'] = df_reviews['review_answer_timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')
df_reviews['review_answer_timestamp'] = df_reviews['review_answer_timestamp'].fillna('')

# Tratar valores nulos
df_reviews['review_score'] = df_reviews['review_score'].fillna(0).astype(int)
df_reviews['review_comment_title'] = df_reviews['review_comment_title'].fillna('')
df_reviews['review_comment_message'] = df_reviews['review_comment_message'].fillna('')

# Limpar caracteres especiais que podem dar problema no DSBULK
df_reviews['review_comment_title'] = df_reviews['review_comment_title'].str.replace('"', "'", regex=False)
df_reviews['review_comment_message'] = df_reviews['review_comment_message'].str.replace('"', "'", regex=False)
df_reviews['review_comment_title'] = df_reviews['review_comment_title'].str.replace('\n', ' ', regex=False)
df_reviews['review_comment_message'] = df_reviews['review_comment_message'].str.replace('\n', ' ', regex=False)

# Preparar para Cassandra
df_reviews_prepared = df_reviews[[
    'review_id_uuid',
    'order_id_uuid',
    'review_score',
    'review_comment_title',
    'review_comment_message',
    'review_creation_date',
    'review_answer_timestamp'
]].rename(columns={
    'review_id_uuid': 'review_id',
    'order_id_uuid': 'order_id'
})

# Salvar
output_file = f'{trans_dir}/reviews_by_order.csv'
df_reviews_prepared.to_csv(output_file, index=False)
print(f"{len(df_reviews_prepared)} registros → {output_file}")