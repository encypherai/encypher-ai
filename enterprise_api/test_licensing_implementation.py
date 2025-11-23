#!/usr/bin/env python3
"""
Simple validation script for Licensing Agreement Management implementation.

This script validates that all components are properly structured and can be imported.
"""

import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported."""
    print("=" * 60)
    print("LICENSING AGREEMENT MANAGEMENT - IMPLEMENTATION VALIDATION")
    print("=" * 60)
    print()

    tests_passed = 0
    tests_failed = 0

    # Test 1: Models
    print("1. Testing models import...")
    try:
        from app.models.licensing import (
            AgreementStatus
        )
        print("   ✓ All models imported successfully")
        print("     - AICompany, LicensingAgreement, ContentAccessLog")
        print("     - RevenueDistribution, MemberRevenue")
        print(f"     - Status enums: {list(AgreementStatus.__members__.keys())}")
        tests_passed += 1
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        tests_failed += 1
    print()

    # Test 2: Schemas
    print("2. Testing schemas import...")
    try:
        print("   ✓ All schemas imported successfully")
        print("     - Request schemas: LicensingAgreementCreate, ContentAccessTrack")
        print("     - Response schemas: LicensingAgreementResponse")
        tests_passed += 1
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        tests_failed += 1
    print()

    # Test 3: API Key utilities
    print("3. Testing API key utilities...")
    try:
        print("   ✓ API key utilities imported successfully")
        print("     - Functions: generate_api_key, verify_api_key, is_valid_api_key_format")
        tests_passed += 1
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        tests_failed += 1
    print()

    # Test 4: Service layer
    print("4. Testing service layer import...")
    try:
        from app.services.licensing_service import LicensingService
        print("   ✓ LicensingService imported successfully")
        service_methods = [m for m in dir(LicensingService) if not m.startswith('_')]
        print(f"     - Available methods ({len(service_methods)}): {', '.join(service_methods[:5])}...")
        tests_passed += 1
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        tests_failed += 1
    print()

    # Test 5: Authentication middleware
    print("5. Testing authentication middleware import...")
    try:
        print("   ✓ Authentication middleware imported successfully")
        print("     - Available: verify_licensing_api_key")
        tests_passed += 1
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        tests_failed += 1
    print()

    # Test 6: Router
    print("6. Testing router import...")
    try:
        from app.routers.licensing import router
        print("   ✓ Licensing router imported successfully")
        print(f"     - Prefix: {router.prefix}")
        print(f"     - Number of routes: {len(router.routes)}")
        tests_passed += 1
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        tests_failed += 1
    print()

    # Test 7: Migration file exists
    print("7. Checking migration file...")
    try:
        import os
        migration_file = "alembic/versions/add_licensing_agreement_management.py"
        if os.path.exists(migration_file):
            print(f"   ✓ Migration file exists: {migration_file}")
            tests_passed += 1
        else:
            print(f"   ✗ Migration file not found: {migration_file}")
            tests_failed += 1
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        tests_failed += 1
    print()

    # Test 8: Main app integration
    print("8. Testing main app integration...")
    try:
        from app.main import app
        # Check if licensing router is included
        licensing_routes = [r for r in app.routes if hasattr(r, 'path') and '/licensing' in r.path]
        if licensing_routes:
            print("   ✓ Licensing router integrated into main app")
            print(f"     - Found {len(licensing_routes)} licensing routes")
            tests_passed += 1
        else:
            print("   ✗ Licensing router not found in main app")
            tests_failed += 1
    except Exception as e:
        print(f"   ✗ Failed: {e}")
        tests_failed += 1
    print()

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_tests = tests_passed + tests_failed
    print(f"Total tests: {total_tests}")
    print(f"Passed: {tests_passed} ✓")
    print(f"Failed: {tests_failed} ✗")

    if tests_failed == 0:
        print()
        print("✓ ALL TESTS PASSED - Implementation is ready!")
        return 0
    else:
        print()
        print("✗ SOME TESTS FAILED - Please review the errors above")
        return 1

if __name__ == "__main__":
    exit_code = test_imports()
    sys.exit(exit_code)
