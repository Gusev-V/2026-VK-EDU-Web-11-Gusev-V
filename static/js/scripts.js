$(document).ready(function() {

    // CSRF
    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!(/^http:.*/.test(settings.url) || /^https:.*/.test(settings.url))) {
                var csrftoken = $('input[name=csrfmiddlewaretoken]').val();
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Like Question
    $('.question-like-btn').click(function() {
        var $btn = $(this);
        var questionId = $btn.data('question-id');
        var action = $btn.hasClass('liked') ? 'dislike' : 'like';

        $.ajax({
            url: '/ajax/like-question/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                question_id: questionId,
                action: action
            }),
            success: function(data) {
                if (data.status === 'ok') {
                    $('#question-likes-' + questionId).text(data.likes_count);

                    if (action === 'like') {
                        $btn.addClass('liked btn-success').removeClass('btn-outline-success');
                    } else {
                        $btn.removeClass('liked btn-success').addClass('btn-outline-success');
                    }
                }
            },
            error: function(xhr) {
                var error = JSON.parse(xhr.responseText).error;
                if (xhr.status === 403) {
                    alert('Please log in to like.');
                } else {
                    alert('Error: ' + error);
                }
            }
        });
    });

    // Like Answer
    $('.answer-like-btn').click(function() {
        var $btn = $(this);
        var answerId = $btn.data('answer-id');
        var action = $btn.hasClass('liked') ? 'dislike' : 'like';

        $.ajax({
            url: '/ajax/like-answer/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                answer_id: answerId,
                action: action
            }),
            success: function(data) {
                if (data.status === 'ok') {
                    $('#answer-likes-' + answerId).text(data.likes_count);

                    if (action === 'like') {
                        $btn.addClass('liked btn-success').removeClass('btn-outline-success');
                    } else {
                        $btn.removeClass('liked btn-success').addClass('btn-outline-success');
                    }
                }
            },
            error: function(xhr) {
                var error = JSON.parse(xhr.responseText).error;
                alert('Error: ' + error);
            }
        });
    });

    // Correct Answer
    $('.mark-correct-btn').click(function() {
        var $checkbox = $(this);
        var answerId = $checkbox.data('answer-id');

        $.ajax({
            url: '/ajax/mark-correct/',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                answer_id: answerId
            }),
            success: function(data) {
                if (data.status === 'ok') {
                    $checkbox.prop('checked', data.is_correct);

                    if (data.is_correct) {
                        $checkbox.closest('.answer').addClass('border-success');
                    } else {
                        $checkbox.closest('.answer').removeClass('border-success');
                    }
                }
            },
            error: function(xhr) {
                var error = JSON.parse(xhr.responseText).error;
                if (xhr.status === 403) {
                    alert('Only the question author can mark correct answers.');
                } else {
                    alert('Error: ' + error);
                }
            }
        });
    });

});