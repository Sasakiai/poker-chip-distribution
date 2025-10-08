"""
Simple test script for Poker Chip Distribution API

Run this after starting the API with: python api.py
"""

import requests
import json
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


def print_section(title: str):
    """Print a section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_result(result: Dict[Any, Any], indent: int = 0):
    """Pretty print a result."""
    print(json.dumps(result, indent=2))


def test_health():
    """Test health check endpoint."""
    print_section("TEST 1: Health Check")

    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print_result(response.json())

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✓ Health check passed")


def test_inventory():
    """Test inventory endpoint."""
    print_section("TEST 2: Get Inventory")

    response = requests.get(f"{BASE_URL}/inventory")
    print(f"Status Code: {response.status_code}")
    print_result(response.json())

    assert response.status_code == 200
    assert "inventory" in response.json()
    print("✓ Inventory check passed")


def test_basic_distribution():
    """Test basic distribution calculation."""
    print_section("TEST 3: Basic Distribution (6 players, 100 PLN each)")

    payload = {
        "num_players": 6,
        "buy_ins": [100, 100, 100, 100, 100, 100],
        "small_blind": 1,
        "big_blind": 2,
        "include_alternatives": True,
        "max_alternatives": 3,
    }

    response = requests.post(f"{BASE_URL}/distribute", json=payload)
    print(f"Status Code: {response.status_code}")

    result = response.json()

    print(f"\nMultiplier: {result['optimal']['multiplier']}")
    print(f"Feasible: {result['optimal']['is_feasible']}")
    print(f"Stack Depth: {result['optimal']['info'].get('bb_per_player', 'N/A')} BB")
    print(f"Alternatives Found: {len(result['alternatives'])}")
    print(f"\nRecommendation: {result['recommendation']}")

    assert response.status_code == 200
    assert result["optimal"]["multiplier"] > 0
    print("\n✓ Basic distribution test passed")


def test_forced_multiplier():
    """Test forced multiplier."""
    print_section("TEST 4: Forced Multiplier (0.01)")

    payload = {
        "num_players": 6,
        "buy_ins": [100, 100, 100, 100, 100, 100],
        "small_blind": 1,
        "big_blind": 2,
        "force_multiplier": 0.01,
        "include_alternatives": False,
    }

    response = requests.post(f"{BASE_URL}/distribute", json=payload)
    print(f"Status Code: {response.status_code}")

    result = response.json()

    print(f"\nMultiplier: {result['optimal']['multiplier']}")
    print(f"Feasible: {result['optimal']['is_feasible']}")

    assert response.status_code == 200
    assert result["optimal"]["multiplier"] == 0.01
    print("\n✓ Forced multiplier test passed")


def test_variable_buyins():
    """Test variable buy-ins."""
    print_section("TEST 5: Variable Buy-ins")

    payload = {
        "num_players": 5,
        "buy_ins": [50, 100, 100, 150, 200],
        "small_blind": 1,
        "big_blind": 2,
        "include_alternatives": True,
        "max_alternatives": 3,
    }

    response = requests.post(f"{BASE_URL}/distribute", json=payload)
    print(f"Status Code: {response.status_code}")

    result = response.json()

    print(f"\nMultiplier: {result['optimal']['multiplier']}")
    print(f"Feasible: {result['optimal']['is_feasible']}")

    # Show per-player chip values
    print("\nPer-player distributions:")
    for i, dist in enumerate(result["optimal"]["distribution_per_player"], 1):
        total = sum(n * c for n, c in dist.items())
        value = total * result["optimal"]["multiplier"]
        print(f"  Player {i}: {value:.2f} PLN")

    assert response.status_code == 200
    print("\n✓ Variable buy-ins test passed")


def test_custom_distribution():
    """Test custom distribution validation."""
    print_section("TEST 6: Custom Distribution (Your Config)")

    payload = {
        "num_players": 6,
        "buy_ins": [10, 10, 10, 10, 10, 10],
        "multiplier": 0.01,
        "chips_per_player": {"1": 10, "5": 18, "25": 12, "100": 6},
        "small_blind": 0.1,
        "big_blind": 0.2,
    }

    response = requests.post(f"{BASE_URL}/custom-distribution", json=payload)
    print(f"Status Code: {response.status_code}")

    result = response.json()

    print(f"\nMultiplier: {result['multiplier']}")
    print(f"Feasible: {result['is_feasible']}")

    if "actual_value_per_player" in result["info"]:
        actual = result["info"]["actual_value_per_player"]
        expected = result["info"]["expected_value_per_player"]
        diff = result["info"]["value_difference"]

        print(f"\nValue Verification:")
        print(f"  Expected: {expected:.2f} PLN")
        print(f"  Actual:   {actual:.2f} PLN")
        print(f"  Difference: {diff:+.2f} PLN")

    assert response.status_code == 200
    assert result["is_feasible"] == True
    print("\n✓ Custom distribution test passed")


def test_no_blinds():
    """Test without blind structure."""
    print_section("TEST 7: No Blinds Specified")

    payload = {
        "num_players": 4,
        "buy_ins": [50, 100, 150, 200],
        "include_alternatives": True,
        "max_alternatives": 3,
    }

    response = requests.post(f"{BASE_URL}/distribute", json=payload)
    print(f"Status Code: {response.status_code}")

    result = response.json()

    print(f"\nMultiplier: {result['optimal']['multiplier']}")
    print(f"Feasible: {result['optimal']['is_feasible']}")
    print(f"BB per player: {result['optimal']['info'].get('bb_per_player', 'N/A')}")

    assert response.status_code == 200
    print("\n✓ No blinds test passed")


def test_error_handling():
    """Test error handling."""
    print_section("TEST 8: Error Handling")

    # Test: Mismatched buy_ins length
    print("Test 8a: Mismatched buy_ins length")
    payload = {
        "num_players": 6,
        "buy_ins": [100, 100, 100],  # Only 3 buy-ins for 6 players
        "small_blind": 1,
        "big_blind": 2,
    }

    response = requests.post(f"{BASE_URL}/distribute", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Error: {response.json().get('detail', 'N/A')}")

    assert response.status_code == 422  # Validation error
    print("✓ Correctly rejected mismatched length\n")

    # Test: Invalid big blind
    print("Test 8b: Big blind not greater than small blind")
    payload = {
        "num_players": 4,
        "buy_ins": [100, 100, 100, 100],
        "small_blind": 2,
        "big_blind": 1,  # Should be greater than small blind
    }

    response = requests.post(f"{BASE_URL}/distribute", json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Error: {response.json().get('detail', 'N/A')}")

    assert response.status_code == 422
    print("✓ Correctly rejected invalid blinds")


def test_large_game():
    """Test with many players to see alternatives in action."""
    print_section("TEST 9: Large Game (10 players)")

    payload = {
        "num_players": 10,
        "buy_ins": [200] * 10,
        "small_blind": 2,
        "big_blind": 5,
        "include_alternatives": True,
        "max_alternatives": 5,
    }

    response = requests.post(f"{BASE_URL}/distribute", json=payload)
    print(f"Status Code: {response.status_code}")

    result = response.json()

    print(f"\nOptimal Multiplier: {result['optimal']['multiplier']}")
    print(f"Optimal Feasible: {result['optimal']['is_feasible']}")

    if not result["optimal"]["is_feasible"]:
        print(f"\nOptimal has shortages, showing alternatives:")
        feasible_alts = [alt for alt in result["alternatives"] if alt["is_feasible"]]
        print(f"Feasible alternatives found: {len(feasible_alts)}")

        if feasible_alts:
            best = feasible_alts[0]
            print(f"\nBest alternative:")
            print(f"  Multiplier: {best['multiplier']}")
            print(f"  Stack depth: {best['info'].get('bb_per_player', 'N/A')} BB")

    print(f"\nRecommendation: {result['recommendation']}")

    assert response.status_code == 200
    print("\n✓ Large game test passed")


def run_all_tests():
    """Run all tests."""
    print("\n" + "🎰" * 40)
    print("  POKER CHIP DISTRIBUTION API - TEST SUITE")
    print("🎰" * 40)

    try:
        test_health()
        test_inventory()
        test_basic_distribution()
        test_forced_multiplier()
        test_variable_buyins()
        test_custom_distribution()
        test_no_blinds()
        test_error_handling()
        test_large_game()

        print_section("ALL TESTS PASSED ✓")
        print("✨ All API tests completed successfully!\n")

    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to API")
        print("Make sure the API is running with: python api.py")
        print("Then run this test script again.\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")

    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")


if __name__ == "__main__":
    run_all_tests()
