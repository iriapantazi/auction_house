#! /usr/bin/env python 

import auction_house as ah
import pytest
import unittest


@pytest.mark.parametrize('sample,expected', [
    ('13|5|SELL|toaster_1|10|21', True), 
    ('13|5|BID|toaster_1|10', True), 
    ('13', True), 
    ('13|', False), 
    ('a', False), 
    ('\n', False), 
    ('', False), 
    ('13|5|BID|toaster_1|10', True), 
    ('13|5|BID|toaster_1|10|21', False),
    ('13|5|SELL|toaster_1|10|no', False),
    ('13|5|SE|toaster_1|10|21', False),
    ('13|5|SELL|toaster_1|10|21', True),
    ])
def test_message_isValid(sample, expected):
    """
    """
    amazon = ah.AuctionHouse(sample)
    returned = amazon.message_isValid()
    assert returned == expected


@pytest.mark.parametrize('fields,msg_type,expected', [
    ([13, 5, 'SELL', 'toaster_1', 10, 21], 'SELL', True), 
    ([13, 5, 'SELL', 'toaster_1', 10, 'no'], 'SELL', False), 
    ([13, 5, 'SELL', 'toaster_1', 10], 'SELL', False), 
    ([13, 5, 'SELL', 'toaster_1', 10], 'BID', True), 
    ([13, 5, 'BID', 'toaster_1', 10], 'BID', True), 
    ([13, 5, 'BID', 'toaster_1', 'no'], 'BID', False), 
    ])
def test_validate_message(fields, msg_type, expected):
    """
    this function will only assert that the expected
    type of argument was inserted in fields
    It is a bit naive to test it since does not
    catch major errors, like expected fields list
    of size 5 and received a list of size 6.
    Also will not catch an error of having
    msg_type='SELL' but received a different
    fields[2] that is a string.
    Those mistakes are taken under consideration
    in the function test_isValid that calls the
    function test_validate_message to assert
    the correct type of the fields.
    """
    returned = ah.validate_message(fields, msg_type)
    assert returned == expected


