import base64
import json

from rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers

from blackblox_modules.crypto import get_Ed521


def restore_bytes_from_string(pk_string):
    bytes_encoded = pk_string.encode()
    return base64.b64decode(bytes_encoded)


class PastelRegisterSerializer(RegisterSerializer):
    public_key = serializers.CharField(write_only=True)
    signature = serializers.CharField(write_only=True)

    def validate(self, data):
        data = super(PastelRegisterSerializer, self).validate(data)
        signature = data.pop('signature')
        public_key = data.pop('public_key')
        raw_data = json.dumps(data).encode()
        signature_bytes = restore_bytes_from_string(signature)
        public_key_bytes = restore_bytes_from_string(public_key)
        ed_521 = get_Ed521()
        signature_valid = ed_521.verify(public_key_bytes, raw_data, signature_bytes)
        if not signature_valid:
            raise serializers.ValidationError("Signature is invalid")
        return data

