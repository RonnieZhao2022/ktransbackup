

import os
import zmail


def tor2Email(receiverList,subtitle,content,attachments = [],CCEmail = ['doc1@ktranslogistics.com']):


    end = '''
    <br>
    <p>———————————————————————————————————————</p>
    <p><b>Ronnie│Logistic Coordinator</b></p>
    <p><b>+1 647-725-2283 Ext 213</b></p>
    <a href="www.ktranslogistics.com"> www.ktranslogistics.com</a>
    <p>Customer Support Wechat: KT6042561256</p>
    <p>Manager Wechat:17788656668</p>
    <br>
    <img src="https://i.ibb.co/kJKdhCB/ktrans.jpg" />
    <br>
    <p><b>K Trans Worldwide Logistics Ltd.</b></p>
    <p><b>Toronto Office:</b> </p>
    <p>4-110 Claireport Cres, Toronto, ON M9W 6P3</p>
    <p>Phone: +1 647-725-2283</p>
    <p><b>Vancouver Office:</b></p>
    <p> Unit 106-3850 Jacombs Road, Richmond, BC V6V 1Y6</p>
    <p>Phone: +1 604-256-1256  Fax: +1 604-229-1721</p>
    <p><b>K Trans worldwide logistics LLC</b></p>
    <p>1259 E Locust Street, Ontario, California, USA 91761</p>
    <p>Phone: +1 626-604-9111</p>
    <br>'''

    content += end

    mail = {
        'subject':subtitle,
        # 'content_text': 'This message from zmail',
        'content_html': content,
        'attachments': attachments,
    }
    server = zmail.server('tor2@ktranslogistics.com', 'Ge6xbRHCVHyca9Pi', config='qq')  # password: TorontoJane123
    server.send_mail(receiverList, mail, cc=CCEmail)

    return