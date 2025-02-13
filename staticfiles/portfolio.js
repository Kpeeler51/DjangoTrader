// Function handles form submissions for buy/sell actions.
function handleFormSubmit(event) {
    event.preventDefault();
    const form = event.target;
    const formData = new FormData(form);

    // Convert symbol to uppercase to prevent case sensitivity.
    const symbolInput = formData.get('symbol');
    if (symbolInput) {
        formData.set('symbol', symbolInput.toUpperCase());
    }

    // send form data to server using fetch API.
    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': formData.get('csrfmiddlewaretoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update portfolio data.
            const portfolio = data.portfolio.map(position => ({
                ...position,
                current_price: parseFloat(position.current_price),
                total_value: parseFloat(position.total_value)
            }));
            const portfolioValue = parseFloat(data.portfolio_value);
            const totalValue = parseFloat(data.total_value);
            const balance = parseFloat(data.balance);
            // Update UI with updated data.
            updatePortfolio(portfolio, portfolioValue, totalValue);
            updateBalance(balance);
            showNotification(data.message, 'success');
        } else {
            showNotification(data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred. Please try again.', 'error');
    });

    return false;
}
// Function to display notifications.
function showNotification(message, type = 'success') {
    const container = document.getElementById('notification-container');
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;

    container.appendChild(notification);

    notification.offsetHeight;

    notification.classList.add('show');
//  Notifications appear in corner of screen. then disappear after 5 seconds.
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            container.removeChild(notification);
        }, 300);
    }, 5000);
}
// Function updates user balance display.
function updateBalance(balance) {
    const balanceValue = parseFloat(balance);
    const balanceElement = document.querySelector('#user-balance');
    if (balanceElement) {
        balanceElement.textContent = `Balance: $${balanceValue.toFixed(2)}`;
    } else {
        console.warn("Element with id 'user-balance' not found. Unable to update balance display.");
    }
}

// Function updates users portfolio tables
function updatePortfolio(portfolio, portfolioValue, totalValue) {
    const tbody = document.querySelector('table tbody');
    tbody.innerHTML = '';
    // For each position in portfolio, create a new row in the table.
    portfolio.forEach(position => {
        const currentPrice = parseFloat(position.current_price);
        const totalPositionValue = parseFloat(position.total_value);
        
        const row = `
            <tr class="port-info">
                <td>${position.symbol.toUpperCase()}</td>
                <td>${position.quantity}</td>
                <td>$${currentPrice.toFixed(2)}</td>
                <td>$${totalPositionValue.toFixed(2)}</td>
                <td>
                    <form id="buy-form-${position.symbol.toUpperCase()}" method="post" action="${buyStockUrl}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                        <input type="hidden" name="symbol" value="${position.symbol.toUpperCase()}">
                        <input type="number" name="quantity" min="1" required>
                        <button type="submit">Buy</button>
                    </form>
                </td>
                <td>
                    <form id="sell-form-${position.symbol.toUpperCase()}" method="post" action="${sellStockUrl}">
                        <input type="hidden" name="csrfmiddlewaretoken" value="${csrfToken}">
                        <input type="hidden" name="symbol" value="${position.symbol.toUpperCase()}">
                        <input type="number" name="quantity" min="1" max="${position.quantity}" required>
                        <button type="submit">Sell</button>
                    </form>
                </td>
            </tr>
        `;
        tbody.insertAdjacentHTML('beforeend', row);
    });

    document.getElementById('portfolio-value').textContent = parseFloat(portfolioValue).toFixed(2);
    document.getElementById('total-account-value').textContent = parseFloat(totalValue).toFixed(2);

    document.querySelectorAll('form[id^="buy-form-"], form[id^="sell-form-"]').forEach(form => {
        form.addEventListener('submit', (event) => handleFormSubmit(event, form.id.startsWith('buy') ? 'buy' : 'sell'));
    });
}
// Global variables for URLs and CSRF token
let buyStockUrl = '';
let sellStockUrl = '';
let csrfToken = '';
// Function to initialize the portfolio JavaScript
function initializePortfolioJS(buyUrl, sellUrl, csrf) {
    buyStockUrl = buyUrl;
    sellStockUrl = sellUrl;
    csrfToken = csrf;

    const primaryBuyForm = document.getElementById('primarybuy');
    if (primaryBuyForm) {
        primaryBuyForm.addEventListener('submit', (event) => handleFormSubmit(event, 'buy'));
    }

    document.querySelectorAll('form[id^="buy-form-"], form[id^="sell-form-"]').forEach(form => {
        form.addEventListener('submit', (event) => handleFormSubmit(event, form.id.startsWith('buy') ? 'buy' : 'sell'));
    });
}