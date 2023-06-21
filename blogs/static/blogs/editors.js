function confirmExit() {
    return "Are you sure you want to close this page?";
}

window.onbeforeunload = confirmExit;

document.addEventListener("DOMContentLoaded", (event) => {
  let idContent = $("#id_content");
  let progressTag = $(".progress");
  progressTag.removeClass("d-none");
  tinymce.init({
    selector: "#id_content",
    plugins: "preview image",
    toolbar: "undo redo | blocks fontfamily fontsize | bold italic underline strikethrough | link image media table mergetags | addcomment showcomments | spellcheckdialog a11ycheck typography | align lineheight | checklist numlist bullist indent outdent | emoticons charmap | removeformat",
    tinycomments_mode: "embedded",
    min_height: 400,
    setup: function(editor) {
      editor.on('init', function(e) {
        progressTag.addClass("d-none");
      });
    }
  });
  $("#submit-button").click(function() {
    window.onbeforeunload = null;
    // Dirty hack
    idContent.text(tinyMCE.activeEditor.getContent());
  });
});