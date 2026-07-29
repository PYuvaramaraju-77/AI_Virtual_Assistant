// Intent Directory with Category and Sample query for testing
const INTENT_DIRECTORY = [
    { name: 'cancel_order', category: 'ORDER', sample: "I want to cancel my recent order" },
    { name: 'change_order', category: 'ORDER', sample: "Can I change my order details?" },
    { name: 'change_shipping_address', category: 'SHIPPING', sample: "Please update my shipping address" },
    { name: 'check_cancellation_fee', category: 'FEE', sample: "How much is the cancellation fee?" },
    { name: 'check_invoice', category: 'INVOICE', sample: "Where can I find my invoice?" },
    { name: 'check_payment_methods', category: 'PAYMENT', sample: "What payment methods do you accept?" },
    { name: 'check_refund_policy', category: 'REFUND', sample: "What is your return policy?" },
    { name: 'complaint', category: 'FEEDBACK', sample: "I want to file a complaint about my experience" },
    { name: 'contact_customer_service', category: 'CONTACT', sample: "How can I contact customer support?" },
    { name: 'contact_human_agent', category: 'CONTACT', sample: "I want to speak with a human agent" },
    { name: 'create_account', category: 'ACCOUNT', sample: "How do I create a new account?" },
    { name: 'delete_account', category: 'ACCOUNT', sample: "I want to close my account" },
    { name: 'delivery_options', category: 'DELIVERY', sample: "What delivery options do you have?" },
    { name: 'delivery_period', category: 'DELIVERY', sample: "How long does shipping take?" },
    { name: 'edit_account', category: 'ACCOUNT', sample: "How do I update my profile details?" },
    { name: 'get_invoice', category: 'INVOICE', sample: "Send me the invoice for my order" },
    { name: 'get_refund', category: 'REFUND', sample: "I want to request a refund" },
    { name: 'newsletter_subscription', category: 'NEWSLETTER', sample: "How do I sign up for the newsletter?" },
    { name: 'payment_issue', category: 'PAYMENT', sample: "My credit card payment was declined" },
    { name: 'place_order', category: 'ORDER', sample: "How do I submit an order?" },
    { name: 'recover_password', category: 'ACCOUNT', sample: "I need help resetting my password" },
    { name: 'registration_problems', category: 'ACCOUNT', sample: "I am getting errors during signup" },
    { name: 'review', category: 'FEEDBACK', sample: "How can I write a product review?" },
    { name: 'set_up_shipping_address', category: 'SHIPPING', sample: "Add a new shipping address to my profile" },
    { name: 'switch_account', category: 'ACCOUNT', sample: "How to log out and switch users" },
    { name: 'track_order', category: 'ORDER', sample: "Where is my package?" },
    { name: 'track_refund', category: 'REFUND', sample: "Has my refund been processed yet?" }
];

// Cache DOM Elements
const chatMessages = document.getElementById('chat-messages');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const btnClear = document.getElementById('btn-clear-chat');
const btnRetrain = document.getElementById('btn-retrain');
const loaderOverlay = document.getElementById('loader-overlay');
const intentsList = document.getElementById('intents-list');

// Stat values
const statAccuracy = document.getElementById('stat-accuracy');
const statSamples = document.getElementById('stat-samples');
const statIntents = document.getElementById('stat-intents');
const statTime = document.getElementById('stat-time');

// Welcome state reference HTML
const welcomeHTML = chatMessages.innerHTML;

// Initialize Web App
document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    renderIntentDirectory();
    setupEventListeners();
});

// Event Listeners setup
function setupEventListeners() {
    // Form submit
    chatForm.addEventListener('submit', (e) => {
        e.preventDefault();
        sendMessage();
    });

    // Clear feed
    btnClear.addEventListener('click', () => {
        chatMessages.innerHTML = welcomeHTML;
        showSystemNotification("Chat workspace cleared");
    });

    // Retrain button
    btnRetrain.addEventListener('click', retrainModel);

    // Quick replies chips
    document.querySelectorAll('.chip').forEach(chip => {
        chip.addEventListener('click', () => {
            const query = chip.getAttribute('data-query');
            submitQuery(query);
        });
    });
}

