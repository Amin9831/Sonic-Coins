function setActive(element) {
    // حذف کلاس active از تمامی گزینه‌ها
    var items = document.querySelectorAll('.menu-item');
    items.forEach(function(item) {
        item.classList.remove('active');
    });

    // افزودن کلاس active به گزینه کلیک شده
    element.classList.add('active');
}
