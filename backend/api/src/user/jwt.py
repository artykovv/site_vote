import jwt
from pathlib import Path
from config import algorithm, access_token_exp_min, PrivateKey, PublicKey
from datetime import datetime, timedelta

private_key = Path(PrivateKey).read_text()
public_key = Path(PublicKey).read_text()



def encoded_jwt(
    payload: dict, 
    private_key: str = private_key, 
    algorithm: str = algorithm, 
    exp_min: int = access_token_exp_min
    ):
    expiry = datetime.utcnow() + timedelta(minutes=exp_min)
    payload['exp'] = expiry
    encoded = jwt.encode(
        payload, 
        private_key, 
        algorithm=algorithm,
        )
    return encoded



def decoded_jwt(
    token: str | bytes, 
    public_key: str = public_key, 
    algorithm: str = algorithm, 
    ):
    decoded = jwt.decode(
        token, 
        public_key, 
        algorithms=algorithm,
        )
    return decoded

