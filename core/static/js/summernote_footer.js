// static/js/summernote_footer_toolbar.js
$(document).ready(function() {
    // Initialize Summernote with a custom callback
    $('.django-summernote').summernote({
        toolbar: [
            ['style', ['bold', 'italic', 'underline', 'clear']],
            ['para', ['ul']],
        ],
        height: 400,
        callbacks: {
            onInit: function() {
                var toolbar = $('.note-toolbar');
                var editor = $('.note-editor');

                // Move toolbar to the bottom
                toolbar.css({
                    'position': 'absolute',
                    'bottom': 0,
                    'width': '100%',
                    'z-index': 10,
                    'background-color': 'white'
                });
                editor.css('padding-bottom', toolbar.outerHeight());
                editor.append(toolbar);
            }
        }
    });
});
