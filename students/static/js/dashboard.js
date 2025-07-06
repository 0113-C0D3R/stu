document.addEventListener("DOMContentLoaded", function () {

  // 1) استخدم data المضمّنة
  const data = window.initialData;

  // 2) رسم Chart.js كما كان
  const ncCtx = document.getElementById("nationalityChart").getContext("2d");
  const nationalityChart = new Chart(ncCtx, {
    type: "bar",
    data: {
      labels: data.nationalityLabels,
      datasets: [{ data: data.nationalityCounts }],
    },
  });

  const gcCtx = document.getElementById("genderChart").getContext("2d");
  const genderChart = new Chart(gcCtx, {
    type: "doughnut",
    data: {
      labels: ["ذكور", "إناث"],
      datasets: [{ data: [data.male, data.female] }],
    },
  });

  // 3) ربط القائمة المنسدلة
  const yearSelect = document.getElementById("year-select");
  yearSelect.addEventListener("change", () => {
    fetch(`/dashboard-data/?year=${yearSelect.value}`)
      .then((resp) => resp.json())
      .then((d) => {
        nationalityChart.data.labels = d.nationality_labels;
        nationalityChart.data.datasets[0].data = d.nationality_counts;
        nationalityChart.update();

        genderChart.data.datasets[0].data = [d.male, d.female];
        genderChart.update();
      });
  });
});
