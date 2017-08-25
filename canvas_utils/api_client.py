"""
Добропорядочно утащил из интернета
"""
import requests

from .models import Accounts


class CanvasAPIClient:
    """
    API client for Canvas platform
    """
    def __init__(self, app_id, token):
        """
        :param app_id: app identifier
        e.g "www.canvas-lms.com"
        :param token: and auth token from canvas-lms.
        see https://canvas.instructure.com/doc/api/file.oauth.html for details
        :return: CanvasAPI object
        """
        # save the api address for all future requests
        self.address = 'https://{}.netacad.com/api/v1'.format(app_id)
        self.headers = {
            'Authorization': 'Bearer {}'.format(token),
            'Content-Type': 'application/json'
        }
        self.accounts = Accounts(self)

    def get(self, url, absolute=False):
        """
        :param url: string, the url for the request.
        e.g "courses" or "https://www.canvas-lms.com/api/v1/courses"
        :param absolute: boolean, notes if the url is absolute or relative.
        e.g "https://www.canvas-lms.com/api/v1/courses" or "courses"
        :return: urllib.response object with the response for the request.
        """
        # If URL is absolute, then use it as it was provided.
        if absolute:
            request_url = url
        # Otherwise, augment the URL with the server address
        else:
            request_url = self.address + url

        # GET request to the url
        response = requests.get(request_url, headers=self.headers)
        # raise any errors
        response.raise_for_status()
        # return response
        return response

    def pages(self, url, absolute=False):
        """
        :param url: string, the url for the request.
        e.g "courses" or "https://www.canvas-lms.com/api/v1/courses"
        :param absolute: boolean, notes if the url is absolute or relative.
        e.g "https://www.canvas-lms.com/api/v1/courses" or "courses"
        :return: generator object, generates the pages of the response one by one.
        """
        # Make the initial call to the API to retrieve the first page.
        while True:
            # call the API to retrieve the page.
            response = self.get(url, absolute)
            # Send back the page if it's not None.
            if response:
                yield response
            else:
                break
            # Check if there are more pages of results.
            header = response.headers.get('Link')
            # If there is a 'Link' header, then search for a 'next' link.
            if header:
                # All the links are separated by commas.
                url = self.find_link(header.split(','), 'next')
                # The url from the link will be absolute.
                absolute = True
                if url is None:
                    # If we didn't find a 'next' link, then stop.
                    break
            else:
                # If we didn't find a 'Link' header, stop.
                break

    def get_all(self, url, absolute=False):
        """
        :param url: string, the url for the request.
        e.g "courses" or "https://www.canvas-lms.com/api/v1/courses"
        :param absolute: boolean, notes if the url is absolute or relative.
        e.g "https://www.canvas-lms.com/api/v1/courses" or "courses"
        :return:list, of all the pages of the response.
        """
        # A list to accumulate all of the results from all of the pages.
        results = []
        # Read all of the pages of results from this API call.
        for _page in self.pages(url, absolute):
            results += _page.json()
        return results

    def post(self, url, data=None):
        """ post data """
        response = requests.post(
            self.address + url,
            json=data,
            headers=self.headers
        )
        # raise any errors
        response.raise_for_status()
        return response

    def put(self, url, data=None):
        """ pud data """
        # PUT request to the url
        response = requests.put(
            self.address + url,
            json=data,
            headers=self.headers
        )
        # raise any errors
        response.raise_for_status()
        # return response
        return response

    @staticmethod
    def find_link(links, rel):
        """ find links """
        for lnk in links:
            # URL, and 'rel' attribute
            parts = lnk.split(';')
            if rel in parts[1]:
                return parts[0].strip('<>')
        return None
