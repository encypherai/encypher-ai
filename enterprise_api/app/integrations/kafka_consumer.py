"""
Kafka Consumer Integration for Streaming API.

Provides Kafka consumer functionality for consuming unsigned content and signing it.
"""
import logging
import json
import asyncio
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timezone
from kafka import KafkaConsumer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class EncypherKafkaConsumer:
    """
    Kafka consumer for consuming and signing content.
    
    Features:
    - Configurable consumer groups
    - JSON deserialization
    - Callback support for signed content
    - Offset management
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Kafka consumer.
        
        Args:
            config: Kafka configuration dictionary
                - bootstrap_servers: List of Kafka brokers
                - topics: List of topics to subscribe to
                - group_id: Consumer group ID
                - auto_commit: Auto-commit offsets (default: True)
                - security_protocol: Security protocol (optional)
                - sasl_mechanism: SASL mechanism (optional)
                - sasl_username: SASL username (optional)
                - sasl_password: SASL password (optional)
        """
        self.config = config
        self.bootstrap_servers = config.get("bootstrap_servers", ["localhost:9092"])
        self.topics = config.get("topics", [])
        self.group_id = config.get("group_id", "encypher-signing-service")
        self.callback_topic = config.get("callback_topic")
        self.running = False
        
        # Build consumer config
        consumer_config = {
            "bootstrap_servers": self.bootstrap_servers,
            "group_id": self.group_id,
            "value_deserializer": lambda m: json.loads(m.decode('utf-8')),
            "key_deserializer": lambda k: k.decode('utf-8') if k else None,
            "auto_offset_reset": "earliest",
            "enable_auto_commit": config.get("auto_commit", True),
            "max_poll_records": 100,
        }
        
        # Add security config if provided
        if config.get("security_protocol"):
            consumer_config["security_protocol"] = config["security_protocol"]
        if config.get("sasl_mechanism"):
            consumer_config["sasl_mechanism"] = config["sasl_mechanism"]
        if config.get("sasl_username"):
            consumer_config["sasl_plain_username"] = config["sasl_username"]
        if config.get("sasl_password"):
            consumer_config["sasl_plain_password"] = config["sasl_password"]
        
        try:
            self.consumer = KafkaConsumer(**consumer_config)
            if self.topics:
                self.consumer.subscribe(self.topics)
            logger.info(
                f"Kafka consumer initialized: group={self.group_id}, "
                f"topics={self.topics}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}", exc_info=True)
            raise
    
    def subscribe(self, topics: List[str]):
        """
        Subscribe to topics.
        
        Args:
            topics: List of topic names
        """
        try:
            self.topics = topics
            self.consumer.subscribe(topics)
            logger.info(f"Subscribed to topics: {topics}")
        except Exception as e:
            logger.error(f"Failed to subscribe to topics: {e}", exc_info=True)
            raise
    
    def is_subscribed(self) -> bool:
        """Check if consumer is subscribed to topics."""
        return len(self.consumer.subscription()) > 0
    
    def subscription(self) -> set:
        """Get current subscription."""
        return self.consumer.subscription()
    
    async def consume(
        self,
        timeout: Optional[float] = None,
        max_messages: Optional[int] = None
    ):
        """
        Consume messages from Kafka.
        
        Args:
            timeout: Timeout in seconds
            max_messages: Maximum number of messages to consume
            
        Yields:
            Kafka messages
        """
        count = 0
        timeout_ms = int(timeout * 1000) if timeout else 1000
        
        try:
            for message in self.consumer:
                yield message
                count += 1
                
                if max_messages and count >= max_messages:
                    break
                
                # Allow other async tasks to run
                await asyncio.sleep(0)
        
        except KafkaError as e:
            logger.error(f"Kafka consume error: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error consuming from Kafka: {e}", exc_info=True)
            raise
    
    async def start_consuming(
        self,
        message_handler: Callable[[Any], Any],
        error_handler: Optional[Callable[[Exception], None]] = None
    ):
        """
        Start consuming messages with a handler.
        
        Args:
            message_handler: Async function to handle each message
            error_handler: Optional async function to handle errors
        """
        self.running = True
        logger.info(f"Starting Kafka consumer loop for topics: {self.topics}")
        
        try:
            while self.running:
                try:
                    # Poll for messages
                    messages = self.consumer.poll(timeout_ms=1000)
                    
                    for topic_partition, records in messages.items():
                        for record in records:
                            try:
                                # Process message
                                await message_handler(record)
                            except Exception as e:
                                logger.error(
                                    f"Error processing message: {e}",
                                    exc_info=True
                                )
                                if error_handler:
                                    await error_handler(e)
                    
                    # Allow other async tasks to run
                    await asyncio.sleep(0.01)
                
                except Exception as e:
                    logger.error(f"Error in consumer loop: {e}", exc_info=True)
                    if error_handler:
                        await error_handler(e)
                    await asyncio.sleep(1)  # Back off on error
        
        finally:
            logger.info("Kafka consumer loop stopped")
    
    def stop_consuming(self):
        """Stop the consumer loop."""
        self.running = False
        logger.info("Stopping Kafka consumer")
    
    async def commit_offset(self, message: Any):
        """
        Manually commit offset for a message.
        
        Args:
            message: Kafka message
        """
        try:
            self.consumer.commit()
            logger.debug(f"Committed offset for message at offset {message.offset}")
        except Exception as e:
            logger.error(f"Error committing offset: {e}")
    
    async def committed_offsets(self) -> Dict:
        """
        Get committed offsets.
        
        Returns:
            Dictionary of committed offsets
        """
        try:
            partitions = self.consumer.assignment()
            offsets = {}
            
            for partition in partitions:
                offset = self.consumer.committed(partition)
                offsets[str(partition)] = offset
            
            return offsets
        except Exception as e:
            logger.error(f"Error getting committed offsets: {e}")
            return {}
    
    def close(self):
        """Close the Kafka consumer."""
        try:
            self.running = False
            self.consumer.close()
            logger.info("Kafka consumer closed")
        except Exception as e:
            logger.error(f"Error closing Kafka consumer: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get consumer metrics.
        
        Returns:
            Dictionary of metrics
        """
        try:
            metrics = self.consumer.metrics()
            return {
                "bootstrap_servers": self.bootstrap_servers,
                "group_id": self.group_id,
                "topics": list(self.topics),
                "subscription": list(self.subscription()),
                "metrics": metrics
            }
        except Exception as e:
            logger.error(f"Error getting Kafka metrics: {e}")
            return {}


# Global consumer registry (per organization)
_consumer_registry: Dict[str, EncypherKafkaConsumer] = {}


def get_consumer(organization_id: str) -> Optional[EncypherKafkaConsumer]:
    """
    Get Kafka consumer for organization.
    
    Args:
        organization_id: Organization ID
        
    Returns:
        Kafka consumer or None if not configured
    """
    return _consumer_registry.get(organization_id)


def register_consumer(organization_id: str, consumer: EncypherKafkaConsumer):
    """
    Register Kafka consumer for organization.
    
    Args:
        organization_id: Organization ID
        consumer: Kafka consumer instance
    """
    _consumer_registry[organization_id] = consumer
    logger.info(f"Registered Kafka consumer for org {organization_id}")


def unregister_consumer(organization_id: str):
    """
    Unregister and close Kafka consumer for organization.
    
    Args:
        organization_id: Organization ID
    """
    if organization_id in _consumer_registry:
        consumer = _consumer_registry.pop(organization_id)
        consumer.close()
        logger.info(f"Unregistered Kafka consumer for org {organization_id}")
