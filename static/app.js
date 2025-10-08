// ===================================
// State Management
// ===================================

const state = {
  numPlayers: 6,
  buyIns: [],
  smallBlind: 1,
  bigBlind: 2,
  forceMultiplier: null,
  includeAlternatives: true,
  maxAlternatives: 5,
  variableBuyIns: false,
};

// ===================================
// DOM Elements
// ===================================

const elements = {
  form: document.getElementById("distributionForm"),
  numPlayersInput: document.getElementById("numPlayers"),
  buyInAmountInput: document.getElementById("buyInAmount"),
  smallBlindInput: document.getElementById("smallBlind"),
  bigBlindInput: document.getElementById("bigBlind"),
  forceMultiplierInput: document.getElementById("forceMultiplier"),
  maxAlternativesInput: document.getElementById("maxAlternatives"),
  includeAlternativesCheckbox: document.getElementById("includeAlternatives"),
  variableBuyInsCheckbox: document.getElementById("variableBuyIns"),
  variableBuyInsContainer: document.getElementById("variableBuyInsContainer"),
  buyInsList: document.getElementById("buyInsList"),
  advancedToggle: document.getElementById("advancedToggle"),
  advancedOptions: document.getElementById("advancedOptions"),
  calculateBtn: document.getElementById("calculateBtn"),
  resultsSection: document.getElementById("resultsSection"),
  recommendationBanner: document.getElementById("recommendationBanner"),
  optimalBadge: document.getElementById("optimalBadge"),
  optimalResult: document.getElementById("optimalResult"),
  alternativesContainer: document.getElementById("alternativesContainer"),
  alternativesList: document.getElementById("alternativesList"),
  loadingSpinner: document.getElementById("loadingSpinner"),
  errorMessage: document.getElementById("errorMessage"),
  inventoryLink: document.getElementById("inventoryLink"),
  inventoryModal: document.getElementById("inventoryModal"),
  closeModal: document.getElementById("closeModal"),
  inventoryContent: document.getElementById("inventoryContent"),
};

// ===================================
// Initialization
// ===================================

function init() {
  setupEventListeners();
  updateBuyInsList();
}

function setupEventListeners() {
  // Form submission
  elements.form.addEventListener("submit", handleFormSubmit);

  // Number of players change
  elements.numPlayersInput.addEventListener("change", () => {
    state.numPlayers = parseInt(elements.numPlayersInput.value);
    updateBuyInsList();
  });

  // Variable buy-ins toggle
  elements.variableBuyInsCheckbox.addEventListener("change", (e) => {
    state.variableBuyIns = e.target.checked;
    elements.variableBuyInsContainer.style.display = e.target.checked
      ? "block"
      : "none";
    updateBuyInsList();
  });

  // Advanced options toggle
  elements.advancedToggle.addEventListener("click", () => {
    const isOpen = elements.advancedOptions.style.display === "block";
    elements.advancedOptions.style.display = isOpen ? "none" : "block";
    const chevron = elements.advancedToggle.querySelector(".chevron");
    chevron.classList.toggle("open", !isOpen);
  });

  // Modal controls
  elements.inventoryLink.addEventListener("click", (e) => {
    e.preventDefault();
    showInventoryModal();
  });

  elements.closeModal.addEventListener("click", () => {
    elements.inventoryModal.style.display = "none";
  });

  elements.inventoryModal.addEventListener("click", (e) => {
    if (e.target === elements.inventoryModal) {
      elements.inventoryModal.style.display = "none";
    }
  });

  // ESC key to close modal
  document.addEventListener("keydown", (e) => {
    if (
      e.key === "Escape" &&
      elements.inventoryModal.style.display === "block"
    ) {
      elements.inventoryModal.style.display = "none";
    }
  });
}

// ===================================
// Buy-ins Management
// ===================================

