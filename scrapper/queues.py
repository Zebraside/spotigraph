import pika

from config import MQ


class QueueBase:
    durable = True

    def __init__(self, queue_name, consume_handler=None):
        self.queue_name = queue_name

        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.push_channel = connection.channel()
        self.push_channel.queue_declare(queue=self.queue_name, durable=self.durable)

        self.consume_channel = None
        if consume_handler:
            self.consume_channel = connection.channel()
            self.consume_channel.basic_qos(prefetch_count=100)
            self.consume_channel.basic_consume(queue=self.queue_name,
                                               on_message_callback=consume_handler,
                                               auto_ack=True)

        # connection.close()

    def start_consuming(self):
        if not self.consume_channel:
            raise Exception("consume channel is not initilized")

        self.consume_channel.start_consuming()

    def push(self, msg: str):
        self.push_channel.basic_publish(
            exchange='',
            routing_key=self.queue_name,
            body=str.encode(msg),
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
            ))


class ScrapperQueue(QueueBase):
    def __init__(self, handler=None):
        super(ScrapperQueue, self).__init__(MQ.SCRAPPER_QUEUE_NAME, handler)


class ArtistQueue(QueueBase):
    def __init__(self, handler=None):
        super(ArtistQueue, self).__init__(MQ.ARTISTS_QUEUE_NAME, handler)
