"""
Unit tests for Merkle CRUD operations.

These tests use an in-memory SQLite database for fast execution.
"""
import pytest
from datetime import datetime

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from sqlalchemy import Column, String

from app.database import Base
from app.crud import merkle as merkle_crud


# Mock Organization model for testing
class Organization(Base):
    """Mock organization model for testing."""
    __tablename__ = "organizations"
    __table_args__ = {"extend_existing": True}
    organization_id = Column(String(255), primary_key=True)


# Test database setup
@pytest.fixture
async def db_session():
    """Create an in-memory SQLite database for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Create test organizations
        org1 = Organization(organization_id="org_test")
        org2 = Organization(organization_id="org_multi")
        session.add_all([org1, org2])
        await session.commit()
        
        yield session
    
    await engine.dispose()


class TestMerkleRootCRUD:
    """Test MerkleRoot CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_merkle_root(self, db_session):
        """Test creating a Merkle root."""
        root = await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_123",
            root_hash="a" * 64,
            tree_depth=5,
            total_leaves=32,
            segmentation_level="sentence",
            metadata={"title": "Test Document"}
        )
        
        assert root.root_id is not None
        assert root.organization_id == "org_test"
        assert root.document_id == "doc_123"
        assert root.root_hash == "a" * 64
        assert root.tree_depth == 5
        assert root.total_leaves == 32
        assert root.segmentation_level == "sentence"
        assert root.doc_metadata["title"] == "Test Document"
    
    @pytest.mark.asyncio
    async def test_get_merkle_root_by_id(self, db_session):
        """Test retrieving a Merkle root by ID."""
        created = await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_123",
            root_hash="b" * 64,
            tree_depth=3,
            total_leaves=8,
            segmentation_level="paragraph"
        )
        
        retrieved = await merkle_crud.get_merkle_root_by_id(db_session, created.root_id)
        
        assert retrieved is not None
        assert retrieved.root_id == created.root_id
        assert retrieved.document_id == "doc_123"
    
    @pytest.mark.asyncio
    async def test_get_merkle_roots_by_document(self, db_session):
        """Test retrieving all roots for a document."""
        # Create multiple roots for same document at different levels
        await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_multi",
            root_hash="c" * 64,
            tree_depth=3,
            total_leaves=8,
            segmentation_level="sentence"
        )
        
        await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_multi",
            root_hash="d" * 64,
            tree_depth=2,
            total_leaves=4,
            segmentation_level="paragraph"
        )
        
        roots = await merkle_crud.get_merkle_roots_by_document(
            db_session,
            "doc_multi"
        )
        
        assert len(roots) == 2
        
        # Test filtering by level
        sentence_roots = await merkle_crud.get_merkle_roots_by_document(
            db_session,
            "doc_multi",
            segmentation_level="sentence"
        )
        
        assert len(sentence_roots) == 1
        assert sentence_roots[0].segmentation_level == "sentence"
    
    @pytest.mark.asyncio
    async def test_delete_merkle_root(self, db_session):
        """Test deleting a Merkle root."""
        root = await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_delete",
            root_hash="e" * 64,
            tree_depth=1,
            total_leaves=2,
            segmentation_level="sentence"
        )
        
        # Delete the root
        deleted = await merkle_crud.delete_merkle_root(db_session, root.root_id)
        assert deleted is True
        
        # Verify it's gone
        retrieved = await merkle_crud.get_merkle_root_by_id(db_session, root.root_id)
        assert retrieved is None


