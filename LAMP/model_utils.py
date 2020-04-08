# coding: utf-8

"""
    LAMP Platform

    The LAMP Platform API.

    The version of the OpenAPI document: 1.0.0
    Contact: team@digitalpsych.org
"""


from datetime import date, datetime
import inspect
import os
import pprint
import re
import tempfile

from dateutil.parser import parse
import six

from LAMP.exceptions import (
    ApiKeyError,
    ApiTypeError,
    ApiValueError,
)

none_type = type(None)
if six.PY3:
    import io
    file_type = io.IOBase
    # these are needed for when other modules import str and int from here
    str = str
    int = int
else:
    file_type = file
    str_py2 = str
    unicode_py2 = unicode
    long_py2 = long
    int_py2 = int
    # this requires that the future library is installed
    from builtins import int, str


class OpenApiModel(object):
    """The base class for all OpenAPIModels"""

    def set_attribute(self, name, value):
        # this is only used to set properties on self

        path_to_item = []
        if self._path_to_item:
            path_to_item.extend(self._path_to_item)
        path_to_item.append(name)

        openapi_types = self.openapi_types()
        if name in openapi_types:
            required_types_mixed = openapi_types[name]
        elif self.additional_properties_type is None:
            raise ApiKeyError(
                "{0} has no key '{1}'".format(type(self).__name__, name),
                path_to_item
            )
        elif self.additional_properties_type is not None:
            required_types_mixed = self.additional_properties_type

        if get_simple_class(name) != str:
            error_msg = type_error_message(
                var_name=name,
                var_value=name,
                valid_classes=(str,),
                key_type=True
            )
            raise ApiTypeError(
                error_msg,
                path_to_item=path_to_item,
                valid_classes=(str,),
                key_type=True
            )

        if self._check_type:
            value = validate_and_convert_types(
                value, required_types_mixed, path_to_item, self._from_server,
                self._check_type, configuration=self._configuration)
        if (name,) in self.allowed_values:
            check_allowed_values(
                self.allowed_values,
                (name,),
                value
            )
        if (name,) in self.validations:
            check_validations(
                self.validations,
                (name,),
                value
            )
        self.__dict__['_data_store'][name] = value

    def __setitem__(self, name, value):
        """this allows us to set values with instance[field_name] = val"""
        self.__setattr__(name, value)

    def __getitem__(self, name):
        """this allows us to get a value with val = instance[field_name]"""
        return self.__getattr__(name)

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other


class ModelSimple(OpenApiModel):
    """the parent class of models whose type != object in their
    swagger/openapi"""

    def __setattr__(self, name, value):
        """this allows us to set a value with instance.field_name = val"""
        if name in self.required_properties:
            self.__dict__[name] = value
            return

        self.set_attribute(name, value)

    def __getattr__(self, name):
        """this allows us to get a value with val = instance.field_name"""
        if name in self.required_properties:
            return self.__dict__[name]

        if name in self.__dict__['_data_store']:
            return self.__dict__['_data_store'][name]

        path_to_item = []
        if self._path_to_item:
            path_to_item.extend(self._path_to_item)
        path_to_item.append(name)
        raise ApiKeyError(
            "{0} has no key '{1}'".format(type(self).__name__, name),
            [name]
        )

    def to_str(self):
        """Returns the string representation of the model"""
        return str(self.value)

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, self.__class__):
            return False

        this_val = self._data_store['value']
        that_val = other._data_store['value']
        types = set()
        types.add(this_val.__class__)
        types.add(that_val.__class__)
        vals_equal = this_val == that_val
        if not six.PY3 and len(types) == 2 and unicode in types:
            vals_equal = (
                this_val.encode('utf-8') == that_val.encode('utf-8')
            )
        if not vals_equal:
            return False
        return True


class ModelNormal(OpenApiModel):
    """the parent class of models whose type == object in their
    swagger/openapi"""

    def __setattr__(self, name, value):
        """this allows us to set a value with instance.field_name = val"""
        if name in self.required_properties:
            self.__dict__[name] = value
            return

        self.set_attribute(name, value)

    def __getattr__(self, name):
        """this allows us to get a value with val = instance.field_name"""
        if name in self.required_properties:
            return self.__dict__[name]

        if name in self.__dict__['_data_store']:
            return self.__dict__['_data_store'][name]

        path_to_item = []
        if self._path_to_item:
            path_to_item.extend(self._path_to_item)
        path_to_item.append(name)
        raise ApiKeyError(
            "{0} has no key '{1}'".format(type(self).__name__, name),
            [name]
        )

    def to_dict(self):
        """Returns the model properties as a dict"""
        return model_to_dict(self, serialize=False)

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, self.__class__):
            return False

        if not set(self._data_store.keys()) == set(other._data_store.keys()):
            return False
        for _var_name, this_val in six.iteritems(self._data_store):
            that_val = other._data_store[_var_name]
            types = set()
            types.add(this_val.__class__)
            types.add(that_val.__class__)
            vals_equal = this_val == that_val
            if (not six.PY3 and
                    len(types) == 2 and unicode in types):
                vals_equal = (
                    this_val.encode('utf-8') == that_val.encode('utf-8')
                )
            if not vals_equal:
                return False
        return True


