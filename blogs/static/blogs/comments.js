/**
 *
 * This file is created to create/read/update/delete comments for blog posts.
 * For now application is a monolith, but some parts of the code use API, it is done
 * in case of moving to ReactJS.
 *
 * Some parts of the code could be improved, such as bulk insert comments, not 1 by 1.
 * Or insert and load comment 1 by 1. Not sure what is the best approach, but any MR's are appreciated.
 *
 * @summary Simple comment system.
 * @link    https://github.com/AivGitHub/qworpa/blob/master/blogs/static/blogs/comments.js
 * @author  Ivan Koldakov <coldie322@gmail.com>
 *
 * Created at: 2023-05-29
 */

"use strict";

function getQueryVars(fullUrl) {
  let vars = [], hash;
  let hashes = fullUrl.slice(fullUrl.indexOf("?") + 1).split("&");
  for(let i = 0; i < hashes.length; i++) {
    hash = hashes[i].split("=");
    vars.push(hash[0]);
    vars[hash[0]] = hash[1];
  }
  return vars;
}

function setCommentLikes(button, hasLiked, likesAmount, likesAmountSpan) {
  let buttonI = button.find("i.bi");
  buttonI.removeClass("bi-hand-thumbs-up");
  buttonI.removeClass("bi-hand-thumbs-up-fill");
  button.attr("data-has-liked", (hasLiked === true) ? "True" : "False");
  if (hasLiked === true) {
    buttonI.addClass("bi-hand-thumbs-up-fill");
  } else {
    buttonI.addClass("bi-hand-thumbs-up");
  }
  if (likesAmount === 0) {
    likesAmountSpan.addClass("d-none");
  } else {
    likesAmountSpan.removeClass("d-none");
  }
  likesAmountSpan.text(likesAmount);
}

function toggleCommentLike() {
  let button = $(this);
  let inputHelpers = $(".input-helpers");
  let csrf = inputHelpers.find("input[name='csrfmiddlewaretoken']").val();
  let postId = inputHelpers.find("input[name='postId']").val();
  let hasLiked = button.attr("data-has-liked") === "True";
  let likesAmountSpan = button.find(".comment-likes-amount");
  let likesAmount = parseInt($(likesAmountSpan).text());
  let commentId = button.data("comment-id");
  let buttonI = button.find("i.bi");
  button.prop("disabled", true);
  $.ajax({
    url: `/api/v1/posts/${postId}/comments/${commentId}/likes/toggle/`,
    method: "post",
    headers: {
      "X-CSRFToken": csrf,
    },
  }).done(function() {
    buttonI.toggleClass("bi-hand-thumbs-up");
    buttonI.toggleClass("bi-hand-thumbs-up-fill");
    button.attr("data-has-liked", (hasLiked === true) ? "False" : "True");
    if (hasLiked) {
      likesAmount--;
    } else {
      likesAmount++;
    }
    likesAmountSpan.text(likesAmount);
    if (likesAmount === 0) {
      likesAmountSpan.addClass("d-none");
    } else {
      likesAmountSpan.removeClass("d-none");
    }
  }).fail(function() {
    alert("Something went wrong! Try again later.");
  }).always(function() {
    button.prop("disabled", false);
  });
}

function deleteCommentLike(e) {
  if (confirm("Are you sure you want to delete the comment?") === false) {
    return;
  }
  let inputHelpers = $(".input-helpers");
  let csrf = inputHelpers.find("input[name='csrfmiddlewaretoken']").val();
  let postId = inputHelpers.find("input[name='postId']").val();
  let commentDiv = $(e.target).parent().closest(".comment");
  let commentId = commentDiv.data("comment-id");

  $.ajax({
    url: `/api/v1/posts/${postId}/comments/${commentId}/delete/`,
    method: "post",
    headers: {
      "X-CSRFToken": csrf,
    },
  }).done(function(comments) {
    commentDiv.remove();
  }).fail(function() {
    alert("Something went wrong! Try again later.");
  });
  e.preventDefault();
}

