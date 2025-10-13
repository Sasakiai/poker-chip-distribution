"""
Poker Chip Distribution Algorithm

This module provides an intelligent algorithm for distributing poker chips based on:
- Number of players
- Individual buy-in amounts
- Optional small blind and big blind values

The algorithm finds the optimal chip value multiplier to ensure:
1. Easy mental math for players (chip values are round numbers)
2. Appropriate stack depths (100-200 big blinds when blinds are specified)
3. Balanced chip distributions (more large chips, fewer small chips)
4. Validation against available chip inventory

Example:
    >>> result = distribution_algorithm(
    ...     num_players=6,
    ...     buy_ins=[100, 100, 100, 100, 100, 100],
    ...     small_blind=1,
    ...     big_blind=2
    ... )
    >>> print(f"Multiplier: {result['multiplier']}")
    Multiplier: 0.02
"""

from typing import Optional, Any
import math

# Available chip inventory: {nominal: count}
# Modify this dictionary to match your actual chip set
chips = {1: 150, 5: 150, 25: 100, 100: 50, 500: 25, 1000: 25}


def calc_chips_value():
    """Calculate the total monetary value of all available chips."""
    value = 0
    for nominate, val in chips.items():
        value += val * nominate
    return value


def find_optimal_multiplier(
    total_buy_in: float,
    num_players: int,
    big_blind: Optional[float] = None,
    target_bb_stack: int = 150,
) -> tuple[float, dict[str, Any]]:
    """
    Find the optimal chip value multiplier.

    Args:
        total_buy_in: Total money in the game (sum of all buy-ins)
        num_players: Number of players
        big_blind: Big blind value in real money (optional)
        target_bb_stack: Target starting stack in big blinds (default 150)

    Returns:
        Tuple of (multiplier, info_dict)
    """
    possible_multipliers = [
        0.01,
        0.02,
        0.05,
        0.1,
        0.2,
        0.5,
        1,
        2,
        5,
        10,
        20,
        50,
        100,
        200,
        500,
        1000,
    ]

    # Available chip nominals
    available_nominals = sorted(chips.keys())
    min_nominal = available_nominals[0]

    if big_blind:
        # If big blind is provided, find multiplier that makes BB a round number in chips
        # AND ensures the smallest chip nominal is useful
        preferred_bb_in_chips = [5, 10, 20, 25, 50, 100, 200, 500]

        best_multiplier = None
        best_score = float("inf")

        for multiplier in possible_multipliers:
            bb_in_chips = big_blind / multiplier

            # Check if smallest chip is reasonable for blinds (should be <= SB/2)
            smallest_chip_value = min_nominal * multiplier
            if smallest_chip_value > big_blind / 4:
                continue  # Skip - smallest chip is too large

            # Check if this gives us a reasonable BB in chips
            for preferred_bb in preferred_bb_in_chips:
                if abs(bb_in_chips - preferred_bb) < 0.01:
                    # Calculate how many BB each player gets
                    avg_buy_in = total_buy_in / num_players
                    chips_per_player = avg_buy_in / multiplier
                    bb_per_player = chips_per_player / bb_in_chips

                    # Score based on how close we are to target BB stack
                    # Prefer multipliers where smallest chip is 1-5% of BB
                    chip_to_bb_ratio = (min_nominal * multiplier) / big_blind
                    ratio_penalty = 0 if 0.01 <= chip_to_bb_ratio <= 0.05 else 100

                    score = abs(bb_per_player - target_bb_stack) + ratio_penalty

                    if score < best_score:
                        best_score = score
                        best_multiplier = multiplier

        if best_multiplier:
            bb_in_chips = big_blind / best_multiplier
            avg_buy_in = total_buy_in / num_players
            chips_per_player = avg_buy_in / best_multiplier

            return best_multiplier, {
                "bb_in_chips": bb_in_chips,
                "sb_in_chips": bb_in_chips / 2,
                "chips_per_player": chips_per_player,
                "bb_per_player": chips_per_player / bb_in_chips,
            }

    # If no big blind or couldn't find good match, optimize for chip count
    avg_buy_in = total_buy_in / num_players

    # Target: smallest chip should be about 0.5-2% of average buy-in
    # This keeps chip counts reasonable
    target_smallest_value = avg_buy_in * 0.01
    target_multiplier = target_smallest_value / min_nominal

    # Find closest standard multiplier
    closest_multiplier = min(
        possible_multipliers, key=lambda x: abs(x - target_multiplier)
    )

    chips_per_player = avg_buy_in / closest_multiplier

    return closest_multiplier, {
        "bb_in_chips": None,
        "sb_in_chips": None,
        "chips_per_player": chips_per_player,
        "bb_per_player": None,
    }


