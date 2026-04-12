from otree.api import *
import os
import time
import random
import pickle
import numpy as np
from difflib import SequenceMatcher

doc = """
In this app we perform the collaborative evaluation.
"""


def openJson(filename):
    with open(filename, 'rb') as fp:
        imagesToEvaluate = pickle.load(fp)
    return imagesToEvaluate


class C(BaseConstants):
    NAME_IN_URL = 'evaluation'
    PLAYERS_PER_GROUP = 2
    NUM_ROUNDS = 1
    # TREATMENT VARS
    SHOW = False  # Show/NoShow treatments
    FIGURE_NAMES = os.listdir('evaluation/static/images')
    filename = 'sessions_19sept2023.json'
    # TIMEOUTS
    TIMEOUT = 15  # what do we use this for? to reload MyWaitPage
    INDIVIDUAL_TIME = 7  # 7/8 mins ALSO CHANGE IN AUDIO TEXT AND SURVEY APP!!!
    COLLABORATIVE_TIME = 14  # 13/12 mins ALSO CHANGE IN AUDIO TEXT AND SURVEY APP!!!
    INDIVIDUAL_ATTENTION_TIME = 1  # in seconds ALSO CHANGE IN AUDIO TEXT!!!
    REDIRECT_PROLIFIC = 30
    NO_MATCH_FOUND = 60 * 10  # 15 minutes
    MEDIUM_WAIT = 3  # 3 mins to wait for a DR match
    LONG_WAIT = 8  # 8 mins to wait for any match
    # TESTING IN SERVER

    # TESTING IN MAC
    # FIGURE_NAMES.remove('.DS_Store')
    N_IMAGES = len(FIGURE_NAMES)
    # filename = 'session1_29aug2023.json'
    IMAGES_TO_EVALUATE = openJson(filename)
    # FOR TEXT CLEANING AND COMPARING TEXTS
    PUNC = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    REFERENCE_ROLE = 'Reference'
    COMPARER_ROLE = 'Comparer'
    SIMILARITY_SCORE = 0.5
    # FOR IndividualQsMis.HTML
    ONLINE_ACTIVITY = [
        dict(name='wikipedia', label="Editing Wikipedia"),
        dict(name='onlineReview', label="Leaving a review for a business on Yelp, Google Maps, etc."),
        dict(name='factCheck', label="Fact-checking an online content"),
        dict(name='newsWebsite', label="Leaving a comment on a news website"),
        dict(name='userContent', label="Contributed to any other user-generated content"),
    ]
    MISLEADING = [
        dict(name='factualError', label="It contains a factual error"),
        dict(name='manipulatedMedia', label="It contains manipulated media"),
        dict(name='outdatedInformation', label="It contains outdated information that may be misleading"),
        dict(name='misrepresentation', label="It is a misrepresentation or missing important context"),
        dict(name='disputedClaim', label="It presents a disputed claim as fact"),
        dict(name='satire', label="It is satire/a joke that may be misinterpreted"),
        dict(name='other', label="Other"),
    ]
    # FOR IndividualQsNotMis.HTML
    NOT_MISLEADING = [
        dict(name='factualCorrect', label="It expresses a factually correct claim"),
        dict(name='outdated', label="The tweet was correct when written, but is out of date now"),
        dict(name='joking', label="It is clearly satirical/joking"),
        dict(name='personalOpinion', label="It expresses a personal opinion"),
        dict(name='otherNOTMIS', label="Other"),
    ]


class Subsession(BaseSubsession):
    pass


def creating_session(subsession: Subsession):
    session = subsession.session
    # counter for creating groups
    session.DR_counter = 0
    session.DD_counter = 0
    session.RR_counter = 0
    # counter for assigning images
    session.DR_image_N = 0
    session.DD_image_N = 0
    session.RR_image_N = 0
    session.DI_image_N = 0
    session.RI_image_N = 0
    # when partner does not show up
    for p in subsession.get_players():
        p.completion_code_no_partner = random.randint(10 ** 6, 10 ** 7)


def medium_wait(player):
    participant = player.participant
    return (time.time() - participant.wait_page_arrival) > C.MEDIUM_WAIT * 60  # in mins


def long_wait(player):
    participant = player.participant
    return time.time() - participant.wait_page_arrival > C.LONG_WAIT * 60  # in mins


def fileName(treatment):
    filename = 'None'
    if C.SHOW:
        filename = treatment + '_SHOW'
    else:
        filename = treatment + '_NOSHOW'
    return filename


def group_by_arrival_time_method(subsession, waiting_players):
    session = subsession.session
    democrats = [p for p in waiting_players if p.participant.is_democrat]
    republicans = [p for p in waiting_players if not p.participant.is_democrat]
    waiting = [p for p in waiting_players if medium_wait(p)]
    DR_N_IMAGES = len(C.IMAGES_TO_EVALUATE[fileName('DR')])
    DD_N_IMAGES = len(C.IMAGES_TO_EVALUATE[fileName('DD')])
    RR_N_IMAGES = len(C.IMAGES_TO_EVALUATE[fileName('RR')])

    # if waiting too long, make a single-player group
    for player in waiting_players:
        if long_wait(player):
            return [player]

    if session.DR_counter < DR_N_IMAGES:
        if np.logical_and(len(democrats) >= 1, len(republicans) >= 1):
            session.DR_counter += 1
            return [democrats[0], republicans[0]]
        else:
            if len(waiting) >= 2:
                player1 = waiting[0].participant.is_democrat
                player2 = waiting[1].participant.is_democrat
                if np.logical_and(not player1, not player2) and session.RR_counter < RR_N_IMAGES:  # is RR
                    session.RR_counter += 1
                    return waiting[:2]
                if np.logical_and(player1, player2) and session.DD_counter < DD_N_IMAGES:  # is DD
                    session.DD_counter += 1
                    return waiting[:2]
    else:
        if np.logical_and(session.DD_counter < DD_N_IMAGES, len(democrats) >= 2):
            session.DD_counter += 1
            return democrats[:2]
        if np.logical_and(session.RR_counter < RR_N_IMAGES, len(republicans) >= 2):
            session.RR_counter += 1
            return republicans[:2]


