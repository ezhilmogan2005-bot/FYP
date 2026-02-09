"""
Spray Duration Calculation Logic Block

This module provides the core logic for determining spray duration
based on infection level detected by the AI model.

Logic:
- infection_level <= 0%:      0 seconds (no spray)
- 0% < infection_level < 25%: 3 seconds (low treatment)
- 25% <= infection_level < 50%: 5 seconds (moderate treatment)
- 50% <= infection_level < 75%: 8 seconds (heavy treatment)
- infection_level >= 75%:     10 seconds (maximum treatment)
"""


def calculate_spray_duration(infection_level):
    """
    Calculate spray duration based on infection level.
    
    This function implements the decision logic for determining
    how long the pesticide pump should run based on the severity
    of the detected plant disease.
    
    Args:
        infection_level (float): Percentage of leaf area infected (0-100)
    
    Returns:
        int: Spray duration in seconds
        
    Example:
        >>> calculate_spray_duration(10)
        3
        >>> calculate_spray_duration(45)
        5
        >>> calculate_spray_duration(80)
        10
    """
    if infection_level <= 0:
        # No infection detected - no spray needed
        return 0
    elif infection_level < 25:
        # Low infection - minimal treatment
        return 3
    elif infection_level < 50:
        # Moderate infection - standard treatment
        return 5
    elif infection_level < 75:
        # High infection - extended treatment
        return 8
    else:
        # Severe infection - maximum treatment
        return 10


def calculate_spray_with_safety(infection_level, soil_moisture):
    """
    Calculate spray duration with soil moisture safety check.
    
    Only allows spraying if soil moisture is within safe range (40-70%)
    to prevent plant damage or pesticide dilution.
    
    Args:
        infection_level (float): Percentage of leaf area infected (0-100)
        soil_moisture (float): Current soil moisture percentage
    
    Returns:
        dict: Spray decision with duration and safety status
        {
            'spray_allowed': bool,
            'duration': int,
            'reason': str
        }
    """
    # Check soil moisture safety
    SOIL_MOISTURE_MIN = 40
    SOIL_MOISTURE_MAX = 70
    
    moisture_safe = SOIL_MOISTURE_MIN <= soil_moisture <= SOIL_MOISTURE_MAX
    
    if not moisture_safe:
        return {
            'spray_allowed': False,
            'duration': 0,
            'reason': f'Soil moisture {soil_moisture}% outside safe range ({SOIL_MOISTURE_MIN}-{SOIL_MOISTURE_MAX}%)'
        }
    
    # Calculate spray duration based on infection level
    duration = calculate_spray_duration(infection_level)
    
    if duration == 0:
        return {
            'spray_allowed': False,
            'duration': 0,
            'reason': 'No infection detected - no spray needed'
        }
    
    return {
        'spray_allowed': True,
        'duration': duration,
        'reason': f'Infection level {infection_level}% - spraying for {duration} seconds'
    }


def get_spray_recommendation(infection_level, disease_name="Unknown"):
    """
    Get comprehensive spray recommendation with dosage information.
    
    Args:
        infection_level (float): Percentage of leaf area infected
        disease_name (str): Name of detected disease
    
    Returns:
        dict: Complete spray recommendation
    """
    duration = calculate_spray_duration(infection_level)
    
    recommendations = {
        0: {
            'action': 'No action needed',
            'message': 'Plant appears healthy. Continue regular monitoring.',
            'frequency': 'Weekly inspection'
        },
        3: {
            'action': 'Light treatment',
            'message': f'Low-level {disease_name} detected. Apply preventive treatment.',
            'frequency': 'Single application'
        },
        5: {
            'action': 'Standard treatment',
            'message': f'Moderate {disease_name} detected. Apply full treatment.',
            'frequency': 'Apply now, re-evaluate in 3 days'
        },
        8: {
            'action': 'Intensive treatment',
            'message': f'Severe {disease_name} detected. Apply intensive treatment.',
            'frequency': 'Apply now, repeat in 2 days'
        },
        10: {
            'action': 'Maximum treatment',
            'message': f'Critical {disease_name} detected! Immediate maximum treatment required.',
            'frequency': 'Apply immediately, repeat daily for 3 days'
        }
    }
    
    return {
        'duration': duration,
        'infection_level': infection_level,
        'disease_name': disease_name,
        **recommendations.get(duration, recommendations[0])
    }


# Example usage and testing
if __name__ == "__main__":
    print("=" * 60)
    print("SPRAY DURATION CALCULATION LOGIC BLOCK")
    print("=" * 60)
    
    # Test cases
    test_cases = [
        (0, 55, "Wheat Brown Rust"),
        (10, 55, "Wheat Brown Rust"),
        (35, 55, "Tomato Early Blight"),
        (60, 55, "Rice Blast"),
        (85, 55, "Potato Late Blight"),
        (45, 35, "Tomato Early Blight"),  # Too dry
        (45, 80, "Tomato Early Blight"),  # Too wet
    ]
    
    for infection, moisture, disease in test_cases:
        print(f"\nTest Case: {disease}")
        print(f"  Infection Level: {infection}%")
        print(f"  Soil Moisture: {moisture}%")
        
        result = calculate_spray_with_safety(infection, moisture)
        print(f"  Spray Allowed: {'YES' if result['spray_allowed'] else 'NO'}")
        print(f"  Duration: {result['duration']} seconds")
        print(f"  Reason: {result['reason']}")
    
    print("\n" + "=" * 60)
