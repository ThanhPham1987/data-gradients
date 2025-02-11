from typing import Union, Mapping, Dict, List
from rapidfuzz import process, fuzz
from data_gradients.utils.utils import fuzzy_keys, fuzzy_str, get_fuzzy_mapping_param


class UnknownTypeException(Exception):
    """Type error with message, followed by type suggestion, chosen by fuzzy matching
     (out of 'choices' arg passed in __init__).

    :param unknown_type:    The type that was not found.
    :param choices:         List of valid types
    :param message:         Explanation of the error
    """

    def __init__(self, unknown_type: str, choices: List, message: str = None):
        message = message or f"Unknown object type: {unknown_type} in configuration. valid types are: {choices}"
        err_msg_tip = ""
        if isinstance(unknown_type, str):
            choice, score, _ = process.extractOne(unknown_type, choices, scorer=fuzz.WRatio)
            if score > 70:
                err_msg_tip = f"\n Did you mean: {choice}?"
        self.message = message + err_msg_tip
        super().__init__(self.message)


class AbstractFactory:
    """
    An abstract factory to generate an object from a string, a dictionary or a list
    """

    def get(self, conf: Union[str, dict, list]):
        """
        Get an instantiated object.
            :param conf: a configuration
                if string - assumed to be a type name (not the real name, but a name defined in the Factory)
                if dictionary - assumed to be {type_name(str): {parameters...}} (single item in dict)
                if list - assumed to be a list of the two options above

                If provided value is not one of the three above, the value will be returned as is
        """
        raise NotImplementedError


class BaseFactory(AbstractFactory):
    """
    The basic factory fo a *single* object generation.
    """

    def __init__(self, type_dict: Dict[str, type]):
        """
        :param type_dict: a dictionary mapping a name to a type
        """
        self.type_dict = type_dict

    def get(self, conf: Union[str, dict]):
        """
        Get an instantiated object.
           :param conf: a configuration
           if string - assumed to be a type name (not the real name, but a name defined in the Factory)
           if dictionary - assumed to be {type_name(str): {parameters...}} (single item in dict)

           If provided value is not one of the three above, the value will be returned as is
        """
        if isinstance(conf, str):
            if conf in self.type_dict:
                return self.type_dict[conf]()
            elif fuzzy_str(conf) in fuzzy_keys(self.type_dict):
                return get_fuzzy_mapping_param(conf, self.type_dict)()
            else:
                raise UnknownTypeException(conf, list(self.type_dict.keys()))
        elif isinstance(conf, Mapping):
            if len(conf.keys()) > 1:
                raise RuntimeError(
                    "Malformed object definition in configuration. Expecting either a string of object type or a single entry dictionary"
                    "{type_name(str): {parameters...}}."
                    f"received: {conf}"
                )

            _type = list(conf.keys())[0]  # THE TYPE NAME
            _params = list(conf.values())[0]  # A DICT CONTAINING THE PARAMETERS FOR INIT
            if _type in self.type_dict:
                return self.type_dict[_type](**_params)
            elif fuzzy_str(_type) in fuzzy_keys(self.type_dict):
                return get_fuzzy_mapping_param(_type, self.type_dict)(**_params)
            else:
                raise UnknownTypeException(_type, list(self.type_dict.keys()))
        else:
            return conf