def calculate_chip_distribution(
    chips_needed: float,
    available_nominals: list[int],
    small_blind_chips: Optional[float] = None,
    available_inventory: Optional[dict[int, int]] = None,
    num_players: int = 1,
) -> dict[int, int]:
    """
    Calculate optimal chip distribution for a single player's stack.

    Strategy: Prioritize lower denominations first (greedy from smallest to largest).
    Only move to higher denominations when lower ones are exhausted or unavailable.

    Args:
        chips_needed: Total chip count needed for this player
        available_nominals: List of available chip nominals (sorted)
        small_blind_chips: Small blind value in chips (for better distribution)
        available_inventory: Available chip inventory to work within constraints
        num_players: Number of players (to check inventory limits)

    Returns:
        Dictionary mapping nominal to count
    """
    distribution = {}
    remaining = chips_needed
    # Work from SMALLEST to LARGEST to prioritize lower denominations
    sorted_nominals = sorted(available_nominals)

    # Define reasonable caps per denomination to avoid giving too many tiny chips
    # while still prioritizing lower values
    def get_max_chips_for_nominal(
        nominal: int, position: int, total_nominals: int
    ) -> int:
        """Get maximum reasonable chips for this denomination."""
        if total_nominals == 1:
            return 100  # If only one denomination, allow many

        if position == 0:  # Smallest denomination
            return 30
        elif position == 1:  # Second smallest
            return 25
        elif position == 2:  # Third smallest
            return 20
        elif position == total_nominals - 1:  # Largest denomination
            return 15
        else:  # Middle denominations
            return 18

    # Greedy approach: start with smallest denomination and work up
    for i, nominal in enumerate(sorted_nominals):
        if remaining < nominal:
            continue

        # Check inventory limits if provided
        max_available_per_player = float("inf")
        if available_inventory:
            total_available = available_inventory.get(nominal, 0)
            max_available_per_player = total_available // num_players

        # Calculate how many of this denomination we can use
        max_reasonable = get_max_chips_for_nominal(i, i, len(sorted_nominals))
        max_from_remaining = int(remaining / nominal)

        count = min(max_reasonable, max_from_remaining, int(max_available_per_player))

        if count > 0:
            distribution[nominal] = count
            remaining -= count * nominal

    # If there's still remaining value after first pass, make a second pass
    # to top off with any denomination that can help
    if remaining > 0:
        for nominal in sorted_nominals:
            if remaining < nominal:
                continue

            # Check how much more we can add of this denomination
            max_available_per_player = float("inf")
            if available_inventory:
                total_available = available_inventory.get(nominal, 0)
                already_used = distribution.get(nominal, 0) * num_players
                max_available_per_player = (
                    total_available - already_used
                ) // num_players

            # Allow a few more chips in second pass (up to 10 additional)
            current_count = distribution.get(nominal, 0)
            additional = min(
                10, int(remaining / nominal), int(max_available_per_player)
            )

            if additional > 0:
                distribution[nominal] = current_count + additional
                remaining -= additional * nominal

                if remaining < nominal:
                    break

    # Final pass: if still remaining, round up with smallest denomination
    if remaining > 0 and len(sorted_nominals) > 0:
        smallest = sorted_nominals[0]
        max_available_per_player = float("inf")
        if available_inventory:
            total_available = available_inventory.get(smallest, 0)
            already_used = distribution.get(smallest, 0) * num_players
            max_available_per_player = (total_available - already_used) // num_players

        additional = min(
            int(math.ceil(remaining / smallest)), int(max_available_per_player)
        )

        if additional > 0:
            distribution[smallest] = distribution.get(smallest, 0) + additional

    return distribution


