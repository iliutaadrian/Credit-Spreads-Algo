function openModal(modalId, tradeId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "block";

    var form = document.getElementById(modalId + "Form");
    var tradeData = getById(tradeId, trades);

    if (modalId == 'createModal'){
        form.ticker.value = tradeData.ticker;
        form.trade_type.value = tradeData.option_type;
        form.sold_strike_price.value = parseInt(tradeData.strike_prices);
        form.credit_to_open.value = parseInt(tradeData.min_credit);
        form.trade_expiration_date.value = formatDate(tradeData.expiration_date);
    }
    else{
        var tradeIdInput = form.querySelector("#tradeId");
        tradeIdInput.value = tradeId;

        form.ticker.value = tradeData.ticker;
        form.ticker.value = tradeData.ticker;
        form.trade_type.value = tradeData.trade_type;
        form.sold_strike_price.value = parseInt(tradeData.sold_strike_price);
        form.position_size.value = parseInt(tradeData.position_size);
        form.credit_to_open.value = parseInt(tradeData.credit_to_open);
        form.commission.value = parseInt(tradeData.commission);
        form.trade_open_date.value = formatDate(tradeData.trade_open_date);
        form.trade_expiration_date.value = formatDate(tradeData.trade_expiration_date);
    }
}

function applyMathExpressionToInput(modalId, inputId) {
    var form = document.getElementById(modalId + "Form");
    var input = form.querySelector('#' + inputId);
    var inputValue = input.value.trim();

    if (inputValue.includes("/") || inputValue.includes("*") || inputValue.includes("+") || inputValue.includes("-")) {
        try {
            var result = parseInt(eval(inputValue));

            if (!isNaN(result)) {
                input.value = result;
            }
        } catch (error) {
            // Handle evaluation error if needed
        }
    }
}

function getById(tradeId, userTrades) {
    for (var i = 0; i < userTrades.length; i++) {
        if (userTrades[i].id === tradeId) {
            return userTrades[i];
        }
    }
    return null;
}

function formatDate(dateText) {
    var date = new Date(dateText);
    var year = date.getFullYear();
    var month = (date.getMonth() + 1).toString().padStart(2, '0');
    var day = date.getDate().toString().padStart(2, '0');
    return `${year}-${month}-${day}`;
}

function closeModal(modalId) {
    var modal = document.getElementById(modalId);
    modal.style.display = "none";
}

window.addEventListener("click", function(event) {
    var modals = document.querySelectorAll(".modal");
    modals.forEach(function(modal) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});