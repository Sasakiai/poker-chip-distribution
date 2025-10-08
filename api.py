"""
Poker Chip Distribution REST API

FastAPI application providing endpoints for chip distribution calculation.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
import uvicorn
import os

from main import (
    distribution_algorithm,
    find_alternative_distributions,
    custom_distribution,
    chips,
)

# Initialize FastAPI app
app = FastAPI(
    title="Poker Chip Distribution API",
    description="Calculate optimal poker chip distributions based on players, buy-ins, and blind structure",
    version="2.0.0",
)

# Add CORS middleware for web access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Pydantic Models
class DistributionRequest(BaseModel):
    """Request model for chip distribution calculation."""

    num_players: int = Field(..., ge=1, le=20, description="Number of players (1-20)")
    buy_ins: List[float] = Field(
        ...,
        min_items=1,
        description="Buy-in amount for each player (in PLN or currency)",
    )
    small_blind: Optional[float] = Field(
        None, gt=0, description="Small blind value in real money"
    )
    big_blind: Optional[float] = Field(
        None, gt=0, description="Big blind value in real money"
    )
    force_multiplier: Optional[float] = Field(
        None, gt=0, description="Force a specific chip value multiplier"
    )
    include_alternatives: bool = Field(
        True, description="Include alternative distributions if optimal has shortages"
    )
    max_alternatives: int = Field(
        5, ge=1, le=10, description="Maximum number of alternatives to return"
    )

    @validator("buy_ins")
    def validate_buy_ins_length(cls, v, values):
        if "num_players" in values and len(v) != values["num_players"]:
            raise ValueError(
                f"Length of buy_ins ({len(v)}) must match num_players ({values['num_players']})"
            )
        return v

    @validator("buy_ins")
    def validate_buy_ins_positive(cls, v):
        if any(buy_in <= 0 for buy_in in v):
            raise ValueError("All buy-ins must be positive")
        return v

    @validator("big_blind")
    def validate_blinds_relationship(cls, v, values):
        if (
            v is not None
            and "small_blind" in values
            and values["small_blind"] is not None
        ):
            if v <= values["small_blind"]:
                raise ValueError("Big blind must be greater than small blind")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "num_players": 6,
                "buy_ins": [100, 100, 100, 100, 100, 100],
                "small_blind": 1,
                "big_blind": 2,
                "force_multiplier": None,
                "include_alternatives": True,
                "max_alternatives": 3,
            }
        }


class CustomDistributionRequest(BaseModel):
    """Request model for testing a custom chip distribution."""

    num_players: int = Field(..., ge=1, le=20, description="Number of players")
    buy_ins: List[float] = Field(..., min_items=1, description="Buy-in amounts")
    multiplier: float = Field(..., gt=0, description="Chip value multiplier")
    chips_per_player: Dict[int, int] = Field(
        ..., description="Chip distribution per player (nominal: count)"
    )
    small_blind: Optional[float] = Field(None, gt=0, description="Small blind value")
    big_blind: Optional[float] = Field(None, gt=0, description="Big blind value")

    @validator("buy_ins")
    def validate_buy_ins_length(cls, v, values):
        if "num_players" in values and len(v) != values["num_players"]:
            raise ValueError(f"Length of buy_ins must match num_players")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "num_players": 6,
                "buy_ins": [10, 10, 10, 10, 10, 10],
                "multiplier": 0.01,
                "chips_per_player": {1: 10, 5: 18, 25: 12, 100: 6},
                "small_blind": 0.1,
                "big_blind": 0.2,
            }
        }


class ChipDistribution(BaseModel):
    """Single player's chip distribution."""

    nominal_1: int = Field(0, alias="1")
    nominal_5: int = Field(0, alias="5")
    nominal_25: int = Field(0, alias="25")
    nominal_100: int = Field(0, alias="100")
    nominal_500: int = Field(0, alias="500")
    nominal_1000: int = Field(0, alias="1000")

    class Config:
        populate_by_name = True


class DistributionInfo(BaseModel):
    """Additional information about the distribution."""

    total_buy_in: float
    num_players: int
    small_blind_chips: Optional[float]
    big_blind_chips: Optional[float]
    bb_per_player: Optional[float]
    chips_per_player: float


class DistributionResult(BaseModel):
    """Result of a single distribution calculation."""

    multiplier: float = Field(..., description="Chip value multiplier")
    chip_value_info: str = Field(
        ..., description="Human-readable chip value explanation"
    )
    distribution_per_player: List[Dict[int, int]] = Field(
        ..., description="Chip distribution for each player"
    )
    total_chips_used: Dict[int, int] = Field(
        ..., description="Total chips needed from inventory"
    )
    is_feasible: bool = Field(
        ..., description="Whether distribution is feasible with current inventory"
    )
    shortage: Optional[Dict[int, int]] = Field(
        None, description="Chip shortages if not feasible"
    )
    info: dict = Field(..., description="Additional distribution information")


class DistributionResponse(BaseModel):
    """Response containing optimal result and alternatives."""

    optimal: DistributionResult = Field(..., description="Optimal distribution")
    alternatives: List[DistributionResult] = Field(
        default=[], description="Alternative distributions (if requested)"
    )
    recommendation: str = Field(..., description="Recommendation message")


class InventoryResponse(BaseModel):
    """Current chip inventory information."""

    inventory: Dict[int, int] = Field(..., description="Available chips by nominal")
    total_value: int = Field(..., description="Total nominal value of all chips")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


# API Endpoints
@app.get("/", include_in_schema=False)
async def root():
    """Serve the main UI page."""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    # Fallback to API info if no index.html exists
    return {
        "message": "Poker Chip Distribution API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "POST /distribute": "Calculate chip distribution",
            "POST /custom-distribution": "Test custom chip configuration",
            "GET /inventory": "Get current chip inventory",
            "GET /health": "Health check",
        },
    }


