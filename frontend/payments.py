"""
Payment and subscription management module.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from enum import Enum

logger = logging.getLogger(__name__)


class SubscriptionPlan(Enum):
    """Available subscription plans."""
    FREE = "free"
    BASIC = "basic"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class PaymentStatus(Enum):
    """Payment status."""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class PaymentManager:
    """Manages payments and subscriptions."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the payment manager.
        
        Args:
            config: Payment gateway configuration
        """
        self.config = config or {}
        self.payment_provider = self.config.get("provider", "stripe")
        
        # Plan pricing (monthly in USD)
        self.plans = {
            SubscriptionPlan.FREE: {
                "price": 0,
                "features": ["5 diagnoses per month", "Basic AI models", "Email support"],
                "max_diagnoses": 5,
            },
            SubscriptionPlan.BASIC: {
                "price": 29.99,
                "features": ["50 diagnoses per month", "Standard AI models", "Email support"],
                "max_diagnoses": 50,
            },
            SubscriptionPlan.PROFESSIONAL: {
                "price": 99.99,
                "features": [
                    "Unlimited diagnoses",
                    "Advanced AI models",
                    "Priority support",
                    "Export reports",
                ],
                "max_diagnoses": -1,  # Unlimited
            },
            SubscriptionPlan.ENTERPRISE: {
                "price": 299.99,
                "features": [
                    "Unlimited diagnoses",
                    "All AI models",
                    "24/7 Premium support",
                    "Custom integrations",
                    "API access",
                    "White-label option",
                ],
                "max_diagnoses": -1,  # Unlimited
            },
        }
        
        logger.info(f"Payment manager initialized with provider: {self.payment_provider}")

    def get_plan_details(self, plan: SubscriptionPlan) -> Dict[str, Any]:
        """
        Get details of a subscription plan.
        
        Args:
            plan: Subscription plan
            
        Returns:
            Plan details
        """
        return {
            "plan": plan.value,
            "price": self.plans[plan]["price"],
            "features": self.plans[plan]["features"],
            "max_diagnoses": self.plans[plan]["max_diagnoses"],
        }

    def get_all_plans(self) -> List[Dict[str, Any]]:
        """
        Get all available subscription plans.
        
        Returns:
            List of plan details
        """
        return [self.get_plan_details(plan) for plan in SubscriptionPlan]

    def create_subscription(
        self,
        user_id: int,
        plan: SubscriptionPlan,
        payment_method: str = "card"
    ) -> Dict[str, Any]:
        """
        Create a new subscription.
        
        Args:
            user_id: User ID
            plan: Subscription plan
            payment_method: Payment method
            
        Returns:
            Subscription details
        """
        logger.info(f"Creating subscription for user {user_id}, plan: {plan.value}")
        
        plan_details = self.plans[plan]
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=30)  # Monthly subscription
        
        subscription = {
            "subscription_id": f"sub_{datetime.utcnow().timestamp()}",
            "user_id": user_id,
            "plan": plan.value,
            "price": plan_details["price"],
            "currency": "USD",
            "status": "active",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "payment_method": payment_method,
            "auto_renew": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Subscription created: {subscription['subscription_id']}")
        return subscription

    def process_payment(
        self,
        user_id: int,
        amount: float,
        currency: str = "USD",
        payment_method: str = "card",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a payment.
        
        Args:
            user_id: User ID
            amount: Payment amount
            currency: Currency code
            payment_method: Payment method
            metadata: Additional payment metadata
            
        Returns:
            Payment result
        """
        logger.info(f"Processing payment for user {user_id}: {amount} {currency}")
        
        # In production, this would integrate with Stripe/PayPal/etc.
        payment = {
            "payment_id": f"pay_{datetime.utcnow().timestamp()}",
            "user_id": user_id,
            "amount": amount,
            "currency": currency,
            "status": PaymentStatus.COMPLETED.value,
            "payment_method": payment_method,
            "provider": self.payment_provider,
            "metadata": metadata or {},
            "created_at": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Payment processed: {payment['payment_id']}")
        return payment

    def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Cancel a subscription.
        
        Args:
            subscription_id: Subscription ID
            
        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Cancelling subscription: {subscription_id}")
        
        # In production, this would update the database and payment provider
        # For now, just log the action
        
        logger.info(f"Subscription cancelled: {subscription_id}")
        return True

    def upgrade_subscription(
        self,
        subscription_id: str,
        new_plan: SubscriptionPlan
    ) -> Dict[str, Any]:
        """
        Upgrade a subscription to a higher plan.
        
        Args:
            subscription_id: Current subscription ID
            new_plan: New subscription plan
            
        Returns:
            Updated subscription details
        """
        logger.info(f"Upgrading subscription {subscription_id} to {new_plan.value}")
        
        # Calculate prorated amount
        # In production, this would be more sophisticated
        
        plan_details = self.plans[new_plan]
        
        updated_subscription = {
            "subscription_id": subscription_id,
            "plan": new_plan.value,
            "price": plan_details["price"],
            "status": "active",
            "upgraded_at": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Subscription upgraded: {subscription_id}")
        return updated_subscription

    def check_usage_limit(
        self,
        user_id: int,
        current_usage: int,
        plan: SubscriptionPlan
    ) -> Dict[str, Any]:
        """
        Check if user has exceeded usage limits.
        
        Args:
            user_id: User ID
            current_usage: Current number of diagnoses this month
            plan: User's subscription plan
            
        Returns:
            Usage status
        """
        max_diagnoses = self.plans[plan]["max_diagnoses"]
        
        if max_diagnoses == -1:  # Unlimited
            return {
                "within_limit": True,
                "current_usage": current_usage,
                "max_allowed": "unlimited",
                "percentage_used": 0,
            }
        
        within_limit = current_usage < max_diagnoses
        percentage = (current_usage / max_diagnoses) * 100 if max_diagnoses > 0 else 0
        
        return {
            "within_limit": within_limit,
            "current_usage": current_usage,
            "max_allowed": max_diagnoses,
            "percentage_used": percentage,
            "remaining": max(0, max_diagnoses - current_usage),
        }

    def get_invoice(self, payment_id: str) -> Dict[str, Any]:
        """
        Get invoice for a payment.
        
        Args:
            payment_id: Payment ID
            
        Returns:
            Invoice details
        """
        # In production, this would fetch from database
        invoice = {
            "invoice_id": f"inv_{payment_id}",
            "payment_id": payment_id,
            "generated_at": datetime.utcnow().isoformat(),
            "status": "paid",
        }
        
        return invoice

    def process_refund(
        self,
        payment_id: str,
        amount: Optional[float] = None,
        reason: str = ""
    ) -> Dict[str, Any]:
        """
        Process a refund.
        
        Args:
            payment_id: Original payment ID
            amount: Refund amount (None = full refund)
            reason: Refund reason
            
        Returns:
            Refund details
        """
        logger.info(f"Processing refund for payment: {payment_id}")
        
        refund = {
            "refund_id": f"ref_{datetime.utcnow().timestamp()}",
            "payment_id": payment_id,
            "amount": amount,
            "reason": reason,
            "status": PaymentStatus.REFUNDED.value,
            "processed_at": datetime.utcnow().isoformat(),
        }
        
        logger.info(f"Refund processed: {refund['refund_id']}")
        return refund


# Global payment manager instance
payment_manager = PaymentManager()


def get_user_subscription_status(user_id: int) -> Dict[str, Any]:
    """
    Get user's current subscription status.
    
    Args:
        user_id: User ID
        
    Returns:
        Subscription status
    """
    # In production, this would query the database
    return {
        "user_id": user_id,
        "plan": SubscriptionPlan.FREE.value,
        "status": "active",
        "current_usage": 0,
        "max_diagnoses": 5,
    }
