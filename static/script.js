// ==========================
// HANGMAN PRO MAX
// Advanced JavaScript
// ==========================

let timer = 60;
let timerInterval;

let currentStreak = 0;
let bestStreak = 0;

let achievements = [];

// ==========================
// TIMER
// ==========================

function startTimer() {

    clearInterval(timerInterval);

    timer = 60;

    updateTimer();

    timerInterval = setInterval(() => {

        timer--;

        updateTimer();

        if (timer <= 0) {

            clearInterval(timerInterval);

            showPopup(
                "⏰ Time Up!"
            );

            setTimeout(() => {

                location.reload();

            }, 2000);
        }

    }, 1000);
}

function updateTimer() {

    let timerElement =
        document.getElementById(
            "timer"
        );

    if (timerElement) {

        timerElement.innerHTML =
            "⏱ " + timer + "s";

    }
}

// ==========================
// LOAD GAME STATE
// ==========================

async function loadGame() {

    const response =
        await fetch("/state");

    const data =
        await response.json();

    document.getElementById(
        "category"
    ).innerHTML =
        "📂 " + data.category;

    document.getElementById(
        "score"
    ).innerHTML =
        "⭐ Score: " +
        data.score;

    document.getElementById(
        "lives"
    ).innerHTML =
        "❤️ Lives: " +
        (
            data.max_wrong -
            data.wrong
        );

    document.getElementById(
        "word"
    ).innerHTML =
        data.revealed.join(" ");

    document.getElementById(
        "hint"
    ).innerHTML =
        data.hint;

    updateHangman(
        data.wrong
    );

    if (data.game_over) {

        clearInterval(
            timerInterval
        );

        if (data.won) {

            currentStreak++;

            if (
                currentStreak >
                bestStreak
            ) {
                bestStreak =
                    currentStreak;
            }

            unlockAchievement(
                "🏆 Winner"
            );

            if (
                currentStreak === 5
            ) {
                unlockAchievement(
                    "🔥 5 Win Streak"
                );
            }

            showPopup(
                "🎉 YOU WON!"
            );

        } else {

            currentStreak = 0;

            showPopup(
                "💀 GAME OVER"
            );
        }
    }
}

// ==========================
// GUESS LETTER
// ==========================

async function guessLetter() {

    const input =
        document.getElementById(
            "letter"
        );

    const letter =
        input.value.trim();

    if (!letter) {

        showPopup(
            "⚠ Enter a letter"
        );

        return;
    }

    await fetch("/guess", {

        method: "POST",

        headers: {
            "Content-Type":
                "application/json"
        },

        body: JSON.stringify({

            letter: letter

        })

    });

    input.value = "";

    loadGame();
}

// ==========================
// HINT
// ==========================

async function useHint() {

    await fetch("/hint", {

        method: "POST"

    });

    showPopup(
        "💡 Hint Used"
    );

    loadGame();
}

// ==========================
// NEW GAME
// ==========================

async function newGame() {

    await fetch(
        "/new_game"
    );

    startTimer();

    loadGame();

    showPopup(
        "🚀 New Game Started"
    );
}

// ==========================
// HANGMAN FACE
// ==========================

function updateHangman(
    wrong
) {

    const hangman =
        document.getElementById(
            "hangman"
        );

    const faces = [

        "😎",
        "🙂",
        "😐",
        "😟",
        "😢",
        "😭",
        "💀"
    ];

    if (
        hangman &&
        wrong <
        faces.length
    ) {

        hangman.innerHTML =
            faces[wrong];
    }
}

// ==========================
// ACHIEVEMENTS
// ==========================

function unlockAchievement(
    name
) {

    if (
        achievements.includes(
            name
        )
    ) return;

    achievements.push(
        name
    );

    showPopup(
        "Achievement Unlocked:<br>" +
        name
    );
}

// ==========================
// POPUP
// ==========================

function showPopup(
    message
) {

    let popup =
        document.createElement(
            "div"
        );

    popup.className =
        "popup";

    popup.innerHTML =
        message;

    document.body.appendChild(
        popup
    );

    setTimeout(() => {

        popup.remove();

    }, 3000);
}

// ==========================
// DARK MODE
// ==========================

function toggleTheme() {

    document.body.classList.toggle(
        "light-mode"
    );

    localStorage.setItem(

        "theme",

        document.body.classList.contains(
            "light-mode"
        )
            ? "light"
            : "dark"
    );
}

function loadTheme() {

    const savedTheme =
        localStorage.getItem(
            "theme"
        );

    if (
        savedTheme ===
        "light"
    ) {

        document.body.classList.add(
            "light-mode"
        );
    }
}

// ==========================
// STATS
// ==========================

async function updateStats() {

    try {

        const response =
            await fetch(
                "/stats"
            );

        const data =
            await response.json();

        const statsBox =
            document.getElementById(
                "stats"
            );

        if (
            statsBox
        ) {

            statsBox.innerHTML = `
            <p>🎮 Games: ${data.games_played}</p>
            <p>🏆 Wins: ${data.games_won}</p>
            <p>⭐ Score: ${data.score}</p>
            <p>🔥 Streak: ${currentStreak}</p>
            `;
        }

    } catch (error) {

        console.log(
            error
        );
    }
}

// ==========================
// KEYBOARD SUPPORT
// ==========================

document.addEventListener(
    "keydown",

    function(event) {

        if (
            event.key ===
            "Enter"
        ) {

            guessLetter();
        }

    }
);

// ==========================
// START
// ==========================

window.onload =
function() {

    loadTheme();

    startTimer();

    loadGame();

    updateStats();

    setInterval(

        updateStats,

        5000

    );
};
