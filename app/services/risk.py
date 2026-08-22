from app.models.schemas import PositionSizeRequest, PositionSizeResponse, TrailingStopRequest, TrailingStopResponse


class RiskService:
    def calculate_position_size(self, data: PositionSizeRequest) -> PositionSizeResponse:
        if data.account_balance <= 0:
            raise ValueError("Account balance must be greater than 0")
        if data.risk_percent <= 0 or data.risk_percent > 100:
            raise ValueError("Risk percent must be between 0 and 100")
        if data.entry_price <= 0 or data.stop_loss_price <= 0:
            raise ValueError("Entry and stop loss prices must be positive")
        if data.entry_price == data.stop_loss_price:
            raise ValueError("Entry price cannot equal stop loss price")
        if data.atr_14 <= 0:
            raise ValueError("ATR must be greater than 0")

        risk_amount = data.account_balance * (data.risk_percent / 100)
        stop_distance = abs(data.entry_price - data.stop_loss_price)
        position_size = risk_amount / stop_distance
        position_value = position_size * data.entry_price
        stop_loss_percent = (stop_distance / data.entry_price) * 100

        atr_based_stop_loss = data.atr_14 * 1.5
        atr_based_stop_loss_percent = round((atr_based_stop_loss / data.entry_price) * 100, 2)

        return PositionSizeResponse(
            account_balance=data.account_balance,
            risk_percent=data.risk_percent,
            risk_amount=round(risk_amount, 2),
            entry_price=data.entry_price,
            stop_loss_price=data.stop_loss_price,
            stop_loss_percent=round(stop_loss_percent, 2),
            position_size=round(position_size, 6),
            position_value=round(position_value, 2),
            atr_based_stop_loss_percent=atr_based_stop_loss_percent,
        )



    def calculate_trailing_stop(self, data: TrailingStopRequest) -> TrailingStopResponse:
        if data.entry_price <= 0 or data.current_price <= 0:
            raise ValueError("Prices must be greater than 0")
        if data.atr_14 <= 0:
            raise ValueError("ATR must be greater than 0")
        if data.side.lower() not in ["long", "short"]:
            raise ValueError("Side must be 'long' or 'short'")

        side = data.side.lower()
        atr_distance = data.atr_14 * data.multiplier

        if side == "long":
            initial_stop = data.entry_price - atr_distance
            trailing_stop = data.current_price - atr_distance
            trailing_stop = max(trailing_stop, initial_stop)
            is_profitable = data.current_price > data.entry_price
            distance_percent = ((data.current_price - trailing_stop) / data.current_price) * 100
        else:
            initial_stop = data.entry_price + atr_distance
            trailing_stop = data.current_price + atr_distance
            trailing_stop = min(trailing_stop, initial_stop)
            is_profitable = data.current_price < data.entry_price
            distance_percent = ((trailing_stop - data.current_price) / data.current_price) * 100

        if is_profitable:
            recommendation = "Move stop loss to trailing level to lock profit"
        else:
            recommendation = "Keep initial stop loss. Trade is not yet profitable"

        return TrailingStopResponse(
            entry_price=data.entry_price,
            current_price=data.current_price,
            side=side,
            atr_14=data.atr_14,
            multiplier=data.multiplier,
            initial_stop_loss=round(initial_stop, 4),
            trailing_stop_loss=round(trailing_stop, 4),
            distance_percent=round(distance_percent, 2),
            is_profitable=is_profitable,
            recommendation=recommendation,
        )