// Fetch stats from backend
async function fetchStats() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        updateStatsUI(data);
    } catch (error) {
        console.error('Error fetching model stats:', error);
    }
}

// Update stats dashboard items
function updateStatsUI(stats) {
    if (stats.accuracy) {
        statAccuracy.textContent = `${(stats.accuracy * 100).toFixed(1)}%`;
    }
    if (stats.samples_count) {
        statSamples.textContent = stats.samples_count.toLocaleString();
    }
    if (stats.intents_count) {
        statIntents.textContent = stats.intents_count;
    }
    if (stats.training_time) {
        statTime.textContent = `${stats.training_time.toFixed(2)}s`;
    }
}

// Render Sidebar Intent list
function renderIntentDirectory() {
    intentsList.innerHTML = '';
    
    INTENT_DIRECTORY.forEach(item => {
        const div = document.createElement('div');
        div.className = 'intent-item';
        div.title = `Click to test: "${item.sample}"`;
        
        div.innerHTML = `
            <span class="intent-item-name">${item.name}</span>
            <span class="intent-item-category">${item.category}</span>
        `;
        
        div.addEventListener('click', () => {
            submitQuery(item.sample);
        });
        
        intentsList.appendChild(div);
    });
}

// Trigger query submission directly
function submitQuery(text) {
    userInput.value = text;
    chatForm.dispatchEvent(new Event('submit'));
}

// Send message to api
async function sendMessage() {
    const text = userInput.value.trim();
    if (!text) return;
    
    // Clear input
    userInput.value = '';
    
    // 1. Add User Message
    addMessageBubble(text, 'user');
    scrollToBottom();
    
    // 2. Add Typing Indicator
    const typingIndicatorId = addTypingIndicator();
    scrollToBottom();
    
    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        });
        
        const data = await response.json();
        
        // Remove typing indicator
        removeTypingIndicator(typingIndicatorId);
        
        if (data.error) {
            addMessageBubble(`Error: ${data.error}`, 'assistant', { error: true });
        } else {
            // 3. Add Assistant Message Bubble
            addMessageBubble(data.reply, 'assistant', {
                intent: data.intent,
                confidence: data.confidence,
                actions: data.actions
            });
        }
        
    } catch (error) {
        console.error('Chat error:', error);
        removeTypingIndicator(typingIndicatorId);
        addMessageBubble("Oops, I encountered a communication error with the local Python server.", 'assistant', { error: true });
    }
    
    scrollToBottom();
}

