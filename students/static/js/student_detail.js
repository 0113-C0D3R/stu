document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('performActionBtn').addEventListener('click', performAction);
});

function performAction() {
    const selectedAction = document.getElementById('actionDropdown').value;
    const studentId = document.getElementById('studentId').value;

    if (!selectedAction) {
        alert('الرجاء اختيار إجراء.');
        return;
    }

    let url;
    switch (selectedAction) {
        case 'passports':
            url = `/student/${studentId}/to_passports/`;
            break;
        case 'security':
            url = `/student/${studentId}/to_security/`;
            break;
        case 'students_affairs':
            url = `/student/${studentId}/to_students_affairs/`;
            break;
        default:
            alert('إجراء غير معروف.');
            return;
    }

    // توجيه المستخدم إلى الرابط المحدد
    window.location.href = url;
}