function setCookie(name, value, expireDays) {
  const d = new Date();
  d.setTime(d.getTime() + (expireDays * 24 * 60 * 60 * 1000));
  let expires = "expires="+ d.toUTCString();
  document.cookie = name + "=" + value + ";" + expires + ";path=/;SameSite=Strict";
}

function getCookie(cookieName) {
  let name = cookieName + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(";");
  for(let i = 0; i < ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == " ") {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      return c.substring(name.length, c.length);
    }
  }
  return "";
}

document.addEventListener("DOMContentLoaded", (event) => {
  let cookieName = "koldakov-accepted-cookies";
  if (getCookie(cookieName) === "") {
    $(".cookie-popup").removeClass("d-none").addClass("d-block");
  }

  $(".accept-cookies").on("click", function () {
    setCookie(cookieName, true, 64);
    $(".cookie-popup").removeClass("d-block").addClass("d-none");
  });
});