class ModelComposed(OpenApiModel):
    """the parent class of models whose type == object in their
    swagger/openapi and have oneOf/allOf/anyOf"""

    def __setattr__(self, name, value):
        """this allows us to set a value with instance.field_name = val"""
        if name in self.required_properties:
            self.__dict__[name] = value
            return

        # set the attribute on the correct instance
        model_instances = self._var_name_to_model_instances.get(
            name, self._additional_properties_model_instances)
        if model_instances:
            for model_instance in model_instances:
                if model_instance == self:
                    self.set_attribute(name, value)
                else:
                    setattr(model_instance, name, value)
                if name not in self._var_name_to_model_instances:
                    # we assigned an additional property
                    self.__dict__['_var_name_to_model_instances'][name] = (
                        model_instance
                    )
            return None

        path_to_item = []
        if self._path_to_item:
            path_to_item.extend(self._path_to_item)
        path_to_item.append(name)
        raise ApiKeyError(
            "{0} has no key '{1}'".format(type(self).__name__, name),
            path_to_item
        )

    def __getattr__(self, name):
        """this allows us to get a value with val = instance.field_name"""
        if name in self.required_properties:
            return self.__dict__[name]

        # get the attribute from the correct instance
        model_instances = self._var_name_to_model_instances.get(
            name, self._additional_properties_model_instances)
        path_to_item = []
        if self._path_to_item:
            path_to_item.extend(self._path_to_item)
        path_to_item.append(name)
        values = set()
        if model_instances:
            for model_instance in model_instances:
                if name in model_instance._data_store:
                    values.add(model_instance._data_store[name])
        len_values = len(values)
        if len_values == 0:
            raise ApiKeyError(
                "{0} has no key '{1}'".format(type(self).__name__, name),
                path_to_item
            )
        elif len_values == 1:
            return list(values)[0]
        elif len_values > 1:
            raise ApiValueError(
                "Values stored for property {0} in {1} difffer when looking "
                "at self and self's composed instances. All values must be "
                "the same".format(name, type(self).__name__),
                path_to_item
            )

    def to_dict(self):
        """Returns the model properties as a dict"""
        return model_to_dict(self, serialize=False)

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, self.__class__):
            return False

        if not set(self._data_store.keys()) == set(other._data_store.keys()):
            return False
        for _var_name, this_val in six.iteritems(self._data_store):
            that_val = other._data_store[_var_name]
            types = set()
            types.add(this_val.__class__)
            types.add(that_val.__class__)
            vals_equal = this_val == that_val
            if (not six.PY3 and
                    len(types) == 2 and unicode in types):
                vals_equal = (
                    this_val.encode('utf-8') == that_val.encode('utf-8')
                )
            if not vals_equal:
                return False
        return True


COERCION_INDEX_BY_TYPE = {
    ModelComposed: 0,
    ModelNormal: 1,
    ModelSimple: 2,
    none_type: 3,
    list: 4,
    dict: 5,
    float: 6,
    int: 7,
    bool: 8,
    datetime: 9,
    date: 10,
    str: 11,
    file_type: 12,
}

# these are used to limit what type conversions we try to do
# when we have a valid type already and we want to try converting
# to another type
UPCONVERSION_TYPE_PAIRS = (
    (str, datetime),
    (str, date),
    (list, ModelComposed),
    (dict, ModelComposed),
    (list, ModelNormal),
    (dict, ModelNormal),
    (str, ModelSimple),
    (int, ModelSimple),
    (float, ModelSimple),
    (list, ModelSimple),
)

COERCIBLE_TYPE_PAIRS = {
    False: (  # client instantiation of a model with client data
        # (dict, ModelComposed),
        # (list, ModelComposed),
        # (dict, ModelNormal),
        # (list, ModelNormal),
        # (str, ModelSimple),
        # (int, ModelSimple),
        # (float, ModelSimple),
        # (list, ModelSimple),
        # (str, int),
        # (str, float),
        # (str, datetime),
        # (str, date),
        # (int, str),
        # (float, str),
    ),
    True: (  # server -> client data
        (dict, ModelComposed),
        (list, ModelComposed),
        (dict, ModelNormal),
        (list, ModelNormal),
        (str, ModelSimple),
        (int, ModelSimple),
        (float, ModelSimple),
        (list, ModelSimple),
        # (str, int),
        # (str, float),
        (str, datetime),
        (str, date),
        # (int, str),
        # (float, str),
        (str, file_type)
    ),
}


