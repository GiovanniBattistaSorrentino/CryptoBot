from msrest.authentication import CognitiveServicesCredentials
from botbuilder.ai.qna import QnAMaker, QnAMakerEndpoint, QnAMakerOptions

from config import DefaultConfig

CONFIG = DefaultConfig()

class QnAMakerManager:
    @staticmethod
    def get_qna_maker() -> QnAMaker:
        qna_maker = QnAMaker(
            QnAMakerEndpoint(
                knowledge_base_id=CONFIG.QNA_KNOWLEDGEBASE_ID,
                endpoint_key=CONFIG.QNA_ENDPOINT_KEY,
                host=CONFIG.QNA_ENDPOINT_HOST,
            )
        )
        return qna_maker


    @staticmethod
    def get_qna_maker_top_qna(top_options=10) -> QnAMaker:
        qna_maker = QnAMaker(
            QnAMakerEndpoint(
                knowledge_base_id=CONFIG.QNA_KNOWLEDGEBASE_ID,
                endpoint_key=CONFIG.QNA_ENDPOINT_KEY,
                host=CONFIG.QNA_ENDPOINT_HOST,
            ), QnAMakerOptions(
                top=top_options
            )
        )
        return qna_maker