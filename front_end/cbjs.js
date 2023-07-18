const apiUrl = "https://jks1yxo910.execute-api.us-east-1.amazonaws.com/test-user/index";
const table = document.getElementById('currency-table');
const colors = [
  { background: '#1abc9c', text: '#ffffff' },
  { background: '#3498db', text: '#ffffff' },
  { background: '#9b59b6', text: '#ffffff' },
  { background: '#e74c3c', text: '#ffffff' },
  // Add more color combinations here
];

const hoverColor = { background: '#f1c40f', text: '#ffffff' };

function applyHoverColor(row) {
  row.style.backgroundColor = hoverColor.background;
  row.style.color = hoverColor.text;
}

function removeHoverColor(row, originalColor) {
  row.style.backgroundColor = originalColor.background;
  row.style.color = originalColor.text;
}

axios.get(apiUrl)
.then(response => {
    const currencyData = response.data.rates;
    Object.entries(currencyData).forEach(([currencyName, currency], index) => {
        const row = table.insertRow();
        row.classList.add('currency-row');
        const color = colors[index % colors.length];
        row.style.backgroundColor = color.background;
        row.style.color = color.text;

        row.onmouseenter = () => applyHoverColor(row);
        row.onmouseleave = () => removeHoverColor(row, color);

        row.onclick = () => {
          window.location.href = "./display.html";
          localStorage.setItem("currency", currencyName.toLowerCase());
        };

        const nameCell = row.insertCell(0);
        const priceCell = row.insertCell(1);
        const highCell = row.insertCell(2);
        const lowCell = row.insertCell(3);

        nameCell.innerHTML = currencyName;
        priceCell.innerHTML = parseFloat(currency.rate).toFixed(5);
        highCell.innerHTML = parseFloat(currency.highest).toFixed(5);
        lowCell.innerHTML = parseFloat(currency.lowest).toFixed(5);
    });
})
.catch(error => {
    console.error('Error fetching data:', error);
});



const chatboxBtn = document.getElementById("chatbox-btn");
const chatbox = document.getElementById("chatbox");
const chatboxClose = document.getElementById("chatbox-close");
chatbox.style.display = "none";

chatboxBtn.addEventListener("click", () => {
    chatbox.style.display = "block";
    chatboxBtn.style.display = "none";
});

chatboxClose.addEventListener("click", () => {
chatbox.style.display = "none";
chatboxBtn.style.display = "block";
});

const messagesList = document.querySelector(".messages");
const messageForm = document.querySelector(".message-form");
const messageInput = document.querySelector(".message-input");

const useSampleData = false;

const sampleData = [
"Hi there!",
"How can I help you?",
"That's a great question!",
"Sorry, I don't understand.",
"Have a nice day!"
];

messageForm.addEventListener("submit", async (e) => {
e.preventDefault();
const message = messageInput.value.trim();
if (!message) return;

appendMessage(message, "user");

messageInput.value = "";

let response;
if (useSampleData) {
    response = getRandomResponse(sampleData);
} else {
    try {
        response = await sendMessageToServer(message);
    } catch (error) {
        console.error("Error:", error);
        response = "Error sending message to server.";
    }
}

appendMessage(response, "server");
});

function appendMessage(text, type) {
const li = document.createElement("li");
li.textContent = text;
li.classList.add(type);
messagesList.appendChild(li);
messagesList.scrollTop = messagesList.scrollHeight;
}

function getRandomResponse(responses) {
return responses[Math.floor(Math.random() * responses.length)];
}

async function sendMessageToServer(message) {
const url = `https://jks1yxo910.execute-api.us-east-1.amazonaws.com/demo/chatbot?messages=${encodeURIComponent(message)}`;
const response = await fetch(url, {
method: "POST",
headers: {
"Content-Type": "application/json"
},
});
if (!response.ok) {
    throw new Error("Failed to send message");
}

const data = await response.json();
return data;
}

// Invoke chatbox with welcome message
appendMessage("Hi! How can I help you?", "server");
