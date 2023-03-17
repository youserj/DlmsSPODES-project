from ..profile_generic.ver1 import ProfileGeneric


class SPODES3CurrentProfile(ProfileGeneric):
    """Cosem3 Б.1 Текущие значения"""
    scaler_profile_key = bytes((1, 0, 94, 7, 3, 255))


class SPODES3MonthProfile(ProfileGeneric):
    """СПОДЭС3 В.4 Параметры ежемесячного профиля"""
    scaler_profile_key = bytes((1, 0, 94, 7, 1, 255))


class SPODES3DailyProfile(ProfileGeneric):
    """СПОДЭС3 В.3 Параметры ежесуточного профиля"""
    scaler_profile_key = bytes((1, 0, 94, 7, 2, 255))


class SPODES3LoadProfile(ProfileGeneric):
    """СПОДЭС3 В.2 Параметры профиля нагрузки"""
    scaler_profile_key = bytes((1, 0, 94, 7, 4, 255))





