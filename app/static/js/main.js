document.addEventListener('DOMContentLoaded', function () {
    // Hamburger Menu Toggle
    const hamburger = document.querySelector('#hamburger');
    const navLinks = document.querySelector('#navLinks');
    const userMenu = document.querySelector('#userMenu');

    function toggleMenu() {
        navLinks.classList.toggle('active');
        hamburger.textContent = navLinks.classList.contains('active') ? '✕' : '☰';
    }

    if (hamburger && navLinks) {
        hamburger.addEventListener('click', toggleMenu);
    }

    // Gộp user menu vào nav-links trên tablet/mobile
    function updateMenu() {
        const isTabletOrMobile = window.innerWidth < 992;
        const existingUserItems = navLinks.querySelectorAll('.user-menu-item');
        existingUserItems.forEach(item => item.remove());

        if (isTabletOrMobile && userMenu && navLinks) {
            // Thêm các mục từ user menu
            const userItems = userMenu.querySelectorAll('a');
            userItems.forEach(item => {
                const clone = item.cloneNode(true);
                clone.classList.add('user-menu-item');
                if (clone.classList.contains('dark-mode-option')) {
                    clone.addEventListener('click', (e) => {
                        e.preventDefault();
                        toggleDarkMode();
                    });
                }
                navLinks.appendChild(clone);
            });

            // Ẩn các mục không yêu cầu
            const allLinks = navLinks.querySelectorAll('a');
            allLinks.forEach(link => {
                const text = link.textContent.trim();
                const allowedItems = ['Trang Chủ', 'Giới Thiệu', 'Blog', 'Bảng Giá', 'Liên Hệ', 'Thông tin cá nhân', 'Đổi mật khẩu', 'Chuyển chế độ tối', 'Đăng Xuất'];
                if (!allowedItems.includes(text)) {
                    link.style.display = 'none';
                } else {
                    link.style.display = 'block';
                }
            });
        } else {
            // Khôi phục hiển thị tất cả mục trên desktop
            const allLinks = navLinks.querySelectorAll('a');
            allLinks.forEach(link => {
                link.style.display = 'block';
            });
        }
    }

    updateMenu();
    window.addEventListener('resize', updateMenu);

    // Dark Mode Toggle
    const darkModeToggle = document.querySelector('.dark-mode-toggle');
    const darkModeOption = document.querySelector('.dark-mode-option');

    function toggleDarkMode() {
        document.documentElement.classList.toggle('dark-mode');
        const isDarkMode = document.documentElement.classList.contains('dark-mode');
        localStorage.setItem('darkMode', isDarkMode);
        if (darkModeToggle) {
            darkModeToggle.textContent = isDarkMode ? '☀️' : '🌙';
        }
        const darkModeOptions = document.querySelectorAll('.dark-mode-option');
        darkModeOptions.forEach(option => {
            option.textContent = isDarkMode ? 'Chuyển chế độ sáng' : 'Chuyển chế độ tối';
        });
    }

    if (darkModeToggle) {
        darkModeToggle.addEventListener('click', toggleDarkMode);
    }

    if (darkModeOption) {
        darkModeOption.addEventListener('click', (e) => {
            e.preventDefault();
            toggleDarkMode();
        });
    }

    // Check for saved dark mode preference
    if (localStorage.getItem('darkMode') === 'true') {
        document.documentElement.classList.add('dark-mode');
        if (darkModeToggle) darkModeToggle.textContent = '☀️';
        const darkModeOptions = document.querySelectorAll('.dark-mode-option');
        darkModeOptions.forEach(option => {
            option.textContent = 'Chuyển chế độ sáng';
        });
    }

    // Toast Notifications
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach(toast => {
        toast.classList.add('show');
        const closeBtn = toast.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                toast.classList.remove('show');
            });
        }
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
    });

    // Contact Form Ajax
    const contactForm = document.querySelector('#contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function (e) {
            e.preventDefault();
            fetch('/contact', {
                method: 'POST',
                body: new FormData(this),
                headers: { 'X-Requested-With': 'XMLHttpRequest' }
            })
            .then(response => response.json())
            .then(data => {
                alert('Tin nhắn đã được gửi thành công!');
                contactForm.reset();
            })
            .catch(() => {
                alert('Có lỗi xảy ra. Vui lòng thử lại.');
            });
        });
    }

    // Navbar Scroll Effect
    window.addEventListener('scroll', () => {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    // Slider Functionality
    const slides = document.querySelectorAll('.slider-slide');
    const thumbnails = document.querySelectorAll('.thumbnail-slide');
    const prevButton = document.querySelector('.nav-arrow.prev');
    const nextButton = document.querySelector('.nav-arrow.next');
    let currentIndex = 0;

    function showSlide(index) {
        slides.forEach((slide, i) => {
            slide.classList.toggle('active', i === index);
        });
        thumbnails.forEach((thumb, i) => {
            thumb.classList.toggle('active', i === index);
        });
        currentIndex = index;
    }

    if (prevButton && nextButton) {
        prevButton.addEventListener('click', () => {
            let newIndex = (currentIndex - 1 + slides.length) % slides.length;
            showSlide(newIndex);
        });

        nextButton.addEventListener('click', () => {
            let newIndex = (currentIndex + 1) % slides.length;
            showSlide(newIndex);
        });

        thumbnails.forEach((thumb, i) => {
            thumb.addEventListener('click', () => {
                showSlide(i);
            });
        });

        // Auto-slide every 5 seconds
        setInterval(() => {
            let newIndex = (currentIndex + 1) % slides.length;
            showSlide(newIndex);
        }, 5000);
    }
});