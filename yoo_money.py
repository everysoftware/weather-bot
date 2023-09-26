from yoomoney import Authorize

Authorize(
    client_id='YOUR_CLIENT_ID',
    redirect_uri='YOUR_TG_CHANNEL_LINK',
    scope=[
        'account-info',
        'operation-history',
        'operation-details',
        'incoming-transfers',
        'payment-p2p',
        'payment-shop'
    ]
)
