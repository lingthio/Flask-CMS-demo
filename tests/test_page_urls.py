# Copyright 2014 SolidBuilds.com. All rights reserved
#
# Authors: Ling Thio <ling.thio@gmail.com>

from __future__ import print_function  # Use print() instead of print
from flask import url_for


def test_page_urls(client):
    # Visit home page
    response = client.get(url_for('home_page'), follow_redirects=True)
    assert response.status_code==200

    # Login as user and visit User page
    response = client.post(
        url_for('user.login'), follow_redirects=True,
        data=dict(email='editor@example.com', password='Password1'))
    assert response.status_code==200

    # Logout
    response = client.get(url_for('user.logout'), follow_redirects=True)
    assert response.status_code==200
