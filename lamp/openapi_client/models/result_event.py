# coding: utf-8

"""
    LAMP Platform

    The LAMP Platform API.  # noqa: E501

    OpenAPI spec version: 0.1
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class ResultEvent(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        'id': 'str',
        'attachments': 'dict(str, object)',
        'activity': 'str',
        'timestamp': 'int',
        'duration': 'int',
        'static_data': 'object',
        'temporal_events': 'list[TemporalEvent]'
    }

    attribute_map = {
        'id': 'id',
        'attachments': 'attachments',
        'activity': 'activity',
        'timestamp': 'timestamp',
        'duration': 'duration',
        'static_data': 'static_data',
        'temporal_events': 'temporal_events'
    }

    def __init__(self, id=None, attachments=None, activity=None, timestamp=None, duration=None, static_data=None, temporal_events=None):  # noqa: E501
        """ResultEvent - a model defined in OpenAPI"""  # noqa: E501

        self._id = None
        self._attachments = None
        self._activity = None
        self._timestamp = None
        self._duration = None
        self._static_data = None
        self._temporal_events = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if attachments is not None:
            self.attachments = attachments
        if activity is not None:
            self.activity = activity
        if timestamp is not None:
            self.timestamp = timestamp
        if duration is not None:
            self.duration = duration
        if static_data is not None:
            self.static_data = static_data
        if temporal_events is not None:
            self.temporal_events = temporal_events

    @property
    def id(self):
        """Gets the id of this ResultEvent.  # noqa: E501

        A globally unique reference for objects within the LAMP platform.  # noqa: E501

        :return: The id of this ResultEvent.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this ResultEvent.

        A globally unique reference for objects within the LAMP platform.  # noqa: E501

        :param id: The id of this ResultEvent.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def attachments(self):
        """Gets the attachments of this ResultEvent.  # noqa: E501


        :return: The attachments of this ResultEvent.  # noqa: E501
        :rtype: dict(str, object)
        """
        return self._attachments

    @attachments.setter
    def attachments(self, attachments):
        """Sets the attachments of this ResultEvent.


        :param attachments: The attachments of this ResultEvent.  # noqa: E501
        :type: dict(str, object)
        """

        self._attachments = attachments

    @property
    def activity(self):
        """Gets the activity of this ResultEvent.  # noqa: E501

        A globally unique reference for objects within the LAMP platform.  # noqa: E501

        :return: The activity of this ResultEvent.  # noqa: E501
        :rtype: str
        """
        return self._activity

    @activity.setter
    def activity(self, activity):
        """Sets the activity of this ResultEvent.

        A globally unique reference for objects within the LAMP platform.  # noqa: E501

        :param activity: The activity of this ResultEvent.  # noqa: E501
        :type: str
        """

        self._activity = activity

    @property
    def timestamp(self):
        """Gets the timestamp of this ResultEvent.  # noqa: E501


        :return: The timestamp of this ResultEvent.  # noqa: E501
        :rtype: int
        """
        return self._timestamp

    @timestamp.setter
    def timestamp(self, timestamp):
        """Sets the timestamp of this ResultEvent.


        :param timestamp: The timestamp of this ResultEvent.  # noqa: E501
        :type: int
        """

        self._timestamp = timestamp

    @property
    def duration(self):
        """Gets the duration of this ResultEvent.  # noqa: E501


        :return: The duration of this ResultEvent.  # noqa: E501
        :rtype: int
        """
        return self._duration

    @duration.setter
    def duration(self, duration):
        """Sets the duration of this ResultEvent.


        :param duration: The duration of this ResultEvent.  # noqa: E501
        :type: int
        """

        self._duration = duration

    @property
    def static_data(self):
        """Gets the static_data of this ResultEvent.  # noqa: E501

        The summary information for the result event as determined by the activity that created this result event.  # noqa: E501

        :return: The static_data of this ResultEvent.  # noqa: E501
        :rtype: object
        """
        return self._static_data

    @static_data.setter
    def static_data(self, static_data):
        """Sets the static_data of this ResultEvent.

        The summary information for the result event as determined by the activity that created this result event.  # noqa: E501

        :param static_data: The static_data of this ResultEvent.  # noqa: E501
        :type: object
        """

        self._static_data = static_data

    @property
    def temporal_events(self):
        """Gets the temporal_events of this ResultEvent.  # noqa: E501

        The specific interaction details of the result event.  # noqa: E501

        :return: The temporal_events of this ResultEvent.  # noqa: E501
        :rtype: list[TemporalEvent]
        """
        return self._temporal_events

    @temporal_events.setter
    def temporal_events(self, temporal_events):
        """Sets the temporal_events of this ResultEvent.

        The specific interaction details of the result event.  # noqa: E501

        :param temporal_events: The temporal_events of this ResultEvent.  # noqa: E501
        :type: list[TemporalEvent]
        """

        self._temporal_events = temporal_events

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, ResultEvent):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other