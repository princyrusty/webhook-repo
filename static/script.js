async function loadEvents() {
  const res = await fetch("/api/events");
  const data = await res.json();
  const log = document.getElementById("log");
  log.innerHTML = "";

  data.forEach(e => {
    const date = new Date(e.timestamp).toUTCString();
    let text = "";

    if (e.action === "PUSH")
      text = `${e.author} pushed to ${e.to_branch} on ${date}`;
    else if (e.action === "PULL_REQUEST")
      text = `${e.author} submitted a pull request from ${e.from_branch} to ${e.to_branch} on ${date}`;
    else if (e.action === "MERGE")
      text = `${e.author} merged branch ${e.from_branch} to ${e.to_branch} on ${date}`;

    const li = document.createElement("li");
    li.innerText = text;
    log.appendChild(li);
  });
}

loadEvents();
setInterval(loadEvents, 15000);
