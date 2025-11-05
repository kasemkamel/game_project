# systems/actions_system.py
from dataclasses import dataclass
from typing import List, Callable, Any, Optional
from enum import Enum


class ActionCategory(Enum):
    """Action classification"""

    MOVEMENT = "Movement"
    MILITARY = "Military"
    ESPIONAGE = "Espionage"
    MANAGEMENT = "Management"
    PRODUCTION = "Production"


@dataclass
class Action:
    """Represents a single executable action"""

    id: str
    name: str
    description: str
    category: ActionCategory
    icon: Optional[str] = None  # Icon name or symbol
    hotkey: Optional[str] = None  # Keyboard shortcut

    # Function to check if action can be executed
    can_execute: Optional[Callable[[Any], bool]] = None

    # Actual execution function
    execute: Optional[Callable[[Any], None]] = None

    # Function to get additional data (like tooltip)
    get_tooltip: Optional[Callable[[Any], str]] = None

    def is_available(self, entity) -> bool:
        """Check if action is available for execution"""
        if self.can_execute is None:
            return True
        return self.can_execute(entity)

    def run(self, entity, **kwargs):
        """Execute the action"""
        if self.execute:
            return self.execute(entity, **kwargs)
        return None


class ActionsSystem:
    """System for managing available actions for each entity"""

    def __init__(self):
        self.actions = {}  # {entity_type: [Action, ...]}
        self._register_default_actions()

    def _register_default_actions(self):
        """Register default actions for each entity type"""

        # ========== Army Actions ==========
        self.register_action(
            "Army",
            Action(
                id="move_to",
                name="Move To",
                description="Move the army to a specific location",
                category=ActionCategory.MOVEMENT,
                icon="→",
                hotkey="M",
                can_execute=lambda army: army.city
                is None,  # Only available outside cities
                get_tooltip=lambda army: "Click on the map to set destination",
            ),
        )

        self.register_action(
            "Army",
            Action(
                id="enter_city",
                name="Enter City",
                description="Enter the army into a nearby city",
                category=ActionCategory.MOVEMENT,
                icon="🏰",
                hotkey="E",
                can_execute=lambda army: army.city is None and army.path is None,
                get_tooltip=lambda army: "Click on a city to enter it",
            ),
        )

        self.register_action(
            "Army",
            Action(
                id="change_commander",
                name="Change Commander",
                description="Assign a new commander to the army",
                category=ActionCategory.MANAGEMENT,
                icon="👤",
                hotkey="C",
                can_execute=lambda army: True,
                get_tooltip=lambda army: f"Current commander: {army.commander}",
            ),
        )

        self.register_action(
            "Army",
            Action(
                id="change_assistant",
                name="Change Assistant",
                description="Assign a new assistant to the army",
                category=ActionCategory.MANAGEMENT,
                icon="👥",
                hotkey="A",
                can_execute=lambda army: True,
                get_tooltip=lambda army: f"Current assistant: {army.assistant}",
            ),
        )

        self.register_action(
            "Army",
            Action(
                id="manage_units",
                name="Manage Units",
                description="Add, remove, or modify units",
                category=ActionCategory.MILITARY,
                icon="⚔️",
                hotkey="U",
                can_execute=lambda army: True,
                get_tooltip=lambda army: f"Number of units: {len(army.units)}",
            ),
        )

        # ========== City Actions ==========
        self.register_action(
            "City",
            Action(
                id="expel_army",
                name="Expel Army",
                description="Expel an army from the garrison",
                category=ActionCategory.MILITARY,
                icon="⬅️",
                hotkey="X",
                can_execute=lambda city: len(city.garrison) > 0,
                get_tooltip=lambda city: f"Garrison: {len(city.garrison)} army/armies",
            ),
        )

        self.register_action(
            "City",
            Action(
                id="expel_army",
                name="Expel Army",
                description="Select and expel an army from the garrison",
                category=ActionCategory.MILITARY,
                icon="⬅️",
                hotkey="X",
                can_execute=lambda city: len(city.garrison) > 0,
                execute=lambda city, **kwargs: city.expel_specific_army(
                    kwargs.get("army")
                ),
                get_tooltip=lambda city: f"Garrison: {len(city.garrison)} army/armies",
            ),
        )

        self.register_action(
            "City",
            Action(
                id="view_garrison",
                name="View Garrison",
                description="Display all armies in the city",
                category=ActionCategory.MANAGEMENT,
                icon="🛡️",
                hotkey="G",
                can_execute=lambda city: len(city.garrison) > 0,
                get_tooltip=lambda city: f"Garrison: {len(city.garrison)} army/armies",
            ),
        )

        self.register_action(
            "City",
            Action(
                id="change_owner",
                name="Change Owner",
                description="Transfer city ownership",
                category=ActionCategory.MANAGEMENT,
                icon="👑",
                can_execute=lambda city: True,
                get_tooltip=lambda city: f"Current owner: {city.owner}",
            ),
        )

        self.register_action(
            "City",
            Action(
                id="build",
                name="Build",
                description="Construct new buildings",
                category=ActionCategory.PRODUCTION,
                icon="🏗️",
                hotkey="B",
                can_execute=lambda city: True,
            ),
        )

        # ========== Spy Actions ==========
        self.register_action(
            "Spy",
            Action(
                id="assign_mission",
                name="Assign Mission",
                description="Assign a new mission to the spy",
                category=ActionCategory.ESPIONAGE,
                icon="🎯",
                hotkey="M",
                can_execute=lambda spy: spy.state.name == "READY",
                get_tooltip=lambda spy: "Only available when spy is ready",
            ),
        )

        self.register_action(
            "Spy",
            Action(
                id="cancel_mission",
                name="Cancel Mission",
                description="Cancel the current mission",
                category=ActionCategory.ESPIONAGE,
                icon="❌",
                hotkey="C",
                can_execute=lambda spy: spy.state.name == "ON_MISSION",
                get_tooltip=lambda spy: f"Current mission: {spy.mission}",
            ),
        )

        self.register_action(
            "Spy",
            Action(
                id="level_up",
                name="Level Up",
                description="Upgrade spy skills",
                category=ActionCategory.MANAGEMENT,
                icon="⬆️",
                hotkey="L",
                can_execute=lambda spy: True,
                get_tooltip=lambda spy: f"Current level: {spy.skill_level}",
            ),
        )

        self.register_action(
            "Spy",
            Action(
                id="view_intel",
                name="View Intelligence",
                description="Display collected intelligence",
                category=ActionCategory.ESPIONAGE,
                icon="📊",
                hotkey="I",
                can_execute=lambda spy: True,
            ),
        )

    def register_action(self, entity_type: str, action: Action):
        """Register a new action for a specific entity type"""
        if entity_type not in self.actions:
            self.actions[entity_type] = []
        self.actions[entity_type].append(action)

    def get_actions(self, entity) -> List[Action]:
        """Get all available actions for a specific entity"""
        entity_type = entity.__class__.__name__

        if entity_type not in self.actions:
            return []

        # Return only actions available for execution
        return [
            action
            for action in self.actions[entity_type]
            if action.is_available(entity)
        ]

    def get_all_actions(self, entity) -> List[Action]:
        """Get all actions (available and unavailable)"""
        entity_type = entity.__class__.__name__
        return self.actions.get(entity_type, [])

    def get_actions_by_category(self, entity, category: ActionCategory) -> List[Action]:
        """Get available actions by category"""
        return [
            action for action in self.get_actions(entity) if action.category == category
        ]

    def execute_action(self, entity, action_id: str, **kwargs):
        """Execute a specific action"""
        entity_type = entity.__class__.__name__

        if entity_type not in self.actions:
            print(f"[ActionsSystem] No actions registered for {entity_type}")
            return False

        for action in self.actions[entity_type]:
            if action.id == action_id:
                if action.is_available(entity):
                    action.run(entity, **kwargs)
                    return True
                else:
                    print(f"[ActionsSystem] Action '{action_id}' not available")
                    return False

        print(f"[ActionsSystem] Action '{action_id}' not found")
        return False
