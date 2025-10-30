"""
Kafka Producer Integration for Streaming API.

Provides Kafka producer functionality for publishing signed content.
"""
import logging
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from kafka import KafkaProducer
from kafka.errors import KafkaError

logger = logging.getLogger(__name__)


class EncypherKafkaProducer:
    """
    Kafka producer for publishing signed content.
    
    Features:
    - Configurable bootstrap servers
    - JSON serialization
    - Error handling and retries
    - Partition key support
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Kafka producer.
        
        Args:
            config: Kafka configuration dictionary
                - bootstrap_servers: List of Kafka brokers
                - security_protocol: Security protocol (optional)
                - sasl_mechanism: SASL mechanism (optional)
                - sasl_username: SASL username (optional)
                - sasl_password: SASL password (optional)
        """
        self.config = config
        self.bootstrap_servers = config.get("bootstrap_servers", ["localhost:9092"])
        self.topic = config.get("topic", "encypher.signed.content")
        
        # Build producer config
        producer_config = {
            "bootstrap_servers": self.bootstrap_servers,
            "value_serializer": lambda v: json.dumps(v).encode('utf-8'),
            "key_serializer": lambda k: k.encode('utf-8') if k else None,
            "acks": "all",  # Wait for all replicas
            "retries": 3,
            "max_in_flight_requests_per_connection": 1,  # Ensure ordering
        }
        
        # Add security config if provided
        if config.get("security_protocol"):
            producer_config["security_protocol"] = config["security_protocol"]
        if config.get("sasl_mechanism"):
            producer_config["sasl_mechanism"] = config["sasl_mechanism"]
        if config.get("sasl_username"):
            producer_config["sasl_plain_username"] = config["sasl_username"]
        if config.get("sasl_password"):
            producer_config["sasl_plain_password"] = config["sasl_password"]
        
        try:
            self.producer = KafkaProducer(**producer_config)
            logger.info(f"Kafka producer initialized: {self.bootstrap_servers}")
        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}", exc_info=True)
            raise
    
    async def send(
        self,
        value: Dict[str, Any],
        key: Optional[str] = None,
        topic: Optional[str] = None
    ) -> Any:
        """
        Send a message to Kafka.
        
        Args:
            value: Message value (will be JSON serialized)
            key: Optional partition key
            topic: Optional topic (defaults to configured topic)
            
        Returns:
            RecordMetadata from Kafka
            
        Raises:
            KafkaError: If send fails
        """
        target_topic = topic or self.topic
        
        try:
            # Add timestamp
            if "timestamp" not in value:
                value["timestamp"] = datetime.now(timezone.utc).isoformat()
            
            # Send message
            future = self.producer.send(
                target_topic,
                value=value,
                key=key
            )
            
            # Wait for result
            record_metadata = future.get(timeout=10)
            
            logger.info(
                f"Message sent to Kafka: topic={target_topic}, "
                f"partition={record_metadata.partition}, "
                f"offset={record_metadata.offset}"
            )
            
            return record_metadata
        
        except KafkaError as e:
            logger.error(f"Kafka send error: {e}", exc_info=True)
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending to Kafka: {e}", exc_info=True)
            raise
    
    async def send_batch(
        self,
        messages: List[Dict[str, Any]],
        topic: Optional[str] = None
    ) -> List[Any]:
        """
        Send multiple messages to Kafka.
        
        Args:
            messages: List of message dictionaries
            topic: Optional topic (defaults to configured topic)
            
        Returns:
            List of RecordMetadata from Kafka
        """
        results = []
        
        for message in messages:
            try:
                result = await self.send(message, topic=topic)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to send message in batch: {e}")
                results.append(None)
        
        return results
    
    def flush(self, timeout: Optional[float] = None):
        """
        Flush pending messages.
        
        Args:
            timeout: Optional timeout in seconds
        """
        try:
            self.producer.flush(timeout=timeout)
            logger.debug("Kafka producer flushed")
        except Exception as e:
            logger.error(f"Error flushing Kafka producer: {e}")
    
    def close(self):
        """Close the Kafka producer."""
        try:
            self.producer.close()
            logger.info("Kafka producer closed")
        except Exception as e:
            logger.error(f"Error closing Kafka producer: {e}")
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get producer metrics.
        
        Returns:
            Dictionary of metrics
        """
        try:
            metrics = self.producer.metrics()
            return {
                "bootstrap_servers": self.bootstrap_servers,
                "topic": self.topic,
                "metrics": metrics
            }
        except Exception as e:
            logger.error(f"Error getting Kafka metrics: {e}")
            return {}


# Global producer registry (per organization)
_producer_registry: Dict[str, EncypherKafkaProducer] = {}


def get_producer(organization_id: str) -> Optional[EncypherKafkaProducer]:
    """
    Get Kafka producer for organization.
    
    Args:
        organization_id: Organization ID
        
    Returns:
        Kafka producer or None if not configured
    """
    return _producer_registry.get(organization_id)


def register_producer(organization_id: str, producer: EncypherKafkaProducer):
    """
    Register Kafka producer for organization.
    
    Args:
        organization_id: Organization ID
        producer: Kafka producer instance
    """
    _producer_registry[organization_id] = producer
    logger.info(f"Registered Kafka producer for org {organization_id}")


def unregister_producer(organization_id: str):
    """
    Unregister and close Kafka producer for organization.
    
    Args:
        organization_id: Organization ID
    """
    if organization_id in _producer_registry:
        producer = _producer_registry.pop(organization_id)
        producer.close()
        logger.info(f"Unregistered Kafka producer for org {organization_id}")
