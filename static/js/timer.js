const timerText = document.getElementById("timer-text");

const interviewStartedAt = Number(timerText.dataset.startedAt) * 1000;

function updateTimer() {
    const elapsedSeconds = Math.floor (
        (Date.now() - interviewStartedAt) / 1000
    );

    const minutes = Math.floor(elapsedSeconds / 60);
    const seconds = elapsedSeconds % 60;

    timerText.textContent = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
}

updateTimer();
setInterval(updateTimer, 1000);