// Add a bubble to chat interface
function addMessageBubble(text, sender, meta = null) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}-message`;
    
    const avatarDiv = document.createElement('div');
    avatarDiv.className = 'avatar';
    avatarDiv.textContent = sender === 'user' ? 'ME' : 'AI';
    
    const wrapperDiv = document.createElement('div');
    wrapperDiv.className = 'message-content-wrapper';
    
    const bodyDiv = document.createElement('div');
    bodyDiv.className = 'message-body';
    
    if (meta && meta.error) {
        bodyDiv.style.borderColor = 'rgba(239, 68, 68, 0.4)';
        bodyDiv.style.background = 'rgba(239, 68, 68, 0.05)';
        bodyDiv.innerHTML = `<p style="color: #ef4444;">${text}</p>`;
    } else {
        bodyDiv.innerHTML = `<p>${text}</p>`;
    }
    
    wrapperDiv.appendChild(bodyDiv);
    
    // Meta data (Confidence and Intent)
    if (meta && meta.intent && sender === 'assistant') {
        const metaDiv = document.createElement('div');
        metaDiv.className = 'message-meta';
        const percent = (meta.confidence * 100).toFixed(1);
        metaDiv.textContent = `Intent: ${meta.intent} • Confidence: ${percent}%`;
        wrapperDiv.appendChild(metaDiv);
        
        // Render actions buttons
        if (meta.actions && meta.actions.length > 0) {
            const actionsDiv = document.createElement('div');
            actionsDiv.className = 'chat-actions';
            
            meta.actions.forEach(act => {
                const btn = document.createElement('button');
                btn.className = 'action-btn';
                btn.textContent = act.label;
                btn.addEventListener('click', () => handleActionClick(act));
                actionsDiv.appendChild(btn);
            });
            
            wrapperDiv.appendChild(actionsDiv);
        }
    } else if (sender === 'user') {
        const timeDiv = document.createElement('div');
        timeDiv.className = 'message-meta';
        timeDiv.textContent = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        wrapperDiv.appendChild(timeDiv);
    }
    
    messageDiv.appendChild(avatarDiv);
    messageDiv.appendChild(wrapperDiv);
    
    chatMessages.appendChild(messageDiv);
}

// Handle action button clicking
function handleActionClick(actionObj) {
    showSystemNotification(`Action Triggered: ${actionObj.label}`);
    
    // Create an assistant reply mock for the action
    const typingId = addTypingIndicator();
    scrollToBottom();
    
    setTimeout(() => {
        removeTypingIndicator(typingId);
        let mockReply = "";
        
        switch (actionObj.action) {
            case 'cancel_order_workflow':
                mockReply = "🔄 **Cancellation Request Submitted**: I have initialized the cancellation workflow for your last order. A confirmation code has been generated: **#CAN-987123**.";
                break;
            case 'edit_order':
                mockReply = "📝 **Order Editor Opened**: You can now replace items or adjust quantities in your open orders dashboard panel.";
                break;
            case 'change_address':
                mockReply = "📍 **Shipping Redirect System**: Please type your new shipping address below, and I will confirm verification with the logistics carrier.";
                break;
            case 'cancellation_terms':
                mockReply = "📄 **Cancellation Policy details**: Orders are fully refundable if cancelled within 60 minutes of payment. Post-dispatch cancellations require a processing fee of $5.00.";
                break;
            case 'get_invoice':
            case 'download_invoice':
                mockReply = "📥 **Invoice Prepared**: Invoice **#INV-2026-89** has been successfully generated as a PDF and dispatched to your registered customer email.";
                break;
            case 'show_payments':
                mockReply = "💳 **Payment Methods Available**: You have a Visa ending in **4242** set as your default card. You can add alternative cards or checkout with Apple Pay / PayPal.";
                break;
            case 'refund_policy':
                mockReply = "🛡️ **Refund Guarantees**: We offer money-back guarantees on all standard items returned within 30 days. No restocking fee is applied. Return label is free.";
                break;
            case 'file_complaint':
                mockReply = "⚠️ **Complaint Ticket Lodged**: Ticket **#CMP-30291** has been opened. Our relations team will respond within 4 hours. We apologize for the inconvenience.";
                break;
            case 'escalate':
            case 'connect_human':
                mockReply = "📞 **Live Agent Queue**: Connecting you to a Senior Care Specialist... **Position in line: 1**. Estimated wait time: **less than 2 minutes**.";
                break;
            case 'call_support':
                mockReply = "📞 **Phone Helpline**: You can dial our direct support line at **+1 (800) 555-0190** (Toll-Free). Please use PIN **4930** to bypass the line.";
                break;
            case 'create_account':
                mockReply = "👤 **Sign Up Portal**: Navigating you to the Registration Form page. You will receive a verification email to complete the activation.";
                break;
            case 'delete_account':
                mockReply = "⚠️ **Account Deletion Warning**: Are you sure? This deletes your lifetime reward points. If yes, click the security link sent to your phone to confirm.";
                break;
            case 'delivery_rates':
                mockReply = "🚚 **Shipping rates**: Free standard delivery is applied to orders over $35. Express courier delivery is fixed at $9.99.";
                break;
            case 'track_order_workflow':
                mockReply = "📦 **Real-Time Tracker**: Package status: **In Transit (Out for Delivery)** via DHL Express. Tracking Number: `DHL-883910-US`. Estimated delivery: **Today before 6:00 PM**.";
                break;
            case 'start_refund':
                mockReply = "💸 **Return Center**: Please paste the purchase transaction ID, and I will generate a prepaid return shipping slip.";
                break;
            case 'newsletter_subscribe':
                mockReply = "📧 **Subscription Active**: Thank you! You have subscribed to our Newsletter. Here is your 10% discount code for your next purchase: **WELCOME10**.";
                break;
            case 'retry_payment':
                mockReply = "💳 **Payment Retry Gateway**: Please re-enter your CVV or authorize the payment in your bank app to complete order #78902.";
                break;
            case 'contact_billing':
                mockReply = "✉️ **Billing Desk**: Opening a line to our Finance Department. You can upload payment receipts or screenshots directly here.";
                break;
            case 'view_cart':
                mockReply = "🛒 **Shopping Cart**: Opening your checkout bag. You have **2 items** ($45.98 total) awaiting completion.";
                break;
            case 'reset_password':
                mockReply = "🔑 **Reset Email Dispatched**: A secure link to change your password has been sent to your registered email address.";
                break;
            case 'registration_help':
                mockReply = "⚙️ **Registration Diagnostics**: Make sure JavaScript is enabled and check if your email has already been registered. Try logging in directly.";
                break;
            case 'write_review':
                mockReply = "⭐ **Review portal**: Please rate your purchased item (1-5 stars) and write a comment. We reward reviews with 50 loyalty points!";
                break;
            case 'manage_addresses':
                mockReply = "🏠 **Address Profile Manager**: You can edit your home and billing addresses, or set a primary delivery address.";
                break;
            default:
                mockReply = `🤖 Executed action payload: \`${actionObj.action}\``;
        }
        
        addMessageBubble(mockReply, 'assistant', {
            intent: 'contextual_action',
            confidence: 1.0
        });
        scrollToBottom();
    }, 800);
}