def custom_distribution(
    num_players: int,
    buy_ins: list[float],
    multiplier: float,
    chips_per_player: dict[int, int],
    small_blind: Optional[float] = None,
    big_blind: Optional[float] = None,
) -> dict:
    """
    Create a distribution using a custom chip configuration per player.

    This function allows you to specify exactly which chips each player should get,
    then validates if it matches the buy-in and if you have enough chips.

    Args:
        num_players: Number of players
        buy_ins: List of buy-in amounts (all should be equal for this function)
        multiplier: The chip value multiplier
        chips_per_player: Dict specifying chip count per nominal (e.g., {1: 10, 5: 18, 25: 12, 100: 6})
        small_blind: Small blind value in real money (optional)
        big_blind: Big blind value in real money (optional)

    Returns:
        Distribution result dict similar to distribution_algorithm
    """
    # Calculate what this distribution is worth
    total_chips_value = sum(
        nominal * count for nominal, count in chips_per_player.items()
    )
    actual_value_per_player = total_chips_value * multiplier
    expected_value = buy_ins[0] if buy_ins else 0

    # Create distributions for all players (same for each)
    distributions = [chips_per_player.copy() for _ in range(num_players)]

    # Calculate total chips needed
    total_chips_used = {}
    for nominal, count in chips_per_player.items():
        total_chips_used[nominal] = count * num_players

    # Validate availability
    is_feasible, shortage = validate_chip_availability(
        chips_per_player, num_players, chips
    )

    # Calculate blind info if provided
    if big_blind:
        bb_in_chips = big_blind / multiplier
        sb_in_chips = bb_in_chips / 2 if small_blind else bb_in_chips / 2
        bb_per_player = total_chips_value / bb_in_chips
        multiplier_info = {
            "bb_in_chips": bb_in_chips,
            "sb_in_chips": sb_in_chips,
            "chips_per_player": total_chips_value,
            "bb_per_player": bb_per_player,
        }
    else:
        multiplier_info = {
            "bb_in_chips": None,
            "sb_in_chips": None,
            "chips_per_player": total_chips_value,
            "bb_per_player": None,
        }

    available_nominals = sorted(chips.keys())

    return {
        "multiplier": multiplier,
        "chip_value_info": f"1 chip = {multiplier} PLN (e.g., chip nominal {available_nominals[0]} = {available_nominals[0] * multiplier} PLN)",
        "distribution_per_player": distributions,
        "total_chips_used": total_chips_used,
        "is_feasible": is_feasible,
        "shortage": shortage if not is_feasible else None,
        "info": {
            **multiplier_info,
            "total_buy_in": sum(buy_ins),
            "num_players": num_players,
            "small_blind_chips": multiplier_info.get("sb_in_chips"),
            "big_blind_chips": multiplier_info.get("bb_in_chips"),
            "actual_value_per_player": actual_value_per_player,
            "expected_value_per_player": expected_value,
            "value_difference": actual_value_per_player - expected_value,
        },
    }


def validate_chip_availability(
    distribution_per_player: dict[int, int],
    num_players: int,
    available_chips: dict[int, int],
) -> tuple[bool, dict[int, int]]:
    """
    Check if we have enough chips in inventory for all players.

    Returns:
        Tuple of (is_valid, shortage_dict)
    """
    shortage = {}
    is_valid = True

    for nominal, count_per_player in distribution_per_player.items():
        total_needed = count_per_player * num_players
        available = available_chips.get(nominal, 0)

        if total_needed > available:
            shortage[nominal] = total_needed - available
            is_valid = False

    return is_valid, shortage


