"""
CareerOS Unified Command Engine Package
======================================
Autonomous career operating system command bus and registry.
"""

from engine.commands.registry import CommandRegistry, execute_command

__all__ = ["CommandRegistry", "execute_command"]