@app.get("/api", tags=["General"])
async def api_info():
    """API information endpoint."""
    return {
        "message": "Poker Chip Distribution API",
        "version": "2.0.0",
        "docs": "/docs",
        "endpoints": {
            "POST /distribute": "Calculate chip distribution",
            "POST /custom-distribution": "Test custom chip configuration",
            "GET /inventory": "Get current chip inventory",
            "GET /health": "Health check",
        },
    }


@app.get("/health", response_model=HealthResponse, tags=["General"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "2.0.0"}


@app.get("/inventory", response_model=InventoryResponse, tags=["Inventory"])
async def get_inventory():
    """Get current chip inventory."""
    from main import calc_chips_value

    return {"inventory": chips, "total_value": calc_chips_value()}


@app.post("/distribute", response_model=DistributionResponse, tags=["Distribution"])
async def calculate_distribution(request: DistributionRequest):
    """
    Calculate optimal chip distribution and alternatives.

    This endpoint:
    1. Calculates the optimal distribution based on your parameters
    2. If optimal has shortages and alternatives are requested, finds 3-5 alternative solutions
    3. Returns both optimal and alternatives, ranked by feasibility and quality

    The optimal distribution is always returned, even if it has chip shortages.
    Alternatives (if requested) provide backup options that may work better with your inventory.
    """
    try:
        # Calculate optimal distribution
        optimal_result = distribution_algorithm(
            num_players=request.num_players,
            buy_ins=request.buy_ins,
            small_blind=request.small_blind,
            big_blind=request.big_blind,
            force_multiplier=request.force_multiplier,
        )

        response_data = {
            "optimal": optimal_result,
            "alternatives": [],
            "recommendation": "",
        }

        # Get alternatives if requested
        if request.include_alternatives:
            alternatives = find_alternative_distributions(
                num_players=request.num_players,
                buy_ins=request.buy_ins,
                small_blind=request.small_blind,
                big_blind=request.big_blind,
                max_alternatives=request.max_alternatives,
            )

            # Filter out the optimal solution if it appears in alternatives
            alternatives = [
                alt
                for alt in alternatives
                if alt["multiplier"] != optimal_result["multiplier"]
            ]

            response_data["alternatives"] = alternatives

        # Generate recommendation
        if optimal_result["is_feasible"]:
            if response_data["alternatives"]:
                response_data["recommendation"] = (
                    "✓ Optimal distribution is feasible with current inventory. "
                    f"Use multiplier {optimal_result['multiplier']}. "
                    f"Check alternatives below for other options."
                )
            else:
                response_data["recommendation"] = (
                    "✓ Optimal distribution is feasible with current inventory. "
                    f"Use multiplier {optimal_result['multiplier']}."
                )
        else:
            # Check if any alternative is feasible
            if response_data["alternatives"]:
                feasible_alts = [
                    alt for alt in response_data["alternatives"] if alt["is_feasible"]
                ]

                if feasible_alts:
                    best_alt = feasible_alts[0]
                    response_data["recommendation"] = (
                        f"⚠ Optimal distribution has shortages. "
                        f"Recommended alternative: Use multiplier {best_alt['multiplier']} "
                        f"(Stack depth: {best_alt['info'].get('bb_per_player', 'N/A')} BB)"
                    )
                else:
                    shortage_info = ", ".join(
                        f"{count} x nominal {nominal}"
                        for nominal, count in optimal_result["shortage"].items()
                    )
                    response_data["recommendation"] = (
                        f"✗ No feasible distribution found. Shortages: {shortage_info}. "
                        "Try: reduce players, lower buy-ins, or adjust blinds."
                    )
            else:
                shortage_info = ", ".join(
                    f"{count} x nominal {nominal}"
                    for nominal, count in optimal_result["shortage"].items()
                )
                response_data["recommendation"] = (
                    f"⚠ Optimal distribution has shortages: {shortage_info}. "
                    "Enable 'include_alternatives' to see other options."
                )

        return response_data

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.post(
    "/custom-distribution", response_model=DistributionResult, tags=["Distribution"]
)
async def test_custom_distribution(request: CustomDistributionRequest):
    """
    Test a custom chip distribution configuration.

    Use this endpoint to validate your specific chip setup before game night.
    It checks if your configuration:
    - Matches the expected buy-in amounts
    - Fits within your available chip inventory
    - Provides appropriate stack depths
    """
    try:
        result = custom_distribution(
            num_players=request.num_players,
            buy_ins=request.buy_ins,
            multiplier=request.multiplier,
            chips_per_player=request.chips_per_player,
            small_blind=request.small_blind,
            big_blind=request.big_blind,
        )

        return result

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@app.put("/inventory", tags=["Inventory"])
async def update_inventory(inventory: Dict[int, int]):
    """
    Update chip inventory.

    WARNING: This modifies the global chip inventory.
    In production, this should be protected with authentication.
    """
    global chips

    # Validate inventory
    valid_nominals = {1, 5, 25, 100, 500, 1000}
    for nominal in inventory.keys():
        if nominal not in valid_nominals:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid chip nominal: {nominal}. Must be one of {valid_nominals}",
            )

    for nominal, count in inventory.items():
        if count < 0:
            raise HTTPException(
                status_code=400,
                detail=f"Chip count cannot be negative for nominal {nominal}",
            )

    # Update inventory
    chips.clear()
    chips.update(inventory)

    from main import calc_chips_value

    return {
        "message": "Inventory updated successfully",
        "inventory": chips,
        "total_value": calc_chips_value(),
    }


# Run the API
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("api:app", host="0.0.0.0", port=port, reload=True)