def distribution_algorithm(
    num_players: int,
    buy_ins: list[float],
    small_blind: Optional[float] = None,
    big_blind: Optional[float] = None,
    force_multiplier: Optional[float] = None,
) -> dict:
    """
    Main chip distribution algorithm - finds optimal chip distribution for poker game.

    This function calculates the best way to distribute poker chips to players based
    on their buy-in amounts and the game's blind structure. It automatically determines
    an optimal chip value multiplier that makes mental math easy while ensuring
    appropriate stack depths and balanced chip distributions.

    Args:
        num_players: Number of players in the game
        buy_ins: List of buy-in amounts for each player (in PLN or your currency)
                 Length must equal num_players
        small_blind: Small blind value in real money (optional, auto-generated if not provided)
        big_blind: Big blind value in real money (optional, auto-generated if not provided)
        force_multiplier: Force a specific multiplier instead of calculating optimal (optional)

    Returns:
        Dictionary containing:
        - multiplier (float): The chip value multiplier (chip nominal × multiplier = real money)
        - chip_value_info (str): Human-readable explanation of chip values
        - distribution_per_player (List[Dict[int, int]]): List of chip distributions,
                                   one dict per player mapping nominal to count
        - total_chips_used (Dict[int, int]): Total chips needed from inventory by nominal
        - is_feasible (bool): Whether we have enough chips in inventory
        - shortage (Dict[int, int] or None): Chip shortages by nominal if not feasible
        - info (Dict): Additional information including blind structure and stack depths

    Raises:
        ValueError: If length of buy_ins doesn't match num_players

    Example:
        >>> result = distribution_algorithm(
        ...     num_players=4,
        ...     buy_ins=[100, 100, 150, 200],
        ...     small_blind=1,
        ...     big_blind=2
        ... )
        >>> print(result['multiplier'])
        0.02
        >>> print(result['is_feasible'])
        True
    """
    if len(buy_ins) != num_players:
        raise ValueError(
            f"Number of buy-ins ({len(buy_ins)}) must match number of players ({num_players})"
        )

    total_buy_in = sum(buy_ins)

    # Auto-generate blinds if not provided (standard poker blind structure)
    # Target: starting stacks of 100-150 big blinds
    if big_blind is None and small_blind is None:
        avg_buy_in = total_buy_in / num_players
        # Set big blind to get ~125 BB starting stacks
        big_blind = avg_buy_in / 125
        small_blind = big_blind / 2
    elif big_blind is None and small_blind is not None:
        # If only small blind provided, derive big blind (standard 1:2 ratio)
        big_blind = small_blind * 2
    elif small_blind is None and big_blind is not None:
        # If only big blind provided, derive small blind
        small_blind = big_blind / 2

    # Use forced multiplier or find optimal
    if force_multiplier:
        multiplier = force_multiplier
        avg_buy_in = total_buy_in / num_players
        chips_per_player = avg_buy_in / multiplier

        if big_blind:
            bb_in_chips = big_blind / multiplier
            sb_in_chips = bb_in_chips / 2
            bb_per_player = chips_per_player / bb_in_chips
            multiplier_info = {
                "bb_in_chips": bb_in_chips,
                "sb_in_chips": sb_in_chips,
                "chips_per_player": chips_per_player,
                "bb_per_player": bb_per_player,
            }
        else:
            multiplier_info = {
                "bb_in_chips": None,
                "sb_in_chips": None,
                "chips_per_player": chips_per_player,
                "bb_per_player": None,
            }
    else:
        # Find optimal multiplier
        multiplier, multiplier_info = find_optimal_multiplier(
            total_buy_in, num_players, big_blind
        )

    # Calculate distribution for each player
    available_nominals = sorted(chips.keys())
    distributions = []

    for buy_in in buy_ins:
        chips_needed = buy_in / multiplier
        sb_chips = multiplier_info.get("sb_in_chips")
        distribution = calculate_chip_distribution(
            chips_needed, available_nominals, sb_chips, chips, num_players
        )
        distributions.append(distribution)

    # Aggregate total chips needed
    total_chips_used = {}
    for distribution in distributions:
        for nominal, count in distribution.items():
            total_chips_used[nominal] = total_chips_used.get(nominal, 0) + count

    # Validate availability
    is_feasible, shortage = validate_chip_availability(
        {
            nominal: total_chips_used[nominal] / num_players
            for nominal in total_chips_used
        },
        num_players,
        chips,
    )

    return {
        "multiplier": multiplier,
        "chip_value_info": f"1 chip = {multiplier} PLN (e.g., chip nominal {available_nominals[0]} = {available_nominals[0] * multiplier} PLN)",
        "distribution_per_player": distributions,
        "total_chips_used": total_chips_used,
        "is_feasible": is_feasible,
        "shortage": shortage if not is_feasible else None,
        "info": {
            **multiplier_info,
            "total_buy_in": total_buy_in,
            "num_players": num_players,
            "small_blind_chips": multiplier_info.get("sb_in_chips"),
            "big_blind_chips": multiplier_info.get("bb_in_chips"),
        },
    }


