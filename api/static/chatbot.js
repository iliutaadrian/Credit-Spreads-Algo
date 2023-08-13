document.addEventListener("DOMContentLoaded", function () {
    const chatMessages = document.querySelector(".chat-messages");
    const sendMessageButton = document.getElementById("sendMessage");
    const chatInput = document.getElementById("chatInput");

    // // Load chat history from local storage
    const chatHistory = JSON.parse(localStorage.getItem("chat_history")) || [];
    // Display chat history messages on page load
    for (const [bot, user] of chatHistory) {
        messageElement = createMessageElement(bot, "user");
        chatMessages.appendChild(messageElement);
        messageElement = createMessageElement(user, "bot");
        chatMessages.appendChild(messageElement);
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;

    sendMessageButton.addEventListener("click", sendMessage);
    chatInput.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            sendMessage();
        }
    });

    function sendMessage() {
        const userMessage = chatInput.value;
        if (userMessage.trim() !== "") {
            addUserMessage(userMessage);
            simulateBotResponse(userMessage);
            chatInput.value = "";
        }
    }

    // Function to add a user message to the chat area
    function addUserMessage(message) {
        const userMessageElement = createMessageElement(message, "user");
        chatMessages.appendChild(userMessageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Function to create a message element
    function createMessageElement(message, sender) {
        const messageElement = document.createElement("div");
        messageElement.classList.add("message");
        messageElement.classList.add(sender);
        messageElement.innerHTML = `
            <div class="avatar">
                <img src="static/${sender}.png" alt="${sender} Avatar">
            </div>
            <p class="message-text">${message}</p>
        `;
        return messageElement;
    }

    // Function to simulate bot response
    function simulateBotResponse(userMessage) {
        const apiUrl = "/chatbot"; // Update this URL to match your Flask app's API endpoint
        const requestData = {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ userMessage, chatHistory }) // Pass the user's message in the request body
        };

        const pendingMessage = "Pending..."; // Message to show while waiting for the response
        const pendingMessageElement = createMessageElement(pendingMessage, "bot");
        chatMessages.appendChild(pendingMessageElement);
        chatMessages.scrollTop = chatMessages.scrollHeight;

        sendMessageButton.disabled = true;

        // Make the API request
        fetch(apiUrl, requestData)
            .then(response => response.json())
            .then(data => {
                const botResponse = data.botResponse; // Assuming the response from the API has a field "botResponse"
                const botMessageElement = createMessageElement(botResponse, "bot");
                chatMessages.removeChild(pendingMessageElement); // Remove the pending message
                chatMessages.appendChild(botMessageElement);
                chatMessages.scrollTop = chatMessages.scrollHeight;

                chatHistory.push([userMessage, botResponse]);
                localStorage.setItem("chat_history", JSON.stringify(chatHistory));
                sendMessageButton.disabled = false;
            })
            .catch(error => {
                sendMessageButton.disabled = false;
                console.error("Error fetching bot response:", error);
            });
    }
});