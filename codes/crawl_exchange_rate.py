#_*_ coding:UTF-8 _*_

import re
from lxml import etree
import requests
import datetime
import numpy as np


class ExchangeRate:

    def __init__(self, ):
        self.npy_path = '../data/exchange_rate.npy'
        self.ret_dict = {}
        self.key_arr = ['美元', '港币', '新加坡元']

    
    def get_exchange_rate(self, name):
        # output: array [name, exchage_buy, exchange_sell, date_print ]
        
        url = 'https://www.boc.cn/sourcedb/whpj/index.html'
        html = requests.get(url).content.decode('utf-8')
        
        #print('type html isd %s' %(type(html)))
        a = html.index('<td>%s</td>' %(name)) # locate index of goal
        s = html[a:a+394] # multi-try && calcute
        #print('\ta = %s' %(a))
        
        ret = re.findall('<td>(.*?)</td>', s)
        date_arr = re.findall('<td class="pjrq">(.*?)</td>', s)
        date = datetime.datetime.strptime(date_arr[0], '%Y.%m.%d %H:%M:%S') # format: 2022-11-08 11:09:02
        date = date.strftime('%Y-%m-%d')
        date = '%s' %(date) # output string

        name = ret[0]
        exchange_dict = { "exchange_buy" : '%.4f' %(float(ret[1])/100),
                          "exchange_sell" : '%.4f' %(float(ret[3])/100),
                          "update_date" : date }
        update_dict = self.update( name=name, name_dict=exchange_dict )

        
        
        return { name:update_dict  }
    
    
    def save(self):
        
        for key in self.key_arr:
            ret = self.get_exchange_rate(key)
            #print(ret)
            self.ret_dict.update(ret)
    
        np.save(self.npy_path, self.ret_dict)


    def load(self):
        ret_dict = np.load( self.npy_path, allow_pickle='True' ).item()
        for k, v in ret_dict.items():
            print('{}\t{}'.format(k, v))
            continue
        return ret_dict

    def update(self, name, name_dict):
        # function: input single dict
        #           output: single dict
        # compare name_dict and ret
        # new_ret_dict = self.ret_dict
        ret_dict = self.load() # old records
        ret = ret_dict.get(name)
        exchange_buy = float(ret.get('exchange_buy'))
        exchange_sell = float(ret.get('exchange_sell'))
        if abs(float(name_dict.get('exchange_buy')) - exchange_buy)/exchange_buy > 0.01 or\
           abs(float(name_dict.get('exchange_sell')) - exchange_sell)/exchange_sell > 0.01:
            ret.update(name_dict)
            print('\t[UPDATE] %s\t%s' %(name, name_dict) )
        #print(ret)
        return ret

            
if __name__ == '__main__':

    er = ExchangeRate()
    er.save()
    er.load()
    #er.update('美元', { "exchange_buy" : 6.23, "exchange_sell" : 6.23,"update_date" : "2022-11-08"} )
    #print(float(1.2)/100)