def find_alternative_distributions(
    num_players: int,
    buy_ins: list[float],
    small_blind: Optional[float] = None,
    big_blind: Optional[float] = None,
    max_alternatives: int = 5,
) -> list[dict]:
    """
    Find multiple alternative chip distributions, ranked by feasibility and quality.

    This function tries different multipliers and distribution strategies to find
    solutions that work with available inventory. It returns multiple options
    ranked by:
    1. Feasibility (solutions without shortages first)
    2. Stack depth (closer to 150 BB is better)
    3. Distribution quality (fewer small chips is better)

    Args:
        num_players: Number of players in the game
        buy_ins: List of buy-in amounts for each player
        small_blind: Small blind value in real money (optional)
        big_blind: Big blind value in real money (optional)
        max_alternatives: Maximum number of alternatives to return

    Returns:
        List of distribution results, sorted by quality (best first)
    """
    # Try various multipliers
    test_multipliers = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1, 2, 5, 10]

    # Filter multipliers that make sense for the buy-in amounts
    avg_buy_in = sum(buy_ins) / len(buy_ins)
    valid_multipliers = [m for m in test_multipliers if 50 <= avg_buy_in / m <= 10000]

    results = []

    for multiplier in valid_multipliers:
        try:
            result = distribution_algorithm(
                num_players=num_players,
                buy_ins=buy_ins,
                small_blind=small_blind,
                big_blind=big_blind,
                force_multiplier=multiplier,
            )

            # Score this solution
            score = 0

            # Feasibility is most important
            if result["is_feasible"]:
                score += 1000
            else:
                # Penalize by shortage severity
                if result["shortage"]:
                    total_shortage = sum(result["shortage"].values())
                    score -= total_shortage

            # Prefer stack depths close to 150 BB
            if result["info"].get("bb_per_player"):
                bb_depth = result["info"]["bb_per_player"]
                bb_penalty = abs(bb_depth - 150)
                score -= bb_penalty

            # Prefer fewer total chips (easier to handle)
            total_chips = sum(result["total_chips_used"].values())
            score -= total_chips * 0.01

            # Prefer round big blind values
            if result["info"].get("bb_in_chips"):
                bb_chips = result["info"]["bb_in_chips"]
                if bb_chips in [5, 10, 20, 25, 50, 100, 200, 500]:
                    score += 50

            result["_score"] = score
            results.append(result)

        except Exception:
            continue

    # Sort by score (highest first)
    results.sort(key=lambda x: x["_score"], reverse=True)

    # Remove score from output
    for result in results:
        if "_score" in result:
            del result["_score"]

    return results[:max_alternatives]


def print_distribution_result(result: dict):
    """Pretty print the distribution result."""
    print("=" * 60)
    print("CHIP DISTRIBUTION ANALYSIS")
    print("=" * 60)
    print(f"\nChip Value Multiplier: {result['multiplier']}")
    print(f"{result['chip_value_info']}")

    info = result["info"]
    print(f"\nTotal Buy-in: {info['total_buy_in']} PLN")
    print(f"Number of Players: {info['num_players']}")

    if info.get("big_blind_chips"):
        print(f"\nBlind Structure:")
        print(f"  Small Blind: {info['small_blind_chips']} chips")
        print(f"  Big Blind: {info['big_blind_chips']} chips")
        print(f"  Starting Stack: {info['bb_per_player']:.1f} BB per player")

    print(f"\n{'Player':<10} {'Buy-in':<12} {'Total Chips':<12} Distribution")
    print("-" * 60)

    for i, distribution in enumerate(result["distribution_per_player"], 1):
        buy_in = (
            sum(nominal * count for nominal, count in distribution.items())
            * result["multiplier"]
        )
        total_chips = sum(nominal * count for nominal, count in distribution.items())
        dist_str = ", ".join(
            f"{count}x{nominal}" for nominal, count in sorted(distribution.items())
        )
        print(f"Player {i:<3} {buy_in:<12.2f} {total_chips:<12.0f} {dist_str}")

    print("\n" + "=" * 60)
    print("TOTAL CHIPS NEEDED FROM INVENTORY")
    print("=" * 60)
    for nominal in sorted(result["total_chips_used"].keys()):
        count_needed = result["total_chips_used"][nominal]
        count_available = chips[nominal]
        status = "✓" if count_needed <= count_available else "✗ SHORTAGE"
        print(
            f"Nominal {nominal:>4}: {count_needed:>3} needed / {count_available:>3} available {status}"
        )

    if not result["is_feasible"]:
        print("\n⚠️  WARNING: Not enough chips in inventory!")
        print("Shortage:")
        for nominal, shortage in result["shortage"].items():
            print(f"  Nominal {nominal}: need {shortage} more chips")
    else:
        print("\n✓ Chip distribution is feasible with current inventory!")


