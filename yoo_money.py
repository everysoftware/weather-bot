from yoomoney import Authorize

# https://t.me/ivans_weather_bot
Authorize(
    client_id='75F5E59960114B23ED47E367F3CEE4772256DD9B317566E3067308D0D3AC8A11',
    redirect_uri='https://t.me/is_market_bot',
    scope=[
        'account-info',
        'operation-history',
        'operation-details',
        'incoming-transfers',
        'payment-p2p',
        'payment-shop'
    ]
)