function updateBuyInsList() {
  if (!state.variableBuyIns) {
    return;
  }

  const buyInAmount = parseFloat(elements.buyInAmountInput.value) || 100;

  elements.buyInsList.innerHTML = "";

  for (let i = 0; i < state.numPlayers; i++) {
    const buyInInput = document.createElement("div");
    buyInInput.className = "buyin-input";
    buyInInput.innerHTML = `
            <label>Player ${i + 1}:</label>
            <input
                type="number"
                class="player-buyin"
                data-player="${i}"
                min="1"
                step="0.01"
                value="${buyInAmount}"
                required
            >
        `;
    elements.buyInsList.appendChild(buyInInput);
  }
}

function getBuyIns() {
  if (state.variableBuyIns) {
    const inputs = document.querySelectorAll(".player-buyin");
    return Array.from(inputs).map((input) => parseFloat(input.value));
  } else {
    const buyInAmount = parseFloat(elements.buyInAmountInput.value);
    return Array(state.numPlayers).fill(buyInAmount);
  }
}

// ===================================
// Form Handling
// ===================================

async function handleFormSubmit(e) {
  e.preventDefault();

  // Hide previous results and errors
  elements.resultsSection.style.display = "none";
  elements.errorMessage.style.display = "none";
  elements.loadingSpinner.style.display = "block";

  try {
    // Prepare request data
    const requestData = {
      num_players: parseInt(elements.numPlayersInput.value),
      buy_ins: getBuyIns(),
      small_blind: elements.smallBlindInput.value
        ? parseFloat(elements.smallBlindInput.value)
        : null,
      big_blind: elements.bigBlindInput.value
        ? parseFloat(elements.bigBlindInput.value)
        : null,
      force_multiplier: elements.forceMultiplierInput.value
        ? parseFloat(elements.forceMultiplierInput.value)
        : null,
      include_alternatives: elements.includeAlternativesCheckbox.checked,
      max_alternatives: parseInt(elements.maxAlternativesInput.value),
    };

    // Make API request
    const response = await fetch("/distribute", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Failed to calculate distribution");
    }

    const data = await response.json();

    // Display results
    displayResults(data);
  } catch (error) {
    console.error("Error:", error);
    showError(error.message);
  } finally {
    elements.loadingSpinner.style.display = "none";
  }
}

// ===================================
// Results Display
// ===================================

function displayResults(data) {
  // Show results section
  elements.resultsSection.style.display = "block";

  // Display recommendation banner
  displayRecommendationBanner(data.recommendation, data.optimal.is_feasible);

  // Display optimal distribution
  displayDistribution(
    data.optimal,
    elements.optimalResult,
    elements.optimalBadge,
    true,
  );

  // Display alternatives
  if (data.alternatives && data.alternatives.length > 0) {
    elements.alternativesContainer.style.display = "block";
    elements.alternativesList.innerHTML = "";

    data.alternatives.forEach((alternative, index) => {
      const altCard = document.createElement("div");
      altCard.className = "card result-card alternative-card";

      const altHeader = document.createElement("div");
      altHeader.className = "result-header";
      altHeader.innerHTML = `
                <h2>Alternative ${index + 1}</h2>
                <span class="badge ${alternative.is_feasible ? "feasible" : "shortage"}">
                    ${alternative.is_feasible ? "Feasible" : "Has Shortages"}
                </span>
            `;
      altCard.appendChild(altHeader);

      const altContent = document.createElement("div");
      displayDistribution(alternative, altContent, null, false);
      altCard.appendChild(altContent);

      elements.alternativesList.appendChild(altCard);
    });
  } else {
    elements.alternativesContainer.style.display = "none";
  }

  // Scroll to results
  elements.resultsSection.scrollIntoView({
    behavior: "smooth",
    block: "nearest",
  });
}

function displayRecommendationBanner(recommendation, isFeasible) {
  elements.recommendationBanner.innerHTML = recommendation;

  // Determine banner type based on symbols in recommendation
  if (recommendation.includes("✓")) {
    elements.recommendationBanner.className = "banner success";
  } else if (recommendation.includes("⚠")) {
    elements.recommendationBanner.className = "banner warning";
  } else if (recommendation.includes("✗")) {
    elements.recommendationBanner.className = "banner error";
  } else {
    elements.recommendationBanner.className = "banner";
  }
}

