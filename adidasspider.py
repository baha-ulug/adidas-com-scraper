import scrapy
import json
import time
from scrapy.http import Request
import pandas as pd
import datetime
import pandas as pd
from io import StringIO   
from os.path import basename
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from datetime import datetime
from dotenv import load_dotenv
import boto3 
import os, signal, smtplib, math, ssl, re

class AdidasSpider(scrapy.Spider):
    name = 'adidas-api-spider'
    allowed_domains = ['www.adidas.com.tr']
    start = 0
    csv_data = []
    start_urls = [f'https://www.adidas.com.tr/api/plp/content-engine/search?sitePath=tr&query=all&sort=price-low-to-high']
    count = []

    def parse(self, response):
        jsonresponse = json.loads(response.text)
        pages = jsonresponse["raw"]["itemList"]["items"]

        for page in pages: 
            item_page = f'https://www.adidas.com.tr/api/search/product/{page["productId"]}?sitePath=tr'
            time.sleep(0.0825)
            yield response.follow(item_page, callback=self.productDetail)
                    
        if (self.start < jsonresponse["raw"]["itemList"]["count"]): 
            print('offset is-------------------------------------------------------------------------: ', self.start)
            self.start += 48
            next_page = f'https://www.adidas.com.tr/api/plp/content-engine/search?sitePath=tr&query=all&sort=price-low-to-high&start={self.start}'
            time.sleep(0.190)
            yield response.follow(next_page, callback=self.parse)
        
    def productDetail(self,response):
        jsonresponse = json.loads(response.text)
        orderable_status =  jsonresponse["orderable"]
        item_link = "https://www.adidas.com.tr"+jsonresponse["link"]
        self.count.append(1)
        regex_product = re.search("/([A-Z0-9]+).html",jsonresponse["link"]).group(1)
        breadcrumb_link = f"https://www.adidas.com.tr/api/products/{regex_product}"
        if str(orderable_status).strip() == 'False':
          print("orderable_status: ", str(orderable_status)) 
          print("item_link is: ", item_link)
          print("breadcrumb_link is : ", breadcrumb_link)

          yield response.follow(breadcrumb_link, callback=lambda response: self.productBreadDetail(item_link,response))
            
    def productBreadDetail(self,item_link,response):
        jsonresponse = json.loads(response.text)
        try:
          breadcrumbList =  jsonresponse["breadcrumb_list"]
        except:
          breadcrumbList = [{"text":"None"}, {"text":"None"}]

        breadcrumb_text = ''
        for breadcrumb in breadcrumbList:
          breadcrumb_text += ' > ' + breadcrumb['text']
          breadcrumb_link = breadcrumb['link']
          
        self.csv_data.append([item_link, 'Out of Stock', breadcrumb_text[3:], "https://www.adidas.com.tr" + breadcrumb_link])

    def send_email(self):
        df = pd.DataFrame(self.csv_data)
        df.columns = ['ProductURL', 'ProductStockStatus', 'BreadCrumbText', 'BreadCrumbLink']
        print('df is ready')

        #GETS THE TIME FOR NAME OF THE .CSV FILE
        now = datetime.now() 
        date_time = now.strftime("%d.%m.%Y_%H.%M")
        file_name = f'Adidas_{date_time}.csv'
        date = now.strftime("%d-%m-%Y")
        hour = now.strftime("%H:%M")
        
        #CONVERT PANDAS DF TO .CSV FILE
        s = StringIO()
        df.to_csv(s, index = False, encoding='ISO-8859-9')
        csv_file = s.getvalue()
        print('csv file is ready')
        
        #LOADING THE ENVIRONMENT INFO TO CREATE E-MAIL
        load_dotenv()
        print('load_env has run')
        #smtp_server = os.getenv("SMTP_SERVER")
        #print('smtp_server info has been imported')
        #port = os.getenv("PORT")  # For starttls
        #password = os.getenv("PASSWORD")
        #print('port info has been imported')
        
        from_addr = os.getenv("FROM_ADDR")
        print('from addr info has been imported')
        to_addr = os.getenv("TO_ADDR")
        print('to addr info has been imported')
        secret_key = os.getenv("SECRET_KEY")
        print('secret key info has been imported')
        access_key = os.getenv("ACCESS_KEY")
        print('access key info has been imported')
        subject = os.getenv("SUBJECT")
        print('all env info has been imported')
        
        content = """
        <html>
  <head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <title>Simple Transactional Email</title>
    <style>
     
      img {
        border: none;
        -ms-interpolation-mode: bicubic;
        max-width: 100%; 
      }

      body {
        background-color: #f6f6f6;
        font-family: sans-serif;
        -webkit-font-smoothing: antialiased;
        font-size: '14px';
        line-height: 1.4;
        margin: 0;
        padding: 0;
        -ms-text-size-adjust: 100%;
        -webkit-text-size-adjust: 100%; 
      }

      table {
        border-collapse: separate;
        mso-table-lspace: '0pt';
        mso-table-rspace: '0pt';
        width: 100%; }
        table td {
          font-family: sans-serif;
          font-size: '14px';
          vertical-align: top; 
      }


      .body {
        background-color: #f6f6f6;
        width: 100%; 
      }

     
      .container {
        display: block;
        margin: 0 auto '!important';
        /* makes it centered */
        max-width: '580px';
        padding: '10px';
        width: '580px'; 
      }

     
      .content {
        box-sizing: border-box;
        display: block;
        margin: 0 auto;
        max-width: '580px';
        padding: '10px'; 
      }

     
      .main {
        background: #ffffff;
        border-radius: '3px';
        width: 100%; 
      }

      .wrapper {
        box-sizing: border-box;
        padding: '20px'; 
      }

      .content-block {
        padding-bottom: '10px';
        padding-top: '10px';
      }

      .footer {
        clear: both;
        margin-top: '10px';
        text-align: center;
        width: 100%; 
      }
        .footer td,
        .footer p,
        .footer span,
        .footer a {
          color: #999999;
          font-size: '12px';
          text-align: center; 
      }

      
      h1,
      h2,
      h3,
      h4 {
        color: '#000000';
        font-family: 'sans-serif';
        font-weight: 400;
        line-height: 1.4;
        margin: 0;
        margin-bottom: '30px'; 
      }

      h1 {
        font-size: '35px';
        font-weight: 300;
        text-align: 'center';
        text-transform: 'capitalize'; 
      }

      p,
      ul,
      ol {
        font-family: sans-serif;
        font-size: '14px';
        font-weight: normal;
        margin: 0;
        margin-bottom: '15px'; 
      }
        p li,
        ul li,
        ol li {
          list-style-position: inside;
          margin-left: '5px'; 
      }

      a {
        color: '#3498db';
        text-decoration: underline; 
      }

     
      .btn {
        box-sizing: border-box;
        width: 100%; }
        .btn > tbody > tr > td {
          padding-bottom: '15px'; }
        .btn table {
          width: auto; 
      }
        .btn table td {
          background-color: #ffffff;
          border-radius: '5px';
          text-align: center; 
      }
        .btn a {
          background-color: #ffffff;
          border: solid '1px #3498db';
          border-radius: '5px';
          box-sizing: border-box;
          color: '#3498db';
          cursor: pointer;
          display: inline-block;
          font-size: '14px';
          font-weight: bold;
          margin: 0;
          padding: '12px 25px';
          text-decoration: none;
          text-transform: capitalize; 
      }

      .btn-primary table td {
        background-color: '#3498db'; 
      }

      .btn-primary a {
        background-color: '#3498db';
        border-color: '#3498db';
        color: #ffffff; 
      }

      
      .last {
        margin-bottom: 0; 
      }

      .first {
        margin-top: 0; 
      }

      .align-center {
        text-align: center; 
      }

      .align-right {
        text-align: right; 
      }

      .align-left {
        text-align: left; 
      }

      .clear {
        clear: both; 
      }

      .mt0 {
        margin-top: 0; 
      }

      .mb0 {
        margin-bottom: 0; 
      }

      .preheader {
        color: transparent;
        display: none;
        height: 0;
        max-height: 0;
        max-width: 0;
        opacity: 0;
        overflow: hidden;
        mso-hide: all;
        visibility: hidden;
        width: 0; 
      }

      .powered-by a {
        text-decoration: none; 
      }

      hr {
        border: 0;
        border-bottom: '1px' solid #f6f6f6;
        margin: '20px' 0; 
      }

      
      @media only screen and (max-width: 620px) {
        table.body h1 {
            font-size: '28px !important';
            margin-bottom: '10px !important'; 
        }
        table.body p,
        table.body ul,
        table.body ol,
        table.body td,
        table.body span,
        table.body a {
          font-size: '16px !important'; 
        }
        table.body .wrapper,
        table.body .article {
          padding: '10px !important'; 
        }
        table.body .content {
          padding: 0 '!important'; 
        }
        table.body .container {
          padding: 0 '!important';
          width: 100% '!important'; 
        }
        table.body .main {
          border-left-width: 0 '!important';
          border-radius: 0 '!important';
          border-right-width: 0 '!important'; 
        }
        table.body .btn table {
          width: 100% '!important'; 
        }
        table.body .btn a {
          width: 100% '!important'; 
        }
        table.body .img-responsive {
          height: auto '!important';
          max-width: 100% '!important';
          width: auto '!important'; 
        }
      }

     
      @media all {
        .ExternalClass {
          width: 100%; 
        }
        .ExternalClass,
        .ExternalClass p,
        .ExternalClass span,
        .ExternalClass font,
        .ExternalClass td,
        .ExternalClass div {
          line-height: 100%; 
        }
        .apple-link a {
          color: inherit '!important';
          font-family: inherit '!important';
          font-size: inherit '!important';
          font-weight: inherit '!important';
          line-height: inherit '!important';
          text-decoration: none '!important'; 
        }
        #MessageViewBody a {
          color: inherit;
          text-decoration: none;
          font-size: inherit;
          font-family: inherit;
          font-weight: inherit;
          line-height: inherit;
        }
        .btn-primary table td:hover {
          background-color: '#34495e !important'; 
        }
        .btn-primary a:hover {
          background-color: '#34495e !important';
          border-color: '#34495e !important'; 
        } 
      }

    </style>
  </head>
  <body>
    <span class="preheader">The result of the scraping of the Adidas web site is ready</span>
    <table role="presentation" border="0" cellpadding="0" cellspacing="0" class="body">
      <tr>
        <td>&nbsp;</td>
        <td class="container">
          <div class="content">

            <!-- START CENTERED WHITE CONTAINER -->
            <table role="presentation" class="main">

              <!-- START MAIN CONTENT AREA -->
              <tr>
                <td class="wrapper">
                  <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                    <tr>
                      <td>
                                <p> Hello there!  </p>
                                <p> The result of the scraping of the Adidas web site is ready. </p>
                                <p> Reach the <strong> """ + file_name + """ </strong> file for the date <strong> """ + date + """ </strong>, and exact time is <strong> """ + hour + """ </strong>. </p>
                                <p> <strong> """ + str(len(df)) + """ </strong> out of a total of <strong> """ + str(len(self.count)) + """ </strong> products are sold out. </p>
     
                      </td>
                    </tr>
                  </table>
                </td>
              </tr>

          
            </table>
          

           
            <div class="footer">
              <table role="presentation" border="0" cellpadding="0" cellspacing="0">
                <tr>
                  <td class="content-block">
                    <span class="apple-link">Astoria Avm Kat.2, No:127 Buyukdere Caddesi, Istanbul/Turkiye </span>
                  </td>
                </tr>
                <tr>
                  <td class="content-block powered-by">
                    Powered by <a href="https://www.groupm.com.tr/">GroupM Turkiye</a>.
                  </td>
                </tr>
              </table>
            </div>
            <!-- END FOOTER -->

          </div>
        </td>
        <td>&nbsp;</td>
      </tr>
    </table>
  </body>
</html>
        """
        #print('content is ready')
        #msg = MIMEMultipart()
        #print('msg variable is created')
        #msg['From'] = from_addr
        #msg['To'] = to_addr
        #msg['Subject'] = subject
        #body = MIMEText(content, 'html')
        #print('body is created')
        #msg.attach(body)
        #print('body attached to msg')
    
        #part = MIMEApplication(csv_file, Name=basename(file_name))
        #part['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(file_name))
        #msg.attach(part)
        #print('csv file is attached to body')
        '''
        try:
          print("ON THE TRY LEVEL")
          server = smtplib.SMTP(smtp_server, port)
          server.set_debuglevel(1)
          print('server is created')
        except smtplib.SMTPException as e:
          print(e)
        server.starttls()
        print('starttles run')
        server.ehlo()  # Can be omitted
        print('ehlo run')
        server.login(from_addr, password)
        print('login is succesfull')
        server.send_message(msg, from_addr=from_addr, to_addrs=[to_addr])
        print('email is sent')
        
         # Create a secure SSL context
        context = ssl.create_default_context()
        print('context is created')
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(smtp_server, port) as server:
                print('smtplib is opened')
                server.starttls(context=context)
                print('starttles run')
                server.ehlo()  # Can be omitted
                print('ehlo run')
                server.login(from_addr, password)
                print('login is succesfull')
                server.send_message(msg, from_addr, to_addrs=[to_addr])
                print('email is sent')
        except Exception as e:
            print(e)
        '''
        # Create a recipients list
        recipients = to_addr.split(',')
        print('email recipients are defined:', recipients)

        # Set message
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = from_addr
        msg["To"] = ', '.join(recipients)

        # Set body of the message 
        body = MIMEText(content, 'html')
        msg.attach(body)
        print('body is attached to message')

        # Set attachment of the message 
        part = MIMEApplication(csv_file, Name=basename(file_name))
        part['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(file_name))
        print('content is created')

        # Attachment of the CSV file to the message 
        msg.attach(part)
        print('csv file is attached to body')
        
        # Create an SES client
        ses_client = boto3.client('ses', aws_access_key_id=access_key, aws_secret_access_key=secret_key, region_name="eu-west-1")
        print('client is created')

        # Convert message to string and send
        response = ses_client.send_raw_email(
        Source=from_addr,
        Destinations=recipients,
        RawMessage={"Data": msg.as_string()}
        )
        print(response)
        print('email is sent')
        print( f'{str(len(df))} out of a total of {str(len(self.count))} products are sold out and, total page is {math.ceil(len(self.count)/48)}' )

    

            

        