class Group(BaseGroup):
    treatment = models.StringField()
    image = models.StringField()
    id_in_treatment = models.IntegerField()


def image_counters_DICT(group: Group):
    session = group.subsession.session
    counters = {
        'DR': session.DR_image_N,
        'DD': session.DD_image_N,
        'RR': session.RR_image_N,
        'DI': session.DI_image_N,
        'RI': session.RI_image_N,
    }
    return counters


def image_index(group: Group):
    treatment = group.treatment
    counters = image_counters_DICT(group)
    counter = counters[group.treatment]
    if treatment != 'RI' and treatment != 'DI':
        IMAGE_LIST = C.IMAGES_TO_EVALUATE[fileName(treatment)]
        N_IMAGES = len(C.IMAGES_TO_EVALUATE[fileName(treatment)])
    else:
        IMAGE_LIST = C.FIGURE_NAMES
        N_IMAGES = C.N_IMAGES
    if counter < N_IMAGES:
        i = counter
    else:
        i = random.randint(0, N_IMAGES - 1)
    image = IMAGE_LIST[i]
    return image


class Player(BasePlayer):
    nickname = models.StringField()
    endCode = models.StringField(initial='000')
    # INDIVIDUAL EVAL VARIABLES
    starts_individualEval = models.FloatField()
    timeout_individualEval = models.BooleanField(initial=False)
    evidenceEval_IND = models.IntegerField(
        label="Based on the latest available evidence, the tweet is:",
        choices=[
            [1, 'Misinformed, or potentially misleading'],
            [2, 'Somewhat misleading'],
            [3, 'Not misleading'],
        ]
    )
    suggestedEdit_IND = models.LongStringField(
        label="Text edit",
        max_length=4000,
    )
    attention_check_IND = models.IntegerField(
        label="Which of the following is a vegetable?",
        choices=[
            [1, 'Salmon'],
            [2, 'Broccoli'],
            [3, 'Cheeseburger'],
            [4, 'Pizza'],
            [5, 'Milk'],
        ]
    )
    failed_attention_check = models.BooleanField(initial=False)
    completion_code_no_partner = models.IntegerField()
    timeout = models.FloatField()  # if partner not found
    is_group_single = models.BooleanField(initial=False)
    # COLLABORATIVE EVAL VARIABLES
    starts_collaborativeEval = models.FloatField()
    starts_collaborativeEvalTakeTwo = models.FloatField()
    timeout_collaborativeEval = models.BooleanField(initial=False)
    timeout_collaborativeEvalTakeTwo = models.BooleanField(initial=False)
    collabEval_tryN = models.IntegerField(initial=0)
    evidenceEval_COLL = models.IntegerField(
        label="Based on the latest available evidence, the tweet is:",
        choices=[
            [1, 'Misinformed, or potentially misleading'],
            [2, 'Somewhat misleading'],
            [3, 'Not misleading'],
        ]
    )
    evidenceEval_COLL_TakeTwo = models.IntegerField(
        label="Based on the latest available evidence, the tweet is:",
        choices=[
            [1, 'Misinformed, or potentially misleading'],
            [2, 'Somewhat misleading'],
            [3, 'Not misleading'],
        ]
    )
    suggestedEdit_COLL = models.LongStringField(
        label="Text edit",
        max_length=4000,
    )
    suggestedEdit_COLL_TakeTwo = models.LongStringField(
        label="Text edit",
        max_length=4000,
    )
    cleanText = models.LongStringField()
    cleanText_TakeTwo = models.LongStringField()
    text_similarity = models.FloatField()
    text_similarity_TakeTwo = models.FloatField()
    failed_similarity = models.BooleanField(initial=False)
    failed_misinformation = models.BooleanField(initial=False)
    why_label = models.IntegerField(
        label="Why do you believe your evaluation labels (i.e. misleading/not misleading) do not match?",
        blank=True,
        choices=[
            [1, 'We had different opinions and couldn\'t agree on a label'],
            [2, 'My partner was unresponsive'],
            [3, 'I believe this is a mistake but I couldn\'t go back to the task to review the label'],
            [4, 'Other'],
        ])
    why_text = models.IntegerField(
        label="Why do you believe your evaluation texts do not match?",
        blank=True,
        choices=[
            [1, 'We had different opinions and couldn\'t agree on a text'],
            [2, 'My partner was unresponsive'],
            [3, 'I believe this is a mistake but I couldn\'t go back to the task to review the text'],
            [4, 'I don\'t believe the texts to be significantly different. Both convey the same message'],
            [5, 'Other'],
        ])
    other_expand = models.LongStringField(
        label="Is there anything you'd like to share with us that will help us understand your results?",
        initial='No comments'
    )
    # RETURN LOOPS
    back_label = models.BooleanField(initial=False)
    reason_return = models.IntegerField(
        initial=0,
        choices=[
            [1, 'Evaluation does not match, text matches'],
            [2, 'Evaluation matches, text does not match'],
            [3, 'Neither evaluation, nor text match'],
            [4, 'Both evaluation and text match'],
        ]
    )
    # FOR IndividualQsMis.HTML
    fewBelieve = models.BooleanField(
        label="If the tweet was widely spread, its message would likely be believed by:",
        choices=[[True, 'Few'],
                 [False, 'Many']],
    )
    littleHarm = models.BooleanField(
        label="If many believed the tweet, it might cause:",
        choices=[[True, 'Little harm'],
                 [False, 'Considerable harm']],
    )
    easyInfo = models.BooleanField(
        label="Finding and understanding the correct information would be:",
        choices=[[True, 'Easy'],
                 [False, 'Challenging']],
    )
    # labels for C.MISLEADING
    factualError = models.BooleanField(blank=True)
    manipulatedMedia = models.BooleanField(blank=True)
    outdatedInformation = models.BooleanField(blank=True)
    misrepresentation = models.BooleanField(blank=True)
    disputedClaim = models.BooleanField(blank=True)
    satire = models.BooleanField(blank=True)
    other = models.BooleanField(blank=True)
    # labels for C.ONLINE_ACTIVITY
    wikipedia = models.BooleanField(blank=True)
    onlineReview = models.BooleanField(blank=True)
    factCheck = models.BooleanField(blank=True)
    newsWebsite = models.BooleanField(blank=True)
    userContent = models.BooleanField(blank=True)
    # labels for C.NOT_MISLEADING
    factualCorrect = models.BooleanField(blank=True)
    outdated = models.BooleanField(blank=True)
    joking = models.BooleanField(blank=True)
    personalOpinion = models.BooleanField(blank=True)
    otherNOTMIS = models.BooleanField(blank=True)
    # COLLABORATION EVAL
    collabEval = models.IntegerField(
        label="How easy was it for you and your partner to come up with a text you agreed on?",
        choices=[
            [1, 'Extremely easy'],
            [2, 'Somewhat easy'],
            [3, 'Somewhat difficult'],
            [4, 'Extremely difficult'],
        ]
    )
    # SHOW VARIABLES
    show_IndividualQs = models.BooleanField(initial=True)
    show_take_two = models.BooleanField(initial=False)


