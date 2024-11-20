const baseUrl = 'https://countriesnow.space/api/v0.1';
const countryName = "United States";

function fetchStates() {
    fetch(`${baseUrl}/countries/states`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ country: countryName }),
    })
        .then((response) => response.json())
        .then((data) => {
            const stateSelect = document.getElementById("state-select");
            stateSelect.innerHTML = '<option value="" disabled selected>Choose a state</option>'; // Reset states
            if (data.data && data.data.states) {
                data.data.states.forEach((state) => {
                    const option = document.createElement("option");
                    option.value = state.name;
                    option.textContent = state.name;
                    stateSelect.appendChild(option);
                });
                stateSelect.disabled = false; // Enable the state dropdown
            }
        })
        .catch((error) => console.error("Error fetching states:", error));
}

// Fetch and populate the cities dropdown based on the selected state
function fetchCities(stateName) {
    fetch(`${baseUrl}/countries/state/cities`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ country: countryName, state: stateName }),
    })
        .then((response) => response.json())
        .then((data) => {
            const citySelect = document.getElementById("city-select");
            citySelect.innerHTML = '<option value="" disabled selected>Choose a city</option>'; // Reset cities
            if (data.data) {
                data.data.forEach((city) => {
                    const option = document.createElement("option");
                    option.value = city;
                    option.textContent = city;
                    citySelect.appendChild(option);
                });
                citySelect.disabled = false; // Enable the city dropdown
            }
        })
        .catch((error) => console.error("Error fetching cities:", error));
}

document.addEventListener("DOMContentLoaded", () => {
    // Fetch states for United States on page load
    fetchStates();

    // Populate cities when a state is selected
    document.getElementById("state-select").addEventListener("change", function () {
        const stateName = this.value;
        document.getElementById("city-select").disabled = true; // Disable cities while loading
        fetchCities(stateName);
    });
    // Toggle the visibility of the extra filters section
    const expandFiltersButton = document.getElementById("expand-filters");
    const extraFiltersSection = document.getElementById("extra-filters");

    expandFiltersButton.addEventListener("click", function () {
        if (extraFiltersSection.style.display === "none") {
            extraFiltersSection.style.display = "block"; // Show extra filters
            expandFiltersButton.textContent = "Hide Filters";
        } else {
            extraFiltersSection.style.display = "none"; // Hide extra filters
            expandFiltersButton.textContent = "Expand Filters";
        }
    });

    // Assign random food emojis to post images
    const foodEmojis = [
        "🍔", "🍕", "🍣", "🥗", "🍜", "🍤", "🍩", "🍪", "🍫", "🧁",
        "🍟", "🌮", "🍲", "🥞", "🍇", "🍉", "🍎", "🍋", "🥝", "🥥"
    ];
    const postImages = document.querySelectorAll(".post-image");

    postImages.forEach((image) => {
        const randomEmoji = foodEmojis[Math.floor(Math.random() * foodEmojis.length)];
        image.textContent = randomEmoji; // Set the emoji as the content of the div
    });

    // /* Reset Logic */
    // document.getElementById("reset-filters").addEventListener("click", function () {
    //     // Reset date
    //     document.getElementById("date").value = "";

    //     // Reset location filters
    //     document.getElementById("state-select").value = "";
    //     document.getElementById("city-select").value = "";
    //     document.getElementById("street-info").value = "";

    //     // Disable dependent dropdowns and fields
    //     document.getElementById("state-select").disabled = false;
    //     document.getElementById("city-select").disabled = true;
    //     document.getElementById("street-info").disabled = true;

    //     // Reset additional filters (if any)
    //     const checkboxes = document.querySelectorAll(
    //         ".dietary-restrictions input[type='checkbox'], .meal-types input[type='checkbox'], .in-return input[type='checkbox']"
    //     );
    //     checkboxes.forEach((checkbox) => {
    //         checkbox.checked = false;
    //     });

    //     // Clear the posts container
    //     window.location.href = "/";
    // });
});