"""
CMS Video
"""

import os
import requests
from bok_choy.promise import EmptyPromise, Promise
from bok_choy.javascript import wait_for_js, js_defined
from ....tests.helpers import YouTubeStubConfig
from ...lms.video.video import VideoPage


CLASS_SELECTORS = {
    'video_container': 'div.video',
    'video_init': '.is-initialized',
    'video_xmodule': '.xmodule_VideoModule',
    'video_spinner': '.video-wrapper .spinner',
    'video_controls': 'section.video-controls',
    'attach_handout': '.upload-dialog > input[type="file"]',
    'upload_dialog': '.wrapper-modal-window-assetupload',
    'xblock': '.add-xblock-component',
}

BUTTON_SELECTORS = {
    'create_video': "a[data-category='video']",
    'handout_download': '.video-handout.video-download-button a',
    'handout_download_editor': '.wrapper-comp-setting.file-uploader .download-action',
    'upload_handout': '.upload-action',
    'handout_submit': '.action-upload',
    'handout_clear': '.wrapper-comp-setting.file-uploader .setting-clear',
}


@js_defined('window.Video', 'window.RequireJS.require', 'window.jQuery', 'window.XModule', 'window.XBlock',
            'window.MathJax.isReady')
class VideoComponentPage(VideoPage):
    """
    CMS Video Component Page
    """

    url = None

    @wait_for_js
    def is_browser_on_page(self):
        return self.q(css='div{0}'.format(CLASS_SELECTORS['video_xmodule'])).present or self.q(
            css='div{0}'.format(CLASS_SELECTORS['xblock'])).present

    def get_element_selector(self, video_display_name, class_name, vertical=True):
        return super(VideoComponentPage, self).get_element_selector(None, class_name, vertical=False)

    def _wait_for(self, check_func, desc, result=False, timeout=200):
        """
        Calls the method provided as an argument until the Promise satisfied or BrokenPromise

        Arguments:
            check_func (callable): Promise function to be fulfilled.
            desc (str): Description of the Promise, used in log messages.
            result (bool): Indicates whether we need result from Promise or not
            timeout (float): Maximum number of seconds to wait for the Promise to be satisfied before timing out.

        """
        if result:
            return Promise(check_func, desc, timeout=timeout).fulfill()
        else:
            return EmptyPromise(check_func, desc, timeout=timeout).fulfill()

    def wait_for_video_component_render(self):
        """
        Wait until video component rendered completely
        """
        if not YouTubeStubConfig.get_configuration().get('youtube_api_blocked'):
            self._wait_for(lambda: self.q(css=CLASS_SELECTORS['video_init']).present, 'Video Player Initialized')
            self._wait_for(lambda: not self.q(css=CLASS_SELECTORS['video_spinner']).visible, 'Video Buffering Completed')
            self._wait_for(lambda: self.q(css=CLASS_SELECTORS['video_controls']).visible, 'Player Controls are Visible')

    def click_button(self, button_name):
        """
        Click on a button as specified by `button_name`

        Arguments:
            button_name (str): button name

        """
        self.q(css=BUTTON_SELECTORS[button_name]).first.click()
        self.wait_for_ajax()

    @staticmethod
    def file_path(filename):
        """
        Construct file path to be uploaded to assets.

        Arguments:
            filename (str): asset filename

        """
        return os.sep.join(__file__.split(os.sep)[:-5]) + '/data/uploads/' + filename

    def upload_handout(self, handout_filename):
        """
        Upload a handout file to assets

        Arguments:
            handout_filename (str): handout file name

        """
        handout_path = self.file_path(handout_filename)

        self.click_button('upload_handout')

        self.q(css=CLASS_SELECTORS['attach_handout']).results[0].send_keys(handout_path)

        self.click_button('handout_submit')

        # confirm upload completion
        self._wait_for(lambda: not self.q(css=CLASS_SELECTORS['upload_dialog']).present, 'Upload Handout Completed')

    def clear_handout(self):
        """
        Clear handout from settings
        """
        self.click_button('handout_clear')

    def _get_handout(self, url):
        """
        Download handout at `url`
        """
        kwargs = dict()

        session_id = [{i['name']: i['value']} for i in self.browser.get_cookies() if i['name'] == u'sessionid']
        if session_id:
            kwargs.update({
                'cookies': session_id[0]
            })

        response = requests.get(url, **kwargs)
        return response.status_code < 400, response.headers

    def download_handout(self, mime_type, is_editor=False):
        """
        Download handout with mime type specified by `mime_type`

        Arguments:
            mime_type (str): mime type of handout file

        Returns:
            tuple: Handout download result.

        """
        selector = BUTTON_SELECTORS['handout_download_editor'] if is_editor else BUTTON_SELECTORS['handout_download']

        handout_url = self.q(css=selector).attrs('href')[0]
        result, headers = self._get_handout(handout_url)

        return result, headers['content-type'] == mime_type

    @property
    def is_handout_button_visible(self):
        """
        Check if handout download button is visible
        """
        # TODO! Remove .present below after bok-choy is updated to latest commit, Only .visible is enough
        return self.q(css=BUTTON_SELECTORS['handout_download']).present and self.q(
            css=BUTTON_SELECTORS['handout_download']).visible

    def _goto_files_upload_page(self):
        """
        Navigate to `Files & Uploads` page
        """
        menu_selector = 'li.nav-course-courseware'
        uploads_selector = 'li.nav-course-courseware-uploads a'

        self.q(css=menu_selector).first.click()
        self.q(css=uploads_selector).first.click()

        # Ensure that `Upload New File` button is visible
        upload_new_file_button_selector = '.upload-button.new-button'
        self._wait_for(lambda: self.q(css=upload_new_file_button_selector).visible, 'Upload New File is Visible')

    def upload_subtitles(self, subtitle_filename):
        """
        Upload subtitle file specified by `subtitle_filename`

        Arguments:
            subtitle_filename (str): subtitle filename

        """
        self._goto_files_upload_page()

        upload_new_file_button_selector = '.upload-button.new-button'
        self.q(css=upload_new_file_button_selector).first.click()

        # Ensure File Upload Modal Dialog is Visible
        upload_dialog_selector = '.modal-body'
        self._wait_for(lambda: self.q(css=upload_dialog_selector).visible, 'Upload New File Dialog is Visible')

        # Selenium send_keys function only works with visible web elements
        # The Browse button on upload dialog is hidden due to class="file-input"
        # which causes the selenium to through an ElementNotVisibleException
        # So we first remove class="file-input" to make Browse button visible
        js_code = '$(".file-chooser > input").removeClass( "file-input" )'
        self.browser.execute_script(js_code)

        attach_file_selector = '.file-chooser input[type="file"]'
        self.q(css=attach_file_selector).results[0].send_keys(self.file_path(subtitle_filename))

        upload_status_selector = '.progress-fill'
        self._wait_for(lambda: 'Upload completed' in self.q(css=upload_status_selector).text[0], 'Upload Completed')

        upload_dialog_close_selector = '.close-button'
        self.q(css=upload_dialog_close_selector).first.click()
