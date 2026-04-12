from otree.api import *
import numpy as np
import time

doc = """
This app serves as a pre-screening. 
"""


class C(BaseConstants):
    NAME_IN_URL = 'survey'
    PLAYERS_PER_GROUP = None
    NUM_ROUNDS = 1
    # TEMPLATES
    CONSENTS_TEMPLATE = 'survey/ConsentTemplate.html'
    INSTRUCTIONS_TEMPLATE = 'survey/InstructionsTemplate.html'
    COMMITMENT_TEMPLATE = 'survey/CommitmentTemplate.html'
    # TIMEOUTS IN SECS
    NOCONSENT_PAGE = 30  # wait in seconds to be redirected to Prolific
    INDIVIDUAL_TIME = 7  # 7/8 mins ALSO CHANGE IN AUDIO TEXT AND SURVEY APP!!!
    COLLABORATIVE_TIME = 13  # 13/12 mins ALSO CHANGE IN AUDIO TEXT AND SURVEY APP!!!


class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    gives_consent = models.BooleanField(initial=True)
    back_consent = models.BooleanField(initial=False)
    back_attention = models.BooleanField(initial=False)
    prolific_id = models.StringField(label="Enter your Prolific ID:")
    political_affiliation = models.IntegerField(
        label="How strongly do you identify with either of these two parties?",
        widget=widgets.RadioSelectHorizontal(),
        choices=[[1, '1: Strongly Democrat'],
                 [2, '2'],
                 [3, '3'],
                 [4, '4'],
                 [5, '5'],
                 [6, '6'],
                 [7, '7'],
                 [8, '8'],
                 [9, '9'],
                 [10, '10: Strongly Republican'],
                 ]
    )
    commit_collaboration_Q1 = models.BooleanField(
        label="I commit to actively collaborating with my assigned partner during the evaluation process.",
        choices=[
            [True, 'Agree'],
            [False, 'Disagree'],
        ]
    )
    commit_collaboration_Q2 = models.BooleanField(
        label="I understand that leaving the study midway may hinder my partner completing it successfully.",
        choices=[
            [True, 'Agree'],
            [False, 'Disagree'],
        ]
    )
    commit_attention_Q1 = models.BooleanField(
        label="I commit to giving this study my full and undivided attention.",
        choices=[
            [True, 'Agree'],
            [False, 'Disagree'],
        ]
    )
    commit_attention_Q2 = models.BooleanField(
        label="I'll remain at my computer station and refrain from opening other tabs or browsers during the "
              "experiment.",
        choices=[
            [True, 'Agree'],
            [False, 'Disagree'],
        ]
    )
    failed_attention = models.BooleanField(initial=False)


def EndCode_text(player):
    code = player.participant.endCode
    errorCodes = {
        '000': 'No errors have been recorded.',
        '001': 'You have exceeded the maximum allowed time to complete this study.',
        '002': 'You didn\'t agree to the study\'s terms and conditions.',
        '003': 'You failed the commitment check.',
        '004': 'You failed the commitment check twice.',
    }
    return errorCodes[code]


def commitmentCheck(player):
    suma = np.sum([player.commit_attention_Q1, player.commit_attention_Q2,
                   player.commit_collaboration_Q1, player.commit_collaboration_Q2])
    return suma


def checkConditionals(player):
    participant = player.participant
    keyVariables = {
        "Dropped?": participant.dropped,
        "EndCode": participant.endCode,
        "Gives consent?": player.gives_consent,
        "Change consent?": player.back_consent,
        "Failed attention?": player.failed_attention,
        "Change attention?": player.back_attention,
    }
    return keyVariables


# PAGES
class Consent(Page):
    form_model = 'player'
    form_fields = ['gives_consent']

    @staticmethod
    def before_next_page(player, timeout_happened):
        # init dropped & endCode
        player.participant.dropped = False
        player.participant.endCode = '000'
        # drop if page timed out by Prolific's standards i.e. 77 mins
        if timeout_happened:
            player.participant.dropped = True
            player.participant.endCode = '001'  # max time
        else:
            if not player.gives_consent:
                player.participant.endCode = '002'  # didn't consent


class NoConsent(Page):
    timeout_seconds = C.NOCONSENT_PAGE  # 60 seconds
    form_model = 'player'
    form_fields = ['back_consent']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endCode_text=EndCode_text(player))

    @staticmethod
    def before_next_page(player, timeout_happened):
        # if timed out then "Next"
        if timeout_happened:
            player.back_consent = False

    @staticmethod
    def is_displayed(player: Player):
        if not player.participant.dropped:
            return not player.gives_consent


