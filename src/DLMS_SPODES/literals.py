from typing import Literal


Attributes = Literal[
    'value', 'scaler_unit', 'status', 'capture_time', 'current_average_value', 'last_average_value', 'start_time_current', 'period', 'number_of_periods', 'mask', 'active_value',
    'active_objects', 'buffer', 'capture_objects', 'capture_period', 'sort_method', 'sort_object', 'entries_in_use', 'profile_entries', 'table', 'table_cell_values', 'status_map',
    'compact_buffer', 'object_list', 'access_rights_list', 'sap_assignment_list', 'image_block_size', 'image_transferred_blocks_status',
    'image_first_not_transferred_block_number', 'image_transfer_enabled', 'image_transfer_status', 'security_policy', 'security_suite', 'push_object_list',
    'send_destination_and_method', 'protection_parameters_get', 'protection_parameters_set', 'function', 'array_components', 'protection_mode', 'time', 'time_zone', 'scripts',
    'entries', 'calendar_name', 'season_profile', 'week_profile', 'thresholds', 'monitored_value', 'executed_script', 'output_state', 'sensor_values', 'action_sets',
    'payment_mode', 'account_balance', 'current_credit_amount', 'unit_charge_active', 'token'
]
Methods = Literal[
    'reset', 'next_period', 'image_transfer_initiate', 'image_block_transfer', 'image_verify', 'image_activate', 'security_activate', 'push', 'get_protected_attributes',
    'set_protected_attributes', 'invoke_protected_method', 'add_element', 'remove_element', 'adjust_to_measurement', 'adjust_to_quarter', 'adjust_to_minute', 'activate',
    'disconnect', 'reconnect', 'credit_payment', 'debit_payment', 'set_credit', 'collect_charge', 'process_token'
]
