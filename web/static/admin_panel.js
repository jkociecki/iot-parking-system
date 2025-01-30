// Inicjalizacja wykresu
document.addEventListener("DOMContentLoaded", function () {
  const parkingData = JSON.parse(
    document.getElementById("parking-data").textContent
  );
  const ctx = document.getElementById("parkingUsageChart").getContext("2d");

  const gradient = ctx.createLinearGradient(0, 0, 0, 400);
  gradient.addColorStop(0, "rgba(129, 140, 248, 0.2)");
  gradient.addColorStop(1, "rgba(129, 140, 248, 0)");

  new Chart(ctx, {
    type: "line",
    data: {
      labels: parkingData.map((d) => d.hour + ":00"),
      datasets: [
        {
          label: "Liczba pojazdów",
          data: parkingData.map((d) => d.count),
          borderColor: "#818cf8",
          backgroundColor: gradient,
          tension: 0.4,
          fill: true,
          pointBackgroundColor: "#818cf8",
          pointBorderColor: "#fff",
          pointHoverRadius: 6,
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "#818cf8",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        intersect: false,
        mode: "index",
      },
      plugins: {
        legend: {
          labels: {
            color: "#fff",
            font: {
              family: "'Inter', sans-serif",
              size: 12,
            },
          },
        },
        tooltip: {
          backgroundColor: "rgba(17, 24, 39, 0.9)",
          titleColor: "#fff",
          bodyColor: "#fff",
          borderColor: "#374151",
          borderWidth: 1,
          padding: 12,
          displayColors: false,
          callbacks: {
            label: function (context) {
              return `Liczba pojazdów: ${context.parsed.y}`;
            },
          },
        },
      },
      scales: {
        y: {
          beginAtZero: true,
          grid: {
            color: "rgba(55, 65, 81, 0.3)",
            drawBorder: false,
          },
          ticks: {
            color: "#fff",
            font: {
              family: "'Inter', sans-serif",
            },
            padding: 10,
          },
        },
        x: {
          grid: {
            color: "rgba(55, 65, 81, 0.3)",
            drawBorder: false,
          },
          ticks: {
            color: "#fff",
            font: {
              family: "'Inter', sans-serif",
            },
            padding: 10,
          },
        },
      },
    },
  });
});

// Funkcje zarządzania firmami
async function updateFreeHours(companyId, value) {
  try {
    const response = await fetch(`/admin/companies/${companyId}/free-hours`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ freeHours: parseInt(value) }),
    });

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.error || "Błąd aktualizacji godzin");
    }

    showNotification("Zaktualizowano liczbę darmowych godzin", "success");
  } catch (error) {
    console.error("Error:", error);
    showNotification("Wystąpił błąd podczas aktualizacji godzin", "error");
  }
}

async function updateCompanyStatus(companyId, status) {
  try {
    const response = await fetch(`/admin/companies/${companyId}/status`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ status }),
    });

    const result = await response.json();
    if (!result.success) {
      throw new Error(result.error || "Błąd aktualizacji statusu");
    }

    showNotification("Zaktualizowano status firmy", "success");
  } catch (error) {
    console.error("Error:", error);
    showNotification("Wystąpił błąd podczas aktualizacji statusu", "error");
  }
}

async function deleteCompany(companyId) {
  console.log("Rozpoczęcie usuwania firmy:", companyId);

  try {
    // Potwierdzenie
    const confirmed = await confirmDialog(
      "Czy na pewno chcesz usunąć tę firmę?",
      "Ta operacja jest nieodwracalna."
    );

    console.log("Potwierdzenie usuwania:", confirmed);

    if (!confirmed) {
      console.log("Usuwanie anulowane przez użytkownika");
      return;
    }

    console.log(
      "Wysyłanie żądania DELETE do:",
      `/admin/companies/${companyId}`
    );

    const response = await fetch(`/admin/companies/${companyId}`, {
      method: "DELETE",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest", // Dodajemy nagłówek AJAX
      },
      credentials: "same-origin", // Dodajemy credentials dla CSRF
    });

    console.log("Odpowiedź serwera:", response.status, response.statusText);

    const result = await response.json();
    console.log("Dane odpowiedzi:", result);

    if (!result.success) {
      throw new Error(result.error || "Błąd usuwania firmy");
    }

    // Znajdź i usuń wiersz
    const row = document.querySelector(
      `tr:has(button[data-company-id="${companyId}"])`
    );
    if (!row) {
      console.error("Nie znaleziono wiersza o ID:", companyId);
      return;
    }

    // Animacja
    row.style.transition = "all 0.3s ease-out";
    row.style.opacity = "0";
    row.style.transform = "translateX(20px)";

    setTimeout(() => {
      row.remove();
    }, 300);

    showNotification("Firma została usunięta", "success");
  } catch (error) {
    console.error("Błąd podczas usuwania firmy:", error);
    showNotification("Wystąpił błąd podczas usuwania firmy", "error");
  }
}

