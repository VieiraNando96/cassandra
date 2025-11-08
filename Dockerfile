FROM jupyter/pyspark-notebook:latest

USER root

# Instalar DSBulk
ENV DSBULK_VERSION=1.11.0
RUN wget -q https://downloads.datastax.com/dsbulk/dsbulk-${DSBULK_VERSION}.tar.gz \
    && tar -xzf dsbulk-${DSBULK_VERSION}.tar.gz \
    && mv dsbulk-${DSBULK_VERSION} /opt/dsbulk \
    && rm dsbulk-${DSBULK_VERSION}.tar.gz

ENV DSBULK_HOME=/opt/dsbulk
ENV PATH=$PATH:$DSBULK_HOME/bin

# Baixar Spark Cassandra Connector
RUN wget -q https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.5.0/spark-cassandra-connector_2.12-3.5.0.jar \
    -P $SPARK_HOME/jars/

# Instalar dependências Python adicionais (se necessário)
COPY requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

USER $NB_UID

WORKDIR /home/jovyan/work