// static/js/main.js

document.addEventListener('DOMContentLoaded', function() {

    // =================================================================
    // الكود الخاص بخطاب "تفويض مندوب استقبال"
    // =================================================================
    const delegateLink = document.querySelector('.reception-delegate-link');
    if (delegateLink) {
        delegateLink.addEventListener('click', function(event) {
            event.preventDefault();
            const baseUrl = this.getAttribute('data-url');

            Swal.fire({
                title: 'تفويض مندوب استقبال',
                html: `
                    <div style="text-align: right;">
                        <p class="text-muted" style="margin-bottom: 1.5rem;">الرجاء إدخال بيانات الوصول لإكمال التفويض.</p>
                        <div style="margin-bottom: 1rem;">
                            <label for="swal-delegate-name" style="display: block; margin-bottom: .5rem; font-weight: 500;">اسم المندوب المفوض</label>
                            <input type="text" id="swal-delegate-name" class="swal2-input" value="الأخ حسن محمد حسين الحامد" required>
                        </div>
                        <div style="margin-bottom: 1rem;">
                            <label for="swal-arrival-date" style="display: block; margin-bottom: .5rem; font-weight: 500;">تاريخ الوصول</label>
                            <input type="text" id="swal-arrival-date" class="swal2-input" placeholder="انقر لاختيار تاريخ..." required>
                        </div>
                    </div>
                `,
                confirmButtonText: 'إنشاء الخطاب',
                showCancelButton: true,
                cancelButtonText: 'إلغاء',
                customClass: { popup: 'swal-full-width-content' },
                didOpen: () => {
                    flatpickr("#swal-arrival-date", { dateFormat: "Y-m-d" });
                },
                preConfirm: () => {
                    const data = {
                        arrivalDate: document.getElementById('swal-arrival-date').value,
                        delegateName: document.getElementById('swal-delegate-name').value
                    };
                    if (!data.arrivalDate || !data.delegateName) {
                        Swal.showValidationMessage('الرجاء إدخال كافة البيانات المطلوبة');
                        return false;
                    }
                    return data;
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    const finalUrl = `${baseUrl}&arrival_date=${result.value.arrivalDate}&delegate_name=${encodeURIComponent(result.value.delegateName)}`;
                    window.open(finalUrl, '_blank');
                }
            });
        });
    }

    // =================================================================
    // الكود الخاص بخطاب "إفادة قبول للدراسة"
    // =================================================================
    const acceptanceLink = document.querySelector('.acceptance-letter-link');
    if (acceptanceLink) {
        acceptanceLink.addEventListener('click', function(event) {
            event.preventDefault();
            const baseUrl = this.getAttribute('data-url');

            Swal.fire({
                title: 'بيانات الجهة المرسل إليها',
                html: `
                    <div style="text-align: right;">
                        <p class="text-muted" style="margin-bottom: 1.5rem;">الرجاء إدخال اسم ووصف الجهة.</p>
                        <div style="margin-bottom: 1rem;">
                            <label for="swal-correspondent-name" style="display: block; margin-bottom: .5rem; font-weight: 500;">اسم الجهة / الشخص</label>
                            <input type="text" id="swal-correspondent-name" class="swal2-input" placeholder="مثال: مصطفى صادق الجنيد">
                        </div>
                        <div>
                            <label for="swal-correspondent-title" style="display: block; margin-bottom: .5rem; font-weight: 500;">الوصف / المنصب</label>
                            <input type="text" id="swal-correspondent-title" class="swal2-input" placeholder="مثال: المدير التنفيذي لمعهد..">
                        </div>
                    </div>
                `,
                confirmButtonText: 'إنشاء الخطاب',
                showCancelButton: true,
                cancelButtonText: 'إلغاء',
                customClass: { popup: 'swal-full-width-content' },
                preConfirm: () => {
                    const name = document.getElementById('swal-correspondent-name').value;
                    const title = document.getElementById('swal-correspondent-title').value;
                    if (!name || !title) {
                        Swal.showValidationMessage('الرجاء إدخال كافة البيانات');
                        return false;
                    }
                    return { name: name, title: title };
                }
            }).then((result) => {
                if (result.isConfirmed) {
                    const finalUrl = `${baseUrl}&correspondent_name=${encodeURIComponent(result.value.name)}&correspondent_title=${encodeURIComponent(result.value.title)}`;
                    window.open(finalUrl, '_blank');
                }
            });
        });
    }


    
});