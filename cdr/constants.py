import pandas as pd

CDR_TYPES = {
    '00000000': {
        'method': 'parse_standard',
        'report': 'standard'
    },
    '00000001': {
        'method': 'parse_intermediate',
        'report': None
    },
    '00000004': {
        'method': 'parse_queue',
        'report': 'queue'
    },
    '00000005': {
        'method': 'parse_call_forwarding',
        'report': None
    },
    '10000001': {
        'method': 'parse_long_call',
        'report': None
    },
    '10000010': {
        'method': 'parse_change_of_software',
        'report': None
    },
    '10000100': {
        'method': 'parse_feature',
        'report': None
    },
    '10000101': {
        'method': 'parse_half_call',
        'report': None
    },
    '10000111': {
        'method': 'parse_qos',
        'report': None
    }
}

RESULTS = {
    0: 'Completada',
    1: 'Ocupado',
    2: 'Numero invalido',
    3: 'Lineas no disponibles',
    4: 'Abandono',
    5: 'No atendida',
    6: 'Problema de red',
    7: 'Desconocido',
    8: 'Cuenta no existente',
    9: 'No autorizado',
    10: 'LNP',
    11: 'LNP bis',
    12: 'Automatic Collect Call Blocking'
}

ABANDON = {
    1: 0,
    2: 1
}

ELASTICSEARCH_STANDARD_MAPPINGS = {
  "@timestamp": {
    "type": "date"
  },
  "call_duration": {
    "type": "long"
  },
  "detination": {
    "type": "keyword"
  },
  "hang_time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  },
  "id": {
    "type": "keyword"
  },
  "incoming_leg_hang_time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  },
  "incoming_leg_pickup_time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  },
  "origin": {
    "type": "keyword"
  },
  "osv_destination": {
    "type": "keyword"
  },
  "osv_origin": {
    "type": "keyword"
  },
  "outgoing_leg_hang_time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  },
  "outgoing_leg_pickup_time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  },
  "pickup_time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  },
  "result": {
    "type": "keyword"
  },
  "time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  },
  "switch_id": {
    "type": "keyword"
  }
}

ELASTICSEARCH_QUEUE_MAPPINGS = {
  "@timestamp": {
    "type": "date"
  },
  "abandon": {
    "type": "keyword"
  },
  "destination": {
    "type": "keyword"
  },
  "end_time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  },
  "id": {
    "type": "keyword"
  },
  "queue_id": {
    "type": "keyword"
  },
  "start_time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  },
  "time": {
    "type": "date",
    "format": "yyyy-MM-dd HH:mm:ss"
  }
}

STANDARD_FIELDS = [
    'switch_id',
    'id',
    'time',
    'duration',
    'origin',
    'destination',
    'result',
    'osv_origin',
    'osv_destination',
    'pickup_time',
    'hang_time',
    'incoming_leg_pickup_time',
    'incoming_leg_hang_time',
    'outgoing_leg_pickup_time',
    'outgoing_leg_hang_time',
    'wait_time',
    'session_time',
    'duration_minutes',
    'is_agent_call',
    'is_abandoned_call'
]

QUEUE_FIELDS = [
    'id',
    'time',
    'queue_id',
    'start_time',
    'end_time',
    'abandon',
    'destination',
    'total_time'
]

FIELDS_COLUMNS = ['name', 'index', 'type']

STANDARD_RECORD_TYPE = '00000000'

QUEUE_RECORD_TYPE = '00000004'

FIELDS_DF = {
  STANDARD_RECORD_TYPE: pd.DataFrame([
      ['sequential_record_number', 1, 'int64'],
      ['record_type', 2, 'category'],
      ['start_time', 3, 'date'],
      ['duration_of_call', 4, 'int64'],
      ['switch_id', 5, 'category'],
      ['record_id', 6],
      ['customer_name', 7, 'object'],
      ['call_segment_duration', 9, 'int64'],
      ['terminating_number', 11],
      ['originating_number', 12],
      ['paying_party', 13],
      ['attempt_indicator', 18, 'category'],
      ['release_cause', 19, 'category'],
      ['originating_party_identifier', 40, 'category'],
      ['terminating_party_identifier', 41, 'category'],
      ['call_answer_time', 48, 'date'],
      ['call_release_time', 49, 'date'],
      ['incoming_leg_connect_time', 50, 'date'],
      ['incoming_leg_release_time', 51, 'date'],
      ['outgoing_leg_connect_time', 52, 'date'],
      ['outgoing_leg_release_time', 53, 'date'],
      ['per_call_feature', 64, 'category'],
      ['forwarding_party', 65],
      ['intermediate_indicator', 66],
      ['originating_side_codec_negotiated', 67, 'category'],
      ['terminating_side_codec_negotiated', 77, 'category'],
      ['bg_orig_mdr_customer_id', 87],
      ['bg_term_mdr_customer_id', 88],
      ['bg_authorization_code', 89],
      ['bg_account_code', 90],
      ['bg_orig_facility_type', 91, 'category'],
      ['bg_term_facility_type', 92, 'category'],
      ['bg_orig_station_facility_id', 93],
      ['bg_term_station_facility_id', 94],
      ['bg_call_completion_code', 95, 'category'],
      ['bg_business_feature_code', 96, 'category'],
      ['bg_access_code', 99],
      ['additional_cdrs', 100, 'category'],
      ['original_dialed_digits', 101],
      ['bg_department_name', 102],
      ['number_of_fax_pages_sent_or_received', 103],
      ['media_type', 104, 'category'],
      ['incoming_phone_context', 105],
      ['per_call_feature_extension', 106, 'category'],
      ['call_event_indicator', 107, 'category'],
      ['secure_rtp_indicator', 108, 'category'],
      ['originating_domain', 109],
      ['terminating_domain', 110],
      ['traffic_type_id', 111],
      ['global_call_id_node', 121],
      ['global_call_id_sequence', 122],
      ['transferred_from_dn', 123],
      ['global_thread_id_node', 124],
      ['global_thread_id_sequence', 125],
      ['ingress_sip_endpoint_address', 126],
      ['egress_sip_endpoint_address', 127],
      ['destination_party_number', 128],
      ['total_hold_time', 129, 'int64'],
      ['bg_additional_mdr_customer_id', 130],
      ['precedence_level_of_call', 131, 'category']
  ], columns=FIELDS_COLUMNS),
  QUEUE_RECORD_TYPE: pd.DataFrame([
      ['sequential_record_number', 1, 'int64'],
      ['record_type', 2, 'category'],
      ['start_time', 3, 'date'],
      ['switch_id', 4, 'category'],
      ['record_id', 5],
      ['spare', 6],
      ['queue_identification', 7],
      ['queue_start_time', 8, 'date'],
      ['queue_end_time', 9, 'date'],
      ['queue_elapsed_time', 10, 'int64'],
      ['disposition_queued_call', 11, 'category'],
      ['queued_call_presented_to_party_number', 12]
  ], columns=FIELDS_COLUMNS)
}