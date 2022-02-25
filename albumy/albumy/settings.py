class Operations:

    CONFIRM='confirm'
    RESET_PASSWORD='reset_password'
    CHANGE_EMAIL= 'change_email'

class BaseConfig:
    pass


class DevelopmentConfig(BaseConfig):
    pass


class TestingConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    pass


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}