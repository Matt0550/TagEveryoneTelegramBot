$(document).ready(function () {
    console.log("ready!");
    console.log(window.Telegram);
});

$("#test").click(function () {
    window.Telegram.WebApp.sendData("test");
});