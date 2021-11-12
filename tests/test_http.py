from urllib.request import urlopen


def test_urllib_basic_get(httpserver):
    body = 'Simple HTTP webpage'
    endpoint = '/simple-test'
    httpserver.expect_request(endpoint).respond_with_data(body)
    with urlopen(httpserver.url_for(endpoint)) as response:
        result = response.read().decode()
    assert body == result