// System powiadomień
function showNotification(message, type = "info") {
  const notification = document.createElement("div");
  notification.className = `fixed bottom-4 right-4 px-6 py-3 rounded-lg text-white transform transition-all duration-300 ease-out translate-y-20 opacity-0 ${
    type === "success"
      ? "bg-green-600"
      : type === "error"
      ? "bg-red-600"
      : "bg-blue-600"
  }`;
  notification.innerHTML = `
      <div class="flex items-center gap-2">
          ${
            type === "success"
              ? `
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
              </svg>
          `
              : type === "error"
              ? `
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
          `
              : `
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
          `
          }
          <span>${message}</span>
      </div>
  `;

  document.body.appendChild(notification);
  requestAnimationFrame(() => {
    notification.style.transform = "translateY(0)";
    notification.style.opacity = "1";
  });

  setTimeout(() => {
    notification.style.transform = "translateY(20px)";
    notification.style.opacity = "0";
    setTimeout(() => {
      notification.remove();
    }, 300);
  }, 3000);
}

// Dialog potwierdzenia
function confirmDialog(title, message) {
  return new Promise((resolve) => {
    const dialog = document.createElement("div");
    dialog.className =
      "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50";
    dialog.innerHTML = `
          <div class="bg-gray-800 rounded-lg p-6 max-w-md w-full transform transition-all scale-95 opacity-0">
              <h3 class="text-xl font-bold text-white mb-2">${title}</h3>
              <p class="text-gray-300 mb-6">${message}</p>
              <div class="flex justify-end gap-4">
                  <button id="cancelBtn" class="px-4 py-2 text-gray-400 hover:text-white transition-colors">
                      Anuluj
                  </button>
                  <button id="confirmBtn" class="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors">
                      Potwierdź
                  </button>
              </div>
          </div>
      `;

    document.body.appendChild(dialog);

    // Dodajemy event listenery zamiast inline onclick
    dialog.querySelector("#cancelBtn").addEventListener("click", () => {
      dialog.remove();
      resolve(false);
    });

    dialog.querySelector("#confirmBtn").addEventListener("click", () => {
      dialog.remove();
      resolve(true);
    });

    // Animacja pojawienia się
    requestAnimationFrame(() => {
      dialog.querySelector(".bg-gray-800").style.transform = "scale(1)";
      dialog.querySelector(".bg-gray-800").style.opacity = "1";
    });
  });
}

// Modal dodawania firmy
let addCompanyModal = null;

function createAddCompanyModal() {
  const modal = document.createElement("div");
  modal.className =
    "fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50 opacity-0 transition-opacity duration-300";
  modal.innerHTML = `
      <div class="bg-gray-800 rounded-lg p-6 max-w-md w-full transform transition-all scale-95 opacity-0">
          <h3 class="text-xl font-bold text-white mb-4">Dodaj nową firmę</h3>
          <form onsubmit="handleAddCompany(event)">
              <div class="space-y-4">
                  <div>
                      <label class="block text-sm font-medium text-gray-300 mb-1">Nazwa firmy</label>
                      <input type="text" name="companyName" required
                          class="w-full p-2 bg-gray-700 rounded-lg border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                  </div>
                  <div>
                      <label class="block text-sm font-medium text-gray-300 mb-1">Darmowe godziny</label>
                      <input type="number" name="freeHours" required min="0"
                          class="w-full p-2 bg-gray-700 rounded-lg border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500">
                  </div>
                  <div class="flex justify-end gap-4 mt-6">
                      <button type="button" onclick="hideAddCompanyModal()"
                          class="px-4 py-2 text-gray-400 hover:text-white transition-colors">
                          Anuluj
                      </button>
                      <button type="submit"
                          class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                          Dodaj firmę
                      </button>
                  </div>
              </div>
          </form>
      </div>
  `;

  return modal;
}