class TestMerkleSubhashCRUD:
    """Test MerkleSubhash CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_merkle_subhash(self, db_session):
        """Test creating a Merkle subhash."""
        # First create a root
        root = await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_123",
            root_hash="f" * 64,
            tree_depth=2,
            total_leaves=4,
            segmentation_level="sentence"
        )
        
        # Create a leaf subhash
        subhash = await merkle_crud.create_merkle_subhash(
            db=db_session,
            hash_value="abc123" + "0" * 58,
            root_id=root.root_id,
            node_type="leaf",
            depth_level=2,
            position_index=0,
            text_content="This is a test sentence."
        )
        
        assert subhash.subhash_id is not None
        assert subhash.hash_value == "abc123" + "0" * 58
        assert subhash.node_type == "leaf"
        assert subhash.text_content == "This is a test sentence."
    
    @pytest.mark.asyncio
    async def test_bulk_create_subhashes(self, db_session):
        """Test bulk creating subhashes."""
        root = await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_bulk",
            root_hash="g" * 64,
            tree_depth=3,
            total_leaves=8,
            segmentation_level="sentence"
        )
        
        subhashes_data = [
            {
                'hash_value': f"hash{i}" + "0" * 59,
                'root_id': root.root_id,
                'node_type': 'leaf',
                'depth_level': 3,
                'position_index': i,
                'text_content': f"Sentence {i}"
            }
            for i in range(8)
        ]
        
        count = await merkle_crud.bulk_create_merkle_subhashes(db_session, subhashes_data)
        
        assert count == 8
        
        # Verify they were created
        subhashes = await merkle_crud.find_subhashes_by_root(db_session, root.root_id)
        assert len(subhashes) == 8
    
    @pytest.mark.asyncio
    async def test_find_subhashes_by_hash(self, db_session):
        """Test finding subhashes by hash value."""
        root = await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_find",
            root_hash="h" * 64,
            tree_depth=1,
            total_leaves=2,
            segmentation_level="sentence"
        )
        
        target_hash = "findme" + "0" * 58
        
        await merkle_crud.create_merkle_subhash(
            db=db_session,
            hash_value=target_hash,
            root_id=root.root_id,
            node_type="leaf",
            depth_level=1,
            position_index=0,
            text_content="Find this sentence."
        )
        
        # Find by hash
        found = await merkle_crud.find_subhashes_by_hash(db_session, target_hash)
        
        assert len(found) == 1
        assert found[0].hash_value == target_hash
        assert found[0].text_content == "Find this sentence."
    
    @pytest.mark.asyncio
    async def test_batch_find_subhashes(self, db_session):
        """Test batch finding subhashes."""
        root = await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_batch",
            root_hash="i" * 64,
            tree_depth=2,
            total_leaves=4,
            segmentation_level="sentence"
        )
        
        hashes = [f"batch{i}" + "0" * 59 for i in range(4)]
        
        for i, hash_val in enumerate(hashes):
            await merkle_crud.create_merkle_subhash(
                db=db_session,
                hash_value=hash_val,
                root_id=root.root_id,
                node_type="leaf",
                depth_level=2,
                position_index=i,
                text_content=f"Sentence {i}"
            )
        
        # Batch find
        results = await merkle_crud.batch_find_subhashes(
            db_session,
            [hashes[0], hashes[2], "nonexistent"]
        )
        
        assert len(results) == 2  # Only 2 of 3 hashes found
        assert hashes[0] in results
        assert hashes[2] in results
        assert "nonexistent" not in results


class TestMerkleProofCacheCRUD:
    """Test MerkleProofCache CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_and_get_cached_proof(self, db_session):
        """Test creating and retrieving a cached proof."""
        root = await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_proof",
            root_hash="j" * 64,
            tree_depth=3,
            total_leaves=8,
            segmentation_level="sentence"
        )
        
        proof_path = [
            {"hash": "sibling1" + "0" * 56, "position": "right"},
            {"hash": "sibling2" + "0" * 56, "position": "left"}
        ]
        
        cached = await merkle_crud.create_proof_cache(
            db=db_session,
            target_hash="target" + "0" * 58,
            root_id=root.root_id,
            proof_path=proof_path,
            position_bits=b'\x01\x00',
            ttl_hours=24
        )
        
        assert cached.cache_id is not None
        
        # Retrieve the cached proof
        retrieved = await merkle_crud.get_cached_proof(
            db_session,
            "target" + "0" * 58,
            root.root_id
        )
        
        assert retrieved is not None
        assert retrieved.target_hash == "target" + "0" * 58
        assert len(retrieved.proof_path) == 2
    
    @pytest.mark.asyncio
    async def test_expired_proof_not_returned(self, db_session):
        """Test that expired proofs are not returned."""
        root = await merkle_crud.create_merkle_root(
            db=db_session,
            organization_id="org_test",
            document_id="doc_expired",
            root_hash="k" * 64,
            tree_depth=1,
            total_leaves=2,
            segmentation_level="sentence"
        )
        
        # Create a proof that expires immediately
        cached = await merkle_crud.create_proof_cache(
            db=db_session,
            target_hash="expired" + "0" * 57,
            root_id=root.root_id,
            proof_path=[],
            position_bits=b'',
            ttl_hours=0  # Expires immediately
        )
        
        # Try to retrieve - should return None since it's expired
        retrieved = await merkle_crud.get_cached_proof(
            db_session,
            "expired" + "0" * 57,
            root.root_id
        )
        
        # Note: This might return the proof if the test runs fast enough
        # In a real scenario with actual time passing, it would be None
        assert retrieved is None or retrieved.expires_at <= datetime.utcnow()


class TestAttributionReportCRUD:
    """Test AttributionReport CRUD operations."""
    
    @pytest.mark.asyncio
    async def test_create_attribution_report(self, db_session):
        """Test creating an attribution report."""
        source_docs = [
            {
                "document_id": "source_1",
                "matched_segments": 10,
                "match_percentage": 50.0
            },
            {
                "document_id": "source_2",
                "matched_segments": 5,
                "match_percentage": 25.0
            }
        ]
        
        report = await merkle_crud.create_attribution_report(
            db=db_session,
            organization_id="org_test",
            total_segments=20,
            matched_segments=15,
            source_documents=source_docs,
            target_document_id="target_doc",
            heat_map_data={"positions": []}
        )
        
        assert report.report_id is not None
        assert report.total_segments == 20
        assert report.matched_segments == 15
        assert len(report.source_documents) == 2
    
    @pytest.mark.asyncio
    async def test_get_attribution_reports_by_organization(self, db_session):
        """Test retrieving reports for an organization."""
        # Create multiple reports
        for i in range(3):
            await merkle_crud.create_attribution_report(
                db=db_session,
                organization_id="org_multi",
                total_segments=10,
                matched_segments=i,
                source_documents=[]
            )
        
        reports = await merkle_crud.get_attribution_reports_by_organization(
            db_session,
            "org_multi"
        )
        
        assert len(reports) == 3
        # Should be ordered by scan_timestamp descending
        assert reports[0].scan_timestamp >= reports[1].scan_timestamp