function displayDistribution(distribution, container, badgeElement, isOptimal) {
  container.innerHTML = "";

  // Update badge if provided
  if (badgeElement) {
    badgeElement.className = `badge ${distribution.is_feasible ? "feasible" : "shortage"}`;
    badgeElement.textContent = distribution.is_feasible
      ? "Feasible"
      : "Has Shortages";
  }

  // Distribution info section
  const infoSection = document.createElement("div");
  infoSection.className = "distribution-info";

  const infoTitle = document.createElement("h3");
  infoTitle.textContent = "Configuration";
  infoSection.appendChild(infoTitle);

  const chipValueInfo = document.createElement("p");
  chipValueInfo.innerHTML = `<strong>Chip Values:</strong> ${distribution.chip_value_info}`;
  chipValueInfo.style.marginTop = "var(--spacing-md)";
  chipValueInfo.style.color = "var(--color-text-secondary)";
  infoSection.appendChild(chipValueInfo);

  const infoGrid = document.createElement("div");
  infoGrid.className = "info-grid";

  const info = distribution.info;
  const infoItems = [
    { label: "Multiplier", value: distribution.multiplier },
    { label: "Total Buy-in", value: `${info.total_buy_in} PLN` },
    { label: "Players", value: info.num_players },
    { label: "Chips per Player", value: info.chips_per_player },
    {
      label: "Small Blind",
      value: info.small_blind_chips ? `${info.small_blind_chips} chips` : "N/A",
    },
    {
      label: "Big Blind",
      value: info.big_blind_chips ? `${info.big_blind_chips} chips` : "N/A",
    },
    {
      label: "Stack Depth",
      value: info.bb_per_player ? `${info.bb_per_player} BB` : "N/A",
    },
  ];

  infoItems.forEach((item) => {
    const infoItem = document.createElement("div");
    infoItem.className = "info-item";
    infoItem.innerHTML = `
            <div class="info-label">${item.label}</div>
            <div class="info-value">${item.value}</div>
        `;
    infoGrid.appendChild(infoItem);
  });

  infoSection.appendChild(infoGrid);
  container.appendChild(infoSection);

  // Chip distribution table
  const chipSection = document.createElement("div");
  chipSection.className = "chip-distribution";

  const chipTitle = document.createElement("h3");
  chipTitle.textContent = "Chip Distribution per Player";
  chipSection.appendChild(chipTitle);

  const table = document.createElement("table");
  table.className = "chip-table";

  // Table header
  const thead = document.createElement("thead");
  const headerRow = document.createElement("tr");
  headerRow.innerHTML = `
        <th>Player</th>
        <th>1 chip</th>
        <th>5 chips</th>
        <th>25 chips</th>
        <th>100 chips</th>
        <th>500 chips</th>
        <th>1000 chips</th>
    `;
  thead.appendChild(headerRow);
  table.appendChild(thead);

  // Table body
  const tbody = document.createElement("tbody");
  distribution.distribution_per_player.forEach((playerChips, index) => {
    const row = document.createElement("tr");
    const chipCounts = [
      playerChips[1] || 0,
      playerChips[5] || 0,
      playerChips[25] || 0,
      playerChips[100] || 0,
      playerChips[500] || 0,
      playerChips[1000] || 0,
    ];

    row.innerHTML = `
            <td><strong>Player ${index + 1}</strong></td>
            ${chipCounts.map((count) => `<td>${count || "—"}</td>`).join("")}
        `;
    tbody.appendChild(row);
  });
  table.appendChild(tbody);

  chipSection.appendChild(table);
  container.appendChild(chipSection);

  // Total chips needed
  const totalSection = document.createElement("div");
  totalSection.className = "total-chips";

  const totalTitle = document.createElement("h4");
  totalTitle.textContent = "Total Chips Needed from Inventory";
  totalSection.appendChild(totalTitle);

  const chipList = document.createElement("div");
  chipList.className = "chip-list";

  const nominals = [1, 5, 25, 100, 500, 1000];
  nominals.forEach((nominal) => {
    const count = distribution.total_chips_used[nominal] || 0;
    if (count > 0) {
      const chipCount = document.createElement("div");
      chipCount.className = "chip-count";
      chipCount.innerHTML = `
                <span class="chip-nominal" data-value="${nominal}">${nominal}</span>
                <span>×</span>
                <span>${count}</span>
            `;
      chipList.appendChild(chipCount);
    }
  });

  totalSection.appendChild(chipList);
  container.appendChild(totalSection);

  // Shortage information
  if (!distribution.is_feasible && distribution.shortage) {
    const shortageSection = document.createElement("div");
    shortageSection.className = "shortage-info";

    const shortageTitle = document.createElement("h4");
    shortageTitle.innerHTML = `
            <svg style="width: 20px; height: 20px;" viewBox="0 0 20 20" fill="currentColor">
                <path fill-rule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
            </svg>
            Chip Shortages
        `;
    shortageSection.appendChild(shortageTitle);

    const shortageList = document.createElement("div");
    shortageList.className = "chip-list";

    Object.entries(distribution.shortage).forEach(([nominal, count]) => {
      const chipCount = document.createElement("div");
      chipCount.className = "chip-count";
      chipCount.innerHTML = `
                <span class="chip-nominal" data-value="${nominal}">${nominal}</span>
                <span>×</span>
                <span>${count}</span>
                <span style="color: var(--color-error);">short</span>
            `;
      shortageList.appendChild(chipCount);
    });

    shortageSection.appendChild(shortageList);
    container.appendChild(shortageSection);
  }
}

