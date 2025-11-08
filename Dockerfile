FROM python:3.11-bullseye

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    openjdk-11-jdk \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Configurar JAVA_HOME
ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$PATH:$JAVA_HOME/bin

# Instalar Spark
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark \
    && rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV PYSPARK_PYTHON=python3

# Instalar DSBulk
ENV DSBULK_VERSION=1.11.0
RUN wget -q https://downloads.datastax.com/dsbulk/dsbulk-${DSBULK_VERSION}.tar.gz \
    && tar -xzf dsbulk-${DSBULK_VERSION}.tar.gz \
    && mv dsbulk-${DSBULK_VERSION} /opt/dsbulk \
    && rm dsbulk-${DSBULK_VERSION}.tar.gz

ENV DSBULK_HOME=/opt/dsbulk
ENV PATH=$PATH:$DSBULK_HOME/bin

# Copiar requirements e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Baixar Spark Cassandra Connector
RUN wget -q https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.5.0/spark-cassandra-connector_2.12-3.5.0.jar \
    -P $SPARK_HOME/jars/

COPY . .

CMD ["bash"]