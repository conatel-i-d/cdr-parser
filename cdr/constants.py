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