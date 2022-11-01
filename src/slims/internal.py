import base64
import os
from typing import Any, Callable, List, Optional, Sequence, Union

import requests
from requests_oauthlib import OAuth2Session
from werkzeug.local import Local

local = Local()


def _slims_local() -> Local:
    return local


class _SlimsApiException(Exception):
    pass


class _SlimsApi(object):

    def __init__(self,
                 url: str,
                 username: str = None,
                 password: str = None,
                 repo_location: str = None,
                 oauth: bool = False,
                 token_updater: Callable = None,
                 redirect_url: str = "",
                 client_id: str = None,
                 client_secret: str = None,
                 **request_params: Any):
        self.url = url + ("" if url.endswith('/') else '/') + "rest/"
        self.raw_url = url + ("" if url.endswith('/') else '/')
        self.username = username
        self.password = password
        self.repo_location = repo_location
        self.oauth = oauth
        self.client_id = client_id
        self.client_secret = client_secret
        self.request_params = request_params
        if self.oauth:
            if self.client_id is None:
                raise _SlimsApiException(
                    "client_id is required when using OAuth")
            if self.client_secret is None:
                raise _SlimsApiException(
                    "client_secret is required when using OAuth")
            self.oauth_session = OAuth2Session(client_id,
                                               redirect_uri=redirect_url,
                                               scope=["api"],
                                               auto_refresh_url=self.raw_url + "oauth/token",
                                               token_updater=token_updater)
        elif self.username is None or self.password is None:
            raise _SlimsApiException(
                "Username and password are required when not using OAuth")

    def get_entities(self, url: str, body: dict[str, Any] = None) -> List['Record']:
        if(self.url.startswith('https') and url.startswith('http') and url[4:].startswith(self.url[5:])):
            url = 'https' + url[4:]
        if not url.startswith(self.url):
            url = self.url + url

        if self.oauth:
            response = self.oauth_session.get(
                url, headers=_SlimsApi._headers(), json=body, **self.request_params)
        else:
            assert self.username is not None and self.password is not None
            response = requests.get(url,
                                    auth=(self.username, self.password),
                                    headers=_SlimsApi._headers(),
                                    json=body,
                                    **self.request_params)
        records: List['Record'] = []
        if response.status_code == 200:
            for entity in response.json()["entities"]:
                if entity["tableName"] == "Attachment":
                    records.append(Attachment(entity, self))
                else:
                    records.append(Record(entity, self))
            return records
        else:
            raise _SlimsApiException(
                "Could not fetch entities: " + response.text)

    def get(self, url: str) -> requests.Response:
        if self.oauth:
            return self.oauth_session.get(self.url + url,
                                          headers=_SlimsApi._headers(),
                                          client_id=self.client_id,
                                          client_secret=self.client_secret,
                                          **self.request_params)
        else:
            assert self.username is not None and self.password is not None
            return requests.get(self.url + url,
                                auth=(self.username, self.password),
                                headers=_SlimsApi._headers(),
                                **self.request_params)

    def post(self, url: str, body: dict[str, Any] = None) -> requests.Response:
        if self.oauth:
            return self.oauth_session.post(self.url + url,
                                           json=body,
                                           headers=_SlimsApi._headers(),
                                           client_id=self.client_id,
                                           client_secret=self.client_secret,
                                           **self.request_params)
        else:
            assert self.username is not None and self.password is not None
            return requests.post(self.url + url, json=body,
                                 auth=(self.username, self.password),
                                 headers=_SlimsApi._headers(),
                                 **self.request_params)

    def put(self, url: str, body: dict[str, Any] = None) -> requests.Response:
        if self.oauth:
            return self.oauth_session.put(self.url + url,
                                          json=body,
                                          headers=_SlimsApi._headers(),
                                          client_id=self.client_id,
                                          client_secret=self.client_secret,
                                          **self.request_params)
        else:
            assert self.username is not None and self.password is not None
            return requests.put(self.url + url, json=body,
                                auth=(self.username, self.password),
                                headers=_SlimsApi._headers(),
                                **self.request_params)

    def delete(self, url: str) -> requests.Response:
        if self.oauth:
            return self.oauth_session.delete(self.url + url,
                                             headers=_SlimsApi._headers(),
                                             client_id=self.client_id,
                                             client_secret=self.client_secret,
                                             **self.request_params)
        else:
            assert self.username is not None and self.password is not None
            return requests.delete(self.url + url,
                                   auth=(self.username, self.password),
                                   headers=_SlimsApi._headers(),
                                   **self.request_params)

    def authorization_url(self) -> str:
        return self.oauth_session.authorization_url(self.raw_url + "oauth/authorize", **self.request_params)[0]

    def fetch_token(self, code: Optional[Any]) -> dict[str, Any]:
        return self.oauth_session.fetch_token(self.raw_url + 'oauth/token',
                                              client_id=self.client_id,
                                              client_secret=self.client_secret,
                                              code=code,
                                              **self.request_params)

    @staticmethod
    def _headers() -> dict[str, Any]:
        try:
            return {'X-SLIMS-REQUESTED-FOR': local.user}
        except AttributeError:
            return {}


