$(() => {
  let date = new Date();
  let time = date.toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "numeric"
  });
  $(".bubble .time").text(time);
});