def get_simple_class(input_value):
    """Returns an input_value's simple class that we will use for type checking
    Python2:
    float and int will return int, where int is the python3 int backport
    str and unicode will return str, where str is the python3 str backport
    Note: float and int ARE both instances of int backport
    Note: str_py2 and unicode_py2 are NOT both instances of str backport

    Args:
        input_value (class/class_instance): the item for which we will return
                                            the simple class
    """
    if isinstance(input_value, type):
        # input_value is a class
        return input_value
    elif isinstance(input_value, tuple):
        return tuple
    elif isinstance(input_value, list):
        return list
    elif isinstance(input_value, dict):
        return dict
    elif isinstance(input_value, none_type):
        return none_type
    elif isinstance(input_value, file_type):
        return file_type
    elif isinstance(input_value, bool):
        # this must be higher than the int check because
        # isinstance(True, int) == True
        return bool
    elif isinstance(input_value, int):
        # for python2 input_value==long_instance -> return int
        # where int is the python3 int backport
        return int
    elif isinstance(input_value, datetime):
        # this must be higher than the date check because
        # isinstance(datetime_instance, date) == True
        return datetime
    elif isinstance(input_value, date):
        return date
    elif (six.PY2 and isinstance(input_value, (str_py2, unicode_py2, str)) or
            isinstance(input_value, str)):
        return str
    return type(input_value)


def check_allowed_values(allowed_values, input_variable_path, input_values):
    """Raises an exception if the input_values are not allowed

    Args:
        allowed_values (dict): the allowed_values dict
        input_variable_path (tuple): the path to the input variable
        input_values (list/str/int/float/date/datetime): the values that we
            are checking to see if they are in allowed_values
    """
    these_allowed_values = list(allowed_values[input_variable_path].values())
    if (isinstance(input_values, list)
            and not set(input_values).issubset(
                set(these_allowed_values))):
        invalid_values = ", ".join(
            map(str, set(input_values) - set(these_allowed_values))),
        raise ApiValueError(
            "Invalid values for `%s` [%s], must be a subset of [%s]" %
            (
                input_variable_path[0],
                invalid_values,
                ", ".join(map(str, these_allowed_values))
            )
        )
    elif (isinstance(input_values, dict)
            and not set(
                input_values.keys()).issubset(set(these_allowed_values))):
        invalid_values = ", ".join(
            map(str, set(input_values.keys()) - set(these_allowed_values)))
        raise ApiValueError(
            "Invalid keys in `%s` [%s], must be a subset of [%s]" %
            (
                input_variable_path[0],
                invalid_values,
                ", ".join(map(str, these_allowed_values))
            )
        )
    elif (not isinstance(input_values, (list, dict))
            and input_values not in these_allowed_values):
        raise ApiValueError(
            "Invalid value for `%s` (%s), must be one of %s" %
            (
                input_variable_path[0],
                input_values,
                these_allowed_values
            )
        )


def check_validations(validations, input_variable_path, input_values):
    """Raises an exception if the input_values are invalid

    Args:
        validations (dict): the validation dictionary
        input_variable_path (tuple): the path to the input variable
        input_values (list/str/int/float/date/datetime): the values that we
            are checking
    """
    current_validations = validations[input_variable_path]
    if ('max_length' in current_validations and
            len(input_values) > current_validations['max_length']):
        raise ApiValueError(
            "Invalid value for `%s`, length must be less than or equal to "
            "`%s`" % (
                input_variable_path[0],
                current_validations['max_length']
            )
        )

    if ('min_length' in current_validations and
            len(input_values) < current_validations['min_length']):
        raise ApiValueError(
            "Invalid value for `%s`, length must be greater than or equal to "
            "`%s`" % (
                input_variable_path[0],
                current_validations['min_length']
            )
        )

    if ('max_items' in current_validations and
            len(input_values) > current_validations['max_items']):
        raise ApiValueError(
            "Invalid value for `%s`, number of items must be less than or "
            "equal to `%s`" % (
                input_variable_path[0],
                current_validations['max_items']
            )
        )

    if ('min_items' in current_validations and
            len(input_values) < current_validations['min_items']):
        raise ValueError(
            "Invalid value for `%s`, number of items must be greater than or "
            "equal to `%s`" % (
                input_variable_path[0],
                current_validations['min_items']
            )
        )

    items = ('exclusive_maximum', 'inclusive_maximum', 'exclusive_minimum',
             'inclusive_minimum')
    if (any(item in current_validations for item in items)):
        if isinstance(input_values, list):
            max_val = max(input_values)
            min_val = min(input_values)
        elif isinstance(input_values, dict):
            max_val = max(input_values.values())
            min_val = min(input_values.values())
        else:
            max_val = input_values
            min_val = input_values

    if ('exclusive_maximum' in current_validations and
            max_val >= current_validations['exclusive_maximum']):
        raise ApiValueError(
            "Invalid value for `%s`, must be a value less than `%s`" % (
                input_variable_path[0],
                current_validations['exclusive_maximum']
            )
        )

    if ('inclusive_maximum' in current_validations and
            max_val > current_validations['inclusive_maximum']):
        raise ApiValueError(
            "Invalid value for `%s`, must be a value less than or equal to "
            "`%s`" % (
                input_variable_path[0],
                current_validations['inclusive_maximum']
            )
        )

    if ('exclusive_minimum' in current_validations and
            min_val <= current_validations['exclusive_minimum']):
        raise ApiValueError(
            "Invalid value for `%s`, must be a value greater than `%s`" %
            (
                input_variable_path[0],
                current_validations['exclusive_maximum']
            )
        )

    if ('inclusive_minimum' in current_validations and
            min_val < current_validations['inclusive_minimum']):
        raise ApiValueError(
            "Invalid value for `%s`, must be a value greater than or equal "
            "to `%s`" % (
                input_variable_path[0],
                current_validations['inclusive_minimum']
            )
        )
    flags = current_validations.get('regex', {}).get('flags', 0)
    if ('regex' in current_validations and
            not re.search(current_validations['regex']['pattern'],
                          input_values, flags=flags)):
        raise ApiValueError(
            r"Invalid value for `%s`, must be a follow pattern or equal to "
            r"`%s` with flags=`%s`" % (
                input_variable_path[0],
                current_validations['regex']['pattern'],
                flags
            )
          )


