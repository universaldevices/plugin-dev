"""
This class represents Auto Demand/Response Configuration for the system (ISY).
"""

class AutoDRConfig:
    # Default for Far = 12 hours from now
    UD_ADR_CONFIG_FAR = 43200  # 12 hours from now
    
    # Default for Near = 6 hours from now
    UD_ADR_CONFIG_NEAR = 21600  # 6 hours from now
    
    # Default for Very Near = 3 hours from now
    UD_ADR_CONFIG_VERY_NEAR = 10800  # 3 hours from now
    
    # Default thermostat offset when the event is Pending
    UD_ADR_DEFAULT_PENDING_OFFSET = 0
    
    # Default thermostat offset when the mode is normal
    UD_ADR_DEFAULT_NORMAL_OFFSET = 0
    
    # Default thermostat offset when the mode is moderate
    UD_ADR_DEFAULT_MODERATE_OFFSET = 0
    
    # Default thermostat offset when the mode is high
    UD_ADR_DEFAULT_HIGH_OFFSET = 0
    
    # Default thermostat offset when the mode is special
    UD_ADR_DEFAULT_SPECIAL_OFFSET = 0
    
    # Default Load Controller Duty Cycle when the mode is normal
    UD_ADR_DEFAULT_NORMAL_DC = 0
    
    # Default Load Controller Duty Cycle when the mode is moderate
    UD_ADR_DEFAULT_MODERATE_DC = 0
    
    # Default Load Controller Duty Cycle when the mode is high
    UD_ADR_DEFAULT_HIGH_DC = 0
    
    # Default Load Controller Duty Cycle when the mode is Special
    UD_ADR_DEFAULT_SPECIAL_DC = 0
    
    # Default Load Adjustment when the mode is normal
    UD_ADR_DEFAULT_NORMAL_LA = 0
    
    # Default Load Adjustment when the mode is moderate
    UD_ADR_DEFAULT_MODERATE_LA = 0
    
    # Default Load Adjustment when the mode is high
    UD_ADR_DEFAULT_HIGH_LA = 0
    
    # Default Load Adjustment when the mode is special
    UD_ADR_DEFAULT_SPECIAL_LA = 0
    
    # Unknown Profile
    UD_ADR_PROFILE_UNKNOWN = -1
    
    # Profile 1
    UD_ADR_PROFILE_1 = 0
    
    # Profile 2
    UD_ADR_PROFILE_2 = 1
    
    # Pull, polls the VTN based on polling interval
    UD_ADR_PROFILE_2_PULL = 0
    
    # Push, the VTN submits requests to ISY
    UD_ADR_PROFILE_2_PUSH = 1
    
    # Compliance level 2.0a
    UD_ADR_PROFILE_COMPLIANCE_2A = 0
    
    # Compliance level 2.0b
    UD_ADR_PROFILE_COMPLIANCE_2B = 1
    
    # Compliance level 2.0c
    UD_ADR_PROFILE_COMPLIANCE_2C = 2
    
    # New Style
    OADR_DEFAULT_COOL_SETPOINT_BASELINE = 7200
    OADR_DEFAULT_HEAT_SETPOINT_BASELINE = 7000
    OADR_DEFAULT_DIMMER_LEVEL_BASELINE = 10000
    OADR_CONTROL_STYLE_LEGACY = 0x00
    OADR_CONTROL_STYLE_NEW = 0x01
    OADR_DEFAULT_CONTROL_STYLE = OADR_CONTROL_STYLE_LEGACY  # the old should do the old
    
    # Configuration files
    AUTO_DR_CONFIG_FILE = "/CONF/ADR.CFG"
    AUTO_DR_REPORTS_CONFIG_FILE = "/CONF/ADRR.CFG"
    AUTO_DR_OPT_CONFIG_FILE = "/CONF/ADROPT.CFG"
    
    # URL endpoints
    AUTO_DR_OPS_BASE_URL = "/rest/oadr"
    AUTO_DR_OPS_CLEAR_EVENTS_URL = AUTO_DR_OPS_BASE_URL + "/clear"
    AUTO_DR_OPS_REGISTER_URL = AUTO_DR_OPS_BASE_URL + "/party/register"
    AUTO_DR_OPS_UN_REGISTER_URL = AUTO_DR_OPS_BASE_URL + "/party/unregister"
    AUTO_DR_OPS_QUERY_REG_URL = AUTO_DR_OPS_BASE_URL + "/party/queryreg"
    AUTO_DR_OPS_RENEW_RE_REGISTER_URL = AUTO_DR_OPS_BASE_URL + "/party/reregister?type=renew"
    AUTO_DR_OPS_REFRESH_RE_REGISTER_URL = AUTO_DR_OPS_BASE_URL + "/party/reregister?type=refresh"
    AUTO_DR_OPS_REG_USAGE_REPORT_URL = AUTO_DR_OPS_BASE_URL + "/report/register?type=usage"
    AUTO_DR_OPS_REG_STATUS_REPORT_URL = AUTO_DR_OPS_BASE_URL + "/report/register?type=status"
    AUTO_DR_OPS_REG_HISTORY_REPORT_URL = AUTO_DR_OPS_BASE_URL + "/report/register?type=history"
    AUTO_DR_OPS_REG_ALL_REPORTS_URL = AUTO_DR_OPS_BASE_URL + "/report/register?type=all"
    AUTO_DR_OPS_REPORTS_CURRENT_STATUS_URL = AUTO_DR_OPS_BASE_URL + "/report/status"
    AUTO_DR_OPS_OPTS_SCHEDULES = AUTO_DR_OPS_BASE_URL + "/opts"
    AUTO_DR_OPS_OPT_CANCEL = AUTO_DR_OPS_BASE_URL + "/opts/cancel"
    AUTO_DR_OPS_OPTS_CANCEL_ALL = AUTO_DR_OPS_BASE_URL + "/opts/cancelAll"
    AUTO_DR_OPS_OPTS_CLEAR_INACTIVE = AUTO_DR_OPS_BASE_URL + "/opts/clear"
    
    AUTO_DR_OPT_IN_COMMAND = "optin"
    AUTO_DR_OPT_OUT_COMMAND = "optout"
    
    @staticmethod
    def get_cancel_opt_schedule_url(id):
        """Get the cancel opt schedule URL for a given ID"""
        return f"{AutoDRConfig.AUTO_DR_OPS_OPT_CANCEL}/{id}"
    
    def __init__(self, url=None, confirm_url=None, polling_interval=60, user_id=None, password=None,
                 far=None, near=None, very_near=None,
                 normal_offset=None, moderate_offset=None, high_offset=None,
                 normal_dc=None, moderate_dc=None, high_dc=None,
                 normal_la=None, moderate_la=None, high_la=None,
                 revert=False, enabled=False, profile=None,
                 control_style=None, cool_setpoint_baseline=None, 
                 heat_setpoint_baseline=None, dimmer_level_baseline=None):
        """
        Constructor
        
        Creates an AutoDRConfig object from the given parameters
        
        Args:
            url: Auto DR Server's Address
            confirm_url: the URL to which confirmations are sent
            polling_interval: Auto DR's Polling Interval
            user_id: Auto DR Server's Userid
            password: Auto DR Server's Password
            far: The far period
            near: The near period
            very_near: The very near period
            normal_offset: thermostat offset to be applied when in Normal mode
            moderate_offset: thermostat offset to be applied when in Moderate mode
            high_offset: thermostat offset to be applied when in High mode
            normal_dc: Load Controller Duty Cycle to be applied in Normal mode
            moderate_dc: Load Controller Duty Cycle to be applied in Moderate mode
            high_dc: Load Controller Duty Cycle to be applied in High mode
            normal_la: Load Adjustment% to be applied in Normal mode
            moderate_la: Load Adjustment% be applied in Moderate mode
            high_la: Load Adjustment% to be applied in High mode
            revert: whether or not to revert the settings back to those before the start of the event
            enabled: whether or not AutoDR is enabled
            profile: The profile we are operating under
            control_style: how we manage devices
            cool_setpoint_baseline: the baseline based on which we optimize thermostats. MUST MULTIPLE BY 100
            heat_setpoint_baseline: the baseline based on which we optimize thermostats. MUST MULTIPLE BY 100
            dimmer_level_baseline: the baseline based on which we optimize dimmers. MUST MULTIPLE BY 100
        """
        # The OADR profile we are working with
        self.profile = profile if profile is not None else self.UD_ADR_PROFILE_2
        
        # Compliance level (Profile 2 only: a=0, b=1, c=2)
        self.compliance_level = self.UD_ADR_PROFILE_COMPLIANCE_2B
        
        # AutoDR URL
        self.url = url
        
        # URL to which confirmations are sent
        self.confirm_url = confirm_url
        
        # Polling interval
        self.polling_interval = polling_interval
        
        # Evaluation interval for Profile 2
        self.evaluation_interval = 25
        
        # Auto DR Server Account's User ID
        self.user_id = user_id
        
        # Auto DR Server Account's Password
        self.password = password
        
        # The period from start time after which the event is considered Far
        self.far = far if far is not None else self.UD_ADR_CONFIG_FAR
        
        # The period from start time after which the event is considered Near
        self.near = near if near is not None else self.UD_ADR_CONFIG_NEAR
        
        # The period from start time after which the event is considered Very Near
        self.very_near = very_near if very_near is not None else self.UD_ADR_CONFIG_VERY_NEAR
        
        # User defined configuration parameters
        # The offset change to the thermostat when the event is Pending
        self.pending_setpoint_offset = self.UD_ADR_DEFAULT_PENDING_OFFSET
        
        # The offset change to the thermostat when we are in Normal mode
        self.normal_setpoint_offset = normal_offset if normal_offset is not None else self.UD_ADR_DEFAULT_NORMAL_OFFSET
        
        # The offset change to the thermostat when we are in Moderate mode
        self.moderate_setpoint_offset = moderate_offset if moderate_offset is not None else self.UD_ADR_DEFAULT_MODERATE_OFFSET
        
        # The offset change to the thermostat when we are in High mode
        self.high_setpoint_offset = high_offset if high_offset is not None else self.UD_ADR_DEFAULT_HIGH_OFFSET
        
        # The offset change to the thermostat when we are in Special mode
        self.special_setpoint_offset = self.UD_ADR_DEFAULT_SPECIAL_OFFSET
        
        # The duty cycle for Load Controllers when we are in Normal mode
        self.normal_dc = normal_dc if normal_dc is not None else self.UD_ADR_DEFAULT_NORMAL_DC
        
        # The duty cycle for Load Controllers when we are in Moderate mode
        self.moderate_dc = moderate_dc if moderate_dc is not None else self.UD_ADR_DEFAULT_MODERATE_DC
        
        # The duty cycle for Load Controllers when we are in High mode
        self.high_dc = high_dc if high_dc is not None else self.UD_ADR_DEFAULT_HIGH_DC
        
        # The duty cycle for Load Controllers when we are in Special mode
        self.special_dc = self.UD_ADR_DEFAULT_SPECIAL_DC
        
        # The Load Adjustment% when we are in Normal mode
        self.normal_la = normal_la if normal_la is not None else self.UD_ADR_DEFAULT_NORMAL_LA
        
        # The Load Adjustment% when we are in Moderate mode
        self.moderate_la = moderate_la if moderate_la is not None else self.UD_ADR_DEFAULT_MODERATE_LA
        
        # The Load Adjustment% Load Controllers when we are in High mode
        self.high_la = high_la if high_la is not None else self.UD_ADR_DEFAULT_HIGH_LA
        
        # The Load Adjustment% Load Controllers when we are in Special mode
        self.special_la = self.UD_ADR_DEFAULT_SPECIAL_LA
        
        # How do we interact with the VTN
        self.vtn_interaction_mode = self.UD_ADR_PROFILE_2_PULL
        
        # OpenADR 2 - VTN ID
        self.vtn_id = None
        
        # OpenADR 2 - VEN ID
        self.ven_id = None
        
        # OpenADR 2 - Party ID
        self.party_id = None
        
        # OpenADR 2 - Group ID ... could be a comma delimited string with multiple groups
        self.group_id = None
        
        # OpenADR 2 - Resource ID ... could be a comma delimited string with multiple resources
        self.resource_id = None
        
        # OpenADR 2 - Market Context ... could be a comma delimited string with multiple contexts
        self.market_context = None
        
        # Whether or not we should revert to original settings after an event completes
        self.revert = revert
        
        # Whether or not we should use XML Signatures
        self.use_xml_sig = False
        
        # Whether or not ISY should continuously try and query/register to the VTN
        self.auto_reg = False
        
        # Registration ID for 2b
        self.registration_id = None
        
        # Push URL for 2b
        self.push_url_base = None
        
        # Whether or not Auto DR is enabled
        self.enabled = enabled
        
        # New Style
        self.cool_setpoint_baseline = cool_setpoint_baseline if cool_setpoint_baseline is not None else self.OADR_DEFAULT_COOL_SETPOINT_BASELINE
        self.heat_setpoint_baseline = heat_setpoint_baseline if heat_setpoint_baseline is not None else self.OADR_DEFAULT_HEAT_SETPOINT_BASELINE
        self.dimmer_level_baseline = dimmer_level_baseline if dimmer_level_baseline is not None else self.OADR_DEFAULT_DIMMER_LEVEL_BASELINE
        self.control_style = control_style if control_style is not None else self.OADR_DEFAULT_CONTROL_STYLE
    
    def set_pending_offset(self, offset):
        """Set the pending setpoint offset"""
        self.pending_setpoint_offset = offset
    
    def set_profile2_settings(self, compliance_level, vtn_interaction_mode, evaluation_interval,
                             vtn_id, ven_id, party_id, group_id, resource_id, market_context,
                             special_offset, special_dc, special_la, use_xml_sig, auto_reg):
        """
        Sets Profile 2 specific attributes
        
        Args:
            compliance_level: Compliance level
            vtn_interaction_mode: VTN interaction mode
            evaluation_interval: Evaluation interval
            vtn_id: VTN ID
            ven_id: VEN ID
            party_id: Party ID
            group_id: could be comma delimited set of groups
            resource_id: could be comma delimited set of resources
            market_context: could be comma delimited set of contexts
            special_offset: thermostat offset to be applied when in Special mode
            special_dc: Load Controller Duty Cycle to be applied in Special mode
            special_la: Load Adjustment% to be applied in Special mode
            use_xml_sig: Whether or not we should be using XML signature to communicate with the VTN
            auto_reg: Whether or not ISY should continuously query and try to register to the server
        """
        self.compliance_level = compliance_level
        self.vtn_interaction_mode = vtn_interaction_mode
        self.evaluation_interval = evaluation_interval
        self.vtn_id = vtn_id
        self.ven_id = ven_id
        self.party_id = party_id
        self.group_id = group_id
        self.resource_id = resource_id
        self.market_context = market_context
        self.special_setpoint_offset = special_offset
        self.special_dc = special_dc
        self.special_la = special_la
        self.use_xml_sig = use_xml_sig
        self.auto_reg = auto_reg
    
    def set_push_url_base(self, push_url_base):
        """Set the push URL base"""
        self.push_url_base = push_url_base
    
    def is_profile2(self):
        """Whether or not ISY is configured as 2.0 compliant VEN"""
        return self.profile == self.UD_ADR_PROFILE_2
    
    def is_compliance_a(self):
        """Whether or not ISY is compliant with 2.0a"""
        if not self.is_profile2():
            return False
        return self.compliance_level == self.UD_ADR_PROFILE_COMPLIANCE_2A
    
    def is_compliance_b(self):
        """Whether or not ISY is compliant with 2.0b"""
        if not self.is_profile2():
            return False
        return self.compliance_level == self.UD_ADR_PROFILE_COMPLIANCE_2B
    
    def is_compliance_c(self):
        """Whether or not ISY is compliant with 2.0c"""
        if not self.is_profile2():
            return False
        return self.compliance_level == self.UD_ADR_PROFILE_COMPLIANCE_2C
    
    def is_registered(self):
        """
        Whether or not ISY is registered with a VTN
        Requires 2b
        """
        return self.registration_id is not None
    
    def to_dict(self):
        """
        Converts this object to a dictionary representation
        
        Returns:
            Dictionary representation of this configuration
        """
        config = {
            'url': self.url,
            'confirm_url': self.confirm_url,
            'polling_interval': self.polling_interval,
            'user_id': self.user_id,
            'password': self.password,
            'far': self.far,
            'near': self.near,
            'very_near': self.very_near,
            'pending_setpoint_offset': self.pending_setpoint_offset,
            'normal_setpoint_offset': self.normal_setpoint_offset,
            'moderate_setpoint_offset': self.moderate_setpoint_offset,
            'high_setpoint_offset': self.high_setpoint_offset,
            'special_setpoint_offset': self.special_setpoint_offset,
            'normal_dc': self.normal_dc,
            'moderate_dc': self.moderate_dc,
            'high_dc': self.high_dc,
            'special_dc': self.special_dc,
            'normal_la': self.normal_la,
            'moderate_la': self.moderate_la,
            'high_la': self.high_la,
            'special_la': self.special_la,
            'revert': self.revert,
            'enabled': self.enabled,
            'profile': self.profile,
            'control_style': self.control_style,
            'cool_setpoint_baseline': self.cool_setpoint_baseline,
            'heat_setpoint_baseline': self.heat_setpoint_baseline,
            'dimmer_level_baseline': self.dimmer_level_baseline,
        }
        
        if self.is_profile2():
            config.update({
                'compliance_level': self.compliance_level,
                'vtn_interaction_mode': self.vtn_interaction_mode,
                'evaluation_interval': self.evaluation_interval,
                'vtn_id': self.vtn_id,
                'ven_id': self.ven_id,
                'party_id': self.party_id,
                'group_id': self.group_id,
                'resource_id': self.resource_id,
                'market_context': self.market_context,
                'push_url_base': self.push_url_base,
                'use_xml_sig': self.use_xml_sig,
                'auto_reg': self.auto_reg,
                'registration_id': self.registration_id,
            })
        
        return config
    
    def to_xml(self):
        """
        Converts this object to its XML representation
        
        Returns:
            XML string representation of this configuration
        """
        xml_parts = ['<AutoDRConfig>']
        
        xml_parts.append(f'<URL>{self.url if self.url else ""}</URL>')
        xml_parts.append(f'<ConfirmURL>{self.confirm_url if self.confirm_url else ""}</ConfirmURL>')
        xml_parts.append(f'<PollingInterval>{self.polling_interval}</PollingInterval>')
        xml_parts.append(f'<PendingFar>{self.far}</PendingFar>')
        xml_parts.append(f'<PendingNear>{self.near}</PendingNear>')
        xml_parts.append(f'<PendingVeryNear>{self.very_near}</PendingVeryNear>')
        xml_parts.append(f'<PendingOffset>{self.pending_setpoint_offset}</PendingOffset>')
        xml_parts.append(f'<NormalOffset>{self.normal_setpoint_offset}</NormalOffset>')
        xml_parts.append(f'<ModerateOffset>{self.moderate_setpoint_offset}</ModerateOffset>')
        xml_parts.append(f'<HighOffset>{self.high_setpoint_offset}</HighOffset>')
        xml_parts.append(f'<SpecialOffset>{self.special_setpoint_offset}</SpecialOffset>')
        xml_parts.append(f'<NormalDC>{self.normal_dc}</NormalDC>')
        xml_parts.append(f'<ModerateDC>{self.moderate_dc}</ModerateDC>')
        xml_parts.append(f'<HighDC>{self.high_dc}</HighDC>')
        xml_parts.append(f'<SpecialDC>{self.special_dc}</SpecialDC>')
        xml_parts.append(f'<NormalLA>{self.normal_la}</NormalLA>')
        xml_parts.append(f'<ModerateLA>{self.moderate_la}</ModerateLA>')
        xml_parts.append(f'<HighLA>{self.high_la}</HighLA>')
        xml_parts.append(f'<SpecialLA>{self.special_la}</SpecialLA>')
        xml_parts.append(f'<Revert>{"true" if self.revert else "false"}</Revert>')
        xml_parts.append(f'<ControlStyle>{self.control_style}</ControlStyle>')
        xml_parts.append(f'<CoolSPBaseline>{self.cool_setpoint_baseline}</CoolSPBaseline>')
        xml_parts.append(f'<HeatSPBaseline>{self.heat_setpoint_baseline}</HeatSPBaseline>')
        xml_parts.append(f'<DimmerLevelBaseline>{self.dimmer_level_baseline}</DimmerLevelBaseline>')
        xml_parts.append(f'<UserID>{self.user_id if self.user_id else ""}</UserID>')
        xml_parts.append(f'<Password>{self.password if self.password else ""}</Password>')
        xml_parts.append(f'<Enabled>{"true" if self.enabled else "false"}</Enabled>')
        xml_parts.append(f'<Profile>{self.profile}</Profile>')
        
        if self.is_profile2():
            xml_parts.append(f'<ComplianceLevel>{self.compliance_level}</ComplianceLevel>')
            xml_parts.append(f'<VtnInteractionMode>{self.vtn_interaction_mode}</VtnInteractionMode>')
            xml_parts.append(f'<EvaluationInterval>{self.evaluation_interval}</EvaluationInterval>')
            if self.vtn_id:
                xml_parts.append(f'<VtnID>{self.vtn_id}</VtnID>')
            if self.ven_id:
                xml_parts.append(f'<VenID>{self.ven_id}</VenID>')
            if self.party_id:
                xml_parts.append(f'<PartyID>{self.party_id}</PartyID>')
            if self.group_id:
                xml_parts.append(f'<GroupID>{self.group_id}</GroupID>')
            if self.resource_id:
                xml_parts.append(f'<ResourceID>{self.resource_id}</ResourceID>')
            if self.market_context:
                xml_parts.append(f'<MarketContext>{self.market_context}</MarketContext>')
            if self.push_url_base:
                xml_parts.append(f'<PushURLBase>{self.push_url_base}</PushURLBase>')
            xml_parts.append(f'<UseXmlSignature>{"true" if self.use_xml_sig else "false"}</UseXmlSignature>')
            xml_parts.append(f'<AutoReg>{"true" if self.auto_reg else "false"}</AutoReg>')
        
        xml_parts.append('</AutoDRConfig>')
        
        return ''.join(xml_parts)