def chat_nickname(player: Player):
    if C.SHOW:
        nickname = player.participant.politics + " " + str(player.id_in_group)
    else:
        nickname = "Participant " + str(player.id_in_group)
    player.nickname = nickname
    return nickname


def clean_text(player: Player, evaluationText):
    text = evaluationText
    text = text.lower()
    text = text.replace(" ", "").replace('\r', '').replace('\n', '')
    for ele in text:
        if ele in C.PUNC:
            text = text.replace(ele, "")
    return text


def return_misinformation_label(player: Player, label):
    texts = {0: 'no information',
             1: 'misinformed, or potentially misleading',
             2: 'somewhat misleading',
             3: 'not misleading'}
    return texts[label]


def other_player(player: Player):
    return player.get_others_in_group()[0]


def reason_to_return(player: Player):
    reason = player.reason_return
    if player.failed_misinformation and not player.failed_similarity:
        reason = 1
    elif not player.failed_misinformation and player.failed_similarity:
        reason = 2
    elif player.failed_misinformation and player.failed_similarity:
        reason = 3
    else:
        reason = 4
    return reason


def reason_explained(player: Player, reason):
    dictionary = {
        1: 'Label does not match, text matches',
        2: 'Label matches, text does not match',
        3: 'Neither evaluation, nor text match',
        4: 'Both evaluation and text match'
    }
    return dictionary[reason]


def check_sim_vars(player: Player):
    text_similarity = player.field_maybe_none('text_similarity')
    text_similarity_TakeTwo = player.field_maybe_none('text_similarity_TakeTwo')
    sims_vars = {'Similarity score take ONE': text_similarity,
                 'Similarity score take TWO': text_similarity_TakeTwo,
                 'Failed similarity check?': player.failed_similarity,
                 'Failed misinformation check?': player.failed_misinformation,
                 'Reason to return': player.reason_return,
                 'Reason explained': reason_explained(player, player.reason_return)}
    return sims_vars


def EndCode_text(player):
    code = player.participant.endCode
    errorCodes = {
        '000': 'No errors have been recorded.',
        '001': 'You have exceeded the maximum allowed time to complete this study.',
        '002': 'You didn\'t agree to the study\'s terms and conditions.',
        '003': 'You failed the commitment check.',
        '004': 'You failed the commitment check twice.',
        '005': 'You failed to complete the individual evaluation task in the allotted time and failed the attention '
               'check.',
        '006': 'You failed to complete the individual evaluation task in the allotted time twice.',
        '007': 'You have successfully completed the individual evaluation task.',
        '008': 'You have successfully completed the collaborative evaluation task.',
        '009': 'You have completed the task but either label, text or both don\'t match.',
        '010': 'You failed to complete the individual and collaborative tasks in the allotted time.',
        '011': 'You failed to complete the collaborative evaluation task in the allotted time.',
        '012': 'You failed to review your answers in the allotted time.',
        '013': 'You, your partner or both chose not to fix your answers.',
    }
    return errorCodes[code]