def print_custom_distribution_result(result: dict):
    """Pretty print custom distribution result with value comparison."""
    print_distribution_result(result)

    info = result["info"]
    if "actual_value_per_player" in info and "expected_value_per_player" in info:
        actual = info["actual_value_per_player"]
        expected = info["expected_value_per_player"]
        diff = info["value_difference"]

        print("\n" + "=" * 60)
        print("VALUE VERIFICATION")
        print("=" * 60)
        print(f"Expected buy-in:    {expected:.2f} PLN")
        print(f"Actual chip value:  {actual:.2f} PLN")
        print(f"Difference:         {diff:+.2f} PLN ({diff / expected * 100:+.1f}%)")

        if abs(diff) < 0.01:
            print("✓ Perfect match!")
        elif abs(diff) < expected * 0.02:
            print("✓ Close enough (within 2%)")
        else:
            print("⚠ Significant difference - adjust distribution")


def print_alternatives(alternatives: list[dict], show_count: int = 3):
    """Print multiple alternative distributions."""
    print(f"\nFound {len(alternatives)} alternative distribution(s):\n")

    for i, result in enumerate(alternatives[:show_count], 1):
        print("=" * 80)
        print(f"ALTERNATIVE #{i}")
        print("=" * 80)
        print_distribution_result(result)
        print()


def main():
    """
    Run example scenarios demonstrating the chip distribution algorithm.

    This function shows three different use cases:
    1. Equal buy-ins with blind structure (typical cash game)
    2. Variable buy-ins without blinds (casual game)
    3. Tournament-style with higher buy-ins
    4. Forced multiplier example
    5. Alternative distributions when optimal has shortage
    6. Custom distribution (user's exact configuration)
    """
    print(f"Total chip value in inventory: {calc_chips_value()}\n")

    # Example 0: Custom distribution - User's actual game
    print("\n\n### EXAMPLE 0: Custom Distribution (User's config) ###\n")
    print("Testing: 10x1, 18x5, 12x25, 6x100 with multiplier 0.01")
    custom_result = custom_distribution(
        num_players=6,
        buy_ins=[10, 10, 10, 10, 10, 10],  # 10 PLN per player
        multiplier=0.01,
        chips_per_player={1: 10, 5: 18, 25: 12, 100: 6},
        small_blind=0.1,
        big_blind=0.2,
    )
    print_custom_distribution_result(custom_result)

    # Example 1: 6 players, equal buy-ins, with blinds
    print("\n\n### EXAMPLE 1: 6 players, 100 PLN each, 1/2 PLN blinds ###\n")
    result1 = distribution_algorithm(
        num_players=6,
        buy_ins=[100, 100, 100, 100, 100, 100],
        small_blind=1,
        big_blind=2,
    )
    print_distribution_result(result1)

    # Example 2: Forced multiplier (like your game yesterday)
    print("\n\n### EXAMPLE 2: 6 players, 100 PLN each, FORCED multiplier 0.01 ###\n")
    result2 = distribution_algorithm(
        num_players=6,
        buy_ins=[100, 100, 100, 100, 100, 100],
        small_blind=1,
        big_blind=2,
        force_multiplier=0.01,
    )
    print_distribution_result(result2)

    # Example 3: Finding alternatives when there's a shortage
    print("\n\n### EXAMPLE 3: 8 players, 200 PLN - Finding alternatives ###\n")
    alternatives = find_alternative_distributions(
        num_players=8, buy_ins=[200] * 8, small_blind=2, big_blind=5, max_alternatives=3
    )
    print_alternatives(alternatives, show_count=3)


if __name__ == "__main__":
    main()