def order_response_types(required_types):
    """Returns the required types sorted in coercion order

    Args:
        required_types (list/tuple): collection of classes or instance of
            list or dict with classs information inside it

    Returns:
        (list): coercion order sorted collection of classes or instance
            of list or dict with classs information inside it
    """

    def index_getter(class_or_instance):
        if isinstance(class_or_instance, list):
            return COERCION_INDEX_BY_TYPE[list]
        elif isinstance(class_or_instance, dict):
            return COERCION_INDEX_BY_TYPE[dict]
        elif (inspect.isclass(class_or_instance)
                and issubclass(class_or_instance, ModelComposed)):
            return COERCION_INDEX_BY_TYPE[ModelComposed]
        elif (inspect.isclass(class_or_instance)
                and issubclass(class_or_instance, ModelNormal)):
            return COERCION_INDEX_BY_TYPE[ModelNormal]
        elif (inspect.isclass(class_or_instance)
                and issubclass(class_or_instance, ModelSimple)):
            return COERCION_INDEX_BY_TYPE[ModelSimple]
        return COERCION_INDEX_BY_TYPE[class_or_instance]

    sorted_types = sorted(
        required_types,
        key=lambda class_or_instance: index_getter(class_or_instance)
    )
    return sorted_types


def remove_uncoercible(required_types_classes, current_item, from_server,
                       must_convert=True):
    """Only keeps the type conversions that are possible

    Args:
        required_types_classes (tuple): tuple of classes that are required
                          these should be ordered by COERCION_INDEX_BY_TYPE
        from_server (bool): a boolean of whether the data is from the server
                          if false, the data is from the client
        current_item (any): the current item to be converted

    Keyword Args:
        must_convert (bool): if True the item to convert is of the wrong
                          type and we want a big list of coercibles
                          if False, we want a limited list of coercibles

    Returns:
        (list): the remaining coercible required types, classes only
    """
    current_type_simple = get_simple_class(current_item)

    results_classes = []
    for required_type_class in required_types_classes:
        # convert our models to OpenApiModel
        required_type_class_simplified = required_type_class
        if isinstance(required_type_class_simplified, type):
            if issubclass(required_type_class_simplified, ModelComposed):
                required_type_class_simplified = ModelComposed
            elif issubclass(required_type_class_simplified, ModelNormal):
                required_type_class_simplified = ModelNormal
            elif issubclass(required_type_class_simplified, ModelSimple):
                required_type_class_simplified = ModelSimple

        if required_type_class_simplified == current_type_simple:
            # don't consider converting to one's own class
            continue

        class_pair = (current_type_simple, required_type_class_simplified)
        if must_convert and class_pair in COERCIBLE_TYPE_PAIRS[from_server]:
            results_classes.append(required_type_class)
        elif class_pair in UPCONVERSION_TYPE_PAIRS:
            results_classes.append(required_type_class)
    return results_classes


def get_required_type_classes(required_types_mixed):
    """Converts the tuple required_types into a tuple and a dict described
    below

    Args:
        required_types_mixed (tuple/list): will contain either classes or
            instance of list or dict

    Returns:
        (valid_classes, dict_valid_class_to_child_types_mixed):
            valid_classes (tuple): the valid classes that the current item
                                   should be
            dict_valid_class_to_child_types_mixed (doct):
                valid_class (class): this is the key
                child_types_mixed (list/dict/tuple): describes the valid child
                    types
    """
    valid_classes = []
    child_req_types_by_current_type = {}
    for required_type in required_types_mixed:
        if isinstance(required_type, list):
            valid_classes.append(list)
            child_req_types_by_current_type[list] = required_type
        elif isinstance(required_type, tuple):
            valid_classes.append(tuple)
            child_req_types_by_current_type[tuple] = required_type
        elif isinstance(required_type, dict):
            valid_classes.append(dict)
            child_req_types_by_current_type[dict] = required_type[str]
        else:
            valid_classes.append(required_type)
    return tuple(valid_classes), child_req_types_by_current_type