def return_EndCodes_CollabONE(player):
    code = player.field_maybe_none('endCode')
    if player.timeout_collaborativeEval:
        if np.logical_and(player.timeout_individualEval, player.failed_attention_check):
            code = '010'  # show up fee but have them complete individual evaluation
        else:
            code = '011'  # show up fee
    player.participant.endCode = code
    return code


def return_EndCodes_CollabTWO(player):
    code = player.field_maybe_none('endCode')
    if player.timeout_collaborativeEvalTakeTwo:
        code = '012'  # full amount
    player.participant.endCode = code
    return code


# PAGES
class ResultsWaitPage(WaitPage):
    template_name = 'evaluation/ResultsWaitPage.html'
    group_by_arrival_time = True

    # GIVE PLAYER CUSTOM CODES
    @staticmethod
    def js_vars(player: Player):
        print(C.FIGURE_NAMES)
        return dict(timeout=C.NO_MATCH_FOUND)

    @staticmethod
    def vars_for_template(player: Player):
        participant = player.participant
        timeout_happened = time.time() - participant.wait_page_arrival > C.NO_MATCH_FOUND
        return dict(timeout_happened=timeout_happened)


class WaitTreatments(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        session = group.subsession.session
        group_players = group.get_players()
        for p in group_players:
            p.is_group_single = False
        if len(group_players) > 1:
            if np.logical_and(group_players[0].participant.is_democrat, group_players[1].participant.is_democrat):
                group.treatment = 'DD'
                group.image = image_index(group)
                session.DD_image_N += 1
                group.id_in_treatment = session.DD_image_N
            elif np.logical_and(not group_players[0].participant.is_democrat,
                                not group_players[1].participant.is_democrat):
                group.treatment = 'RR'
                group.image = image_index(group)
                session.RR_image_N += 1
                group.id_in_treatment = session.RR_image_N
            else:
                group.treatment = 'DR'
                group.image = image_index(group)
                session.DR_image_N += 1
                group.id_in_treatment = session.DR_image_N
        else:
            if group_players[0].participant.is_democrat:
                group.treatment = 'DI'
                group_players[0].is_group_single = True
                group.image = image_index(group)
                session.DI_image_N += 1
                group.id_in_treatment = session.DI_image_N
            else:
                group.treatment = 'RI'
                group_players[0].is_group_single = True
                group.image = image_index(group)
                session.RI_image_N += 1
                group.id_in_treatment = session.RI_image_N
        print(image_counters_DICT(group))


class IndividualEval(Page):
    timeout_seconds = 60 * C.INDIVIDUAL_TIME

    form_model = 'player'
    form_fields = ['suggestedEdit_IND', 'evidenceEval_IND']

    @staticmethod
    def vars_for_template(player: Player):
        player.starts_individualEval = time.time()
        group = player.group
        return dict(image_path='images/' + group.image,
                    Nickname_chat_one=chat_nickname(player),
                    is_group_of_one=player.is_group_single,
                    code=player.participant.code)

    @staticmethod
    def before_next_page(player, timeout_happened):
        # init participant vars
        participant = player.participant
        participant.misleading_IND = True
        if timeout_happened:
            player.timeout_individualEval = True
            player.show_IndividualQs = False
            if not player.is_group_single:
                player.evidenceEval_IND = 0
                player.suggestedEdit_IND = "None"
        else:
            if player.is_group_single:
                player.participant.endCode = '007'  # individual group successful
            if player.evidenceEval_IND == 3:  # 3: not misleading
                participant.misleading_IND = False

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.dropped


class AttentionCheck(Page):
    timeout_seconds = 60 * C.INDIVIDUAL_ATTENTION_TIME
    form_model = 'player'
    form_fields = ['attention_check_IND']

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.failed_attention_check = True
            player.participant.endCode = '005'  # ind eval timed out and failed attention check
            player.participant.dropped = True
        else:
            if player.attention_check_IND != 2:
                player.failed_attention_check = True
                player.participant.endCode = '005'  # ind eval timed out and failed attention check
                player.participant.dropped = True
            else:
                player.failed_attention_check = False
                player.participant.dropped = False
                if player.is_group_single:
                    player.show_take_two = True

    @staticmethod
    def is_displayed(player: Player):
        return np.logical_and(not player.participant.dropped, player.timeout_individualEval)


class FailedIndividualCheck(Page):
    timeout_seconds = C.REDIRECT_PROLIFIC

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endCode_text=EndCode_text(player))

    @staticmethod
    def is_displayed(player: Player):
        return np.logical_and(player.participant.dropped, player.participant.endCode == '005')


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
        return np.logical_and(player.participant.dropped, player.participant.endCode == '005')


