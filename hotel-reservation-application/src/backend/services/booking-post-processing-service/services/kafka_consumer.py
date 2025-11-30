import json
import os
import requests
from datetime import datetime, timedelta
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
from kafka.errors import TopicAlreadyExistsError
import logging
from .schema_validator import BookingEventValidator
import asyncpg
import asyncio

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BookingEventConsumer:
    def __init__(self):
        self.bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
        self.invoice_service_url = os.getenv('INVOICE_SERVICE_URL', 'http://invoice-service:8003')
        self.db_host = os.getenv('DB_HOST', 'postgres')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME', 'hotel_booking_db')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', 'password')
        
        logger.info(f"Environment KAFKA_BOOTSTRAP_SERVERS: {os.getenv('KAFKA_BOOTSTRAP_SERVERS')}")
        logger.info(f"Using bootstrap_servers: {self.bootstrap_servers}")
        logger.info(f"Invoice service URL: {self.invoice_service_url}")
        
        self.validator = BookingEventValidator()
        
        # Create DLQ topic if it doesn't exist
        self.create_dlq_topic()
        
        self.consumer = KafkaConsumer(
            'booking-events',
            bootstrap_servers=self.bootstrap_servers,
            group_id='booking-post-processing-group',
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            enable_auto_commit=True
        )
        
        # Producer for DLQ
        self.producer = KafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    
    def create_dlq_topic(self):
        """Create DLQ topic if it doesn't exist"""
        try:
            admin_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_servers,
                client_id='booking-post-processing-admin'
            )
            
            dlq_topic = NewTopic(
                name='booking-events-dlq',
                num_partitions=1,
                replication_factor=1
            )
            
            admin_client.create_topics([dlq_topic], validate_only=False)
            logger.info("DLQ topic 'booking-events-dlq' created successfully")
            
        except TopicAlreadyExistsError:
            logger.info("DLQ topic 'booking-events-dlq' already exists")
        except Exception as e:
            logger.error(f"Failed to create DLQ topic: {str(e)}")
        finally:
            try:
                admin_client.close()
            except:
                pass
    
    def send_to_dlq(self, message, error_reason):
        """Send failed message to Dead Letter Queue"""
        dlq_message = {
            "original_message": message,
            "error_reason": error_reason,
            "failed_at": json.dumps(datetime.now().isoformat()),
            "service": "booking-post-processing-service"
        }
        
        try:
            self.producer.send('booking-events-dlq', value=dlq_message)
            self.producer.flush()
            logger.info(f"Message sent to DLQ for booking_id: {message.get('booking_id')}")
        except Exception as e:
            logger.error(f"Failed to send message to DLQ: {str(e)}")
    
    def prepare_invoice_payload(self, message):
        """Remove Kafka-specific fields and prepare payload for invoice API"""
        # Remove fields not needed for invoice generation
        invoice_payload = message.copy()
        fields_to_remove = ['message_version', 'event_type', 'timestamp', 'source_service']
        
        for field in fields_to_remove:
            invoice_payload.pop(field, None)
            
        return invoice_payload
    
    def call_invoice_api(self, booking_data):
        """Call invoice service API"""
        try:
            invoice_payload = self.prepare_invoice_payload(booking_data)
            
            response = requests.post(
                f"{self.invoice_service_url}/invoice/generate",
                json=invoice_payload,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"Invoice generated successfully for booking_id: {booking_data.get('booking_id')}")
                return response.json()
            else:
                logger.error(f"Invoice API failed with status {response.status_code}: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error calling invoice API: {str(e)}")
            return None
    
    async def store_booking_details(self, message, invoice_data):
        """Store complete booking details with invoice information"""
        try:
            # Connect to database
            conn = await asyncpg.connect(
                host=self.db_host,
                port=self.db_port,
                database=self.db_name,
                user=self.db_user,
                password=self.db_password
            )
            
            # Get complete invoice details
            invoice_details = invoice_data["invoice_data"]
            invoice_number = invoice_details['invoice_header']['invoice_number']
            
            # Safely extract payment details
            payment_details = invoice_details.get('payment_details', {})
            payment_method = payment_details.get('payment_method')
            payment_reference = payment_details.get('payment_reference')
            
            # Convert date strings to date objects
            checkin_date = datetime.strptime(message['checkin_date'], '%Y-%m-%d').date()
            checkout_date = datetime.strptime(message['checkout_date'], '%Y-%m-%d').date()
            
            # Calculate cancellation deadline
            checkin_datetime = datetime.strptime(message['checkin_date'], '%Y-%m-%d')
            cancellation_deadline = checkin_datetime - timedelta(
                hours=message['cancellation_policy']['free_cancellation_hours']
            )
            
            # Insert complete booking details
            insert_query = """
                INSERT INTO booking_details (
                    booking_id, user_id, hotel_id, checkin_date, checkout_date,
                    total_guests, total_amount, currency, booking_status,
                    guest_name, guest_email, guest_phone, special_requests,
                    invoice_number, invoice_details, payment_status, payment_method, 
                    payment_reference, cancellation_policy_type, free_cancellation_hours,
                    cancellation_fee_percentage, cancellation_deadline, refund_policy
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23)
            """
            
            await conn.execute(
                insert_query,
                message['booking_id'],
                message['user_id'],
                message['hotel_id'],
                checkin_date,
                checkout_date,
                message['total_guests'],
                message['total_amount'],
                message['currency'],
                message['booking_status'],
                message['guest_details']['guest_name'],
                message['guest_details']['guest_email'],
                message['guest_details'].get('guest_phone'),
                message.get('special_requests'),
                invoice_number,
                json.dumps(invoice_details),
                'PAID',
                payment_method,
                payment_reference,
                message['cancellation_policy']['cancellation_policy_type'],
                message['cancellation_policy']['free_cancellation_hours'],
                message['cancellation_policy']['cancellation_fee_percentage'],
                cancellation_deadline,
                message['cancellation_policy']['refund_policy']
            )
            
            logger.info(f"Booking details inserted with invoice for booking_id: {message['booking_id']}")
            
        except Exception as e:
            logger.error(f"Failed to store booking details: {str(e)}")
            raise
        finally:
            await conn.close()
    
    async def process_booking_event(self, message):
        """Process booking event"""
        booking_id = message.get('booking_id')
        logger.info(f"Processing booking event for booking_id: {booking_id}")
        
        # Validate message against schema
        is_valid, error_message = self.validator.validate_message(message)
        if not is_valid:
            logger.error(f"Schema validation failed for booking_id {booking_id}: {error_message}")
            self.send_to_dlq(message, f"Schema validation failed: {error_message}")
            return False
        
        logger.info(f"Schema validation passed for booking_id: {booking_id}")
        
        # Call invoice API
        invoice_response = self.call_invoice_api(message)
        if not invoice_response:
            logger.error(f"Invoice generation failed for booking_id: {booking_id}")
            self.send_to_dlq(message, "Invoice generation failed")
            return False
        
        # Store complete booking details with invoice
        try:
            await self.store_booking_details(message, invoice_response)
        except Exception as e:
            logger.error(f"Failed to store booking details for booking_id: {booking_id}")
            self.send_to_dlq(message, f"Database storage failed: {str(e)}")
            return False
        
        logger.info(f"Successfully processed booking: {booking_id}")
        return True
    
    def start_consuming(self):
        """Start consuming messages from booking-events topic"""
        logger.info("Starting Kafka consumer for booking-events...")
        
        try:
            for message in self.consumer:
                try:
                    booking_data = message.value
                    logger.info(f"Received message: {booking_data.get('booking_id', 'unknown')}")
                    
                    # Process message asynchronously
                    asyncio.run(self.process_booking_event(booking_data))
                    
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                        
        except KeyboardInterrupt:
            logger.info("Shutting down consumer...")
        finally:
            self.consumer.close()











