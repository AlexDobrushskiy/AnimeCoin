import io

from PIL import Image

from .settings import NetWorkSettings


class FieldValidator:
    pass


class FingerprintField(FieldValidator):
    def __init__(self, innertype):
        self.minsize = NetWorkSettings.DUPE_DETECTION_FINGERPRINT_SIZE
        self.maxsize = NetWorkSettings.DUPE_DETECTION_FINGERPRINT_SIZE
        self.innertype = innertype

    def validate(self, value):
        if type(value) != list:
            raise TypeError("value is not list, was: %s" % type(value))

        if len(value) < self.minsize or len(value) > self.maxsize:
            raise ValueError("encoded value is out of bound (value < %s or value > %s), was: %s" % (self.minsize,
                                                                                                    self.maxsize,
                                                                                                    len(value)))

        for element in value:
            if type(element) != self.innertype:
                raise TypeError("element is not %s, was: %s" % (self.innertype, type(element)))

        # TODO: implement innermin and innermax
        # as msgpack does not support bignum ints and floats, but python does

        return value


class LubyChunkHashField(FieldValidator):
    def validate(self, value):
        if type(value) != list:
            raise TypeError("value is not list, was: %s" % type(value))

        validator = SHA3512Field()
        for element in value:
            validator.validate(element)

        return value


class LubySeedField(FieldValidator):
    def validate(self, value):
        if type(value) != list:
            raise TypeError("value is not list, was: %s" % type(value))

        validator = IntegerField(minsize=0, maxsize=2**32-1)
        for element in value:
            validator.validate(element)

        return value


class LubyChunkField(FieldValidator):
    def validate(self, value):
        if type(value) != list:
            raise TypeError("value is not list, was: %s" % type(value))

        validator = BytesField(minsize=0, maxsize=NetWorkSettings.CHUNKSIZE)
        for element in value:
            validator.validate(element)

        return value


class NotImplementedType(FieldValidator):
    def __eq__(self, other):
        raise NotImplementedError()


class ListTypeValidatorField(FieldValidator):
    accepted_type = NotImplementedType()

    def __init__(self, minsize, maxsize):
        self.minsize = minsize
        self.maxsize = maxsize

    def validate(self, value):
        if type(value) != self.accepted_type:
            raise TypeError("value is not %s, was: %s" % (self.accepted_type, type(value)))

        if len(value) < self.minsize or len(value) > self.maxsize:
            raise ValueError("encoded value is out of bound (value < %s or value > %s), was: %s" % (self.minsize,
                                                                                                    self.maxsize,
                                                                                                    len(value)))

        return value


class ImageTypeValidatorField(ListTypeValidatorField):
    accepted_type = bytes

    def __init__(self, min, max):
        super().__init__(min, max)

    def validate(self, value):
        super().validate(value)

        # TODO: move this to a separate isolated process as image is user-supplied!
        imagefile = io.BytesIO(value)
        Image.open(imagefile)
        return value


class ImageField(ImageTypeValidatorField):
    def __init__(self):
        super().__init__(0, NetWorkSettings.IMAGE_MAX_SIZE)


class ThumbnailField(ImageTypeValidatorField):
    def __init__(self):
        super().__init__(0, NetWorkSettings.THUMBNAIL_MAX_SIZE)


class IntTypeValidatorField(FieldValidator):
    accepted_type = NotImplementedType()

    def __init__(self, minsize, maxsize):
        self.minsize = minsize
        self.maxsize = maxsize

    def validate(self, value):
        if type(value) != self.accepted_type:
            raise TypeError("value is not %s, was: %s" % (self.accepted_type, type(value)))

        if value < self.minsize or value > self.maxsize:
            raise ValueError("encoded value is out of bound (value < %s or value > %s), was: %s" % (self.minsize,
                                                                                                    self.maxsize,
                                                                                                    value))

        return value


class BytesField(ListTypeValidatorField):
    accepted_type = bytes


class StringField(FieldValidator):
    def __init__(self, minsize, maxsize):
        self.minsize = minsize
        self.maxsize = maxsize

    def validate(self, value):
        if type(value) != str:
            raise TypeError("value is not list, was: %s" % (type(value)))

        encoded = value.encode("utf-8")
        if len(encoded) < self.minsize or len(encoded) > self.maxsize:
            raise ValueError("encoded value is out of bounds (value < %s or value > %s), was: %s" % (self.minsize,
                                                                                                     self.maxsize,
                                                                                                     len(encoded)))

        return value


class StringChoiceField(FieldValidator):
    def __init__(self, choices):
        self.choices = set(choices)

    def validate(self, value):
        if type(value) != str:
            raise TypeError("value is not list, was: %s" % (type(value)))

        if value not in self.choices:
            raise ValueError("Value not in choices: %s" % self.choices)

        return value


class IntegerField(IntTypeValidatorField):
    accepted_type = int


class SHA3512Field(BytesField):
    def __init__(self):
        super().__init__(minsize=64, maxsize=64)


class SHA2256Field(BytesField):
    def __init__(self):
        super().__init__(minsize=32, maxsize=32)


class TXIDField(SHA2256Field):
    pass


class SignatureField(BytesField):
    def __init__(self):
        super().__init__(minsize=132, maxsize=132)


class PubkeyField(BytesField):
    def __init__(self):
        super().__init__(minsize=66, maxsize=66)


class BlockChainAddressField(StringField):
    def __init__(self):
        super().__init__(minsize=26, maxsize=35)


class UnixTimeField(IntegerField):
    def __init__(self):
        super().__init__(minsize=0, maxsize=2**32-1)