def change_keys_js_to_python(input_dict, model_class):
    """
    Converts from javascript_key keys in the input_dict to python_keys in
    the output dict using the mapping in model_class
    """

    output_dict = {}
    reversed_attr_map = {value: key for key, value in
                         six.iteritems(model_class.attribute_map)}
    for javascript_key, value in six.iteritems(input_dict):
        python_key = reversed_attr_map.get(javascript_key)
        if python_key is None:
            # if the key is unknown, it is in error or it is an
            # additionalProperties variable
            python_key = javascript_key
        output_dict[python_key] = value
    return output_dict


def get_type_error(var_value, path_to_item, valid_classes, key_type=False):
    error_msg = type_error_message(
        var_name=path_to_item[-1],
        var_value=var_value,
        valid_classes=valid_classes,
        key_type=key_type
    )
    return ApiTypeError(
        error_msg,
        path_to_item=path_to_item,
        valid_classes=valid_classes,
        key_type=key_type
    )


def deserialize_primitive(data, klass, path_to_item):
    """Deserializes string to primitive type.

    :param data: str/int/float
    :param klass: str/class the class to convert to

    :return: int, float, str, bool, date, datetime
    """
    additional_message = ""
    try:
        if klass in {datetime, date}:
            additional_message = (
                "If you need your parameter to have a fallback "
                "string value, please set its type as `type: {}` in your "
                "spec. That allows the value to be any type. "
            )
            if klass == datetime:
                if len(data) < 8:
                    raise ValueError("This is not a datetime")
                # The string should be in iso8601 datetime format.
                parsed_datetime = parse(data)
                date_only = (
                    parsed_datetime.hour == 0 and
                    parsed_datetime.minute == 0 and
                    parsed_datetime.second == 0 and
                    parsed_datetime.tzinfo is None and
                    8 <= len(data) <= 10
                )
                if date_only:
                    raise ValueError("This is a date, not a datetime")
                return parsed_datetime
            elif klass == date:
                if len(data) < 8:
                    raise ValueError("This is not a date")
                return parse(data).date()
        else:
            converted_value = klass(data)
            if isinstance(data, str) and klass == float:
                if str(converted_value) != data:
                    # '7' -> 7.0 -> '7.0' != '7'
                    raise ValueError('This is not a float')
            return converted_value
    except (OverflowError, ValueError):
        # parse can raise OverflowError
        raise ApiValueError(
            "{0}Failed to parse {1} as {2}".format(
                additional_message, repr(data), get_py3_class_name(klass)
            ),
            path_to_item=path_to_item
        )


def fix_model_input_data(model_data, model_class):
    # this is only called on classes where the input data is a dict
    fixed_model_data = change_keys_js_to_python(
        model_data,
        model_class
    )
    if model_class._composed_schemas() is not None:
        for allof_class in model_class._composed_schemas()['allOf']:
            fixed_model_data = change_keys_js_to_python(
                fixed_model_data,
                allof_class
            )
    return fixed_model_data


def deserialize_model(model_data, model_class, path_to_item, check_type,
                      configuration, from_server):
    """Deserializes model_data to model instance.

    Args:
        model_data (list/dict): data to instantiate the model
        model_class (OpenApiModel): the model class
        path_to_item (list): path to the model in the received data
        check_type (bool): whether to check the data tupe for the values in
            the model
        configuration (Configuration): the instance to use to convert files
        from_server (bool): True if the data is from the server
            False if the data is from the client

    Returns:
        model instance

    Raise:
        ApiTypeError
        ApiValueError
        ApiKeyError
    """

    kw_args = dict(_check_type=check_type,
                   _path_to_item=path_to_item,
                   _configuration=configuration,
                   _from_server=from_server)

    used_model_class = model_class
    if model_class.discriminator() is not None:
        used_model_class = model_class.get_discriminator_class(
            from_server, model_data)

    if issubclass(used_model_class, ModelSimple):
        instance = used_model_class(value=model_data, **kw_args)
        return instance
    if isinstance(model_data, list):
        instance = used_model_class(*model_data, **kw_args)
    if isinstance(model_data, dict):
        fixed_model_data = change_keys_js_to_python(
            model_data,
            used_model_class
        )
        kw_args.update(fixed_model_data)
        instance = used_model_class(**kw_args)
    return instance


def deserialize_file(response_data, configuration, content_disposition=None):
    """Deserializes body to file

    Saves response body into a file in a temporary folder,
    using the filename from the `Content-Disposition` header if provided.

    Args:
        param response_data (str):  the file data to write
        configuration (Configuration): the instance to use to convert files

    Keyword Args:
        content_disposition (str):  the value of the Content-Disposition
            header

    Returns:
        (file_type): the deserialized file which is open
            The user is responsible for closing and reading the file
    """
    fd, path = tempfile.mkstemp(dir=configuration.temp_folder_path)
    os.close(fd)
    os.remove(path)

    if content_disposition:
        filename = re.search(r'filename=[\'"]?([^\'"\s]+)[\'"]?',
                             content_disposition).group(1)
        path = os.path.join(os.path.dirname(path), filename)

    with open(path, "wb") as f:
        if six.PY3 and isinstance(response_data, str):
            # in python3 change str to bytes so we can write it
            response_data = response_data.encode('utf-8')
        f.write(response_data)

    f = open(path, "rb")
    return f


