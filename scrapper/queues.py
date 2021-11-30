import pika

from config import MQ


class ConsumerBase:
    def __init__(self, exchange, queue_name, handler):
        self.exchange = exchange
        self.queue_name = queue_name
        self.durable = True

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=exchange)
        self.channel.queue_declare(queue=self.queue_name, durable=self.durable)
        self.channel.queue_bind(self.queue_name, self.exchange)

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=self.queue_name,
                                   on_message_callback=handler,
                                   auto_ack=True)

    def start_consuming(self):
        self.channel.start_consuming()


class ScraperConsumer(ConsumerBase):
    def __init__(self, handler):
        super(ScraperConsumer, self).__init__("scrap", MQ.SCRAPPER_QUEUE_NAME, handler)


class ArtistConsumer(ConsumerBase):
    def __init__(self, handler):
        super(ArtistConsumer, self).__init__("artist", MQ.ARTISTS_QUEUE_NAME, handler)


class PublisherBase:
    def __init__(self, exchange, queue_name):
        self.exchange = exchange
        self.queue_name = queue_name
        self.durable = True

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = connection.channel()
        self.channel.exchange_declare(exchange=exchange)
        self.channel.queue_declare(queue=self.queue_name, durable=self.durable)
        self.channel.queue_bind(self.queue_name, self.exchange)

    def push(self, msg: str):
        print("Push", self.exchange, self.queue_name)
        self.channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.queue_name,
            body=str.encode(msg),
            properties=pika.BasicProperties(
                delivery_mode=2,
            ))


class ScraperPublisher(PublisherBase):
    def __init__(self):
        super(ScraperPublisher, self).__init__("scrap", MQ.SCRAPPER_QUEUE_NAME)


class ArtistPublisher(PublisherBase):
    def __init__(self):
        super(ArtistPublisher, self).__init__("artist", MQ.ARTISTS_QUEUE_NAME)
