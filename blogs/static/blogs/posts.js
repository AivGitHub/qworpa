function setPostLikes(button, hasLiked, likesAmount, likesAmountSpan) {
  (hasLiked === true) ? likesAmount-- : likesAmount++;
  button.toggleClass("btn-dark");
  button.toggleClass("btn-light");
  button.data("has-liked", (hasLiked === true) ? "False" : "True");
  if (likesAmount === 0) {
    likesAmountSpan.toggleClass("d-none");
  } else {
    if (likesAmountSpan.hasClass("d-none")) {
      likesAmountSpan.removeClass("d-none");
    }
  }
  likesAmountSpan.text(likesAmount);
}

$(document).ready(function() {
  $(".delete-post").click(function(e) {
    // TODO: use bootstrap modals.
    if (confirm("Are you sure you want to delete the post?") === false) {
      return;
    }
    let button = $(this);
    let postId = button.data("url-hex");
    $.ajax({
      url: `/api/v1/posts/${postId}/delete/`,
      method: "POST",
      headers: {
        "X-CSRFToken": button.find("input[name='csrfmiddlewaretoken']").val(),
      },
    }).done(function() {
      // TODO: redirect only in case of delete post from /blogs/posts/`${pos_id}`/.
      location.href = "/blogs/im/";
    }).fail(function() {
      alert("Something went wrong! Try again later.");
    });
  });
  $(".post-like-toggler").click(function(e) {
    let button = $(this);
    let hasLiked = (button.data("has-liked") === "True");
    let likesAmount = parseInt($(this).text());
    let likesAmountSpan = button.find(".likes-amount");
    let postId = button.data("url-hex");
    button.prop("disabled", true);
    $.ajax({
      url: `/api/v1/posts/${postId}/likes/toggle/`,
      method: "post",
      headers: {
        "X-CSRFToken": button.find("input[name='csrfmiddlewaretoken']").val(),
      },
    }).done(function() {
      setPostLikes(button, hasLiked, likesAmount, likesAmountSpan);
    }).fail(function() {
      alert("Something went wrong! Try again later.");
    }).always(function() {
      button.prop("disabled", false);
    });
  });
});
