from flask import Flask, Response
from zeep import Client, helpers
import pandas as pd

app = Flask(__name__)

# URL của dịch vụ ASMX
asmx_url = 'http://qlps.vtv.gov.vn/webserviceLPSNew/Service1.asmx?WSDL'

# Tạo một client để gọi dịch vụ ASMX
client = Client(asmx_url)

@app.route('/getData', methods=['GET'])
def get_data():
    try:
        # Gọi hàm từ dịch vụ ASMX
        response = client.service.GetChuongtrinh('13/06/2024', 'VTV8')

        print(type(response))
        print(response)
        print(response['_value_1'])
        print(type(response['_value_1']))
        #
        if str(response['_value_1'])[:8] != '<Element':

            # Chuyển đổi dữ liệu trả về thành DataFrame
            data_dict = helpers.serialize_object(response)
            df = pd.DataFrame(data_dict['_value_1']['_value_1'][0])
            print(type(data_dict['_value_1']['_value_1']))
            print(type(data_dict['_value_1']['_value_1'][0]))
            print(type(data_dict['_value_1']['_value_1'][0]['Table']))
            print(type(data_dict['_value_1']['_value_1'][0]['Table']['MaCT']))

            # Chuyển đổi DataFrame thành bảng HTML
            html_table = df.to_html()

            # Trả về bảng HTML
            return Response(html_table, mimetype='text/html')
            print(f'Có dữ liệu')
        else:
            return 'Không co du lieu'
    except Exception as e:
        return Response(f"<error>{str(e)}</error>", mimetype='text/html')

if __name__ == '__main__':
    app.run(debug=True)