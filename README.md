# OrderFlow

OrderFlow — учебный микросервисный backend-проект на Python и FastAPI.

Проект демонстрирует взаимодействие нескольких независимых сервисов через синхронные HTTP-запросы и асинхронное событийное взаимодействие с использованием RabbitMQ и Apache Kafka.

## Архитектура проекта

```mermaid
flowchart TD
    Client[Клиент / Frontend]
    Nginx[Nginx]
    Gateway[API Gateway]

    Auth[Auth Service]
    Catalog[Catalog Service]
    Order[Order Service]
    Payment[Payment Service]
    Notification[Notification Service]
    Analytics[Analytics Service]

    RabbitMQ[RabbitMQ]
    Kafka[Apache Kafka]

    AuthDB[(PostgreSQL)]
    CatalogDB[(PostgreSQL)]
    OrderDB[(PostgreSQL)]
    PaymentDB[(PostgreSQL)]
    NotificationDB[(PostgreSQL)]
    MongoDB[(MongoDB)]

    Client --> Nginx
    Nginx --> Gateway

    Gateway --> Auth
    Gateway --> Catalog
    Gateway --> Order

    Auth --> AuthDB
    Catalog --> CatalogDB
    Order --> OrderDB

    Order --> Payment
    Payment --> PaymentDB

    Payment --> RabbitMQ
    RabbitMQ --> Order
    RabbitMQ --> Notification
    Notification --> NotificationDB

    Payment --> Kafka
    Kafka --> Analytics
    Analytics --> MongoDB