def attempt_convert_item(input_value, valid_classes, path_to_item,
                         configuration, from_server, key_type=False,
                         must_convert=False, check_type=True):
    """
    Args:
        input_value (any): the data to convert
        valid_classes (any): the classes that are valid
        path_to_item (list): the path to the item to convert
        configuration (Configuration): the instance to use to convert files
        from_server (bool): True if data is from the server, False is data is
            from the client
        key_type (bool): if True we need to convert a key type (not supported)
        must_convert (bool): if True we must convert
        check_type (bool): if True we check the type or the returned data in
            ModelComposed/ModelNormal/ModelSimple instances

    Returns:
        instance (any) the fixed item

    Raises:
        ApiTypeError
        ApiValueError
        ApiKeyError
    """
    valid_classes_ordered = order_response_types(valid_classes)
    valid_classes_coercible = remove_uncoercible(
        valid_classes_ordered, input_value, from_server)
    if not valid_classes_coercible or key_type:
        # we do not handle keytype errors, json will take care
        # of this for us
        if configuration is None or not configuration.discard_unknown_keys:
            raise get_type_error(input_value, path_to_item, valid_classes,
                                 key_type=key_type)
    for valid_class in valid_classes_coercible:
        try:
            if issubclass(valid_class, OpenApiModel):
                return deserialize_model(input_value, valid_class,
                                         path_to_item, check_type,
                                         configuration, from_server)
            elif valid_class == file_type:
                return deserialize_file(input_value, configuration)
            return deserialize_primitive(input_value, valid_class,
                                         path_to_item)
        except (ApiTypeError, ApiValueError, ApiKeyError) as conversion_exc:
            if must_convert:
                raise conversion_exc
            # if we have conversion errors when must_convert == False
            # we ignore the exception and move on to the next class
            continue
    # we were unable to convert, must_convert == False
    return input_value


def validate_and_convert_types(input_value, required_types_mixed, path_to_item,
                               from_server, _check_type, configuration=None):
    """Raises a TypeError is there is a problem, otherwise returns value

    Args:
        input_value (any): the data to validate/convert
        required_types_mixed (list/dict/tuple): A list of
            valid classes, or a list tuples of valid classes, or a dict where
            the value is a tuple of value classes
        path_to_item: (list) the path to the data being validated
            this stores a list of keys or indices to get to the data being
            validated
        from_server (bool): True if data is from the server
            False if data is from the client
        _check_type: (boolean) if true, type will be checked and conversion
            will be attempted.
        configuration: (Configuration): the configuration class to use
            when converting file_type items.
            If passed, conversion will be attempted when possible
            If not passed, no conversions will be attempted and
            exceptions will be raised

    Returns:
        the correctly typed value

    Raises:
        ApiTypeError
    """
    results = get_required_type_classes(required_types_mixed)
    valid_classes, child_req_types_by_current_type = results

    input_class_simple = get_simple_class(input_value)
    valid_type = input_class_simple in set(valid_classes)
    if not valid_type:
        if configuration:
            # if input_value is not valid_type try to convert it
            converted_instance = attempt_convert_item(
                input_value,
                valid_classes,
                path_to_item,
                configuration,
                from_server,
                key_type=False,
                must_convert=True
            )
            return converted_instance
        else:
            raise get_type_error(input_value, path_to_item, valid_classes,
                                 key_type=False)

    # input_value's type is in valid_classes
    if len(valid_classes) > 1 and configuration:
        # there are valid classes which are not the current class
        valid_classes_coercible = remove_uncoercible(
            valid_classes, input_value, from_server, must_convert=False)
        if valid_classes_coercible:
            converted_instance = attempt_convert_item(
                input_value,
                valid_classes_coercible,
                path_to_item,
                configuration,
                from_server,
                key_type=False,
                must_convert=False
            )
            return converted_instance

    if child_req_types_by_current_type == {}:
        # all types are of the required types and there are no more inner
        # variables left to look at
        return input_value
    inner_required_types = child_req_types_by_current_type.get(
        type(input_value)
    )
    if inner_required_types is None:
        # for this type, there are not more inner variables left to look at
        return input_value
    if isinstance(input_value, list):
        if input_value == []:
            # allow an empty list
            return input_value
        for index, inner_value in enumerate(input_value):
            inner_path = list(path_to_item)
            inner_path.append(index)
            input_value[index] = validate_and_convert_types(
                inner_value,
                inner_required_types,
                inner_path,
                from_server,
                _check_type,
                configuration=configuration
            )
    elif isinstance(input_value, dict):
        if input_value == {}:
            # allow an empty dict
            return input_value
        for inner_key, inner_val in six.iteritems(input_value):
            inner_path = list(path_to_item)
            inner_path.append(inner_key)
            if get_simple_class(inner_key) != str:
                raise get_type_error(inner_key, inner_path, valid_classes,
                                     key_type=True)
            input_value[inner_key] = validate_and_convert_types(
                inner_val,
                inner_required_types,
                inner_path,
                from_server,
                _check_type,
                configuration=configuration
            )
    return input_value


