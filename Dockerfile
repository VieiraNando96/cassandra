FROM jupyter/base-notebook:latest

USER root

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

# Instalar Spark 3.5.0
ENV SPARK_VERSION=3.5.0
ENV HADOOP_VERSION=3
RUN wget -q https://archive.apache.org/dist/spark/spark-${SPARK_VERSION}/spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && tar -xzf spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz \
    && mv spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION} /opt/spark \
    && rm spark-${SPARK_VERSION}-bin-hadoop${HADOOP_VERSION}.tgz

ENV SPARK_HOME=/opt/spark
ENV PATH=$PATH:$SPARK_HOME/bin:$SPARK_HOME/sbin
ENV PYSPARK_PYTHON=python3
ENV PYSPARK_DRIVER_PYTHON=jupyter
ENV PYSPARK_DRIVER_PYTHON_OPTS=notebook

# Instalar DSBulk
ENV DSBULK_VERSION=1.11.0
RUN wget -q https://downloads.datastax.com/dsbulk/dsbulk-${DSBULK_VERSION}.tar.gz \
    && tar -xzf dsbulk-${DSBULK_VERSION}.tar.gz \
    && mv dsbulk-${DSBULK_VERSION} /opt/dsbulk \
    && rm dsbulk-${DSBULK_VERSION}.tar.gz

ENV DSBULK_HOME=/opt/dsbulk
ENV PATH=$PATH:$DSBULK_HOME/bin

# Baixar Spark Cassandra Connector 3.5.0
RUN wget -q https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector_2.12/3.5.0/spark-cassandra-connector_2.12-3.5.0.jar \
    -P $SPARK_HOME/jars/ \
    && wget -q https://repo1.maven.org/maven2/com/datastax/spark/spark-cassandra-connector-assembly_2.12/3.5.0/spark-cassandra-connector-assembly_2.12-3.5.0.jar \
    -P $SPARK_HOME/jars/

# Instalar dependências Python para PySpark
RUN pip install --no-cache-dir \
    pyspark==3.5.0 \
    findspark \
    cassandra-driver \
    pandas \
    numpy \
    matplotlib \
    seaborn

# Copiar requirements customizados (se existir)
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt || true

USER $NB_UID

WORKDIR /home/jovyan/work

# Configurar Jupyter para aceitar conexões externas
CMD ["start-notebook.sh", "--NotebookApp.token=''", "--NotebookApp.password=''", "--ip=0.0.0.0"]