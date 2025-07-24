# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import PoolMeta, Pool
from trytond.model import fields


class Configuration(metaclass=PoolMeta):
    __name__ = 'account.configuration'

    b2brouter_state_update_days = fields.MultiValue(fields.Integer(
        'B2BRouter State Update Days'))

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field in {'b2brouter_state_update_days'}:
            return pool.get('account.configuration.facturae')
        return super().multivalue_model(field)

    @classmethod
    def default_b2brouter_state_update_days(cls, **pattern):
        return cls.multivalue_model(
            'b2brouter_state_update_days').default_b2brouter_state_update_days()


class ConfigurationFacturae(metaclass=PoolMeta):
    __name__ = 'account.configuration.facturae'

    b2brouter_state_update_days = fields.Integer(
        'B2BRouter State Update Days')

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.facturae_service.selection += [('b2brouter', 'B2BRouter')]

    @staticmethod
    def default_b2brouter_state_update_days():
        return 30
