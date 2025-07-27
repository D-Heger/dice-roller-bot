import re
import random
from typing import Dict, List, Optional, Union

class DiceParser:
    """Utility class for parsing and rolling dice expressions"""
    
    def __init__(self, max_dice: int = 100, max_sides: int = 1000):
        self.max_dice = max_dice
        self.max_sides = max_sides
    
    def parse_expression(self, expression: str) -> Optional[Dict]:
        """
        Parse dice expressions like 1d20+5, 2d6-1, etc.
        
        Args:
            expression: Dice expression string
            
        Returns:
            Parsed result dictionary or None if invalid
        """
        pattern = r'(\d*)d(\d+)([+-]?\d*)'
        matches = re.findall(pattern, expression.lower().replace(' ', ''))
        
        if not matches:
            return None
        
        rolls = []
        total_modifier = 0
        
        for match in matches:
            num_dice = int(match[0]) if match[0] else 1
            dice_sides = int(match[1])
            modifier = int(match[2]) if match[2] else 0
            
            # Validate limits
            if num_dice > self.max_dice:
                raise ValueError(f"Too many dice! Maximum is {self.max_dice}")
            if dice_sides > self.max_sides:
                raise ValueError(f"Too many sides! Maximum is {self.max_sides}")
            if dice_sides < 1:
                raise ValueError("Dice must have at least 1 side")
            
            dice_rolls = [random.randint(1, dice_sides) for _ in range(num_dice)]
            rolls.append({
                'notation': f"{num_dice}d{dice_sides}",
                'rolls': dice_rolls,
                'sum': sum(dice_rolls),
                'num_dice': num_dice,
                'sides': dice_sides
            })
            total_modifier += modifier
        
        return {
            'rolls': rolls,
            'modifier': total_modifier,
            'expression': expression
        }
    
    def roll_simple(self, num_dice: int, sides: int, modifier: int = 0) -> Dict:
        """Simple dice roll helper"""
        if num_dice > self.max_dice or sides > self.max_sides:
            raise ValueError("Dice or sides exceed maximum allowed")
        
        rolls = [random.randint(1, sides) for _ in range(num_dice)]
        return {
            'rolls': rolls,
            'sum': sum(rolls),
            'modifier': modifier,
            'total': sum(rolls) + modifier
        }
    
    @staticmethod
    def format_result(parsed_result: Dict) -> str:
        """Format roll result for display"""
        rolls = parsed_result['rolls']
        modifier = parsed_result['modifier']
        
        total = sum(roll['sum'] for roll in rolls) + modifier
        
        details = []
        for roll in rolls:
            roll_str = f"{roll['notation']}: [{', '.join(str(r) for r in roll['rolls'])}]"
            details.append(roll_str)
        
        result_parts = [" + ".join(details)]
        
        if modifier != 0:
            result_parts.append(f"{'+' if modifier >= 0 else ''}{modifier}")
        
        return {
            'details': " ".join(result_parts),
            'total': total,
            'rolls': rolls,
            'modifier': modifier
        }