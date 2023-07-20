document.addEventListener("DOMContentLoaded", (event) => {
  let inputHelpers = $(".input-helpers");
  let csrf = inputHelpers.find("input[name='csrfmiddlewaretoken']").val();

  $("#change-password-form").submit(function(e) {
    e.preventDefault();
    let form = $(this);
    let formInputs = form.find("input");
    let passwordHelpMessages = $("#change-password-form-help-messages");
    let passwordSuccessHelpMessage = passwordHelpMessages.find(".password-success");
    let passwordErrorHelpMessage = passwordHelpMessages.find(".password-error");
    form.prop("disabled", true);
    formInputs.find("input").prop("disabled", true);
    $.ajax({
      url: "/api/v1/accounts/settings/passwords/change/",
      dataType: "json",
      method: "post",
      data: {
        old_password: form.find("input[name=old_password]").val(),
        new_password1: form.find("input[name=new_password1]").val(),
        new_password2: form.find("input[name=new_password2]").val()
      },
      headers: {
        "X-CSRFToken": csrf,
      },
    }).done(function(data, textStatus, jqXHR) {
      passwordSuccessHelpMessage.removeClass("d-none");
      passwordErrorHelpMessage.addClass("d-none");
    }).fail(function(xhr, status, err) {
      passwordErrorHelpMessage.text("");
      passwordSuccessHelpMessage.addClass("d-none");
      if (xhr.status !== 400) {
        console.log(xhr.status);
        console.log(xhr);
        alert("Something went wrong! Try again later.");
        return;
      }
      if (xhr.responseJSON.old_password !== undefined) {
        passwordErrorHelpMessage.text(xhr.responseJSON.old_password);
      } else if (xhr.responseJSON.non_field_errors !== undefined) {
        let li = "";
        $.each(xhr.responseJSON.non_field_errors, function(i) {
          li += "<li>" + xhr.responseJSON.non_field_errors[i] + "</li>";
        });
        passwordErrorHelpMessage.append("<ul>" + li + "</ul>");
      }
      passwordErrorHelpMessage.removeClass("d-none");
    }).always(function() {
      form.prop("disabled", false);
      formInputs.prop("disabled", false);
      formInputs.val('');
    });
    e.preventDefault();
  });
});