class ThermostatOptimizer:
    """
    Thermostat optimization algorithm for demand response across four grid states:
    Normal, Moderate, High, and Emergency (Special).
    
    The algorithm adjusts thermostat setpoints based on grid conditions while respecting
    user comfort preferences. If a customer manually changes setpoints during an active
    optimization state, the system opts out until the next day.
    """
    
    # Grid states
    STATE_NORMAL = 0
    STATE_MODERATE = 1
    STATE_HIGH = 2
    STATE_EMERGENCY = 3  # Special/Emergency
    
    def __init__(self, cool_baseline, heat_baseline, 
                 normal_offset=0, moderate_offset=1, high_offset=2, emergency_offset=3):
        """
        Initialize the thermostat optimizer.
        
        Args:
            cool_baseline: Comfort level baseline for cooling (°F)
            heat_baseline: Comfort level baseline for heating (°F)
            normal_offset: Offset for normal state (default: 0)
            moderate_offset: Offset for moderate state (default: 1)
            high_offset: Offset for high state (default: 2)
            emergency_offset: Offset for emergency state (default: 3)
        """
        self.cool_baseline = cool_baseline
        self.heat_baseline = heat_baseline
        self.normal_offset = normal_offset
        self.moderate_offset = moderate_offset
        self.high_offset = high_offset
        self.emergency_offset = emergency_offset
        
        # Track opt-out status
        self.opted_out = False
        self.opt_out_until = None  # Timestamp until which we're opted out
        
        # Track last applied setpoints to detect user changes
        self.last_applied_cool_sp = None
        self.last_applied_heat_sp = None
    
    def get_offset_for_state(self, state):
        """
        Get the offset value for a given grid state.
        
        Args:
            state: Grid state (STATE_NORMAL, STATE_MODERATE, STATE_HIGH, STATE_EMERGENCY)
            
        Returns:
            Offset value for the state
        """
        if state == self.STATE_NORMAL:
            return self.normal_offset
        elif state == self.STATE_MODERATE:
            return self.moderate_offset
        elif state == self.STATE_HIGH:
            return self.high_offset
        elif state == self.STATE_EMERGENCY:
            return self.emergency_offset
        else:
            return 0
    
    def check_user_override(self, current_cool_sp, current_heat_sp, grid_state):
        """
        Check if the user has manually changed setpoints during an active optimization state.
        If detected, opt out of optimization until the next day.
        
        Args:
            current_cool_sp: Current cooling setpoint from thermostat
            current_heat_sp: Current heating setpoint from thermostat
            grid_state: Current grid state
            
        Returns:
            True if user override detected and opted out, False otherwise
        """
        # Only check for overrides during non-normal states
        if grid_state == self.STATE_NORMAL:
            return False
        
        # If we haven't applied any setpoints yet, no override possible
        if self.last_applied_cool_sp is None or self.last_applied_heat_sp is None:
            return False
        
        # Check if current setpoints differ from what we last applied
        # Allow for small floating point differences
        cool_changed = abs(current_cool_sp - self.last_applied_cool_sp) > 0.5
        heat_changed = abs(current_heat_sp - self.last_applied_heat_sp) > 0.5
        
        if cool_changed or heat_changed:
            # User has overridden - opt out until next day
            self.opt_out()
            return True
        
        return False
    
    def opt_out(self):
        """
        Opt out of optimization until the next day (midnight).
        """
        from datetime import datetime, timedelta
        
        self.opted_out = True
        # Set opt-out until midnight of the next day
        now = datetime.now()
        next_day = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        self.opt_out_until = next_day
    
    def check_opt_out_status(self):
        """
        Check if we're still opted out, and clear the opt-out if time has expired.
        
        Returns:
            True if currently opted out, False otherwise
        """
        if not self.opted_out:
            return False
        
        from datetime import datetime
        
        if self.opt_out_until and datetime.now() >= self.opt_out_until:
            # Opt-out period has expired
            self.opted_out = False
            self.opt_out_until = None
            return False
        
        return True
    
    def optimize_thermostat(self, current_cool_sp, current_heat_sp, grid_state):
        """
        Optimize thermostat setpoints based on current grid state and comfort baselines.
        
        Algorithm:
        - Normal state: No changes
        - Other states: 
          * Cooling: If current < cool_baseline + offset, adjust to cool_baseline + offset
          * Heating: If current > heat_baseline - offset, adjust to heat_baseline - offset
        
        Args:
            current_cool_sp: Current cooling setpoint (°F)
            current_heat_sp: Current heating setpoint (°F)
            grid_state: Current grid state (0=Normal, 1=Moderate, 2=High, 3=Emergency)
            
        Returns:
            Tuple of (new_cool_sp, new_heat_sp, adjustment_made, message)
            - new_cool_sp: Optimized cooling setpoint
            - new_heat_sp: Optimized heating setpoint
            - adjustment_made: True if any adjustment was made
            - message: Description of what was done
        """
        # Check if we're opted out
        if self.check_opt_out_status():
            return (current_cool_sp, current_heat_sp, False, 
                    f"Opted out until {self.opt_out_until.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check for user override
        if self.check_user_override(current_cool_sp, current_heat_sp, grid_state):
            return (current_cool_sp, current_heat_sp, False,
                    "User override detected - opted out until next day")
        
        # Normal state: no changes
        if grid_state == self.STATE_NORMAL:
            self.last_applied_cool_sp = current_cool_sp
            self.last_applied_heat_sp = current_heat_sp
            return (current_cool_sp, current_heat_sp, False, "Normal state - no optimization")
        
        # Get offset for current state
        offset = self.get_offset_for_state(grid_state)
        
        # Calculate target setpoints
        target_cool_sp = self.cool_baseline + offset
        target_heat_sp = self.heat_baseline - offset
        
        # Initialize new setpoints
        new_cool_sp = current_cool_sp
        new_heat_sp = current_heat_sp
        adjustments = []
        
        # Cooling optimization
        # If current cooling setpoint is LOWER than baseline + offset, raise it
        if current_cool_sp < target_cool_sp:
            new_cool_sp = target_cool_sp
            adjustments.append(f"Cool SP: {current_cool_sp}°F → {new_cool_sp}°F")
        
        # Heating optimization
        # If current heating setpoint is HIGHER than baseline - offset, lower it
        if current_heat_sp > target_heat_sp:
            new_heat_sp = target_heat_sp
            adjustments.append(f"Heat SP: {current_heat_sp}°F → {new_heat_sp}°F")
        
        # Track what we applied
        self.last_applied_cool_sp = new_cool_sp
        self.last_applied_heat_sp = new_heat_sp
        
        # Build message
        state_names = {
            self.STATE_NORMAL: "Normal",
            self.STATE_MODERATE: "Moderate",
            self.STATE_HIGH: "High",
            self.STATE_EMERGENCY: "Emergency"
        }
        state_name = state_names.get(grid_state, "Unknown")
        
        if adjustments:
            message = f"{state_name} state (offset={offset}°F): " + ", ".join(adjustments)
            return (new_cool_sp, new_heat_sp, True, message)
        else:
            message = f"{state_name} state (offset={offset}°F): No adjustment needed"
            return (new_cool_sp, new_heat_sp, False, message)
    
    def reset_opt_out(self):
        """
        Manually reset the opt-out status (e.g., for testing or user request).
        """
        self.opted_out = False
        self.opt_out_until = None
        self.last_applied_cool_sp = None
        self.last_applied_heat_sp = None
