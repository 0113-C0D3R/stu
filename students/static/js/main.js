// في ملف main.js أو داخل <script> في student_detail.html

document.addEventListener('DOMContentLoaded', function() {
    const delegateLink = document.querySelector('.reception-delegate-link');

    if (delegateLink) {
        delegateLink.addEventListener('click', function(event) {
            event.preventDefault(); // امنع الرابط من الانتقال
            const baseUrl = this.getAttribute('data-url');

            // استخدم SweetAlert2 لإنشاء نافذة منبثقة احترافية
            Swal.fire({
                title: 'تفويض مندوب استقبال',
                // هذا هو الهيكل الجديد للنافذة
                html: `
                    <div style="text-align: right;">
                        <p class="text-muted" style="margin-bottom: 1.5rem;">الرجاء إدخال بيانات الوصول لإكمال التفويض.</p>
                        
                        <div style="margin-bottom: 1rem;">
                            <label for="swal-delegate-name" style="display: block; margin-bottom: .3rem; font-weight: bold;">اسم المندوب المفوض</label>
                            <input type="text" id="swal-delegate-name" class="swal2-input" value="حسن محمد حسين الحامد">
                        </div>

                        <div>
                            <label for="swal-arrival-date" style="display: block; margin-bottom: .3rem; font-weight: bold;">تاريخ الوصول</label>
                            <input type="text" id="swal-arrival-date" class="swal2-input" placeholder="اختر تاريخًا...">
                        </div>
                    </div>
                `,
                confirmButtonText: 'إنشاء الخطاب',
                showCancelButton: true,
                cancelButtonText: 'إلغاء',
                
                // هذا الكود يتم تشغيله بعد فتح النافذة مباشرة
                didOpen: () => {
                    // قم بتهيئة Flatpickr على حقل التاريخ الجديد
                    flatpickr("#swal-arrival-date", {
                        // لا نستخدم inline: true الآن، ليظهر كقائمة منسدلة
                        defaultDate: "today",
                        dateFormat: "Y-m-d", // الصيغة التي سترسل للخادم
                    });
                },

                // هذا الكود يتم تشغيله قبل تأكيد الإرسال للتحقق من البيانات
                preConfirm: () => {
                    const arrivalDate = document.getElementById('swal-arrival-date').value;
                    const delegateName = document.getElementById('swal-delegate-name').value;

                    if (!arrivalDate || !delegateName) {
                        Swal.showValidationMessage('الرجاء إدخال كافة البيانات المطلوبة');
                        return false; // يمنع إغلاق النافذة
                    }
                    return { 
                        arrivalDate: arrivalDate,
                        delegateName: delegateName 
                    };
                }

            }).then((result) => {
                // بعد أن يضغط المستخدم على "إنشاء الخطاب"
                if (result.isConfirmed) {
                    const finalUrl = `${baseUrl}&arrival_date=${result.value.arrivalDate}&delegate_name=${encodeURIComponent(result.value.delegateName)}`;
                    window.open(finalUrl, '_blank');
                }
            });
        });
    }
});