#! /usr/bin/env python

MSG_SELL = 'SELL'
MSG_BID = 'BID'
MSG_TYPES = ['SELL', 'BID']

class AuctionHouse():
    """
    AuctionHouse:
    This class is responsible for validating
    actions of an auction house. Each action
    is described by a delimiter separated string
    and is subject to rules described in the
    README.md file.
    """

    def __init__(self, inline, entries=[], outcome=[]):
        self.inline = inline
        self.entries = entries
        self.outcome = outcome


    def print_outcome(self):
        """
        prints the outcome once a timestamp is received
        """
        for entry in self.outcome: 
            if entry.get("status") == 'SOLD':
                print('{}|{}|{}|{}|{}|{}|{}|{}'.format(
                    entry.get("when_sold"),
                    entry.get("item"),
                    entry.get("validBid1").get("user_id"),
                    entry.get("status"),
                    entry.get("validBid2offer").get("bid_amount"),
                    '_',
                    entry.get("validBid1").get("bid_amount"),
                    '_'
                    ))
            else:
                print('{}|{}||{}|{}|{}|{}|{}'.format(
                    entry.get("when_sold"),
                    entry.get("item"),
                    entry.get("status"),
                    0,
                    '_',
                    entry.get("reserve_price"),
                    '_'
                    ))


    def process_message_sell(self, fields):
        """
        This function will handle SELL messages
        """
        poss_entry = {
                "timestamp": int(fields[0]),
                "user_id": int(fields[1]),
                "action": fields[2],
                "item": fields[3],
                "reserve_price": float(fields[4]),
                "close_time": int(fields[5]),
                "validBid1": {},
                "validBid2offer": {},
                }
        if self.entries == []:
            self.entries.append(poss_entry)
        else: 
            for i in self.entries: 
                if poss_entry.get("item") != i.get("item"):
                    self.entries.append(poss_entry)
    

    def process_message_bid(self, fields):
        """
        This function will handle BID messages
        """
        poss_entry = {
                "timestamp": int(fields[0]),
                "user_id": int(fields[1]),
                "action": fields[2],
                "item": fields[3],
                "bid_amount": float(fields[4]),
                }
        for i in self.entries:
            if satisfied_criteria_bid(poss_entry, i):
                where_to_store(poss_entry, i)



    def process_timestamp(self, timestamp):
        """
        If it is a valid timestamp, process all the SELL and 
        BID messages, close SELLs if timestamp > close_time
        and announce result.
        """
        timestamp = int(timestamp)
        for entry in self.entries:
            if entry.get("close_time") <= timestamp:
                isSold = close_auctions_announce(entry, timestamp)
                if isSold:
                    entry["status"] = "SOLD"
                else:
                    entry["status"] = "UNSOLD"
                entry["when_sold"] = timestamp
                self.outcome.append(entry)


    def message_isValid(self) -> bool:
        """
        message_isValid:
        Args: a message line of type string.
        Returns: True if message was processed,
                and False otherwise.
        """
        
        if not self.inline:
            return False

        if self.inline.find('|') == -1:
            try:
                timestamp = int(self.inline)
                isValid = True
            except Exception as e:
                print('Error: No timestamp in message without delimiters '
                        'in line ', self.inline)
                isValid = False
        else:
            fields = self.inline.strip('\n')
            fields = fields.split('|')
            if len(fields) == 6 and fields[2] == MSG_SELL:
                isValid = validate_message(fields, MSG_SELL)
            elif len(fields) == 5 and fields[2] == MSG_BID:
                isValid = validate_message(fields, MSG_BID)
            else:
                isValid = False
        return(isValid)


def close_auctions_announce(entry, timestamp):
    """
    This function will close the auctions with
    close_time < timestamp.
    """
    isSold = True
    if entry.get("validBid1") == {}:
        isSold = False
    return(isSold)


def where_to_store(accepted, auctioned):
    """
    function that stores the accepted BID
    in the appropriate position.
    It is discarded if does not meet the
    criteria that two BIDs must satisfy.
    """
    if auctioned.get("validBid1") == {}:
        auctioned["validBid1"] = accepted
    elif auctioned.get("validBid2offer") == {}:
        if auctioned.get("validBid1").get("bid_amount") >=\
            accepted.get("bid_amount"):    
            auctioned["validBid2offer"] = accepted
        else:
            auctioned["validBid2offer"] = auctioned["validBid1"]
            auctioned["validBid1"] = accepted
    else:
        first, second = compare_bids(accepted, auctioned.get("validBid1"), auctioned.get("validBid2offer"))
        auctioned["validBid1"] = first
        auctioned["validBid2offer"] = second


def compare_bids(accepted, firstCandidate, secondCandidate):
    """
    """
    if accepted.get("bid_amount") > firstCandidate.get("bid_amount"):
        secondCandidate = firstCandidate
        firstCandidate = accepted
    else:
        if accepted.get("bid_amount") > secondCandidate.get("bid_amount"):
            secondCandidate = accepted
    return(firstCandidate, secondCandidate)
        

def satisfied_criteria_bid(possible, auctioned) ->bool:
    """
    function that returns True if the BID is valid.
    """
    satisfied = False
    if possible.get("item") == auctioned.get("item"):
        if possible.get("bid_amount") > auctioned.get("reserve_price"):
            satisfied = True
    return satisfied


def validate_message(fields:list, msg_type:str) -> bool:
    """
    validate_message:
    Args: fields:list of strings
        msg_type: either 'SELL' of 'BID'
    Returns: boolean
    This function validates the messages only
    for SELL and BID and returns a boolean
    True if the message is valid,
    and False otherwise.
    """
    VALID_MSG_FORMATS = {
            MSG_SELL:{
                0: {'name':'timestampt', 'validType':int},
                1: {'name':'user_id', 'validType':int},
                2: {'name':'action', 'validType':str},
                3: {'name':'item', 'validType':str},
                4: {'name':'reserve_price', 'validType':float},
                5: {'name':'close_time', 'validType':int}
                },
            MSG_BID:{
                0: {'name':'timestampt', 'validType':int},
                1: {'name':'user_id', 'validType':int},
                2: {'name':'action', 'validType':str},
                3: {'name':'item', 'validType':str},
                4: {'name':'bid_amount', 'validType':float}
                }
            }

    if (msg_type not in MSG_TYPES) and (msg_type not in VALID_MSG_FORMATS.keys()):
        print('Unimplemented message type {}'.format(msg_type))
        msgValid = False

    for index, validator in VALID_MSG_FORMATS.get(msg_type).items():
        try:
            validator_function = validator.get('validType')
            expected = validator_function(fields[index])
            expected = type(fields[index])
            msgValid = True
        except Exception as e:
            print('Validator Error: In {} the field {} contains '
                    'an unexpected format of {} while expecting ' 
                    '{}.'.format(fields, index, str(expected),
                    str(validator.get('validType'))))
            msgValid = False
    return msgValid
