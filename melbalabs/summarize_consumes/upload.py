import webbrowser

import requests

from melbalabs.summarize_consumes.main import generate_output


def main():

    output = generate_output()

    username, password = 'summarize_consumes', 'summarize_consumes'
    auth = requests.auth.HTTPBasicAuth(username, password)
    data = output.getvalue().encode('utf8')
    response = requests.post(
        url='http://ix.io',
        files={'f:1': data},
        auth=auth,
        timeout=30,
    )

    print(response.text)
    if 'already exists' in response.text:
        print("didn't get a new url")
        import pdb;pdb.set_trace()
    else:
        url = response.text.strip().split('\n')[-1]
        webbrowser.open(url)


if __name__ == '__main__':
    main()
