from os import environ

SESSION_CONFIGS = [
    dict(
        name='survey',
        app_sequence=['survey', 'evaluation'],
        num_demo_participants=10,
        # PROLIFIC'S COMPLETION CODES
        completionlink='https://app.prolific.co/submissions/complete?cc=70B9BF9A',
        failedattentioncheck='https://app.prolific.co/submissions/complete?cc=C1BHRGF7',
        didnotconsent='https://app.prolific.co/submissions/complete?cc=CM1XD7TQ',
        incompatibledevice='https://app.prolific.co/submissions/complete?cc=C1FD7W2F',
        bonuspayment='https://app.prolific.co/submissions/complete?cc=CMNI950A',
        manualreview='https://app.prolific.co/submissions/complete?cc=CJU7HCZ2'
    ),
]


ROOMS = [
    dict(
        name='session2_19sept2023',
        display_name='session2_19sept2023',
    ),
]


# if you set a property in SESSION_CONFIG_DEFAULTS, it will be inherited by all configs
# in SESSION_CONFIGS, except those that explicitly override it.
# the session config can be accessed from methods in your apps as self.session.config,
# e.g. self.session.config['participation_fee']

SESSION_CONFIG_DEFAULTS = dict(
    real_world_currency_per_point=1.00, participation_fee=0.00, doc=""
)

PARTICIPANT_FIELDS = ['dropped', 'endCode', 'is_democrat', 'politics', 'wait_page_arrival', 'misleading_IND',
                      'misleading_COLL']
SESSION_FIELDS = ['DR_counter', 'DD_counter', 'RR_counter', 'DR_image_N', 'DD_image_N', 'RR_image_N', 'DI_image_N',
                  'RI_image_N']

# ISO-639 code
# for example: de, fr, ja, ko, zh-hans
LANGUAGE_CODE = 'en'

# e.g. EUR, GBP, CNY, JPY
REAL_WORLD_CURRENCY_CODE = 'USD'
USE_POINTS = True

ADMIN_USERNAME = 'admin'
# for security, best to set admin password in an environment variable
ADMIN_PASSWORD = environ.get('OTREE_ADMIN_PASSWORD')

DEMO_PAGE_INTRO_HTML = """ """

SECRET_KEY = '5749958540088'
