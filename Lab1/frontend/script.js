const addHeader = document.getElementById("addHeader");

addHeader.addEventListener("click", () => {
  addForm.classList.toggle("hidden");
});

const addForm = document.getElementById("addForm");

addForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const addFields = [
    { key: "Crime Id", id: "addCrimeId" },
    { key: "Original Crime Type Name", id: "addCrimeType" },
    { key: "Report Date", id: "addReportDate" },
    { key: "Call Date", id: "addCallDate" },
    { key: "Offense Date", id: "addOffenseDate" },
    { key: "Call Time", id: "addCallTime" },
    { key: "Disposition", id: "addDisposition" },
    { key: "Address", id: "addAddress" },
    { key: "City", id: "addCity" },
    { key: "State", id: "addState" },
    { key: "Address Type", id: "addAddressType" },
    { key: "Case Status", id: "addStatus" },
  ];

  const newCrime = {};

  addFields.forEach((field) => {
    newCrime[field.key] = document.getElementById(field.id).value;
  });

  const response = await fetch("http://127.0.0.1:8000/crimes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(newCrime),
  });

  if (!response.ok) {
    const error = await response.json();
    alert(error.detail);
    return;
  }

  addForm.reset();
  addForm.classList.toggle("hidden");
  searchForm.requestSubmit();
});

const searchForm = document.getElementById("searchForm");
const crimeTable = document.getElementById("crimeTable");

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const crimeId = document.getElementById("crimeId").value;
  const crimeType = document.getElementById("crimeType").value;
  const city = document.getElementById("city").value;
  const disposition = document.getElementById("disposition").value;
  const status = document.getElementById("status").value;

  const params = new URLSearchParams();

  if (crimeId) params.append("crime_id", crimeId);

  if (crimeType) params.append("crime_type", crimeType);

  if (city) params.append("city", city);

  if (disposition) params.append("disposition", disposition);

  if (status) params.append("status", status);

  const url = "http://127.0.0.1:8000/crimes?" + params.toString();

  const response = await fetch(url);
  const crimes = await response.json();

  crimeTable.innerHTML = "";
  crimes.forEach((crime, index) => {
    const row = document.createElement("tr");

    row.innerHTML = `
      <td>${index + 1}</td>
      <td>${crime["Crime Id"]}</td>
      <td>${crime["Original Crime Type Name"]}</td>
      <td>${crime["Report Date"]}</td>
      <td>${crime["Call Date"]}</td>
      <td>${crime["Offense Date"]}</td>
      <td>${crime["Call Time"]}</td>
      <td>${crime["Disposition"]}</td>
      <td>${crime["Address"]}</td>
      <td>${crime["City"]}</td>
      <td>${crime["State"]}</td>
      <td>${crime["Address Type"]}</td>
      <td>${crime["Case Status"]}</td>
    `;

    const actionCell = document.createElement("td");
    actionCell.classList.add("action-cell");
    const editButton = document.createElement("button");
    editButton.textContent = "Edit";
    editButton.className = "button";

    const cancelButton = document.createElement("button");
    cancelButton.textContent = "Cancel";
    cancelButton.classList.add("cancel-button", "hidden");

    const editableFields = [
      { column: 2, key: "Original Crime Type Name", type: "text" },
      { column: 3, key: "Report Date", type: "date" },
      { column: 4, key: "Call Date", type: "date" },
      { column: 5, key: "Offense Date", type: "date" },
      { column: 6, key: "Call Time", type: "time" },
      { column: 7, key: "Disposition", type: "text" },
      { column: 8, key: "Address", type: "text" },
      { column: 9, key: "City", type: "text" },
      { column: 10, key: "State", type: "text" },
      { column: 11, key: "Address Type", type: "text" },
      { column: 12, key: "Case Status", type: "text" },
    ];

    let editing = false;
    editButton.addEventListener("click", async () => {
      if (!editing) {
        editableFields.forEach((field) => {
          row.children[field.column].innerHTML =
            `<input type="${field.type}" value="${crime[field.key]}">`;
        });
        editButton.textContent = "Save";
        cancelButton.classList.remove("hidden");

        editing = true;
      } else {
        const updatedCrime = {};

        editableFields.forEach((field) => {
          const input = row.children[field.column].querySelector("input");
          const value = input.value;

          if (value !== crime[field.key]) {
            updatedCrime[field.key] = value;
          }

          crime[field.key] = value;
          row.children[field.column].textContent = value;
        });

        const response = await fetch(
          `http://127.0.0.1:8000/crimes/${crime["Crime Id"]}`,
          {
            method: "PATCH",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify(updatedCrime),
          },
        );

        if (!response.ok) {
          const error = await response.json();
          alert(error.detail);
          return;
        }

        editButton.textContent = "Edit";
        cancelButton.classList.add("hidden");
        editing = false;
      }
    });

    cancelButton.addEventListener("click", () => {
      editableFields.forEach((field) => {
        row.children[field.column].textContent = crime[field.key];
      });
      editButton.textContent = "Edit";
      cancelButton.classList.add("hidden");
      editing = false;
    });

    actionCell.appendChild(cancelButton);
    actionCell.appendChild(editButton);
    row.appendChild(actionCell);

    crimeTable.appendChild(row);
  });
});
