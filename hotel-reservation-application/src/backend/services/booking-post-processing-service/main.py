from services.kafka_consumer import BookingEventConsumer

def main():
    consumer = BookingEventConsumer()
    consumer.start_consuming()

if __name__ == "__main__":
    main()