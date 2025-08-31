class Order:
    def __init__(self):
        self.order_id = ""
        self.order_datetime = None
        self.exchange = ""
        self.symbol = ""
        self.side = ""
        self.quantity = 0
        self.price = 0
        self.fees_amount = 0
        self.fees_coin = ""
        self.is_test = ""

    def __repr__(self):
        return (
            f"Order("
            f"order_id={self.order_id}, "
            f"order_datetime={self.order_datetime}, "
            f"exchange={self.exchange}, "
            f"symbol={self.symbol}, "
            f"side={self.side}, "
            f"quantity={self.quantity}, "
            f"price={self.price}, "
            f"fees_amount={self.fees_amount}, "
            f"fees_coin={self.fees_coin}, "
            f"is_test={self.is_test}"
            ")"
        )
    
class Receipt:
    def __init__(self):
        self.order_id = ""
        self.order_datetime = None
        self.side = ""
        self.exchange = ""
        self.symbol = ""
        self.side = ""
        self.quantity = 0
        self.price = 0
        self.fees_amount = 0
        self.fees_coin = ""
        self.type = ""
        self.time = ""
        self.error = ""
        self.is_test = ""

    def __repr__(self):
        return (
        f"Receipt("
        f"order_id={self.order_id}",
        f"order_datetime={self.order_datetime}, "
        f"side={self.side}, "
        f"exchange={self.exchange}, "
        f"symbol={self.symbol}, "
        f"quantity={self.quantity}, "
        f"type={self.type}"
        ")"
    )