def model_to_dict(model_instance, serialize=True):
    """Returns the model properties as a dict

    Args:
        model_instance (one of your model instances): the model instance that
            will be converted to a dict.

    Keyword Args:
        serialize (bool): if True, the keys in the dict will be values from
            attribute_map
    """
    result = {}

    model_instances = [model_instance]
    if model_instance._composed_schemas() is not None:
        model_instances.extend(model_instance._composed_instances)
    for model_instance in model_instances:
        for attr, value in six.iteritems(model_instance._data_store):
            if serialize:
                # we use get here because additional property key names do not
                # exist in attribute_map
                attr = model_instance.attribute_map.get(attr, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: model_to_dict(x, serialize=serialize)
                    if hasattr(x, '_data_store') else x, value
                ))
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0],
                                  model_to_dict(item[1], serialize=serialize))
                    if hasattr(item[1], '_data_store') else item,
                    value.items()
                ))
            elif hasattr(value, '_data_store'):
                result[attr] = model_to_dict(value, serialize=serialize)
            else:
                result[attr] = value

    return result


def type_error_message(var_value=None, var_name=None, valid_classes=None,
                       key_type=None):
    """
    Keyword Args:
        var_value (any): the variable which has the type_error
        var_name (str): the name of the variable which has the typ error
        valid_classes (tuple): the accepted classes for current_item's
                                  value
        key_type (bool): False if our value is a value in a dict
                         True if it is a key in a dict
                         False if our item is an item in a list
    """
    key_or_value = 'value'
    if key_type:
        key_or_value = 'key'
    valid_classes_phrase = get_valid_classes_phrase(valid_classes)
    msg = (
        "Invalid type for variable '{0}'. Required {1} type {2} and "
        "passed type was {3}".format(
            var_name,
            key_or_value,
            valid_classes_phrase,
            type(var_value).__name__,
        )
    )
    return msg


def get_valid_classes_phrase(input_classes):
    """Returns a string phrase describing what types are allowed
    Note: Adds the extra valid classes in python2
    """
    all_classes = list(input_classes)
    if six.PY2 and str in input_classes:
        all_classes.extend([str_py2, unicode_py2])
    if six.PY2 and int in input_classes:
        all_classes.extend([int_py2, long_py2])
    all_classes = sorted(all_classes, key=lambda cls: cls.__name__)
    all_class_names = [cls.__name__ for cls in all_classes]
    if len(all_class_names) == 1:
        return 'is {0}'.format(all_class_names[0])
    return "is one of [{0}]".format(", ".join(all_class_names))


def get_py3_class_name(input_class):
    if six.PY2:
        if input_class == str:
            return 'str'
        elif input_class == int:
            return 'int'
    return input_class.__name__


def get_allof_instances(self, model_args, constant_args):
    """
    Args:
        self: the class we are handling
        model_args (dict): var_name to var_value
            used to make instances
        constant_args (dict): var_name to var_value
            used to make instances

    Returns
        composed_instances (list)
    """
    composed_instances = []
    for allof_class in self._composed_schemas()['allOf']:

        # transform js keys to python keys in fixed_model_args
        fixed_model_args = change_keys_js_to_python(
            model_args, allof_class)

        # extract a dict of only required keys from fixed_model_args
        kwargs = {}
        var_names = set(allof_class.openapi_types().keys())
        for var_name in var_names:
            if var_name in fixed_model_args:
                kwargs[var_name] = fixed_model_args[var_name]

        # and use it to make the instance
        kwargs.update(constant_args)
        allof_instance = allof_class(**kwargs)
        composed_instances.append(allof_instance)
    return composed_instances


def get_oneof_instance(self, model_args, constant_args):
    """
    Args:
        self: the class we are handling
        model_args (dict): var_name to var_value
            used to make instances
        constant_args (dict): var_name to var_value
            used to make instances

    Returns
        oneof_instance (instance/None)
    """
    if len(self._composed_schemas()['oneOf']) == 0:
        return None

    oneof_instances = []
    for oneof_class in self._composed_schemas()['oneOf']:
        # transform js keys to python keys in fixed_model_args
        fixed_model_args = change_keys_js_to_python(
            model_args, oneof_class)

        # extract a dict of only required keys from fixed_model_args
        kwargs = {}
        var_names = set(oneof_class.openapi_types().keys())
        for var_name in var_names:
            if var_name in fixed_model_args:
                kwargs[var_name] = fixed_model_args[var_name]

        # do not try to make a model with no input args
        if len(kwargs) == 0:
            continue

        # and use it to make the instance
        kwargs.update(constant_args)
        try:
            oneof_instance = oneof_class(**kwargs)
            oneof_instances.append(oneof_instance)
        except Exception:
            pass
    if len(oneof_instances) == 0:
        raise ApiValueError(
            "Invalid inputs given to generate an instance of %s. Unable to "
            "make any instances of the classes in oneOf definition." %
            self.__class__.__name__
        )
    elif len(oneof_instances) > 1:
        raise ApiValueError(
            "Invalid inputs given to generate an instance of %s. Multiple "
            "oneOf instances were generated when a max of one is allowed." %
            self.__class__.__name__
        )
    return oneof_instances[0]