// ===================================
// Inventory Modal
// ===================================

async function showInventoryModal() {
  elements.inventoryModal.style.display = "flex";
  elements.inventoryContent.innerHTML =
    '<div class="loading-spinner"><div class="spinner"></div></div>';

  try {
    const response = await fetch("/inventory");
    if (!response.ok) {
      throw new Error("Failed to fetch inventory");
    }

    const data = await response.json();
    displayInventory(data);
  } catch (error) {
    console.error("Error fetching inventory:", error);
    elements.inventoryContent.innerHTML = `
            <div class="error-message">
                Failed to load inventory: ${error.message}
            </div>
        `;
  }
}

function displayInventory(data) {
  elements.inventoryContent.innerHTML = "";

  const totalValue = document.createElement("div");
  totalValue.className = "info-item";
  totalValue.style.marginBottom = "var(--spacing-lg)";
  totalValue.innerHTML = `
        <div class="info-label">Total Nominal Value</div>
        <div class="info-value">${data.total_value}</div>
    `;
  elements.inventoryContent.appendChild(totalValue);

  const chipList = document.createElement("div");
  chipList.className = "chip-list";
  chipList.style.display = "grid";
  chipList.style.gridTemplateColumns = "1fr";
  chipList.style.gap = "var(--spacing-md)";

  const nominals = [1, 5, 25, 100, 500, 1000];
  nominals.forEach((nominal) => {
    const count = data.inventory[nominal] || 0;
    const chipItem = document.createElement("div");
    chipItem.style.display = "flex";
    chipItem.style.justifyContent = "space-between";
    chipItem.style.alignItems = "center";
    chipItem.style.padding = "var(--spacing-md)";
    chipItem.style.background = "var(--color-surface-light)";
    chipItem.style.borderRadius = "var(--radius-md)";
    chipItem.style.border = "1px solid var(--color-border)";

    chipItem.innerHTML = `
            <span class="chip-nominal" data-value="${nominal}">Chip ${nominal}</span>
            <span style="font-family: var(--font-mono); font-weight: 600; font-size: 1.25rem;">${count}</span>
        `;
    chipList.appendChild(chipItem);
  });

  elements.inventoryContent.appendChild(chipList);
}

// ===================================
// Error Handling
// ===================================

function showError(message) {
  elements.errorMessage.innerHTML = `
        <strong>Error:</strong> ${message}
    `;
  elements.errorMessage.style.display = "block";
  elements.errorMessage.scrollIntoView({
    behavior: "smooth",
    block: "nearest",
  });
}

// ===================================
// Start Application
// ===================================

document.addEventListener("DOMContentLoaded", init);
