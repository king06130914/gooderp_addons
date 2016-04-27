# -*- coding: utf-8 -*-
from openerp.tests.common import TransactionCase
from openerp.exceptions import except_orm


class test_report(TransactionCase):
    
    def setUp(self):
        super(test_report, self).setUp()
        # 审核2015年12月和2016年1月的会计凭证
        self.env.ref('finance.voucher_12').voucher_done()
        self.env.ref('finance.voucher_1').voucher_done()
        self.env.ref('finance.voucher_2').voucher_done()
        
        self.period_id = self.env.ref('finance.period_201601').id
        ''' FIXME
        # 结转2015年12月的期间
        month_end = self.env['checkout.wizard'].create(
                       {'date':'2015-12-31',
                        'period_id':self.env.ref('finance.period_201512').id})
        month_end.button_checkout()
        '''

    def test_trail_balance(self):
        ''' 测试科目余额表 '''
        report = self.env['create.trial.balance.wizard'].create(
            {'period_id': self.period_id}
                    )
        with self.assertRaises(except_orm):
            report.create_trial_balance()

    def test_vouchers_summary(self):
        ''' 测试总账和明细账'''
        report = self.env['create.vouchers.summary.wizard'].create(
            {'period_begin_id': self.period_id,
             'period_end_id': self.period_id,
             'subject_name_id': self.env.ref('finance.account_fund').id}
                    )
        with self.assertRaises(except_orm):
            report.create_vouchers_summary()
        with self.assertRaises(except_orm):
            report.create_general_ledger_account()

    def test_balance_sheet(self):
        ''' 测试科目余额表 '''
        report = self.env['create.balance.sheet.wizard'].create(
            {'period_id': self.period_id}
                    )
        with self.assertRaises(except_orm):
            report.create_balance_sheet()
        with self.assertRaises(except_orm):
            report.create_profit_statement()


class test_checkout_wizard(TransactionCase):
    
    def setUp(self):
        super(test_checkout_wizard, self).setUp()
        self.voucher_15_12 = self.env.ref('finance.voucher_12')
        self.checkout_voucher = self.env.ref('finance.voucher_12_1')
        self.period_15_12 = self.env.ref('finance.period_201512')

    def test_button_checkout(self):
        '''结账按钮,及新建wizard时的onchange'''
        checkout_obj = self.env['checkout.wizard']
        wizard = checkout_obj.create({'date':'20160102'})
        #onchange 拿到会计期间
        wizard.onchange_period_id()
        self.assertTrue(wizard.period_id.name == u'2016年 第1期')
        #上期间未关闭报错
        with self.assertRaises(except_orm):
            wizard.button_checkout()
        wizard.date = u'2015-12-31'
        wizard.onchange_period_id()
        #本期间已结账报错
        self.period_15_12.is_closed = True
        with self.assertRaises(except_orm):
            wizard.button_checkout()
        self.period_15_12.is_closed = False
        #期间内凭证未审核报错
        with self.assertRaises(except_orm):
            wizard.button_checkout()
        #正常流程
        self.voucher_15_12.voucher_done()
        self.checkout_voucher.voucher_done()
        wizard.button_checkout()
        #费用大于收入
        wizard.button_counter_checkout()
        self.env.ref('finance.voucher_12_2_debit').debit = 100000
        self.env.ref('finance.voucher_12_2_credit').credit = 100000
        wizard.button_checkout()
        #检查下一个会计区间
        self.env.ref('finance.voucher_1').voucher_done()
        self.env.ref('finance.voucher_2').voucher_done()
        self.env.ref('finance.voucher_4').voucher_done()
        self.env.ref('finance.voucher_14_12').voucher_done()
        wizard.date='2016-01-31'
        wizard.onchange_period_id()
        wizard.button_checkout()
        wizard.date='2016-02-28'
        wizard.onchange_period_id()
        wizard.button_checkout()
        wizard.date='2014-12-28'
        wizard.onchange_period_id()
        wizard.button_checkout()