def get_anyof_instances(self, model_args, constant_args):
    """
    Args:
        self: the class we are handling
        model_args (dict): var_name to var_value
            used to make instances
        constant_args (dict): var_name to var_value
            used to make instances

    Returns
        anyof_instances (list)
    """
    anyof_instances = []
    if len(self._composed_schemas()['anyOf']) == 0:
        return anyof_instances

    for anyof_class in self._composed_schemas()['anyOf']:
        # transform js keys to python keys in fixed_model_args
        fixed_model_args = change_keys_js_to_python(model_args, anyof_class)

        # extract a dict of only required keys from these_model_vars
        kwargs = {}
        var_names = set(anyof_class.openapi_types().keys())
        for var_name in var_names:
            if var_name in fixed_model_args:
                kwargs[var_name] = fixed_model_args[var_name]

        # do not try to make a model with no input args
        if len(kwargs) == 0:
            continue

        # and use it to make the instance
        kwargs.update(constant_args)
        try:
            anyof_instance = anyof_class(**kwargs)
            anyof_instances.append(anyof_instance)
        except Exception:
            pass
    if len(anyof_instances) == 0:
        raise ApiValueError(
            "Invalid inputs given to generate an instance of %s. Unable to "
            "make any instances of the classes in anyOf definition." %
            self.__class__.__name__
        )
    return anyof_instances


def get_additional_properties_model_instances(
        composed_instances, self):
    additional_properties_model_instances = []
    all_instances = [self]
    all_instances.extend(composed_instances)
    for instance in all_instances:
        if instance.additional_properties_type is not None:
            additional_properties_model_instances.append(instance)
    return additional_properties_model_instances


def get_var_name_to_model_instances(self, composed_instances):
    var_name_to_model_instances = {}
    all_instances = [self]
    all_instances.extend(composed_instances)
    for instance in all_instances:
        for var_name in instance.openapi_types():
            if var_name not in var_name_to_model_instances:
                var_name_to_model_instances[var_name] = [instance]
            else:
                var_name_to_model_instances[var_name].append(instance)
    return var_name_to_model_instances


def get_unused_args(self, composed_instances, model_args):
    unused_args = dict(model_args)
    # arguments apssed to self were already converted to python names
    # before __init__ was called
    for var_name_py in self.attribute_map:
        if var_name_py in unused_args:
            del unused_args[var_name_py]
    for instance in composed_instances:
        if instance.__class__ in self._composed_schemas()['allOf']:
            for var_name_py in instance.attribute_map:
                if var_name_py in unused_args:
                    del unused_args[var_name_py]
        else:
            for var_name_js in instance.attribute_map.values():
                if var_name_js in unused_args:
                    del unused_args[var_name_js]
    return unused_args


def validate_get_composed_info(constant_args, model_args, self):
    """
    For composed schemas/classes, validates the classes to make sure that
    they do not share any of the same parameters. If there is no collision
    then composed model instances are created and returned tot the calling
    self model

    Args:
        constant_args (dict): these are the args that every model requires
        model_args (dict): these are the required and optional spec args that
            were passed in to make this model
        self (class): the class that we are instantiating
            This class contains self._composed_schemas()

    Returns:
        composed_info (list): length three
            composed_instances (list): the composed instances which are not
                self
            var_name_to_model_instances (dict): a dict going from var_name
                to the model_instance which holds that var_name
                the model_instance may be self or an instance of one of the
                classes in self.composed_instances()
            additional_properties_model_instances (list): a list of the
                model instances which have the property
                additional_properties_type. This list can include self
    """
    # create composed_instances
    composed_instances = []
    allof_instances = get_allof_instances(self, model_args, constant_args)
    composed_instances.extend(allof_instances)
    oneof_instance = get_oneof_instance(self, model_args, constant_args)
    if oneof_instance is not None:
        composed_instances.append(oneof_instance)
    anyof_instances = get_anyof_instances(self, model_args, constant_args)
    composed_instances.extend(anyof_instances)

    # map variable names to composed_instances
    var_name_to_model_instances = get_var_name_to_model_instances(
        self, composed_instances)

    # set additional_properties_model_instances
    additional_properties_model_instances = (
        get_additional_properties_model_instances(composed_instances, self)
    )

    # set any remaining values
    unused_args = get_unused_args(self, composed_instances, model_args)
    if len(unused_args) > 0 and \
            len(additional_properties_model_instances) == 0 and \
            (self._configuration is None or
                not self._configuration.discard_unknown_keys):
        raise ApiValueError(
            "Invalid input arguments input when making an instance of "
            "class %s. Not all inputs were used. The unused input data "
            "is %s" % (self.__class__.__name__, unused_args)
        )

    # no need to add additional_properties to var_name_to_model_instances here
    # because additional_properties_model_instances will direct us to that
    # instance when we use getattr or setattr
    # and we update var_name_to_model_instances in setattr

    return [
      composed_instances,
      var_name_to_model_instances,
      additional_properties_model_instances,
      unused_args
    ]