function showAddCompanyModal() {
  if (!addCompanyModal) {
    addCompanyModal = createAddCompanyModal();
    document.body.appendChild(addCompanyModal);
  }

  requestAnimationFrame(() => {
    addCompanyModal.style.opacity = "1";
    addCompanyModal.querySelector(".bg-gray-800").style.transform = "scale(1)";
    addCompanyModal.querySelector(".bg-gray-800").style.opacity = "1";
  });
}

function hideAddCompanyModal() {
  if (addCompanyModal) {
    addCompanyModal.style.opacity = "0";
    addCompanyModal.querySelector(".bg-gray-800").style.transform =
      "scale(0.95)";
    addCompanyModal.querySelector(".bg-gray-800").style.opacity = "0";

    setTimeout(() => {
      addCompanyModal.remove();
      addCompanyModal = null;
    }, 300);
  }
}

async function handleAddCompany(event) {
  event.preventDefault();
  const formData = new FormData(event.target);

  try {
    const requestData = {
      name: formData.get("companyName"),
      max_bonus_hours: parseInt(formData.get("freeHours")),
    };

    console.log("Wysyłanie danych:", requestData);

    const response = await fetch("/admin/companies", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify(requestData),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Błąd podczas dodawania firmy");
    }

    const result = await response.json();
    console.log("Odpowiedź serwera:", result);

    if (!result.success) {
      throw new Error(result.error || "Błąd dodawania firmy");
    }

    // Dodanie nowego wiersza do tabeli
    const tbody = document.querySelector("table tbody");
    const newRow = `
      <tr class="border-b border-gray-700 hover:bg-gray-750 transition-colors opacity-0 transform translate-x-4">
        <td class="p-4 text-white border-r border-gray-700">${result.company.name}</td>
        <td class="p-4 border-r border-gray-700">
          <div class="flex items-center gap-2">
            <span class="text-white" id="hours-display-${result.company.id}">${result.company.max_bonus_hours}</span>
            <input
              type="number"
              min="0"
              value="${result.company.max_bonus_hours}"
              id="hours-input-${result.company.id}"
              data-company-id="${result.company.id}"
              class="hidden w-24 p-2 bg-gray-700 rounded-lg border border-gray-600 text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              onclick="toggleEditHours('${result.company.id}')"
              class="text-blue-400 hover:text-blue-300 transition-colors px-2 py-1 rounded"
              id="edit-btn-${result.company.id}"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
              </svg>
            </button>
            <button
              onclick="saveHours('${result.company.id}')"
              class="hidden text-green-400 hover:text-green-300 transition-colors px-2 py-1 rounded"
              id="save-btn-${result.company.id}"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
            </button>
            <button
              onclick="cancelEdit('${result.company.id}')"
              class="hidden text-red-400 hover:text-red-300 transition-colors px-2 py-1 rounded"
              id="cancel-btn-${result.company.id}"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </td>
        <td class="p-4">
          <button
            type="button"
            data-company-id="${result.company.id}"
            onclick="deleteCompany('${result.company.id}')"
            class="bg-gradient-to-r from-red-600 to-red-500 text-white px-4 py-2 rounded-lg hover:from-red-700 hover:to-red-600 transition-all duration-200 transform hover:scale-105 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-opacity-50 shadow-lg hover:shadow-red-500/25"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 inline-block mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
            </svg>
            Usuń
          </button>
        </td>
      </tr>
    `;

    tbody.insertAdjacentHTML("beforeend", newRow);
    const newRowElement = tbody.lastElementChild;

    requestAnimationFrame(() => {
      newRowElement.style.opacity = "1";
      newRowElement.style.transform = "translateX(0)";
    });

    hideAddCompanyModal();
    showNotification("Firma została dodana", "success");
  } catch (error) {
    console.error("Błąd podczas dodawania firmy:", error);
    showNotification(`Błąd: ${error.message}`, "error");
  }
}

