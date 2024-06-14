from flask import Flask, Response, request
from zeep import Client, helpers
from collections import OrderedDict
import pandas as pd

from datetime import  datetime, timedelta
import xml.etree.ElementTree as ET
from xml.dom import minidom

app = Flask(__name__)

# URL của dịch vụ ASMX
asmx_url = 'http://qlps.vtv.gov.vn/webserviceLPSNew/Service1.asmx?WSDL'



@app.route('/api/query', methods=['GET'])
def get_data():

    # lay param truyen vao tu url
    param_kenh = request.args.get('kenh')
    param_serviceid = request.args.get('serviceid')
    param_songay = int(request.args.get('songay'))
    print(f'{param_kenh} , {param_serviceid} , {param_songay}')

    # List lay tong dữ liệu tra về
    total_event_list = list()


    # lap lay du lieu theo songay
    for i in range(param_songay):
        # Tạo một client để gọi dịch vụ ASMX
        client = Client(asmx_url)

        # lay ngay hien tai
        curent_day = datetime.now()
        # so ngay lay theo i
        get_day = curent_day + timedelta(days=i)
        str_get_day = get_day.strftime('%d/%m/%Y')
        print(str_get_day)
        try:
            # Gọi hàm từ dịch vụ ASMX
            response = client.service.GetChuongtrinh(str_get_day, param_kenh)

            # Chuyển đổi dữ liệu trả về thành DataFrame
            data_dict = helpers.serialize_object(response)
            # print(type(data_dict))
            # print(data_dict['_value_1']['_value_1'][0]['Table']['MaCT'])
            # print(data_dict['_value_1']['_value_1'][0])
            # for key,value in data_dict['_value_1']['_value_1'][0].items():
            #     print(key,value, end='\n')

            # do dai du lieu
            data_dict_length = len(data_dict['_value_1']['_value_1'])
            # print(type(data_dict['_value_1']['_value_1'])) # ->list
            print(f'So event ngay thu {i+1} la: {data_dict_length} event')

            # for key, value in data_dict.items():
            #     print(key + value)

            # total_data_dict = OrderedDict(data_dict['_value_1']['_value_1'])
            # total_data_dict.update(total_data_dict)
            # print(total_data_dict)

            # total_data_list = data_dict['_value_1']['_value_1'] + data_dict['_value_1']['_value_1']
            # Cộng dư liêu các ngày vào total
            total_event_list = total_event_list + data_dict['_value_1']['_value_1']
        except Exception as e:
            return Response(f"<error>{str(e)}</error>", mimetype='text/html')

    print(f'tong so event sau khi update: {len(total_event_list)}')

    #tao xml
    # tao root <eit>
    root = ET.Element('eit', attrib={'total-events': str(len(total_event_list))})


    # Tạo phần tử <event>
    event = ET.SubElement(root, 'event')
    # Tạo và thêm phần tử 'id' vào 'event'
    id_element = ET.SubElement(event, 'id', attrib={'event-id': '20360959', 'service-id': param_serviceid})
    # Tạo phần tử <info> và thêm các phần tử con vào info'
    info = ET.SubElement(event, 'info')

    start_time = ET.SubElement(info, 'start-time')
    start_time.text = '2024-06-06T05:00:00Z'

    duration = ET.SubElement(info, 'duration')
    duration.text = '2400'

    content_type = ET.SubElement(info, 'content-type')
    content_type.text = '0'

    free_ca_mode = ET.SubElement(info, 'free-ca-mode')
    free_ca_mode.text = '0'

    # Tạo phần tử <description> và thêm các phần tử con vào 'description'
    description = ET.SubElement(event, 'description')

    language_code = ET.SubElement(description, 'language-code')
    language_code.text = 'vie'

    name = ET.SubElement(description, 'name')
    name.text = 'Thời sự'

    short_description = ET.SubElement(description, 'short-description')
    short_description.text = 'Thời sự 12h00'

    long_description = ET.SubElement(description, 'long-description')

    # Tạo và thêm phần tử 'rating' vào 'event'
    rating = ET.SubElement(event, 'rating', attrib={'country_code': '902', 'rating': '0', 'position': '0'})

    # Chuyển đổi cây phần tử thành một chuỗi XML
    xml_str = ET.tostring(root, encoding='utf-8')

    # Sử dụng minidom để thêm khai báo DOCTYPE và làm đẹp chuỗi XML
    parsed_str = minidom.parseString(xml_str)
    pretty_xml_as_string = parsed_str.toprettyxml(indent="    ")

    # Thêm khai báo DOCTYPE
    doctype = '<!DOCTYPE eit SYSTEM "eit.dtd">\n'
    xml_declaration = '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n'

    final_xml_str = xml_declaration + doctype + pretty_xml_as_string

    # return Response(final_xml_str, mimetype='application/xml')

    print(final_xml_str)

    # tạo df để show table ra web
    df = pd.DataFrame(total_event_list)

    # Chuyển đổi DataFrame thành bảng HTML
    html_table = df.to_html()

    # Trả về bảng HTML
    return Response(html_table, mimetype='text/html')



if __name__ == '__main__':
    app.run(debug=True)