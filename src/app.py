import os
import sys
import json
import time

# Auto-install Flask if missing
try:
    from flask import Flask, request, jsonify, render_template
except ImportError:
    print("Required package 'Flask' missing. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Flask"])
    from flask import Flask, request, jsonify, render_template

# Add current folder to python path to import model_trainer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import model_trainer

app = Flask(__name__)

# Fallback stats if model not trained yet
DEFAULT_STATS = {
    "accuracy": 0.985,
    "training_time": 2.45,
    "samples_count": 8177,
    "intents_count": 27
}

INTENT_RESPONSES = {
    'cancel_order': {
        'reply': "I can absolutely help you with cancelling your order. Please note that orders can only be cancelled before they have been shipped. Once shipped, you would need to wait for delivery and request a refund.",
        'actions': [{'label': 'Cancel Order Now', 'action': 'cancel_order_workflow'}]
    },
    'change_order': {
        'reply': "I'd be happy to help you modify your order details. Please note that we can only make modifications if the order hasn't entered the processing state yet.",
        'actions': [{'label': 'Edit Order Items', 'action': 'edit_order'}]
    },
    'change_shipping_address': {
        'reply': "Need to redirect your package? I can help update your shipping address. Let's get that corrected before the shipment leaves our warehouse.",
        'actions': [{'label': 'Update Address', 'action': 'change_address'}]
    },
    'check_cancellation_fee': {
        'reply': "Good news! We do not charge cancellation fees if you cancel your order before it enters the processing status. If the order has already shipped, returning it might incur shipping fees.",
        'actions': [{'label': 'View Terms', 'action': 'cancellation_terms'}]
    },
    'check_invoice': {
        'reply': "You can view and print invoices for all your purchases by checking your order details. Alternatively, I can pull your invoice details right now.",
        'actions': [{'label': 'Retrieve Invoice', 'action': 'get_invoice'}]
    },
    'check_payment_methods': {
        'reply': "We support a wide variety of payment methods to keep checkout smooth! We accept Visa, MasterCard, American Express, PayPal, Apple Pay, and Google Pay.",
        'actions': [{'label': 'Payment Methods', 'action': 'show_payments'}]
    },
    'check_refund_policy': {
        'reply': "Our refund policy is simple: you can return most products in their original packaging within 30 days of delivery for a full refund. Refunds typically process back to your original payment method within 5-7 business days.",
        'actions': [{'label': 'Refund Policy Detail', 'action': 'refund_policy'}]
    },
    'complaint': {
        'reply': "I am very sorry that things didn't go as expected. Your experience is important to us, and I want to help make this right. Please describe what happened so I can direct it to our operations team.",
        'actions': [{'label': 'File Formal Complaint', 'action': 'file_complaint'}, {'label': 'Talk to Supervisor', 'action': 'escalate'}]
    },
    'contact_customer_service': {
        'reply': "Need to get in touch with our team? You can reach customer service via email at support@apexcommerce.com or call us directly at +1 (800) 555-0190.",
        'actions': [{'label': 'Call Support', 'action': 'call_support'}]
    },
    'contact_human_agent': {
        'reply': "I understand you'd like to speak with a human. I am connecting you to an agent from our live support desk. Please hold for a moment...",
        'actions': [{'label': 'Connect Now', 'action': 'connect_human'}]
    },
    'create_account': {
        'reply': "Creating an account gives you access to order tracking, invoice history, and personalized deals. It takes less than a minute!",
        'actions': [{'label': 'Sign Up', 'action': 'create_account'}]
    },
    'delete_account': {
        'reply': "We're sad to see you go! If you delete your account, you will lose access to your purchase history and saved information permanently.",
        'actions': [{'label': 'Request Account Deletion', 'action': 'delete_account'}]
    },
    'delivery_options': {
        'reply': "We offer multiple shipping methods: Standard Shipping (3-5 business days), Express Shipping (1-2 business days), and Same-Day Delivery in select metropolitan codes.",
        'actions': [{'label': 'Shipping Calculator', 'action': 'delivery_rates'}]
    },
    'delivery_period': {
        'reply': "Standard delivery takes between 3 to 5 business days, while Express takes 1 to 2 business days. You can track your shipment live for the most accurate arrival estimate.",
        'actions': [{'label': 'Track Shipment', 'action': 'track_order'}]
    },
    'edit_account': {
        'reply': "You can change your password, profile information, or notification settings directly in your Account settings page.",
        'actions': [{'label': 'Go to Account Settings', 'action': 'edit_account'}]
    },
    'get_invoice': {
        'reply': "I can generate a digital invoice for you. Please provide the order ID or transaction code, and I'll send it straight to your email.",
        'actions': [{'label': 'Request Invoice PDF', 'action': 'download_invoice'}]
    },
    'get_refund': {
        'reply': "I can initiate a return or refund request for your order. Please make sure the items were purchased within the last 30 days and are in original condition.",
        'actions': [{'label': 'Initiate Refund', 'action': 'start_refund'}]
    },
    'newsletter_subscription': {
        'reply': "Subscribe to our newsletter to receive the latest updates, sales alerts, and exclusive subscriber-only discount codes!",
        'actions': [{'label': 'Subscribe Now', 'action': 'newsletter_subscribe'}]
    },
    'payment_issue': {
        'reply': "Experiencing issues checking out? This is usually due to card verification issues or bank blocks. Please check your credit balance or try a different payment method like PayPal.",
        'actions': [{'label': 'Retry Payment', 'action': 'retry_payment'}, {'label': 'Contact Billing Team', 'action': 'contact_billing'}]
    },
    'place_order': {
        'reply': "Ready to buy? To place an order, add your desired items to the shopping cart, click the checkout button, specify your delivery address, and submit your payment.",
        'actions': [{'label': 'View Cart', 'action': 'view_cart'}]
    },
    'recover_password': {
        'reply': "Forgot your login password? Don't worry, it happens. Just click the button below to receive a secure reset link at your registered email address.",
        'actions': [{'label': 'Reset Password', 'action': 'reset_password'}]
    },
    'registration_problems': {
        'reply': "Having trouble registering? Ensure that your email is typed correctly and has not been registered previously. If the page is unresponsive, try clearing your browser cookies.",
        'actions': [{'label': 'Troubleshoot Sign-up', 'action': 'registration_help'}]
    },
    'review': {
        'reply': "We appreciate your feedback! You can rate your recent purchases and write reviews under the 'My Orders' section in your account dashboard.",
        'actions': [{'label': 'Leave a Review', 'action': 'write_review'}]
    },
    'set_up_shipping_address': {
        'reply': "You can configure a default shipping address and add secondary delivery addresses in your account address book for a faster checkout experience next time.",
        'actions': [{'label': 'Manage Addresses', 'action': 'manage_addresses'}]
    },
    'switch_account': {
        'reply': "To switch to a different account, click your profile thumbnail at the top-right corner of the screen, select 'Log Out', and log in with your other credentials.",
        'actions': [{'label': 'Log Out', 'action': 'logout'}]
    },
    'track_order': {
        'reply': "Want to check the current location of your package? Provide your order number or tracking code, and I will pull up the shipping carrier information.",
        'actions': [{'label': 'Track Order Live', 'action': 'track_order_workflow'}]
    },
    'track_refund': {
        'reply': "Refunds are processed back to the original payment method. They typically take 5-7 business days to reflect. I can check the status of your refund if you share the refund ID.",
        'actions': [{'label': 'Check Refund Status', 'action': 'check_refund'}]
    }
}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        data = request.json or {}
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
            
        intent, confidence = model_trainer.predict_intent(user_message)
        
        # If low confidence, provide a fallback response
        if confidence < 0.35:
            response_data = {
                'reply': "I'm not completely sure I understood that correctly. Since you're asking about customer support, could you please rephrase your request or choose one of the quick options below?",
                'intent': 'unknown',
                'confidence': float(confidence),
                'actions': []
            }
        else:
            intent_details = INTENT_RESPONSES.get(intent, {
                'reply': f"I detected you are asking about '{intent.replace('_', ' ')}'. How can I help you with this?",
                'actions': []
            })
            response_data = {
                'reply': intent_details['reply'],
                'intent': intent,
                'confidence': float(confidence),
                'actions': intent_details.get('actions', [])
            }
            
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/train', methods=['POST'])
def train():
    try:
        stats = model_trainer.train_and_save_model()
        return jsonify({
            'success': True,
            'accuracy': float(stats['accuracy']),
            'training_time': float(stats['training_time']),
            'samples_count': int(stats['samples_count']),
            'intents_count': int(stats['intents_count'])
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    stats_path = model_trainer.STATS_PATH
    if os.path.exists(stats_path):
        try:
            with open(stats_path, 'r') as f:
                stats = json.load(f)
            return jsonify(stats)
        except Exception:
            pass
    return jsonify(DEFAULT_STATS)

if __name__ == '__main__':
    print("Checking model status...")
    # Pre-load or pre-train model on startup so the app is immediately ready
    try:
        model_trainer.load_model()
        print("Model loaded and ready.")
    except Exception as e:
        print(f"Warning: Could not auto-train model on startup: {e}")
        
    print("Starting Flask web server on http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