class NoConsentProlific(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        player.participant.dropped = True
        return dict(
            didnotconsent=player.subsession.session.config['didnotconsent']
        )

    @staticmethod
    def is_displayed(player: Player):
        # shows for players who haven't been dropped, didn't give consent and chose not to change answer
        if not player.participant.dropped:
            return np.logical_and(not player.back_consent, not player.gives_consent)


class ConsentTakeTwo(Page):
    form_model = 'player'
    form_fields = ['gives_consent']

    @staticmethod
    def before_next_page(player, timeout_happened):
        # drop if page timed out
        if timeout_happened:
            player.participant.dropped = True
            player.participant.endCode = '001'  # max time
        else:
            if player.gives_consent:
                player.participant.endCode = '000'
            else:
                player.back_consent = False
                player.participant.endCode = '002'  # didn't consent

    @staticmethod
    def is_displayed(player: Player):
        # shows for players who haven't been dropped, didn't give consent and want to change answer
        if not player.participant.dropped:
            return np.logical_and(player.back_consent, not player.gives_consent)


class NoConsentTakeTwo(Page):
    timeout_seconds = C.NOCONSENT_PAGE - 40  # 20 seconds
    form_model = 'player'
    form_fields = ['back_consent']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endCode_text=EndCode_text(player))

    @staticmethod
    def before_next_page(player, timeout_happened):
        # if timed out then "Next"
        if timeout_happened:
            player.back_consent = False

    @staticmethod
    def is_displayed(player: Player):
        if not player.participant.dropped:
            return np.logical_and(not player.back_consent, not player.gives_consent)


class Education(Page):
    form_model = 'player'
    form_fields = ['political_affiliation', 'prolific_id']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.participant.dropped = True
            player.participant.endCode = '001'  # max time
        else:
            if player.political_affiliation < 6:
                player.participant.is_democrat = True
                player.participant.politics = 'Democrat'
            else:
                player.participant.is_democrat = False
                player.participant.politics = 'Republican'
            # drop all who did not consent
            if not player.gives_consent:
                player.participant.dropped = True
                player.participant.endCode = '002'  # didn't consent

    @staticmethod
    def is_displayed(player: Player):
        return np.logical_and(player.gives_consent, not player.participant.dropped)


class Instructions(Page):
    @staticmethod
    def vars_for_template(player: Player):
        image_to_display = 'images/2.png'  # change with screenshot image
        return dict(image_path=image_to_display,
                    INDIVIDUAL_TIME=C.INDIVIDUAL_TIME)

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.participant.dropped = True
            player.participant.endCode = '001'  # max time

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.dropped


class Commitment(Page):
    form_model = 'player'
    form_fields = ['commit_attention_Q1', 'commit_attention_Q2', 'commit_collaboration_Q1', 'commit_collaboration_Q2']

    @staticmethod
    def before_next_page(player, timeout_happened):
        suma = commitmentCheck(player)
        if timeout_happened:
            player.participant.dropped = True
            player.participant.endCode = '001'  # max time
        else:
            if suma < 4:
                player.failed_attention = True
                player.participant.endCode = '003'  # failed attention check
            else:
                player.failed_attention = False
                player.participant.endCode = '000'  # no errors
                player.participant.wait_page_arrival = time.time()

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.dropped


class FailedAttention(Page):
    timeout_seconds = C.NOCONSENT_PAGE
    form_model = 'player'
    form_fields = ['back_attention']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endCode_text=EndCode_text(player),
                    suma=commitmentCheck(player))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        # if timed out then "Next"
        if timeout_happened:
            player.back_attention = False
        if player.back_attention:
            player.commit_attention_Q1 = None
            player.commit_attention_Q2 = None
            player.commit_collaboration_Q1 = None
            player.commit_collaboration_Q2 = None

    @staticmethod
    def is_displayed(player: Player):
        if not player.participant.dropped:
            return player.failed_attention


class FailedAttentionProlific(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        player.participant.dropped = True
        return dict(
            failedattentioncheck=player.subsession.session.config['failedattentioncheck']
        )

    @staticmethod
    def is_displayed(player: Player):
        # shows for players who haven't been dropped, didn't give consent and chose not to change answer
        if not player.participant.dropped:
            return np.logical_and(player.failed_attention, not player.back_attention)


class CommitmentTakeTwo(Page):
    form_model = 'player'
    form_fields = ['commit_attention_Q1', 'commit_attention_Q2', 'commit_collaboration_Q1', 'commit_collaboration_Q2']

    @staticmethod
    def before_next_page(player, timeout_happened):
        suma = commitmentCheck(player)
        player.back_attention = False
        if timeout_happened:
            player.participant.dropped = True
            player.participant.endCode = '001'  # max time
        else:
            if suma <= 2:
                player.failed_attention = True
                player.participant.endCode = '004'  # failed attention check
            else:
                player.failed_attention = False
                player.participant.endCode = '000'  # no errors
                player.participant.wait_page_arrival = time.time()

    @staticmethod
    def is_displayed(player: Player):
        if not player.participant.dropped:
            return np.logical_and(player.failed_attention, player.back_attention)


class FailedAttentionTakeTwo(Page):
    timeout_seconds = C.NOCONSENT_PAGE - 40
    form_model = 'player'
    form_fields = ['back_attention']

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endCode_text=EndCode_text(player),
                    suma=commitmentCheck(player))

    @staticmethod
    def before_next_page(player: Player, timeout_happened):
        player.back_attention = False

    @staticmethod
    def is_displayed(player: Player):
        if not player.participant.dropped:
            return player.failed_attention


class Dropped(Page):
    @staticmethod
    def vars_for_template(player: Player):
        return dict(endCode_text=EndCode_text(player))

    @staticmethod
    def is_displayed(player: Player):
        return player.participant.dropped


page_sequence = [Consent, NoConsent, NoConsentProlific, ConsentTakeTwo, NoConsentTakeTwo, NoConsentProlific, Education,
                 Instructions, Commitment, FailedAttention, FailedAttentionProlific, CommitmentTakeTwo,
                 FailedAttentionTakeTwo, FailedAttentionProlific, Dropped]
