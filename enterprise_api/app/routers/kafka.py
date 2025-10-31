"""
Kafka Integration Router.

Provides endpoints for configuring Kafka producers and consumers.
"""
import logging
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_organization
from app.models.organization import Organization
from app.integrations.kafka_producer import (
    EncypherKafkaProducer,
    get_producer,
    register_producer,
    unregister_producer
)
from app.integrations.kafka_consumer import (
    EncypherKafkaConsumer,
    get_consumer,
    register_consumer,
    unregister_consumer
)

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models

class KafkaProducerConfig(BaseModel):
    """Kafka producer configuration."""
    bootstrap_servers: List[str]
    topic: str
    security_protocol: Optional[str] = None
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None


class KafkaConsumerConfig(BaseModel):
    """Kafka consumer configuration."""
    bootstrap_servers: List[str]
    topics: List[str]
    group_id: str
    callback_topic: Optional[str] = None
    auto_commit: bool = True
    security_protocol: Optional[str] = None
    sasl_mechanism: Optional[str] = None
    sasl_username: Optional[str] = None
    sasl_password: Optional[str] = None


class KafkaMessage(BaseModel):
    """Kafka message to send."""
    value: Dict[str, Any]
    key: Optional[str] = None
    topic: Optional[str] = None


# Producer Endpoints

@router.post("/kafka/producer/configure")
async def configure_kafka_producer(
    config: KafkaProducerConfig,
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Configure Kafka producer for organization.
    
    Args:
        config: Kafka producer configuration
        organization: Authenticated organization
        db: Database session
        
    Returns:
        Configuration result
    """
    try:
        # Check if producer already exists
        existing_producer = get_producer(organization.organization_id)
        if existing_producer:
            # Close existing producer
            unregister_producer(organization.organization_id)
        
        # Create new producer
        producer = EncypherKafkaProducer(config.dict())
        register_producer(organization.organization_id, producer)
        
        logger.info(f"Kafka producer configured for org {organization.organization_id}")
        
        return {
            "success": True,
            "message": "Kafka producer configured successfully",
            "organization_id": organization.organization_id,
            "bootstrap_servers": config.bootstrap_servers,
            "topic": config.topic
        }
    
    except Exception as e:
        logger.error(f"Failed to configure Kafka producer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/kafka/producer/send")
async def send_kafka_message(
    message: KafkaMessage,
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message to Kafka.
    
    Args:
        message: Message to send
        organization: Authenticated organization
        db: Database session
        
    Returns:
        Send result
    """
    try:
        # Get producer
        producer = get_producer(organization.organization_id)
        if not producer:
            raise HTTPException(
                status_code=400,
                detail="Kafka producer not configured. Please configure first."
            )
        
        # Send message
        record_metadata = await producer.send(
            value=message.value,
            key=message.key,
            topic=message.topic
        )
        
        return {
            "success": True,
            "message": "Message sent to Kafka",
            "topic": record_metadata.topic,
            "partition": record_metadata.partition,
            "offset": record_metadata.offset
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to send Kafka message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/kafka/producer")
async def delete_kafka_producer(
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete Kafka producer configuration.
    
    Args:
        organization: Authenticated organization
        db: Database session
        
    Returns:
        Deletion result
    """
    try:
        producer = get_producer(organization.organization_id)
        if not producer:
            raise HTTPException(status_code=404, detail="Kafka producer not found")
        
        unregister_producer(organization.organization_id)
        
        return {
            "success": True,
            "message": "Kafka producer deleted successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete Kafka producer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Consumer Endpoints

@router.post("/kafka/consumer/subscribe")
async def subscribe_kafka_consumer(
    config: KafkaConsumerConfig,
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Subscribe to Kafka topics for consuming and signing content.
    
    Args:
        config: Kafka consumer configuration
        organization: Authenticated organization
        db: Database session
        
    Returns:
        Subscription result
    """
    try:
        # Check if consumer already exists
        existing_consumer = get_consumer(organization.organization_id)
        if existing_consumer:
            # Close existing consumer
            unregister_consumer(organization.organization_id)
        
        # Create new consumer
        consumer = EncypherKafkaConsumer(config.dict())
        register_consumer(organization.organization_id, consumer)
        
        # TODO: Start background task to consume and sign messages
        # This would require a background worker or async task
        
        logger.info(
            f"Kafka consumer subscribed for org {organization.organization_id}: "
            f"topics={config.topics}"
        )
        
        return {
            "success": True,
            "message": "Kafka consumer subscribed successfully",
            "organization_id": organization.organization_id,
            "topics": config.topics,
            "group_id": config.group_id,
            "callback_topic": config.callback_topic
        }
    
    except Exception as e:
        logger.error(f"Failed to subscribe Kafka consumer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/kafka/consumer")
async def unsubscribe_kafka_consumer(
    organization: Organization = Depends(get_current_organization),
    db: AsyncSession = Depends(get_db)
):
    """
    Unsubscribe Kafka consumer.
    
    Args:
        organization: Authenticated organization
        db: Database session
        
    Returns:
        Unsubscription result
    """
    try:
        consumer = get_consumer(organization.organization_id)
        if not consumer:
            raise HTTPException(status_code=404, detail="Kafka consumer not found")
        
        unregister_consumer(organization.organization_id)
        
        return {
            "success": True,
            "message": "Kafka consumer unsubscribed successfully"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unsubscribe Kafka consumer: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Status Endpoints

@router.get("/kafka/producer/status")
async def get_producer_status(
    organization: Organization = Depends(get_current_organization)
):
    """
    Get Kafka producer status.
    
    Args:
        organization: Authenticated organization
        
    Returns:
        Producer status
    """
    producer = get_producer(organization.organization_id)
    
    if not producer:
        return {
            "configured": False,
            "message": "Kafka producer not configured"
        }
    
    metrics = producer.get_metrics()
    
    return {
        "configured": True,
        "bootstrap_servers": producer.bootstrap_servers,
        "topic": producer.topic,
        "metrics": metrics
    }


@router.get("/kafka/consumer/status")
async def get_consumer_status(
    organization: Organization = Depends(get_current_organization)
):
    """
    Get Kafka consumer status.
    
    Args:
        organization: Authenticated organization
        
    Returns:
        Consumer status
    """
    consumer = get_consumer(organization.organization_id)
    
    if not consumer:
        return {
            "configured": False,
            "message": "Kafka consumer not configured"
        }
    
    metrics = consumer.get_metrics()
    
    return {
        "configured": True,
        "subscribed": consumer.is_subscribed(),
        "topics": list(consumer.subscription()),
        "group_id": consumer.group_id,
        "running": consumer.running,
        "metrics": metrics
    }


@router.get("/kafka/health")
async def kafka_health_check(
    organization: Organization = Depends(get_current_organization)
):
    """
    Health check for Kafka integration.
    
    Args:
        organization: Authenticated organization
        
    Returns:
        Health status
    """
    health_status = {
        "status": "healthy",
        "components": {}
    }
    
    # Check producer
    producer = get_producer(organization.organization_id)
    if producer:
        health_status["components"]["producer"] = {
            "status": "configured",
            "topic": producer.topic
        }
    else:
        health_status["components"]["producer"] = {
            "status": "not_configured"
        }
    
    # Check consumer
    consumer = get_consumer(organization.organization_id)
    if consumer:
        health_status["components"]["consumer"] = {
            "status": "configured" if consumer.is_subscribed() else "not_subscribed",
            "topics": list(consumer.subscription()),
            "running": consumer.running
        }
    else:
        health_status["components"]["consumer"] = {
            "status": "not_configured"
        }
    
    return health_status
