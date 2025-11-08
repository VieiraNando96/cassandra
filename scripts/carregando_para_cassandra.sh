#!/bin/bash

echo "========================================================================"
echo "📤 CARREGANDO DADOS NO CASSANDRA COM DSBULK"
echo "========================================================================"
echo ""

KEYSPACE="olist_keyspace"
DSBULK_CONTAINER="cassandra-python-app"
CASSANDRA_HOST="cassandra-seed"
DATA_DIR="/app/data/tratado"  

# Função para carregar dados
load_table() {
    local table=$1
    local file=$2
    
    echo "Carregando: $table..."
    
    docker exec -it "$DSBULK_CONTAINER" dsbulk load \
        -url "$DATA_DIR/$file" \
        -k "$KEYSPACE" \
        -t "$table" \
        -h "$CASSANDRA_HOST" \
        -header true \
        -delim ',' \
        -maxErrors 100 \
        -logDir "/tmp/dsbulk_logs/$table"
    
    if [ $? -eq 0 ]; then
        echo "✅ $table carregado com sucesso!"
    else
        echo "❌ Erro ao carregar $table"
    fi
    echo ""
}

# Criar diretório de logs
docker exec -it "$DSBULK_CONTAINER" mkdir -p "/tmp/dsbulk_logs"

echo "🚀 Iniciando carga das tabelas..."
echo ""

# Carregar cada tabela
load_table "customers" "customers.csv"
load_table "sellers" "sellers.csv"
load_table "products" "products.csv"
load_table "orders_by_customer" "orders_by_customer.csv"
load_table "items_by_order" "items_by_order.csv"
load_table "payments_by_order" "payments_by_order.csv"
load_table "reviews_by_order" "reviews_by_order.csv"

echo "========================================================================"
echo "✅ CARGA CONCLUÍDA!"
echo "========================================================================"