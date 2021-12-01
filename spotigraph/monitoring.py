import sys

from spotigraph.scrapper.queues import MetricsConsumer


class Monitoring:
    def __init__(self, metric: str, interval: int = 10):
        # interval in sec
        self.interval = interval
        self.metric = metric

        self.artists_metrics = MetricsConsumer(metric, self.inc_metric)
        self.inc_count = 0

        self.initial_time = None

    def inc_metric(self, body):
        if body.decode("utf-8") == "artist saved":
            return

        cur_time = float(body.decode("utf-8"))

        if self.initial_time is None:
            self.initial_time = cur_time

        self.inc_count += 1

        if cur_time - self.initial_time > self.interval:
            print(f"Metric {self.metric} is {self.inc_count} for {cur_time - self.initial_time}")
            self.initial_time = None
            self.inc_count = 0

    def run(self):
        self.artists_metrics.start_consuming()


if __name__ == "__main__":
    metric = sys.argv[1] if len(sys.argv) > 1 else "save"
    monitor = Monitoring(metric)
    monitor.run()
