class Receipttemplate(object):
    def __init__(self, recipient_name=None, order_number=None, currency='USD', payment_method=None,
                 timestamp=None, elements=None, address=None, summary=0, adjustments=None):
        self.type = 'template'
        self.payload = {
            'template_type': 'receipt',
            'recipient_name': recipient_name,
            'order_number': order_number,
            'currency': currency,
            'payment_method': payment_method,
            'timestamp': timestamp,
            'elements': elements,
            'address': address,
            'summary': summary,
            'adjustments': adjustments
        }