OpenADR 3.1 Certified VEN

This version includes optimization parameters for thermostats, lighting, and switched devices.

## Configuration Parameter
1. VTN Base URL
    This is the base URL for your OpenADR VTN. If none given, the plugin will not start.

2. Auth Server URL
    This is the URL to the auth server. If it starts with http or https, then the whole URL is used. If not, it's appended to '''VTN Base URL'''. If blank, 
    default path is appended to '''VTN Base URL'''

3. Client ID
    This is the Client ID part of the OAuth credentials provided to you by your utility. If none given, the plugin will not start.

4. Client Secret 
    This is the Client Secret part of the OAuth credentials provided to you by your utility. If none given, the plugin will not start.

5. Duration Scale
    Use mostly for testing to scale up/down the event durations. i.e. 
        Scale=1/5, changes the duration to duration /= 5
        scale=5, changes the duration to duration *= 5

6. Event Mode
    Case insenitive '''Price''' or '''Simple''' or '''Both'''
    '''Price''' - The VEN will only process Price and GHG events 
    '''Simple''' - The VEN will only process Simple/Level events for DR
    '''Both''' - The VEN will process both Price and Simple events
    Default: Price 

7. Program ID
    Some utilities may provide a Program ID that's used to get information from the VTN. Supply it here.
    If blank, none will be used.

8. Test Mode
    True, Yes, 1 (case insensitive) put the module in test mode causing shorter opt expiry duration, and 
    faster intervals.

## Runtime 
At runtime, the following parameters are configurable.

### Comfort Level 
Allows you to let the platform know what your comfort level is.
(0=Max Comfort, 1=Balanced, 2=Max Savings)
Default: Max Comfort

### Desired Cooling Setpoint (°F)
This is your desired cool set point when no optimizations are running.
Default: 74°F

### Desired Heating Setpoint (°F)
This is your desired heat set point when no optimizations are running.
Default: 77°F

### Min Setpoint Offset (°F)
This is the set point offset used for Max Comfort.
Default: 1°F

### Max Setpoint Offset (°F)
This is the set point offset used for Max Savings.
Default: 4°F

### Desired Light Level (%)
This is your desired light level (dimmable) when no optimizations are running.
Default: 100%

### Min Light Adjustment Offset (%)
This is the light adjustment offset used for Max Comfort.
Default: 0%

### Max Light Adjustment Offset (%)
This is the light adjustment offset used for Max Savings.
Default: 50%

### Min Duty Cycle Offset (%)
This is the duty cycle offset used for Max Comfort.
Default: 100%

### Max Duty Cycle Offset (%)
This is the duty cycle offset used for Max Savings.
Default: 30%

