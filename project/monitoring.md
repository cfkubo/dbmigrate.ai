# Monitoring Setup

This document outlines the monitoring setup for the project, utilizing Prometheus for metrics collection and Grafana for visualization.

## Components

*   **Prometheus**: An open-source monitoring system with a dimensional data model, flexible query language (PromQL), efficient time series database, and a modern alerting solution.
*   **Grafana**: An open-source platform for monitoring and observability. It allows you to query, visualize, alert on, and explore your metrics, logs, and traces no matter where they are stored.
*   **RabbitMQ**: The message broker used in the project, which exposes metrics that Prometheus collects.

## Prometheus Configuration

Prometheus is configured via the `prometheus.yml` file located in the project root. This file defines:
*   **Scrape configurations**: Specifies targets for Prometheus to scrape metrics from.
    *   **RabbitMQ**: The `gini.sh` script enables the `rabbitmq_prometheus` plugin, allowing Prometheus to scrape metrics from RabbitMQ.
    *   **Other services**: Additional services can be added to `prometheus.yml` for metric collection.

The `gini.sh` script mounts this `prometheus.yml` file into the Prometheus Docker container:
```bash
-v $(pwd)/prometheus.yml:/etc/prometheus/prometheus.yml
```

## Grafana Setup

Grafana is used for visualizing the metrics collected by Prometheus. It is provisioned with data sources and dashboards automatically when started via `gini.sh`.

### Grafana Access

*   **URL**: `http://localhost:3000`
*   **Admin User**: `admin`
*   **Admin Password**: `password`

### Data Source Provisioning

Grafana is configured to automatically add Prometheus as a data source using the `grafana/provisioning/datasources/prometheus.yml` file. This file defines the connection details for Prometheus:

```yaml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090
    access: proxy
    isDefault: true
    editable: true
```

The `gini.sh` script mounts this provisioning file into the Grafana Docker container:
```bash
-v $(pwd)/grafana/provisioning/datasources:/etc/grafana/provisioning/datasources
```

### Dashboard Provisioning

Grafana dashboards are also provisioned automatically. The `grafana/provisioning/dashboards/rabbitmq.yml` file instructs Grafana to load dashboards from a specific directory:

```yaml
apiVersion: 1

providers:
  - name: 'RabbitMQ'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards/rabbitmq
```

The actual RabbitMQ dashboard JSON file (`rabbitmq-overview.json`) is located in `grafana/dashboards/` and is mounted into the Grafana container at `/var/lib/grafana/dashboards/rabbitmq`:

```bash
-v $(pwd)/grafana/dashboards:/var/lib/grafana/dashboards
```

You can replace the content of `grafana/dashboards/rabbitmq-overview.json` with a more comprehensive RabbitMQ dashboard JSON, for example, by downloading one from Grafana Labs (e.g., ID 10990).

## RabbitMQ Metrics

The `gini.sh` script enables the `rabbitmq_prometheus` plugin on the RabbitMQ container:

```bash
docker exec some-rabbit rabbitmq-plugins enable rabbitmq_prometheus
```

This plugin exposes RabbitMQ metrics at `http://some-rabbit:15692/metrics`, which Prometheus then scrapes.

## How to Use

1.  Ensure Docker is running.
2.  Run `./gini.sh start` to start all services, including Prometheus and Grafana.
3.  Access Grafana at `http://localhost:3000` with `admin`/`password`.
4.  The Prometheus data source and RabbitMQ dashboard should be pre-configured.
