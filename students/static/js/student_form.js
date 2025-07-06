/* students/static/js/student_form.js
   - Flatpickr + Select2
   - ملخّص حي + شريط اكتمال
   - إدارة المستندات
   - تأكيد الحفظ
-------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", () => {

  /* ========== 1) Flatpickr & Select2 ========== */
  document.querySelectorAll(".flatpickr").forEach(el => el.type = "text");
  if (window.flatpickr) {
    flatpickr(".flatpickr", { dateFormat: "Y-m-d", locale: "ar" });
  }
  if (window.$ && $.fn.select2) {
    $(".select2").select2({ dir: "rtl", width: "100%", language: "ar" });
  }

  /* ========== 2) ملخّص الطالب + تقدّم ========== */
  const summaryBox   = document.getElementById("student-summary");
  const fullNameIds  = ["id_first_name", "id_middle_name", "id_last_name"];
  const requiredIds  = [
    "id_first_name",
    "id_last_name",
    "id_nationality",
    "id_gender",
    "id_passport_number",
  ];

  /* أنشئ شريط التقدّم إذا لم يكن موجودًا */
  let progressBar = document.getElementById("progress-bar");
  if (!progressBar) {
    const barContainer = document.createElement("div");
    barContainer.className = "progress rounded-0";
    barContainer.style.height = "6px";

    progressBar = document.createElement("div");
    progressBar.id = "progress-bar";
    progressBar.className = "progress-bar bg-success";
    progressBar.style.width = "0%";

    barContainer.appendChild(progressBar);
    summaryBox.parentNode.insertBefore(barContainer, summaryBox);
  }

  function updateProgress() {
    const filled = requiredIds.filter(id => {
      const el = document.getElementById(id);
      return el && el.value.trim();
    }).length;
    const percent = Math.round((filled / requiredIds.length) * 100);
    progressBar.style.width = percent + "%";
    progressBar.setAttribute("aria-valuenow", percent);
  }

  function updateSummary() {
    const name = fullNameIds
      .map(id => document.getElementById(id)?.value.trim())
      .filter(Boolean)
      .join(" ");

    const nationality =
      document.getElementById("id_nationality")?.selectedOptions[0]?.text || "—";

    const passport = document.getElementById("id_passport_number")?.value || "—";

    summaryBox.innerHTML = `
      <ul class="list-unstyled mb-0 small">
        <li><strong>الاسم:</strong> ${name || "—"}</li>
        <li><strong>الجنسية:</strong> ${nationality}</li>
        <li><strong>جواز السفر:</strong> ${passport}</li>
      </ul>`;

    updateProgress();
  }

  const form = document.getElementById("student-form");
  if (form) {
    form.addEventListener("input",  updateSummary);
    form.addEventListener("change", updateSummary);
    updateSummary(); // تهيئة أولى
  }

  /* ========== 3) إدارة المستندات الديناميكية ========== */
  const addBtn      = document.getElementById("add-document-btn");
  const container   = document.getElementById("documents-container");
  const totalForms  = document.querySelector("#id_form-TOTAL_FORMS");
  const templateRow = document.getElementById("empty-document-row")?.content;

  addBtn?.addEventListener("click", () => {
    const index = parseInt(totalForms.value, 10);
    const clone = document.importNode(templateRow, true);
    clone.querySelectorAll("[name]").forEach(el => {
      el.name = el.name.replace("__prefix__", index);
      el.id   = el.id.replace("__prefix__", index);
    });
    container.appendChild(clone);
    totalForms.value = index + 1;
  });

  /* حذف مستند */
  container?.addEventListener("click", e => {
    if (e.target.closest(".btn-delete-doc")) {
      e.preventDefault();
      e.target.closest(".document-row").remove();
    }
  });

  /* معاينة صورة */
  container?.addEventListener("change", e => {
    if (e.target.type === "file") {
      const file = e.target.files[0];
      if (file && file.type.startsWith("image/")) {
        const reader = new FileReader();
        reader.onload = () => {
          let preview = e.target.closest(".document-row").querySelector(".img-preview");
          if (!preview) {
            preview = document.createElement("img");
            preview.className = "img-thumbnail img-preview mt-1";
            preview.style.maxWidth = "120px";
            e.target.closest(".document-row").appendChild(preview);
          }
          preview.src = reader.result;
        };
        reader.readAsDataURL(file);
      }
    }
  });

  /* ========== 4) تأكيد الحفظ ========== */
  form?.addEventListener("submit", evt => {
    evt.preventDefault();
    Swal.fire({
      title: "تأكيد الحفظ",
      text: "هل تريد حفظ بيانات الطالب؟",
      icon: "question",
      showCancelButton: true,
      confirmButtonText: "حفظ",
      cancelButtonText: "إلغاء",
    }).then(result => {
      if (result.isConfirmed) form.submit();
    });
  });
});
