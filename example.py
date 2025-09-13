import random
import uuid
from typing import List, Dict, Any, Optional


class BatchPayoutManager:
    def __init__(self):
        self.batch_records = {}

    def create_batch(
        self,
        total_amount: float,
        recipient_key: str,
        method: int,
        payment_count: Optional[int] = None,
        shuffle: bool = False,
    ) -> Dict[str, Any]:
        batch_id = str(uuid.uuid4())
        pix_transactions = []
        limit = 14999.99

        if total_amount <= 0:
            raise ValueError("Total amount must be greater than zero")

        if method == 1:
            num_payments = int(total_amount // limit) + (
                1 if total_amount % limit > 0 else 0
            )
            if num_payments == 0:
                raise ValueError("Cannot process zero payments")
            remaining = total_amount
            for i in range(num_payments):
                if i == num_payments - 1:
                    amount = round(remaining, 2)
                else:
                    amount = min(limit, round(remaining / (num_payments - i), 2))
                if amount > limit:
                    amount = limit
                pix = {
                    "amount": amount,
                    "endToEndId": str(uuid.uuid4()),
                    "recipientKey": recipient_key,
                }
                pix_transactions.append(pix)
                remaining -= amount

        elif method == 2:
            num_payments = random.randint(3, 10) if shuffle else 7
            if num_payments == 0:
                raise ValueError("Cannot process zero payments")
            remaining = total_amount
            for i in range(num_payments):
                if i == num_payments - 1:
                    amount = round(remaining, 2)
                else:
                    amount = min(limit, round(remaining / (num_payments - i), 2))
                if amount > limit:
                    amount = limit
                pix = {
                    "amount": amount,
                    "endToEndId": str(uuid.uuid4()),
                    "recipientKey": recipient_key,
                }
                pix_transactions.append(pix)
                remaining -= amount

        elif method == 3:
            min_payments = int(total_amount // limit) + (
                1 if total_amount % limit > 0 else 0
            )
            max_payments = min(min_payments + 10, 100)
            num_payments = random.randint(min_payments, max_payments)
            if num_payments == 0:
                raise ValueError("Cannot process zero payments")
            remaining = total_amount
            transactions = []
            for i in range(num_payments - 1):
                available_after = remaining - (num_payments - i - 1) * 0.01
                min_val = max(0.01, remaining - (num_payments - i - 1) * limit)
                max_val = min(limit, available_after)
                if min_val > max_val:
                    raise ValueError("Cannot split amount within constraints")
                amount = round(random.uniform(min_val, max_val), 2)
                transactions.append(
                    {
                        "amount": amount,
                        "endToEndId": str(uuid.uuid4()),
                        "recipientKey": recipient_key,
                    }
                )
                remaining -= amount
            final_amount = round(remaining, 2)
            if final_amount > limit or final_amount < 0:
                raise ValueError(
                    "Final payment exceeds maximum allowed amount or is negative"
                )
            transactions.append(
                {
                    "amount": final_amount,
                    "endToEndId": str(uuid.uuid4()),
                    "recipientKey": recipient_key,
                }
            )
            pix_transactions = transactions

        elif method == 4:
            if payment_count is None:
                raise ValueError("payment_count must be specified for method 4")
            if payment_count <= 0:
                raise ValueError("payment_count must be greater than zero")
            min_payments = int(total_amount // limit) + (
                1 if total_amount % limit > 0 else 0
            )
            if payment_count < min_payments:
                raise ValueError(
                    f"Minimum {min_payments} payments required for this amount"
                )
            if payment_count > 100:
                raise ValueError("Maximum 100 payments allowed per batch")
            remaining = total_amount
            transactions = []
            for i in range(payment_count - 1):
                available_after = remaining - (payment_count - i - 1) * 0.01
                min_val = max(0.01, remaining - (payment_count - i - 1) * limit)
                max_val = min(limit, available_after)
                if min_val > max_val:
                    raise ValueError("Cannot split amount within constraints")
                amount = round(random.uniform(min_val, max_val), 2)
                transactions.append(
                    {
                        "amount": amount,
                        "endToEndId": str(uuid.uuid4()),
                        "recipientKey": recipient_key,
                    }
                )
                remaining -= amount
            final_amount = round(remaining, 2)
            if final_amount > limit or final_amount < 0:
                raise ValueError(
                    "Final payment exceeds maximum allowed amount or is negative"
                )
            transactions.append(
                {
                    "amount": final_amount,
                    "endToEndId": str(uuid.uuid4()),
                    "recipientKey": recipient_key,
                }
            )
            pix_transactions = transactions

        else:
            raise ValueError("Invalid method. Use 1, 2, 3, or 4.")

        total_calculated = sum(tx["amount"] for tx in pix_transactions)
        if abs(total_calculated - total_amount) > 0.02:
            raise ValueError("Sum of transactions does not match requested amount")

        self.batch_records[batch_id] = pix_transactions

        return {
            "batch_id": batch_id,
            "pix_transactions": pix_transactions,
            "total_transactions": len(pix_transactions),
            "total_amount_sent": round(total_calculated, 2),
        }

    def simulate_api_call(self, pix_transaction: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "endToEndId": pix_transaction["endToEndId"],
            "eventDate": "2024-06-15T10:30:00Z",
            "id": random.randint(100000, 999999),
            "payment": {"currency": "BRL", "amount": pix_transaction["amount"]},
            "type": "PIX_CASH_OUT",
        }

    def process_batch(self, batch_id: str) -> List[Dict[str, Any]]:
        if batch_id not in self.batch_records:
            raise KeyError(f"Batch ID {batch_id} not found.")

        responses = []
        for pix in self.batch_records[batch_id]:
            response = self.simulate_api_call(pix)
            responses.append(response)

        return responses

    def get_batch_details(self, batch_id: str) -> Dict[str, Any]:
        if batch_id not in self.batch_records:
            raise KeyError(f"Batch ID {batch_id} not found.")

        transactions = self.batch_records[batch_id]
        total_sent = round(sum(tx["amount"] for tx in transactions), 2)

        return {
            "batch_id": batch_id,
            "pix_transactions": transactions,
            "total_transactions": len(transactions),
            "total_amount_sent": total_sent,
        }