class Column(object):

    def __init__(self, json_column: dict[str, Any]):
        self.__dict__.update(json_column)


class Record(object):
    """ A single record in SLims. Can be of any table, represents one row in the
    database

    Columns can be accessed as properties.

    Examples:
        >>> content = slims.fetch_by_pk("Content", 1)
            print(content.cntn_id.value)
    """

    def __init__(self, json_entity: dict[str, Any], slims_api: _SlimsApi):
        self.json_entity = json_entity
        self.slims_api = slims_api

        for json_column in json_entity["columns"]:
            column = Column(json_column)
            self.__dict__[column.name] = column

    def update(self, values: dict[str, Any]) -> 'Record':
        """ Updates this record

        Args:
            values (dict): Values to update

        Returns:
            The updated record

        Examples:
            >>> content = slims.fetch_by_pk("Content", 1)
                content.update({"cntn_id": "new id"})

            Fetches the content record with primary key 1 and changes
            its id to "new id"
        """
        url = self.table_name() + "/" + str(self.pk())
        response = self.slims_api.post(url=url, body=values)
        if response.status_code != 200:
            raise _SlimsApiException("Update failed: " + response.text)
        new_values = response.json()["entities"][0]
        return Record(new_values, self.slims_api)

    def remove(self) -> None:
        """
        Removes this record.
        """
        url = self.table_name() + "/" + str(self.pk())
        response = self.slims_api.delete(url=url)
        if response.status_code != 200:
            raise _SlimsApiException("Delete failed: " + response.text)

    def table_name(self) -> str:
        """
        Returns:
            The name of the table of this record
        """
        return self.json_entity["tableName"]

    def pk(self) -> int:
        """
        Returns:
            The primary key of this record
        """
        return self.json_entity["pk"]

    def attachments(self) -> Sequence['Record']:
        """
        Returns:
            The attachments related to this record
        """
        return self.slims_api.get_entities(
            "attachment/" + self.json_entity["tableName"] + "/" + str(self.json_entity["pk"]))

    def add_attachment(self, name: str, byte_array: Any) -> int:
        """Adds an attachment to a record (over HTTP).

        Args:
            name (string): The name of the attachment
            byte_array (byte array): The binary content of the attachment

        Returns:
            The primary key of the added attachment

        Examples:
            >>> content.add_attachment("test.txt", b"Hi from python")

            Adds a string as an attachment to a content record

            >>> with open(file_name, 'rb') as to_upload:
                    content.add_attachment("test.txt", to_upload.read())

            Uploads a file as an attachment in SLims
        """

        body = {
            "attm_name": name,
            "atln_recordPk": self.pk(),
            "atln_recordTable": self.table_name(),
            "contents": base64.b64encode(byte_array).decode("utf-8")
        }
        response = self.slims_api.post(url="repo", body=body)
        location = response.headers['Location']
        return int(location[location.rfind("/") + 1:])

    def column(self, column_name: str) -> Column:
        """
        Args:
            column_name (string): The name of the column

        Returns:
            A column of the record

        Examples:
            >>> print(content.column("cntn_id").value)
            >>> print(column.cntn_id.value)

        """
        return self.__dict__[column_name]

    def follow(self, link_name: str) -> Union[Optional['Record'], Sequence['Record']]:
        """
        Follows an incoming or outgoing foreign key

        Args:
            link_name(string): field linking two tables.
                The links should start with a - (minus) if the link is incoming.

        Returns:
            One record (or None) when the link is outgoing
            A list of records when the link is incoming

        Examples:
            >>> content_type = slims.fetch_by_pk("Content", 1)
                    .follow("cntn_fk_contentType")

            This fetches the content record with primary key 1 and then fetches
            its content type (one record).

            >>> results = slims.fetch_by_pk("Content", 1)
                    .follow("-rslt_fk_content")

            This fetches the content record with primary key 1 and then fetches
            its results (a list of records)
        """
        for link in self.json_entity["links"]:
            if link["rel"] == link_name:
                href = link["href"]
                entities = self.slims_api.get_entities(href)
                if link_name.startswith("-"):
                    return entities
                else:
                    if len(entities) > 0:
                        return entities[0]
                    else:
                        return None
        raise KeyError(str(link_name) + "not found in the list of links")


class Attachment(Record):
    """ An extension of the Record class. Returned when the table of the
    record is Attachment."""

    def __init__(self, json_entity: dict[str, Any], slims_api: _SlimsApi):
        super().__init__(json_entity, slims_api)

    def get_local_path(self) -> str:
        """
        Returns:
            The location of an attachment on disk
        Note:
            Only works when slims is defined with a repo_location
        """
        if self.slims_api.repo_location:
            return os.path.join(self.slims_api.repo_location, self.attm_path.value)
        else:
            raise RuntimeError("no repo_location configured")

    def download_to(self, location: str) -> None:
        """
        Downloads an attachment to a file on disk

        Args:
            location(string): The path on disk to download the file to

        Examples:
            >>> attachment.download_to("test.txt")
        """
        with open(location, 'wb') as destination:
            response = self.slims_api.get("repo/" + str(self.pk()))
            destination.write(response.content)
