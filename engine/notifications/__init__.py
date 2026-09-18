"""
CareerOS Notification & Double Opt-In Dispatcher Package
"""
from .dispatcher import NotificationDispatcher
from .templates import NotificationTemplateManager

__all__ = ["NotificationDispatcher", "NotificationTemplateManager"]
