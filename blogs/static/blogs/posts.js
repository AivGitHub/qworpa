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
  $(".subscription-toggler").click(function(e) {
    let button = $(this);
    let authorId = button.data("user-id");
    let buttonsToToggle = $(".subscription-toggler").filter(function () {
      return $(this).data("user-id") == authorId;
    });
    let hasSubscribed = button.find(".has-subscribed");
    let hasNotSubscribed = button.find(".has-not-subscribed");
    let subscribersAmount = $(".subscribers-amount").filter(function () {
      return $(this).data("user-id") == authorId;
    });
    buttonsToToggle.prop("disabled", true);
    $.ajax({
      url: "/api/v1/accounts/subscriptions/toggle/",
      method: "post",
      data: {
        "user_id": authorId,
      },
      headers: {
        "X-CSRFToken": button.find("input[name='csrfmiddlewaretoken']").val(),
      },
    }).done(function() {
      let counter = parseInt(subscribersAmount[0].innerText);
      counter = (button.attr("data-has-subscribed") == "True") ? --counter : ++counter;
      if (counter > 0) {
        subscribersAmount.parent().removeClass("d-none");
      }
      if (counter === 0) {
        subscribersAmount.parent().addClass("d-none");
      }
      subscribersAmount.text(counter);
      buttonsToToggle.toggleClass("btn-dark btn-light");
      buttonsToToggle.attr("data-has-subscribed", (button.attr("data-has-subscribed") == "True") ? "False" : "True");
      hasSubscribed.toggleClass("d-none");
      hasNotSubscribed.toggleClass("d-none");
    }).fail(function() {
      alert("Something went wrong! Try again later.");
    }).always(function() {
      setTimeout(function() {
        buttonsToToggle.prop("disabled", false);
      }, 2000);
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