function populateComment(comment, parentComment, newComment) {
  if (comment.parent !== null) {
    // TODO: Update the code, remove parentComment.
    return;
  }
  let commentClone = $(".comment-snippet").clone();
  let commentLikeTogglerButton = commentClone.find(".comment-like-toggler")
  let likesAmountSpan = commentClone.find(".comment-likes-amount");
  let likesAmount = parseInt(comment.likes_amount);
  commentClone.attr("id", `comment-${comment.id}`)
  commentClone.removeClass("d-none");
  commentClone.removeClass("comment-snippet");
  commentClone.find(".comment-author-full-name").text(comment.author.full_name);
  commentClone.find(".comment-created-at").text(comment.created_at);
  commentClone.find(".comment-content").text(comment.content);
  commentLikeTogglerButton[0].addEventListener("click", toggleCommentLike);
  commentClone.find(".delete-comment")[0].addEventListener("click", deleteCommentLike);
  if (comment.has_add_permission == false) {
    commentLikeTogglerButton.prop("disabled", true);
  }
  if (comment.has_delete_permission == true) {
    commentClone.find(".comment-header-helpers").removeClass("d-none");
  }
  setCommentLikes(commentLikeTogglerButton, comment.has_liked, likesAmount, likesAmountSpan);
  commentLikeTogglerButton.attr("data-comment-id", comment.id);
  commentClone.attr("data-comment-id", comment.id);
  if (parentComment === null) {
    if (newComment === null) {
      $(".post-comment-list").append(commentClone);
    } else {
      $(".post-comment-list").prepend(commentClone);
    }
  } else {
    if (newComment === null) {
      parentComment.append(commentClone);
    } else {
      parentComment.prepend(commentClone);
    }
  }
}

function setComment(textArea, comment) {
  textArea.val("");
  let totalCommentsAmountSpan = $("#total-comments-amount");
  let totalCommentsAmount = parseInt(totalCommentsAmountSpan.text()) + 1;
  totalCommentsAmountSpan.text(totalCommentsAmount);
  populateComment(comment, null, true);
}

function loadInitialComments(postId, csrf) {
  let postCommentBlock = $("#post-comment-block");
  let postCommentsLoader = postCommentBlock.find(".post-comments-loader");
  let loadMoreButton = postCommentsLoader.find(".load-more-button");

  $.ajax({
    url: `/api/v1/posts/${postId}/comments/`,
    method: "get",
    headers: {
      "X-CSRFToken": csrf,
    },
  }).done(function(comments) {
    if (comments.next !== null) {
      let queryArgs = getQueryVars(comments.next);
      postCommentsLoader.removeClass("d-none");
      loadMoreButton.attr("data-next-page", queryArgs["p"]);
    }
    for (let i=0;i<comments.results.length;i++) {
      populateComment(comments.results[i], null, null);
    }
    $(".comments-progress").addClass("d-none");
  }).fail(function() {
    alert("Something went wrong! Try again later.");
  });
}

function loadMoreComments(postId, csrf) {
  $(".comments-progress").removeClass("d-none");
  let postCommentBlock = $("#post-comment-block");
  let postCommentsLoader = postCommentBlock.find(".post-comments-loader");
  let loadMoreButton = postCommentsLoader.find(".load-more-button");
  let pageNumber = loadMoreButton.attr("data-next-page");
  loadMoreButton.prop("disabled", true);
  $.ajax({
    url: `/api/v1/posts/${postId}/comments/?p=${pageNumber}`,
    method: "get",
    headers: {
      "X-CSRFToken": csrf,
    },
  }).done(function(comments) {
    $(".comments-progress").addClass("d-none");
    loadMoreButton.prop("disabled", false);
    if (comments.next !== null) {
      let queryArgs = getQueryVars(comments.next);
      postCommentsLoader.removeClass("d-none");
      loadMoreButton.attr("data-next-page", queryArgs["p"]);
    } else {
      postCommentsLoader.addClass("d-none");
    }
    for (let i=0;i<comments.results.length;i++) {
      populateComment(comments.results[i], null, null);
    }
    $(".comments-progress").addClass("d-none");
    $('html, body').animate({ scrollTop: $(`#comment-${comments.results[0].id}`).offset().top}, 500);
  }).fail(function() {
    alert("Something went wrong! Try again later.");
  });
}

document.addEventListener("DOMContentLoaded", function(){
  let inputHelpers = $(".input-helpers");
  let csrf = inputHelpers.find("input[name='csrfmiddlewaretoken']").val();
  let postId = inputHelpers.find("input[name='postId']").val();
  loadInitialComments(postId, csrf);
  $(".load-more-button").click(function(e) {
    loadMoreComments(postId, csrf);
  });
  $(".comment-form").submit(function(e) {
    let form = $(this);
    let textArea = form.find("textarea");
    form.prop("disabled", true);
    $.ajax({
      url: `/api/v1/posts/${postId}/comments/add/`,
      method: "post",
      data: {
        "content": textArea.val(),
      },
      headers: {
        "X-CSRFToken": csrf,
      },
    }).done(function(comment) {
      setComment(textArea, comment);
      $('html, body').animate({ scrollTop: $(`#comment-${comment.id}`).offset().top}, 500);
    }).fail(function() {
      alert("Something went wrong! Try again later.");
    }).always(function() {
      form.prop("disabled", false);
    });
    e.preventDefault();
  });
});
