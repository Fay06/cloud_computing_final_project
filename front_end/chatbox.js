const messagesList = document.querySelector(".messages");
const messageForm = document.querySelector(".message-form");
const messageInput = document.querySelector(".message-input");

const useSampleData = false; //现在是sample data，如果要用server交互就set = false


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
        method: "POST", // Change this to GET since the URL now contains the message parameter
        headers: {
            "Content-Type": "application/json"
        },
    });

    if (!response.ok) {
        throw new Error("Failed to send message");
    }

    const data = await response.json();
    return data; // Return the content of the response text directly
}