// Funkcje do zarządzania edycją godzin
function toggleEditHours(companyId) {
  // Ukryj wyświetlanie i pokaż input
  document.getElementById(`hours-display-${companyId}`).classList.add("hidden");
  document
    .getElementById(`hours-input-${companyId}`)
    .classList.remove("hidden");

  // Ukryj przycisk edycji, pokaż przyciski zapisz/anuluj
  document.getElementById(`edit-btn-${companyId}`).classList.add("hidden");
  document.getElementById(`save-btn-${companyId}`).classList.remove("hidden");
  document.getElementById(`cancel-btn-${companyId}`).classList.remove("hidden");

  // Fokus na input
  document.getElementById(`hours-input-${companyId}`).focus();
}

function cancelEdit(companyId) {
  const display = document.getElementById(`hours-display-${companyId}`);
  const input = document.getElementById(`hours-input-${companyId}`);

  // Przywróć oryginalną wartość
  input.value = display.textContent;

  // Przełącz widoczność elementów
  display.classList.remove("hidden");
  input.classList.add("hidden");
  document.getElementById(`edit-btn-${companyId}`).classList.remove("hidden");
  document.getElementById(`save-btn-${companyId}`).classList.add("hidden");
  document.getElementById(`cancel-btn-${companyId}`).classList.add("hidden");
}

async function saveHours(companyId) {
  const input = document.getElementById(`hours-input-${companyId}`);
  const display = document.getElementById(`hours-display-${companyId}`);
  const newValue = input.value;

  if (!newValue || newValue < 0) {
    showNotification("Wartość musi być liczbą większą lub równą 0", "error");
    return;
  }

  try {
    console.log("Wysyłanie żądania aktualizacji godzin:", {
      companyId: companyId,
      newValue: newValue,
    });

    const response = await fetch(`/admin/companies/${companyId}/bonus_hours`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({
        max_bonus_hours: parseInt(newValue),
      }),
    });

    console.log("Status odpowiedzi:", response.status);

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const result = await response.json();
    console.log("Odpowiedź serwera:", result);

    if (!result.success) {
      throw new Error(result.error || "Błąd aktualizacji godzin");
    }

    // Aktualizuj wyświetlaną wartość
    display.textContent = newValue;

    // Przełącz widoczność elementów
    display.classList.remove("hidden");
    input.classList.add("hidden");
    document.getElementById(`edit-btn-${companyId}`).classList.remove("hidden");
    document.getElementById(`save-btn-${companyId}`).classList.add("hidden");
    document.getElementById(`cancel-btn-${companyId}`).classList.add("hidden");

    showNotification("Zaktualizowano liczbę darmowych godzin", "success");
  } catch (error) {
    console.error("Błąd podczas aktualizacji godzin:", error);
    showNotification(`Błąd: ${error.message}`, "error");
    cancelEdit(companyId);
  }
}

// Dodaj obsługę klawisza Enter i Escape
document.addEventListener("keydown", function (event) {
  if (
    event.target.type === "number" &&
    event.target.hasAttribute("data-company-id")
  ) {
    const companyId = event.target.dataset.companyId;

    if (event.key === "Enter") {
      event.preventDefault();
      saveHours(companyId);
    } else if (event.key === "Escape") {
      event.preventDefault();
      cancelEdit(companyId);
    }
  }
});

// Eksportuj funkcje do globalnego scope
window.toggleEditHours = toggleEditHours;
window.cancelEdit = cancelEdit;
window.saveHours = saveHours;
window.updateFreeHours = updateFreeHours;
window.updateCompanyStatus = updateCompanyStatus;
window.deleteCompany = deleteCompany;
window.showAddCompanyModal = showAddCompanyModal;
window.hideAddCompanyModal = hideAddCompanyModal;
window.handleAddCompany = handleAddCompany;
window.confirmDialog = confirmDialog;