// Add typing placeholder
function addTypingIndicator() {
    const id = 'typing-' + Date.now();
    const indicatorDiv = document.createElement('div');
    indicatorDiv.className = 'message assistant-message';
    indicatorDiv.id = id;
    
    indicatorDiv.innerHTML = `
        <div class="avatar">AI</div>
        <div class="message-content-wrapper">
            <div class="message-body" style="padding: 0.6rem 1rem; color: var(--color-text-muted);">
                <span>Typing...</span>
            </div>
        </div>
    `;
    
    chatMessages.appendChild(indicatorDiv);
    return id;
}

// Remove typing placeholder
function removeTypingIndicator(id) {
    const indicator = document.getElementById(id);
    if (indicator) {
        indicator.remove();
    }
}

// Show system log message
function showSystemNotification(text) {
    const notifyDiv = document.createElement('div');
    notifyDiv.style.alignSelf = 'center';
    notifyDiv.style.fontSize = '0.75rem';
    notifyDiv.style.color = 'var(--color-text-accent)';
    notifyDiv.style.background = 'rgba(167, 139, 250, 0.08)';
    notifyDiv.style.padding = '0.35rem 0.85rem';
    notifyDiv.style.borderRadius = '9999px';
    notifyDiv.style.margin = '0.5rem 0';
    notifyDiv.style.border = '1px solid rgba(167, 139, 250, 0.15)';
    notifyDiv.style.animation = 'slideIn 0.3s ease forwards';
    notifyDiv.textContent = text;
    
    chatMessages.appendChild(notifyDiv);
    scrollToBottom();
}

// Scroll chat to bottom
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Trigger model training call
async function retrainModel() {
    const iconRefresh = btnRetrain.querySelector('.icon-refresh');
    
    // Show spinner in button and open overlay
    iconRefresh.classList.add('spinning');
    btnRetrain.disabled = true;
    loaderOverlay.classList.add('show');
    
    try {
        const response = await fetch('/api/train', {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.success) {
            updateStatsUI(data);
            showSystemNotification(`Model successfully retrained in ${data.training_time.toFixed(2)}s! Accuracy: ${(data.accuracy * 100).toFixed(1)}%`);
        } else {
            alert(`Training Error: ${data.error}`);
        }
        
    } catch (error) {
        console.error('Error retraining model:', error);
        alert("Server communication error occurred while retraining model.");
    } finally {
        // Hide loader overlay and reset button
        iconRefresh.classList.remove('spinning');
        btnRetrain.disabled = false;
        loaderOverlay.classList.remove('show');
    }
}