class IndividualEvalTakeTwo(Page):
    timeout_seconds = 60 * C.INDIVIDUAL_TIME
    form_model = 'player'
    form_fields = ['suggestedEdit_IND', 'evidenceEval_IND']

    @staticmethod
    def vars_for_template(player: Player):
        player.starts_individualEval = time.time()
        group = player.group
        return dict(image_path='images/' + group.image,
                    Nickname_chat_one=chat_nickname(player),
                    code=player.participant.code)

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        # init important vars for all
        player.show_IndividualQs = True
        participant.misleading_IND = True
        player.timeout_individualEval = False
        if timeout_happened:
            player.timeout_individualEval = True
            player.evidenceEval_IND = 0
            player.suggestedEdit_IND = "None"
            player.show_IndividualQs = False
            player.participant.endCode = '006'  # ind eval timed out twice
            player.participant.dropped = True
        else:
            if player.evidenceEval_IND == 3:  # 3: not misleading
                participant.misleading_IND = False

    @staticmethod
    def is_displayed(player: Player):
        if player.show_take_two:
            return np.logical_and(not player.participant.dropped, not player.failed_attention_check)
        else:
            return False


class FailedIndividualEvalTwice(Page):
    timeout_seconds = C.REDIRECT_PROLIFIC

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endCode_text=EndCode_text(player))

    @staticmethod
    def is_displayed(player: Player):
        return np.logical_and(player.participant.dropped, player.participant.endCode == '006')


