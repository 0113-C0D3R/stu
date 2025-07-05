document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.flatpickr').forEach(el => el.type = 'text'); 
  /* Flatpickr – تقويم عربي */
  if (window.flatpickr) {
    flatpickr('.flatpickr', { dateFormat: 'Y-m-d', locale: 'ar' });
  }

  /* Select2 للحقول القابلة للبحث (مثلاً الجنسية) */
  if (window.$ && $.fn.select2) {
    $('.select2').select2({ dir: 'rtl', width: '100%', language: 'ar' });
  }

  /* === ملخص الطالب الحيّ === */
  const summaryBox = document.getElementById('student-summary');
  const updateSummary = () => {
    const fullName = ['id_first_name', 'id_middle_name', 'id_last_name']
      .map(id => document.getElementById(id)?.value.trim())
      .filter(Boolean).join(' ');
    const nationality = document.getElementById('id_nationality')?.selectedOptions[0]?.text || '—';
    const passport = document.getElementById('id_passport_no')?.value || '—';

    summaryBox.innerHTML = `
      <ul class=\"list-unstyled mb-0\">
        <li><strong>الاسم:</strong> ${fullName || '—'}</li>
        <li><strong>الجنسية:</strong> ${nationality}</li>
        <li><strong>جواز السفر:</strong> ${passport}</li>
      </ul>`;
  };
  ['input', 'change'].forEach(evt =>
    document.getElementById('student-form').addEventListener(evt, updateSummary)
  );
  updateSummary();

  /* === إدارة المستندات الديناميكية === */
  const addBtn      = document.getElementById('add-document-btn');
  const container   = document.getElementById('documents-container');
  const totalForms  = document.querySelector('#id_form-TOTAL_FORMS');
  const templateRow = document.getElementById('empty-document-row').content;

  addBtn?.addEventListener('click', () => {
    const index = parseInt(totalForms.value, 10);
    const clone = document.importNode(templateRow, true);
    clone.querySelectorAll('[name]').forEach(el => {
      el.name = el.name.replace('__prefix__', index);
      el.id   = el.id.replace('__prefix__', index);
    });
    container.appendChild(clone);
    totalForms.value = index + 1;
  });

  /* زر حذف مستند جديد */
  container?.addEventListener('click', e => {
    if (e.target.closest('.btn-delete-doc')) {
      e.preventDefault();
      e.target.closest('.document-row').remove();
    }
  });

  /* معاينة الملف إذا كان صورة */
  container?.addEventListener('change', e => {
    if (e.target.type === 'file') {
      const file = e.target.files[0];
      if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = () => {
          let preview = e.target.closest('.document-row').querySelector('.img-preview');
          if (!preview) {
            preview = document.createElement('img');
            preview.className = 'img-thumbnail img-preview mt-1';
            preview.style.maxWidth = '120px';
            e.target.closest('.document-row').appendChild(preview);
          }
          preview.src = reader.result;
        };
        reader.readAsDataURL(file);
      }
    }
  });

  /* SweetAlert2 عند الحفظ */
  const form = document.getElementById('student-form');
  form?.addEventListener('submit', evt => {
    evt.preventDefault();
    Swal.fire({
      title: 'تأكيد الحفظ',
      text: 'هل تريد حفظ بيانات الطالب؟',
      icon: 'question',
      showCancelButton: true,
      confirmButtonText: 'حفظ',
      cancelButtonText: 'إلغاء'
    }).then(result => {
      if (result.isConfirmed) form.submit();
    });
  });
});
