$(document).ready(function() {
    // Xử lý gửi form liên hệ qua Ajax
    $('#contact-form').on('submit', function(e) {
        e.preventDefault();
        $.ajax({
            url: '/contact',
            type: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                alert('Tin nhắn đã được gửi thành công!');
                $('#contact-form')[0].reset();
            },
            error: function() {
                alert('Có lỗi xảy ra. Vui lòng thử lại.');
            }
        });
    });

    // Hiệu ứng scroll cho navbar
    $(window).scroll(function() {
        if ($(this).scrollTop() > 50) {
            $('.navbar').addClass('scrolled');
        } else {
            $('.navbar').removeClass('scrolled');
        }
    });

    // Hiệu ứng cho các nút
    $('.btn').hover(
        function() {
            $(this).css('background', '#2980b9');
        },
        function() {
            $(this).css('background', '#3498db');
        }
    );
});