class FailedIndividualEvalTwiceProlific(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        player.participant.dropped = True
        return dict(
            failedattentioncheck=player.subsession.session.config['failedattentioncheck']
        )

    @staticmethod
    def is_displayed(player: Player):
        return np.logical_and(player.participant.dropped, player.participant.endCode == '006')


class IndividualQsMis(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        online_activity = [online['name'] for online in C.ONLINE_ACTIVITY]
        misleading = [reason['name'] for reason in C.MISLEADING]
        other_qs = ['fewBelieve', 'littleHarm', 'easyInfo']
        return online_activity + misleading + other_qs

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.is_group_single:
            player.participant.endCode = '007'  # individual group successful

    @staticmethod
    def is_displayed(player: Player):
        if not player.participant.dropped:
            return np.logical_and(player.participant.misleading_IND, player.show_IndividualQs)
        else:
            return False


class IndividualQsNotMis(Page):
    form_model = 'player'

    @staticmethod
    def get_form_fields(player: Player):
        return [online['name'] for online in C.ONLINE_ACTIVITY] + \
               [reason['name'] for reason in C.NOT_MISLEADING]

    @staticmethod
    def before_next_page(player, timeout_happened):
        if player.is_group_single:
            player.participant.endCode = '007'  # individual group successful

    @staticmethod
    def is_displayed(player: Player):
        if not player.participant.dropped:
            return np.logical_and(not player.participant.misleading_IND, player.show_IndividualQs)
        else:
            return False


class IndividualSuccess(Page):
    timeout_seconds = C.REDIRECT_PROLIFIC

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endCode_text=EndCode_text(player))

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.dropped = True  # needed to make sure Collab eval task pages do not show

    @staticmethod
    def is_displayed(player: Player):
        if player.is_group_single:
            return np.logical_and(player.participant.endCode == '007', not player.participant.dropped)
        else:
            False


class IndividualSuccessProlific(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        return dict(
            completionlink=player.subsession.session.config['completionlink']
        )

    @staticmethod
    def is_displayed(player: Player):
        return np.logical_and(player.is_group_single, player.participant.endCode == '007')


##############
class MyWaitPage(WaitPage):
    template_name = 'evaluation/MyWaitPage.html'

    # GIVE PLAYER CUSTOM CODES
    @staticmethod
    def js_vars(player: Player):
        return dict(timeout=C.TIMEOUT)

    @staticmethod
    def vars_for_template(player: Player):
        otherPlayer = other_player(player)
        return dict(otherPlayerDropped=otherPlayer.participant.dropped)

    @staticmethod
    def after_all_players_arrive(group: Group):
        pass


class CollaborativeEval(Page):
    timeout_seconds = 60 * C.COLLABORATIVE_TIME

    form_model = 'player'
    form_fields = ['suggestedEdit_COLL', 'evidenceEval_COLL']

    @staticmethod
    def vars_for_template(player: Player):
        player.starts_collaborativeEval = time.time()
        group = player.group
        return dict(image_path='images/' + group.image,
                    Nickname_chat_one=chat_nickname(player),
                    individual_label=return_misinformation_label(player, player.evidenceEval_IND),
                    individual_text=player.suggestedEdit_IND,
                    code=player.participant.code)

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        if timeout_happened:
            player.timeout_collaborativeEval = True
            participant.endCode = return_EndCodes_CollabONE(player)
            participant.dropped = True
        else:
            # MIS/notMIS
            if player.evidenceEval_COLL == 3:  # 3: not misleading
                participant.misleading_COLL = False
            else:
                participant.misleading_COLL = True
            # PREPARE FOR SIMILARITY CHECK
            player.cleanText = clean_text(player, player.suggestedEdit_COLL)
            # NEEDED TO BLOCK MULTIPLE ATTEMPTS
            player.collabEval_tryN += 1

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.dropped


class TimedOut(Page):
    timeout_seconds = C.REDIRECT_PROLIFIC

    @staticmethod
    def vars_for_template(player: Player):
        return dict(endCode_text=EndCode_text(player))

    @staticmethod
    def is_displayed(player: Player):
        if player.timeout_collaborativeEval:
            return np.logical_or(player.participant.endCode == '010', player.participant.endCode == '011')


class TimedOutProlific(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        return dict(
            manualreview=player.subsession.session.config['manualreview']
        )

    @staticmethod
    def is_displayed(player: Player):
        if player.timeout_collaborativeEval:
            return np.logical_or(player.participant.endCode == '010', player.participant.endCode == '011')


class SimilarityWaitPage(WaitPage):
    template_name = 'evaluation/SimilarityWaitPage.html'

    # GIVE PLAYER CUSTOM CODES
    @staticmethod
    def js_vars(player: Player):
        return dict(timeout=C.COLLABORATIVE_TIME)

    @staticmethod
    def vars_for_template(player: Player):
        otherPlayer = other_player(player)
        return dict(otherPlayerDropped=otherPlayer.participant.dropped)

    @staticmethod
    def after_all_players_arrive(group: Group):
        for player in group.get_players():
            otherPlayer = other_player(player)
            # DEFINING REFERENCE AND COMPARING TEXT
            if player.role == C.REFERENCE_ROLE:
                reference_text = player.cleanText
                comparing_text = otherPlayer.cleanText
            else:
                reference_text = otherPlayer.cleanText
                comparing_text = player.cleanText
            # CALCULATING TEXT SIMILARITY
            player.text_similarity = SequenceMatcher(a=reference_text, b=comparing_text).ratio()
            # HAS FAILED SIMILARITY CHECK?
            if player.text_similarity < C.SIMILARITY_SCORE:
                player.failed_similarity = True
            # HAS FAILED MISINFORMATION CHECK?
            if player.participant.misleading_COLL != otherPlayer.participant.misleading_COLL:
                player.failed_misinformation = True
            player.reason_return = reason_to_return(player)
            if not player.failed_similarity and not player.failed_misinformation:
                player.participant.endCode = '008'  # successful completion
                print("ERROR CODE: ", player.participant.endCode)
            print(check_sim_vars(player), player.participant.endCode)


class CollabTaskCompleted(Page):
    timeout_seconds = C.REDIRECT_PROLIFIC + 60
    form_model = 'player'
    form_fields = ['collabEval']

    @staticmethod
    def vars_for_template(player: Player):
        player.participant.endCode = '008'  # successful completion
        return dict(endCode_text=EndCode_text(player))

    @staticmethod
    def is_displayed(player: Player):
        # shows for players who haven't been dropped and completed task successfully
        if not player.participant.dropped:
            return np.logical_and(not player.failed_similarity, not player.failed_misinformation)


class CollabTaskCompletedProlific(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        return dict(
            bonuspayment=player.subsession.session.config['bonuspayment']
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.dropped = True  # needed to make sure other loops do not show up

    @staticmethod
    def is_displayed(player: Player):
        # shows for players who haven't been dropped and completed task successfully
        if not player.participant.dropped:
            return np.logical_and(not player.failed_similarity, not player.failed_misinformation)


class MisinformationCheck(Page):
    timeout_seconds = 60 * C.INDIVIDUAL_ATTENTION_TIME
    form_model = 'player'
    form_fields = ['back_label']

    @staticmethod
    def vars_for_template(player: Player):
        otherPlayer = other_player(player)
        return dict(my_eval=return_misinformation_label(player, player.evidenceEval_COLL),
                    partner_eval=return_misinformation_label(otherPlayer, otherPlayer.evidenceEval_COLL),
                    my_text=player.suggestedEdit_COLL,
                    partner_text=otherPlayer.suggestedEdit_COLL,
                    reason_one=player.reason_return == 1,
                    reason_two=player.reason_return == 2,
                    reason_three=player.reason_return == 3,
                    )

    @staticmethod
    def before_next_page(player, timeout_happened):
        if timeout_happened:
            player.back_label = False

    @staticmethod
    def is_displayed(player: Player):
        otherPlayer = other_player(player)
        if np.logical_and(not player.participant.dropped, not otherPlayer.participant.dropped):
            return np.logical_or(player.failed_similarity, player.failed_misinformation)


class MisinformationWaitPage(WaitPage):
    pass


class NoReview(Page):
    form_model = 'player'
    form_fields = ['why_label', 'why_text', 'collabEval', 'other_expand']

    @staticmethod
    def vars_for_template(player: Player):
        otherPlayer = other_player(player)
        return dict(
            my_eval=return_misinformation_label(player, player.evidenceEval_COLL),
            partner_eval=return_misinformation_label(otherPlayer, otherPlayer.evidenceEval_COLL),
            my_text=player.suggestedEdit_COLL,
            partner_text=otherPlayer.suggestedEdit_COLL,
            partner_NO_back=(player.back_label and not otherPlayer.back_label),
            reason_one=player.reason_return == 1,
            reason_two=player.reason_return == 2,
            reason_three=player.reason_return == 3,
        )

    @staticmethod
    def before_next_page(player, timeout_happened):
        player.participant.endCode = '013'

    @staticmethod
    def is_displayed(player: Player):
        otherPlayer = other_player(player)
        if np.logical_and(not player.participant.dropped, not otherPlayer.participant.dropped):
            return not (np.logical_and(player.back_label, otherPlayer.back_label))


class SuccessNoReviewProlific(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        player.participant.dropped = True  # needed to make sure Collab eval task pages do not show
        return dict(
            bonuspayment=player.subsession.session.config['bonuspayment']
        )

    @staticmethod
    def is_displayed(player: Player):
        return np.logical_and(not player.participant.dropped, player.participant.endCode == '013')


class CollaborativeEvalTakeTwoR1(Page):
    timeout_seconds = 60 * C.COLLABORATIVE_TIME

    form_model = 'player'
    form_fields = ['evidenceEval_COLL_TakeTwo']

    @staticmethod
    def vars_for_template(player: Player):
        player.starts_collaborativeEvalTakeTwo = time.time()
        group = player.group
        otherPlayer = other_player(player)
        return dict(image_path='images/' + group.image,
                    Nickname_chat_one=chat_nickname(player),
                    individual_label=return_misinformation_label(player, player.evidenceEval_IND),
                    individual_text=player.suggestedEdit_IND,
                    my_eval=return_misinformation_label(player, player.evidenceEval_COLL),
                    partner_eval=return_misinformation_label(otherPlayer, otherPlayer.evidenceEval_COLL),
                    my_text=player.suggestedEdit_COLL,
                    partner_text=otherPlayer.suggestedEdit_COLL,
                    code=player.participant.code
                    )

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        # PREPARE FOR SIMILARITY CHECK
        player.cleanText_TakeTwo = player.cleanText  # TEXT HAS NOT CHANGE
        if timeout_happened:
            player.timeout_collaborativeEvalTakeTwo = True
            player.participant.endCode = return_EndCodes_CollabTWO(player)
        else:
            # MIS/notMIS
            if player.evidenceEval_COLL_TakeTwo == 3:  # 3: not misleading
                participant.misleading_COLL = False
            else:
                participant.misleading_COLL = True
            suggestedEdit_COLL_TakeTwo = player.suggestedEdit_COLL  # TEXT HAS NOT CHANGE
        # NEEDED TO BLOCK MULTIPLE ATTEMPTS
        player.collabEval_tryN = player.collabEval_tryN + 1

    @staticmethod
    def is_displayed(player: Player):
        otherPlayer = other_player(player)
        if np.logical_and(not player.participant.dropped, not otherPlayer.participant.dropped):
            return np.logical_and((player.back_label and otherPlayer.back_label),
                                  (player.reason_return == 1 and otherPlayer.reason_return == 1))


class CollaborativeEvalTakeTwoR2(Page):
    timeout_seconds = 60 * C.COLLABORATIVE_TIME

    form_model = 'player'
    form_fields = ['suggestedEdit_COLL_TakeTwo']

    @staticmethod
    def vars_for_template(player: Player):
        player.starts_collaborativeEvalTakeTwo = time.time()
        group = player.group
        otherPlayer = other_player(player)
        return dict(image_path='images/' + group.image,
                    Nickname_chat_one=chat_nickname(player),
                    individual_label=return_misinformation_label(player, player.evidenceEval_IND),
                    individual_text=player.suggestedEdit_IND,
                    my_eval=return_misinformation_label(player, player.evidenceEval_COLL),
                    partner_eval=return_misinformation_label(otherPlayer, otherPlayer.evidenceEval_COLL),
                    my_text=player.suggestedEdit_COLL,
                    partner_text=otherPlayer.suggestedEdit_COLL,
                    code=player.participant.code
                    )

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        if timeout_happened:
            player.timeout_collaborativeEvalTakeTwo = True
            player.participant.endCode = return_EndCodes_CollabTWO(player)
            # PREPARE FOR SIMILARITY CHECK
            player.cleanText_TakeTwo = player.cleanText  # TEXT HAS NOT CHANGE
        else:
            player.evidenceEval_COLL_TakeTwo = player.evidenceEval_COLL  # LABEL HAS NOT CHANGED
            # PREPARE FOR SIMILARITY CHECK
            player.cleanText_TakeTwo = clean_text(player, player.suggestedEdit_COLL_TakeTwo)
        # NEEDED TO BLOCK MULTIPLE ATTEMPTS
        player.collabEval_tryN = player.collabEval_tryN + 1

    @staticmethod
    def is_displayed(player: Player):
        otherPlayer = other_player(player)
        if np.logical_and(not player.participant.dropped, not otherPlayer.participant.dropped):
            return np.logical_and((player.back_label and otherPlayer.back_label),
                                  (player.reason_return == 2 and otherPlayer.reason_return == 2))


class CollaborativeEvalTakeTwoR3(Page):
    timeout_seconds = 60 * C.COLLABORATIVE_TIME

    form_model = 'player'
    form_fields = ['evidenceEval_COLL_TakeTwo', 'suggestedEdit_COLL_TakeTwo']

    @staticmethod
    def vars_for_template(player: Player):
        player.starts_collaborativeEvalTakeTwo = time.time()
        group = player.group
        otherPlayer = other_player(player)
        return dict(image_path='images/' + group.image,
                    Nickname_chat_one=chat_nickname(player),
                    individual_label=return_misinformation_label(player, player.evidenceEval_IND),
                    individual_text=player.suggestedEdit_IND,
                    my_eval=return_misinformation_label(player, player.evidenceEval_COLL),
                    partner_eval=return_misinformation_label(otherPlayer, otherPlayer.evidenceEval_COLL),
                    my_text=player.suggestedEdit_COLL,
                    partner_text=otherPlayer.suggestedEdit_COLL,
                    code=player.participant.code
                    )

    @staticmethod
    def before_next_page(player, timeout_happened):
        participant = player.participant
        if timeout_happened:
            player.timeout_collaborativeEvalTakeTwo = True
            player.participant.endCode = return_EndCodes_CollabTWO(player)
            # PREPARE FOR SIMILARITY CHECK
            player.cleanText_TakeTwo = player.cleanText  # TEXT HAS NOT CHANGE
        else:
            # MIS/notMIS
            if player.evidenceEval_COLL_TakeTwo == 3:  # 3: not misleading
                participant.misleading_COLL = False
            else:
                participant.misleading_COLL = True
            # PREPARE FOR SIMILARITY CHECK
            player.cleanText_TakeTwo = clean_text(player, player.suggestedEdit_COLL_TakeTwo)
        # NEEDED TO BLOCK MULTIPLE ATTEMPTS
        player.collabEval_tryN = player.collabEval_tryN + 1

    @staticmethod
    def is_displayed(player: Player):
        otherPlayer = other_player(player)
        if np.logical_and(not player.participant.dropped, not otherPlayer.participant.dropped):
            return np.logical_and((player.back_label and otherPlayer.back_label),
                                  (player.reason_return == 3 and otherPlayer.reason_return == 3))


class SimilarityTakeTwoWaitPage(WaitPage):
    @staticmethod
    def after_all_players_arrive(group: Group):
        for player in group.get_players():
            otherPlayer = other_player(player)
            # DEFINING REFERENCE AND COMPARING TEXT
            if player.role == C.REFERENCE_ROLE:
                reference_text = player.cleanText_TakeTwo
                comparing_text = otherPlayer.cleanText_TakeTwo
            else:
                reference_text = otherPlayer.cleanText_TakeTwo
                comparing_text = player.cleanText_TakeTwo
            # CALCULATING TEXT SIMILARITY
            player.text_similarity_TakeTwo = SequenceMatcher(a=reference_text, b=comparing_text).ratio()
            # HAS FAILED SIMILARITY CHECK? NEED TO ADD ELSE TO CHANGE PREVIOUS ANSWER
            if player.text_similarity_TakeTwo < C.SIMILARITY_SCORE:
                player.failed_similarity = True
            else:
                player.failed_similarity = False
            # HAS FAILED MISINFORMATION CHECK? NEED TO ADD ELSE TO CHANGE PREVIOUS ANSWER
            if player.participant.misleading_COLL != otherPlayer.participant.misleading_COLL:
                player.failed_misinformation = True
            else:
                player.failed_misinformation = False
            player.reason_return = reason_to_return(player)
            # RECORD REASON FOR INCONSISTENCY AND END CODES
            if np.logical_and(not player.failed_similarity, not player.failed_misinformation):
                player.participant.endCode = '008'  # successful completion
                print("ERROR CODE: ", player.participant.endCode)
            else:
                player.participant.endCode = '009'  # finish with inconsistencies
                print("ERROR CODE: ", player.participant.endCode)
            print(check_sim_vars(player), player.participant.endCode)

    @staticmethod
    def is_displayed(player: Player):
        otherPlayer = other_player(player)
        if np.logical_and(not player.participant.dropped, not otherPlayer.participant.dropped):
            return np.logical_and(player.back_label, otherPlayer.back_label)


class NoMatchFeedback(Page):
    form_model = 'player'
    form_fields = ['why_label', 'why_text', 'collabEval', 'other_expand']

    @staticmethod
    def vars_for_template(player: Player):
        otherPlayer = other_player(player)
        return dict(
            my_eval=return_misinformation_label(player, player.evidenceEval_COLL),
            partner_eval=return_misinformation_label(otherPlayer, otherPlayer.evidenceEval_COLL),
            my_text=player.suggestedEdit_COLL,
            partner_text=otherPlayer.suggestedEdit_COLL,
            reason_one=player.reason_return == 1,
            reason_two=player.reason_return == 2,
            reason_three=player.reason_return == 3,
        )

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.dropped and player.participant.endCode == '009'


class YesMatchFeedback(Page):
    form_model = 'player'
    form_fields = ['collabEval', 'other_expand']

    @staticmethod
    def is_displayed(player: Player):
        return not player.participant.dropped and player.participant.endCode == '008'


class SuccessEndProlific(Page):
    form_model = 'player'

    @staticmethod
    def js_vars(player):
        player.participant.dropped = True  # needed to make sure Collab eval task pages do not show
        return dict(
            bonuspayment=player.subsession.session.config['bonuspayment']
        )

    @staticmethod
    def is_displayed(player: Player):
        return np.logical_and(not player.participant.dropped, np.logical_or(player.participant.endCode == '008',
                                                                            player.participant.endCode == '009'))


page_sequence = [
    ResultsWaitPage, WaitTreatments, IndividualEval, AttentionCheck, FailedIndividualCheck, FailedAttentionProlific,
    IndividualEvalTakeTwo, FailedIndividualEvalTwice, FailedIndividualEvalTwiceProlific, IndividualQsMis,
    IndividualQsNotMis, IndividualSuccess, IndividualSuccessProlific, MyWaitPage, CollaborativeEval, TimedOut,
    TimedOutProlific, SimilarityWaitPage, CollabTaskCompleted, CollabTaskCompletedProlific, MisinformationCheck,
    MisinformationWaitPage, NoReview, SuccessNoReviewProlific, CollaborativeEvalTakeTwoR1, CollaborativeEvalTakeTwoR2,
    CollaborativeEvalTakeTwoR3, SimilarityTakeTwoWaitPage, NoMatchFeedback, YesMatchFeedback, SuccessEndProlific
]
