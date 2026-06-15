
class SearchController:

    def __init__(
        self,
        view,
        youtube_service
    ):
        self.view = view
        self.youtube_service = youtube_service

        self.view.start_btn.clicked.connect(
            self.search
        )

    def search(self):

        keyword = (
            self.view.keyword_input.text()
        )

        result = self.youtube_service.search_channels(
            keyword
        )

        print(result)