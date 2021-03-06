# Copyright 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Integration tests for firebase_admin.messaging module."""

import re
from datetime import datetime

# import pytest

from firebase_admin import exceptions
from firebase_admin import messaging, credentials

import firebase_admin


_REGISTRATION_TOKEN = (
    'fPW9bjf1Q0GVsTLhqWlbyn:APA91bHbE7EWJuOLkaRez-f513pDW73jvDsqM58YUuAej74dpF7SlEGU-oRXTuAXW9xgNofrw3IOfnlNrNLq3WJEBZjsNIemRuMsVFNk_THUyaOgP9DmbVqwvd3xssubFcJwUe8Sb-Gc')


# def init_firebase():
cred = credentials.Certificate(r"flutter-notification.json")
firebase_admin.initialize_app(cred)
    # firebase_admin.delete_app(default_app)

def test_send():

    msg = messaging.Message(
        topic='foo-bar',
        notification=messaging.Notification('test-title', 'test-body',
                                            'https://images.unsplash.com/photo-1494438639946'
                                            '-1ebd1d20bf85?fit=crop&w=900&q=60'),
        android=messaging.AndroidConfig(
            restricted_package_name='com.example.lcms_app',
            notification=messaging.AndroidNotification(
                title='android-title',
                body='android-body',
                image='https://images.unsplash.com/'
                      'photo-1494438639946-1ebd1d20bf85?fit=crop&w=900&q=60',
                event_timestamp=datetime.now(),
                priority='high',
                vibrate_timings_millis=[100, 200, 300, 400],
                visibility='public',
                sticky=True,
                local_only=False,
                default_vibrate_timings=False,
                default_sound=True,
                default_light_settings=False,
                light_settings=messaging.LightSettings(
                    color='#aabbcc',
                    light_off_duration_millis=200,
                    light_on_duration_millis=300
                ),
                notification_count=1
            )
        ),
        apns=messaging.APNSConfig(payload=messaging.APNSPayload(
            aps=messaging.Aps(
                alert=messaging.ApsAlert(
                    title='apns-title',
                    body='apns-body'
                )
            )
        ))
    )
    msg_id = messaging.send(msg)
    print(msg_id)
    # assert re.match('^projects/.*/messages/.*$', msg_id)


def test_send_invalid_token(title, body, data, registration_token):
    # msg = messaging.Message(
    #     token=registration_token,
    #     notification=messaging.Notification(title, body,
    #                                         'https://images.unsplash.com/photo-1494438639946'
    #                                         '-1ebd1d20bf85?fit=crop&w=900&q=60'),
    #     data= data,
    # )
    # response = messaging.send(msg)

    multicast = messaging.MulticastMessage(
        notification=messaging.Notification('Title', 'Body'),
        tokens=[registration_token])

    response = messaging.send_multicast(multicast)
    # Response is a message ID string.
    # print('Successfully sent message:', response)
    print('response', response.success_count, response.failure_count)
    # print('Successfully sent message:', batch_response)


def test_send_malformed_token():
    msg = messaging.Message(
        token='not-a-token',
        notification=messaging.Notification('test-title', 'test-body')
    )
    with pytest.raises(exceptions.InvalidArgumentError):
        messaging.send(msg, dry_run=True)


def test_send_all():
    messages = [
        messaging.Message(
            topic='foo-bar', notification=messaging.Notification('Title', 'Body')),
        messaging.Message(
            topic='foo-bar', notification=messaging.Notification('Title', 'Body')),
        messaging.Message(
            token='not-a-token', notification=messaging.Notification('Title', 'Body')),
    ]

    batch_response = messaging.send_all(messages, dry_run=True)

    assert batch_response.success_count == 2
    assert batch_response.failure_count == 1
    assert len(batch_response.responses) == 3

    response = batch_response.responses[0]
    assert response.success is True
    assert response.exception is None
    assert re.match('^projects/.*/messages/.*$', response.message_id)

    response = batch_response.responses[1]
    assert response.success is True
    assert response.exception is None
    assert re.match('^projects/.*/messages/.*$', response.message_id)

    response = batch_response.responses[2]
    assert response.success is False
    assert isinstance(response.exception, exceptions.InvalidArgumentError)
    assert response.message_id is None


def test_send_all_500():
    messages = []
    for msg_number in range(500):
        topic = 'foo-bar-{0}'.format(msg_number % 10)
        messages.append(messaging.Message(topic=topic))

    batch_response = messaging.send_all(messages, dry_run=True)

    assert batch_response.success_count == 500
    assert batch_response.failure_count == 0
    assert len(batch_response.responses) == 500
    for response in batch_response.responses:
        assert response.success is True
        assert response.exception is None
        assert re.match('^projects/.*/messages/.*$', response.message_id)


def test_send_multicast():
    multicast = messaging.MulticastMessage(
        notification=messaging.Notification('Title', 'Body'),
        tokens=['not-a-token', 'also-not-a-token'])

    batch_response = messaging.send_multicast(multicast)

    assert batch_response.success_count == 0
    assert batch_response.failure_count == 2
    assert len(batch_response.responses) == 2
    for response in batch_response.responses:
        assert response.success is False
        assert response.exception is not None
        assert response.message_id is None


def test_subscribe():
    resp = messaging.subscribe_to_topic(_REGISTRATION_TOKEN, 'mock-topic')
    assert resp.success_count + resp.failure_count == 1


def test_unsubscribe():
    resp = messaging.unsubscribe_from_topic(_REGISTRATION_TOKEN, 'mock-topic')
    assert resp.success_count + resp.failure_count == 1
