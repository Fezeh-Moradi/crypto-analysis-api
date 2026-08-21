from app.models.schemas import PositionSizeRequest, PositionSizeResponse


class RiskService:
    def calculate_position_size(self, data: PositionSizeRequest) -> PositionSizeResponse:
        if data.account_balance <= 0:
            raise ValueError("Account balance must be greater than 0")
        if data.risk_percent <= 0 or data.risk_percent > 100:
            raise ValueError("Risk percent must be between 0 and 100")
        if data.entry_price <= 0 or data.stop_loss_price <= 0:
            raise ValueError("Prices must be greater than 0")
        if data.entry_price == data.stop_loss_price:
            raise ValueError("Entry price and stop loss cannot be the same")

        risk_amount = data.account_balance * (data.risk_percent / 100)
        stop_loss_percent = abs(data.entry_price - data.stop_loss_price) / data.entry_price * 100
        position_size = risk_amount / abs(data.entry_price - data.stop_loss_price)
        position_value = position_size * data.entry_price

        return PositionSizeResponse(
            account_balance=data.account_balance,
            risk_percent=data.risk_percent,
            risk_amount=round(risk_amount, 2),
            entry_price=data.entry_price,
            stop_loss_price=data.stop_loss_price,
            stop_loss_percent=round(stop_loss_percent, 2),
            position_size=round(position_size, 6),
            position_value=round(position_value, 2),
        )