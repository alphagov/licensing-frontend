from common.models.payment import Payment


class PaymentRepository:
    def __innit__(self):
        self.model = Payment

    def create_payment(self, licence, customisation, application):
        pass
